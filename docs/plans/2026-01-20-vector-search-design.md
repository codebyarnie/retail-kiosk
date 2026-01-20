# Vector Search & Embeddings Design

**Date:** 2026-01-20
**Status:** Approved
**Phase:** 3 (Vector Search & Embeddings)

## Overview

Enable semantic product search using vector embeddings with background processing for data sync.

## Architecture

```
JSON File → [Celery Worker] → PostgreSQL (products)
                ↓
         [EmbeddingService] → Qdrant (vectors)
                ↑
User Query → [SearchService] → Results
```

## Key Decisions

1. **Embedding model:** all-MiniLM-L6-v2 (80MB, 384 dimensions, CPU-friendly)
2. **Embedding timing:** Background worker on data changes (fast queries, fresh data)
3. **Data import:** JSON file import via worker task (matches retail POS workflows)

## Components

### EmbeddingService

```python
class EmbeddingService:
    MODEL_NAME = "all-MiniLM-L6-v2"
    VECTOR_SIZE = 384

    def __init__(self):
        self.model = SentenceTransformer(MODEL_NAME)

    def generate_embedding(self, text: str) -> list[float]
    def batch_embeddings(self, texts: list[str]) -> list[list[float]]
    def get_product_text(self, product: Product) -> str
        # Combines: name + description + category names
```

### Qdrant Collection

- Collection name: `products`
- Vector size: 384
- Distance metric: Cosine similarity
- Payload fields: `sku`, `name`, `price`, `category_ids`

### Celery Tasks

- `sync_product_data(file_path: str)` - Parse JSON, upsert to PostgreSQL, trigger embeddings
- `update_product_embeddings(sku: str | None)` - Generate embeddings, upsert to Qdrant
- `cleanup_stale_vectors()` - Remove vectors for deleted products

### SearchService Changes

Update `_semantic_search()` to:
1. Generate query embedding
2. Search Qdrant with filters
3. Fetch products from PostgreSQL by SKU

## Data Flow

### Product Import

1. Place products.json in backend/data/
2. Trigger: POST /api/admin/sync-products or celery call
3. sync_product_data task:
   - Parse JSON, upsert products to PostgreSQL
   - Queue update_product_embeddings for each SKU
4. update_product_embeddings task:
   - Generate text: "{name}. {description}. Categories: {categories}"
   - Generate embedding via EmbeddingService
   - Upsert to Qdrant with payload

### Search

1. User query → GET /api/search?q=...
2. Generate embedding for query
3. Search Qdrant (top 50, apply filters)
4. Fetch Products from PostgreSQL by SKU
5. Return with relevance scores
6. Fallback to keyword search if Qdrant fails

## JSON File Format

```json
{
  "products": [
    {
      "sku": "DRL-001",
      "name": "DeWalt 20V Hammer Drill",
      "description": "Cordless hammer drill for masonry...",
      "price": 199.99,
      "categories": ["power-tools", "drills"],
      "image_url": "/images/drl-001.jpg",
      "attributes": {"voltage": "20V", "brand": "DeWalt"}
    }
  ]
}
```

## Error Handling

- **Qdrant unavailable:** Fallback to keyword search
- **Embedding model failure:** Worker retries with exponential backoff
- **Invalid JSON:** Task fails, no partial updates
- **Product not found:** Skip and log, continue others
- **Duplicate SKU:** Last entry wins (upsert)

## Initialization

- Qdrant collection created lazily by worker (not blocking API startup)
- Collection recreated if schema changes

## Files to Create

- `backend/app/services/embedding_service.py`
- `backend/app/worker/celery_app.py`
- `backend/app/worker/tasks.py`
- `backend/app/worker/__init__.py`
- `backend/data/products.json` (sample catalog)

## Files to Modify

- `backend/app/services/search_service.py` - Complete semantic search
- `backend/requirements.txt` - Add sentence-transformers

## Dependencies

```
sentence-transformers>=2.2.0
qdrant-client>=1.7.0
celery[redis]>=5.3.0
```

## Testing

- Unit tests for EmbeddingService (mock model)
- Unit tests for Celery tasks (mock DB, Qdrant)
- Integration test: JSON → PostgreSQL → Qdrant → Search
- Fallback test: Simulate Qdrant failure
