"""Search service for semantic product search using Qdrant."""

from typing import Optional

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models import Category, Product, ProductCategory
from app.services.embedding_service import get_embedding_service
from app.services.qdrant_service import QdrantService


class SearchService:
    """Service for product search business logic."""

    # Qdrant collection name for product embeddings
    COLLECTION_NAME = "products"

    def __init__(self, db: AsyncSession) -> None:
        """Initialize the search service."""
        self.db = db
        self._qdrant_client = None

    @property
    def qdrant_client(self):
        """Lazy initialization of Qdrant client."""
        if self._qdrant_client is None:
            try:
                from qdrant_client import QdrantClient

                self._qdrant_client = QdrantClient(
                    host=settings.qdrant_host,
                    port=settings.qdrant_port,
                    api_key=settings.qdrant_api_key,
                    prefer_grpc=settings.qdrant_prefer_grpc,
                )
            except Exception:
                # Qdrant not available, will use keyword search fallback
                self._qdrant_client = None
        return self._qdrant_client

    async def search_products(
        self,
        query: str,
        *,
        category_id: Optional[int] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        attributes: Optional[dict] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[list[tuple[Product, float]], int]:
        """
        Search products using semantic search with fallback to keyword search.

        Args:
            query: Search query string
            category_id: Optional category filter
            min_price: Optional minimum price filter
            max_price: Optional maximum price filter
            attributes: Optional attribute filters
            skip: Number of results to skip
            limit: Maximum results to return

        Returns:
            Tuple of (list of (product, score) tuples, total count)
        """
        # Try semantic search first if Qdrant is available
        if self.qdrant_client:
            try:
                return await self._semantic_search(
                    query,
                    category_id=category_id,
                    min_price=min_price,
                    max_price=max_price,
                    attributes=attributes,
                    skip=skip,
                    limit=limit,
                )
            except Exception:
                # Fall back to keyword search
                pass

        # Keyword search fallback
        return await self._keyword_search(
            query,
            category_id=category_id,
            min_price=min_price,
            max_price=max_price,
            attributes=attributes,
            skip=skip,
            limit=limit,
        )

    async def _semantic_search(
        self,
        query: str,
        *,
        category_id: Optional[int] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        attributes: Optional[dict] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[list[tuple[Product, float]], int]:
        """
        Perform semantic search using Qdrant vector database.

        This method:
        1. Generates embedding for the query
        2. Searches Qdrant for similar product embeddings
        3. Applies filters (category, price, attributes)
        4. Returns products with relevance scores
        """
        # Generate query embedding
        embedding_service = get_embedding_service()
        query_embedding = embedding_service.generate_embedding(query)

        # Prepare category filter
        category_ids = None
        if category_id:
            category_ids = [category_id]

        # Search Qdrant
        qdrant_service = QdrantService()
        qdrant_results = qdrant_service.search(
            query_embedding=query_embedding,
            limit=limit + skip,  # Get extra for pagination
            price_min=min_price,
            price_max=max_price,
            category_ids=category_ids,
        )

        if not qdrant_results:
            return [], 0

        # Extract SKUs and scores
        sku_scores = {sku: score for sku, score in qdrant_results}
        skus = list(sku_scores.keys())

        # Fetch products from database
        products_query = select(Product).where(
            Product.sku.in_(skus),
            Product.is_active == True,
        )
        result = await self.db.execute(products_query)
        products = list(result.scalars().all())

        # Create product-score pairs maintaining Qdrant order
        scored_results = []
        for product in products:
            if product.sku in sku_scores:
                scored_results.append((product, sku_scores[product.sku]))

        # Sort by score descending
        scored_results.sort(key=lambda x: x[1], reverse=True)

        # Apply pagination
        total = len(scored_results)
        paginated = scored_results[skip : skip + limit]

        return paginated, total

    async def _keyword_search(
        self,
        query: str,
        *,
        category_id: Optional[int] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        attributes: Optional[dict] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[list[tuple[Product, float]], int]:
        """
        Perform keyword-based search as fallback.

        Searches in product name, description, and SKU.
        """
        # Build search query with ILIKE for case-insensitive matching
        search_term = f"%{query}%"

        base_query = select(Product).where(
            Product.is_active == True,
            or_(
                Product.name.ilike(search_term),
                Product.description.ilike(search_term),
                Product.short_description.ilike(search_term),
                Product.sku.ilike(search_term),
            ),
        )

        # Apply filters
        if category_id:
            base_query = base_query.join(ProductCategory).where(
                ProductCategory.category_id == category_id
            )

        if min_price is not None:
            base_query = base_query.where(Product.price >= min_price)

        if max_price is not None:
            base_query = base_query.where(Product.price <= max_price)

        # TODO: Implement attribute filtering with JSONB

        # Get total count
        count_query = select(func.count()).select_from(base_query.subquery())
        count_result = await self.db.execute(count_query)
        total = count_result.scalar() or 0

        # Apply pagination and execute
        base_query = base_query.offset(skip).limit(limit).order_by(Product.name)
        result = await self.db.execute(base_query)
        products = list(result.scalars().all())

        # Assign scores based on match quality (simple scoring for keyword search)
        scored_results = []
        query_lower = query.lower()
        for product in products:
            score = 0.5  # Base score
            if query_lower in product.name.lower():
                score += 0.3
            if product.sku.lower() == query_lower:
                score = 1.0
            scored_results.append((product, min(score, 1.0)))

        # Sort by score descending
        scored_results.sort(key=lambda x: x[1], reverse=True)

        return scored_results, total

    async def get_search_suggestions(
        self, partial_query: str, limit: int = 5
    ) -> list[dict]:
        """
        Get search suggestions based on partial query.

        Returns suggestions from:
        - Product names
        - Category names
        - Popular searches (future)
        """
        search_term = f"{partial_query}%"
        suggestions = []

        # Product name suggestions
        product_result = await self.db.execute(
            select(Product.name)
            .where(Product.is_active == True, Product.name.ilike(search_term))
            .limit(limit)
        )
        for (name,) in product_result:
            suggestions.append({"text": name, "type": "product"})

        # Category suggestions
        category_result = await self.db.execute(
            select(Category.name)
            .where(Category.is_active == True, Category.name.ilike(search_term))
            .limit(limit)
        )
        for (name,) in category_result:
            suggestions.append({"text": name, "type": "category"})

        return suggestions[:limit]

    async def get_filter_facets(
        self, category_id: Optional[int] = None
    ) -> dict:
        """
        Get available filter facets for the search UI.

        Returns aggregated values for filterable attributes.
        """
        # Get price range
        price_query = select(
            func.min(Product.price),
            func.max(Product.price),
        ).where(Product.is_active == True)

        if category_id:
            price_query = price_query.join(ProductCategory).where(
                ProductCategory.category_id == category_id
            )

        price_result = await self.db.execute(price_query)
        min_price, max_price = price_result.one()

        # Get categories
        categories_query = select(Category).where(Category.is_active == True)
        if category_id:
            # Get sibling categories
            parent_result = await self.db.execute(
                select(Category.parent_id).where(Category.id == category_id)
            )
            parent_id = parent_result.scalar()
            if parent_id:
                categories_query = categories_query.where(
                    Category.parent_id == parent_id
                )

        categories_result = await self.db.execute(categories_query)
        categories = list(categories_result.scalars().all())

        return {
            "price_range": {"min": min_price or 0, "max": max_price or 0},
            "categories": categories,
            # TODO: Add dynamic attribute facets from JSONB data
        }
