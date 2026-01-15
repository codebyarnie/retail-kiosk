# Development Guidelines

## Table of Contents

1. [Development Environment Setup](#development-environment-setup)
2. [Project Structure](#project-structure)
3. [Development Workflow](#development-workflow)
4. [Code Organization](#code-organization)
5. [Coding Standards](#coding-standards)
6. [Testing Strategy](#testing-strategy)
7. [Git Workflow](#git-workflow)
8. [Code Review Guidelines](#code-review-guidelines)
9. [Performance Best Practices](#performance-best-practices)
10. [Troubleshooting](#troubleshooting)

---

## Development Environment Setup

### Prerequisites

Ensure you have the following installed:

- **Docker** 20.10+ and **Docker Compose** 2.0+
- **Python** 3.11+ with pip
- **Node.js** 18+ and npm 9+
- **Git** 2.30+
- **Make** (optional but recommended)
- **VS Code** or **PyCharm** (recommended IDEs)

### Initial Setup

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd retail-kiosk
   ```

2. **Start infrastructure services**:
   ```bash
   make up
   # This starts PostgreSQL, Redis, and Qdrant in Docker
   ```

3. **Install all dependencies**:
   ```bash
   make install
   # Or install services individually:
   # make install-backend
   # make install-frontend
   # make install-worker
   ```

4. **Set up environment variables**:
   ```bash
   # Copy example environment files
   cp backend/.env.example backend/.env
   cp frontend/.env.example frontend/.env
   cp worker/.env.example worker/.env

   # Edit .env files with your local configuration
   ```

5. **Run database migrations**:
   ```bash
   make db-migrate
   ```

6. **Verify installation**:
   ```bash
   # Check backend
   cd backend && python verify_installation.py

   # Check frontend
   cd frontend && npm run type-check
   ```

### IDE Configuration

#### VS Code

Install recommended extensions:
- Python (Microsoft)
- Pylance
- ESLint
- Prettier
- Tailwind CSS IntelliSense
- Docker

Workspace settings (`.vscode/settings.json`):
```json
{
  "python.linting.enabled": true,
  "python.linting.ruffEnabled": true,
  "python.formatting.provider": "black",
  "python.formatting.blackArgs": ["--line-length", "100"],
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": true,
    "source.organizeImports": true
  },
  "[typescript]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  },
  "[typescriptreact]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  },
  "[python]": {
    "editor.defaultFormatter": "ms-python.black-formatter"
  }
}
```

#### PyCharm

Configure Python interpreter:
1. File → Settings → Project → Python Interpreter
2. Add interpreter → Virtualenv Environment → Existing environment
3. Point to `backend/.venv/bin/python`

Enable formatters:
1. Settings → Tools → Black → On save
2. Settings → Tools → External Tools → Add Ruff

---

## Project Structure

### Overall Structure

```
retail-kiosk/
├── .github/              # GitHub Actions workflows
│   └── workflows/
│       └── ci.yml        # CI/CD pipeline
├── backend/              # FastAPI backend service
│   ├── app/
│   │   ├── models/       # SQLAlchemy models
│   │   ├── routes/       # API endpoints
│   │   ├── services/     # Business logic
│   │   ├── schemas/      # Pydantic schemas
│   │   ├── dependencies/ # FastAPI dependencies
│   │   ├── config.py     # Configuration
│   │   └── main.py       # Application entry
│   ├── alembic/          # Database migrations
│   ├── tests/            # Backend tests
│   ├── Dockerfile
│   ├── requirements.txt
│   └── pyproject.toml
├── frontend/             # React frontend
│   ├── src/
│   │   ├── components/   # Reusable components
│   │   ├── features/     # Feature modules
│   │   ├── hooks/        # Custom hooks
│   │   ├── services/     # API clients
│   │   ├── stores/       # Zustand stores
│   │   ├── types/        # TypeScript types
│   │   ├── utils/        # Utilities
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── public/           # Static assets
│   ├── Dockerfile
│   ├── package.json
│   └── vite.config.ts
├── worker/               # Celery workers
│   ├── tasks/            # Task definitions
│   ├── celery_app.py     # Celery config
│   ├── config.py         # Worker settings
│   └── requirements.txt
├── docs/                 # Documentation
│   ├── ARCHITECTURE.md
│   └── DEVELOPMENT.md
├── docker-compose.yml    # Local development services
├── Makefile              # Development commands
└── README.md             # Project overview
```

### Backend Structure (Detailed)

```
backend/app/
├── __init__.py
├── main.py              # FastAPI app initialization
├── config.py            # Settings and configuration
│
├── models/              # Database models (SQLAlchemy)
│   ├── __init__.py
│   ├── base.py          # Base model class
│   ├── product.py       # Product model
│   ├── session.py       # Session model
│   └── list.py          # List model
│
├── schemas/             # Request/response schemas (Pydantic)
│   ├── __init__.py
│   ├── product.py       # Product schemas
│   ├── search.py        # Search request/response
│   └── list.py          # List schemas
│
├── routes/              # API endpoints
│   ├── __init__.py
│   ├── products.py      # Product endpoints
│   ├── search.py        # Search endpoints
│   └── lists.py         # List management
│
├── services/            # Business logic
│   ├── __init__.py
│   ├── product_service.py
│   ├── search_service.py
│   └── list_service.py
│
├── dependencies/        # FastAPI dependencies
│   ├── __init__.py
│   ├── database.py      # DB session dependency
│   ├── cache.py         # Redis dependency
│   └── auth.py          # Session validation
│
└── middleware/          # Custom middleware
    ├── __init__.py
    ├── logging.py       # Request logging
    └── error_handler.py # Error handling
```

### Frontend Structure (Detailed)

```
frontend/src/
├── main.tsx             # Entry point
├── App.tsx              # Root component
│
├── components/          # Shared UI components
│   ├── common/          # Generic components
│   │   ├── Button.tsx
│   │   ├── Input.tsx
│   │   └── Modal.tsx
│   ├── layout/          # Layout components
│   │   ├── Header.tsx
│   │   ├── Footer.tsx
│   │   └── Sidebar.tsx
│   └── product/         # Product-specific
│       ├── ProductCard.tsx
│       └── ProductGrid.tsx
│
├── features/            # Feature modules
│   ├── search/
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── services/
│   │   └── types.ts
│   ├── products/
│   └── lists/
│
├── hooks/               # Custom React hooks
│   ├── useDebounce.ts
│   ├── useLocalStorage.ts
│   └── useInfiniteScroll.ts
│
├── services/            # API and external services
│   ├── api.ts           # Axios instance
│   ├── productApi.ts    # Product API client
│   └── searchApi.ts     # Search API client
│
├── stores/              # Global state (Zustand)
│   ├── useListStore.ts  # Shopping list state
│   └── useSessionStore.ts # Session state
│
├── types/               # TypeScript definitions
│   ├── product.ts
│   ├── search.ts
│   └── api.ts
│
└── utils/               # Utility functions
    ├── format.ts        # Formatting helpers
    ├── validation.ts    # Validation functions
    └── constants.ts     # App constants
```

---

## Development Workflow

### Daily Development

1. **Start services**:
   ```bash
   # Terminal 1: Infrastructure
   make up

   # Terminal 2: Backend
   make backend-dev

   # Terminal 3: Frontend
   make frontend-dev

   # Terminal 4: Worker (if needed)
   make worker-dev
   ```

2. **Make changes**:
   - Edit code in your IDE
   - Hot reload will automatically update
   - Check browser console for errors

3. **Run tests**:
   ```bash
   # All tests
   make test

   # Backend only
   make test-backend

   # Frontend only
   make test-frontend

   # Watch mode (backend)
   make test-watch
   ```

4. **Check code quality**:
   ```bash
   # Lint and format
   make lint
   make format

   # Or individually
   make lint-backend
   make format-frontend
   ```

5. **Commit changes**:
   ```bash
   git add .
   git commit -m "feat: add product search functionality"
   git push
   ```

### Adding a New Feature

1. **Create a feature branch**:
   ```bash
   git checkout -b feature/product-recommendations
   ```

2. **Backend changes**:
   ```bash
   # 1. Create model (if needed)
   # backend/app/models/recommendation.py

   # 2. Create schema
   # backend/app/schemas/recommendation.py

   # 3. Create service
   # backend/app/services/recommendation_service.py

   # 4. Create route
   # backend/app/routes/recommendations.py

   # 5. Add tests
   # backend/tests/test_recommendations.py

   # 6. Run migrations (if model added)
   cd backend
   alembic revision --autogenerate -m "add recommendation model"
   alembic upgrade head
   ```

3. **Frontend changes**:
   ```bash
   # 1. Create feature directory
   mkdir -p frontend/src/features/recommendations

   # 2. Add components
   # frontend/src/features/recommendations/components/RecommendationList.tsx

   # 3. Add API service
   # frontend/src/services/recommendationApi.ts

   # 4. Add types
   # frontend/src/types/recommendation.ts

   # 5. Add tests
   # frontend/src/features/recommendations/__tests__/RecommendationList.test.tsx
   ```

4. **Test the feature**:
   ```bash
   # Backend tests
   cd backend
   pytest tests/test_recommendations.py -v

   # Frontend tests
   cd frontend
   npm run test -- recommendations
   ```

5. **Update documentation**:
   - Add API documentation in backend route
   - Update README if user-facing
   - Add comments for complex logic

### Database Migrations

#### Creating a Migration

```bash
cd backend

# Generate migration from model changes
alembic revision --autogenerate -m "add product reviews"

# Create empty migration for data changes
alembic revision -m "populate product categories"
```

#### Applying Migrations

```bash
# Upgrade to latest
alembic upgrade head

# Upgrade by 1 version
alembic upgrade +1

# Downgrade by 1 version
alembic downgrade -1

# View current version
alembic current

# View migration history
alembic history
```

#### Migration Best Practices

- ✅ Always review auto-generated migrations
- ✅ Test migrations on copy of production data
- ✅ Make migrations reversible when possible
- ✅ Use batch operations for large tables
- ❌ Never edit applied migrations
- ❌ Don't mix schema and data changes

---

## Code Organization

### Backend Code Organization

#### Models (SQLAlchemy)

```python
# backend/app/models/product.py
from sqlalchemy import Column, Integer, String, Float, JSON
from sqlalchemy.orm import relationship
from .base import Base

class Product(Base):
    """Product model representing items in the catalog."""

    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    sku = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    description = Column(String, nullable=True)
    price = Column(Float, nullable=False)
    metadata = Column(JSON, nullable=True)

    # Relationships
    reviews = relationship("Review", back_populates="product")

    def __repr__(self):
        return f"<Product(sku={self.sku}, name={self.name})>"
```

#### Schemas (Pydantic)

```python
# backend/app/schemas/product.py
from pydantic import BaseModel, Field
from typing import Optional

class ProductBase(BaseModel):
    """Base product schema with common fields."""

    sku: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    price: float = Field(..., gt=0)

class ProductCreate(ProductBase):
    """Schema for creating a new product."""
    pass

class ProductUpdate(BaseModel):
    """Schema for updating a product (all fields optional)."""

    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    price: Optional[float] = Field(None, gt=0)

class ProductResponse(ProductBase):
    """Schema for product responses."""

    id: int

    class Config:
        from_attributes = True  # Pydantic v2
```

#### Services (Business Logic)

```python
# backend/app/services/product_service.py
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..models.product import Product
from ..schemas.product import ProductCreate, ProductUpdate

class ProductService:
    """Service for product-related business logic."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_product_by_sku(self, sku: str) -> Optional[Product]:
        """Get product by SKU."""
        result = await self.db.execute(
            select(Product).where(Product.sku == sku)
        )
        return result.scalar_one_or_none()

    async def list_products(
        self, skip: int = 0, limit: int = 100
    ) -> List[Product]:
        """List products with pagination."""
        result = await self.db.execute(
            select(Product).offset(skip).limit(limit)
        )
        return result.scalars().all()

    async def create_product(self, product_data: ProductCreate) -> Product:
        """Create a new product."""
        product = Product(**product_data.model_dump())
        self.db.add(product)
        await self.db.commit()
        await self.db.refresh(product)
        return product

    async def update_product(
        self, product_id: int, product_data: ProductUpdate
    ) -> Optional[Product]:
        """Update an existing product."""
        product = await self.db.get(Product, product_id)
        if not product:
            return None

        update_data = product_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(product, field, value)

        await self.db.commit()
        await self.db.refresh(product)
        return product
```

#### Routes (API Endpoints)

```python
# backend/app/routes/products.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from ..dependencies.database import get_db
from ..services.product_service import ProductService
from ..schemas.product import ProductResponse, ProductCreate, ProductUpdate

router = APIRouter(prefix="/products", tags=["Products"])

@router.get("/", response_model=List[ProductResponse])
async def list_products(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    """
    List all products with pagination.

    - **skip**: Number of products to skip (default: 0)
    - **limit**: Maximum number of products to return (default: 100, max: 1000)
    """
    if limit > 1000:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Limit cannot exceed 1000"
        )

    service = ProductService(db)
    products = await service.list_products(skip=skip, limit=limit)
    return products

@router.get("/{sku}", response_model=ProductResponse)
async def get_product(
    sku: str,
    db: AsyncSession = Depends(get_db),
):
    """Get a product by SKU."""
    service = ProductService(db)
    product = await service.get_product_by_sku(sku)

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with SKU '{sku}' not found"
        )

    return product

@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    product_data: ProductCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new product."""
    service = ProductService(db)

    # Check if SKU already exists
    existing = await service.get_product_by_sku(product_data.sku)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Product with SKU '{product_data.sku}' already exists"
        )

    product = await service.create_product(product_data)
    return product
```

### Frontend Code Organization

#### Components

```typescript
// frontend/src/components/product/ProductCard.tsx
import React from 'react';
import { Product } from '../../types/product';

interface ProductCardProps {
  product: Product;
  onAddToList?: (product: Product) => void;
  onView?: (product: Product) => void;
}

export const ProductCard: React.FC<ProductCardProps> = ({
  product,
  onAddToList,
  onView,
}) => {
  const handleAddClick = () => {
    onAddToList?.(product);
  };

  const handleCardClick = () => {
    onView?.(product);
  };

  return (
    <div
      className="product-card border rounded-lg p-4 hover:shadow-lg transition-shadow cursor-pointer"
      onClick={handleCardClick}
    >
      {product.imageUrl && (
        <img
          src={product.imageUrl}
          alt={product.name}
          className="w-full h-48 object-cover rounded-md mb-3"
        />
      )}

      <h3 className="text-lg font-semibold mb-2">{product.name}</h3>

      <p className="text-gray-600 text-sm mb-3 line-clamp-2">
        {product.description}
      </p>

      <div className="flex items-center justify-between">
        <span className="text-xl font-bold">${product.price.toFixed(2)}</span>

        <button
          onClick={(e) => {
            e.stopPropagation();
            handleAddClick();
          }}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
        >
          Add to List
        </button>
      </div>
    </div>
  );
};
```

#### Custom Hooks

```typescript
// frontend/src/hooks/useDebounce.ts
import { useState, useEffect } from 'react';

export function useDebounce<T>(value: T, delay: number = 500): T {
  const [debouncedValue, setDebouncedValue] = useState<T>(value);

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => {
      clearTimeout(handler);
    };
  }, [value, delay]);

  return debouncedValue;
}
```

#### API Services

```typescript
// frontend/src/services/productApi.ts
import axios from 'axios';
import { Product, ProductSearchParams, ProductSearchResponse } from '../types/product';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const productApi = {
  /**
   * Search products by query
   */
  async searchProducts(params: ProductSearchParams): Promise<ProductSearchResponse> {
    const { data } = await api.get<ProductSearchResponse>('/search', { params });
    return data;
  },

  /**
   * Get product by SKU
   */
  async getProduct(sku: string): Promise<Product> {
    const { data } = await api.get<Product>(`/products/${sku}`);
    return data;
  },

  /**
   * List products with pagination
   */
  async listProducts(skip: number = 0, limit: number = 100): Promise<Product[]> {
    const { data } = await api.get<Product[]>('/products', {
      params: { skip, limit },
    });
    return data;
  },
};
```

#### State Management (Zustand)

```typescript
// frontend/src/stores/useListStore.ts
import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { Product } from '../types/product';

interface ListItem {
  product: Product;
  quantity: number;
}

interface ListStore {
  items: ListItem[];
  addItem: (product: Product) => void;
  removeItem: (sku: string) => void;
  updateQuantity: (sku: string, quantity: number) => void;
  clearList: () => void;
  getTotalItems: () => number;
}

export const useListStore = create<ListStore>()(
  persist(
    (set, get) => ({
      items: [],

      addItem: (product) => {
        const items = get().items;
        const existingIndex = items.findIndex((item) => item.product.sku === product.sku);

        if (existingIndex >= 0) {
          // Increment quantity if already in list
          const newItems = [...items];
          newItems[existingIndex].quantity += 1;
          set({ items: newItems });
        } else {
          // Add new item
          set({ items: [...items, { product, quantity: 1 }] });
        }
      },

      removeItem: (sku) => {
        set({ items: get().items.filter((item) => item.product.sku !== sku) });
      },

      updateQuantity: (sku, quantity) => {
        const items = get().items;
        const index = items.findIndex((item) => item.product.sku === sku);

        if (index >= 0) {
          const newItems = [...items];
          newItems[index].quantity = quantity;
          set({ items: newItems });
        }
      },

      clearList: () => {
        set({ items: [] });
      },

      getTotalItems: () => {
        return get().items.reduce((total, item) => total + item.quantity, 0);
      },
    }),
    {
      name: 'shopping-list', // LocalStorage key
    }
  )
);
```

---

## Coding Standards

### Python (Backend/Worker)

#### Style Guide

- **Line Length**: 100 characters
- **Indentation**: 4 spaces
- **Quotes**: Double quotes for strings
- **Imports**: Organized by stdlib, third-party, local
- **Type Hints**: Required for all function signatures
- **Docstrings**: Google style for all public functions/classes

#### Linting & Formatting

- **Ruff**: Fast Python linter (replaces Flake8, isort, pydocstyle)
- **Black**: Code formatter
- **Mypy**: Static type checker

```bash
# Run linters
ruff check backend/
mypy backend/

# Format code
black backend/

# Auto-fix issues
ruff check --fix backend/
```

#### Example

```python
"""
Module docstring describing the purpose.
"""

from typing import List, Optional
import logging

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


class ProductService:
    """
    Service for product-related operations.

    This service encapsulates business logic for product management
    including CRUD operations and search functionality.
    """

    def __init__(self, db: AsyncSession) -> None:
        """
        Initialize the product service.

        Args:
            db: Database session for queries
        """
        self.db = db

    async def get_products(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Product]:
        """
        Retrieve a list of products with pagination.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of product instances

        Raises:
            HTTPException: If database query fails
        """
        try:
            # Implementation here
            pass
        except Exception as e:
            logger.error(f"Failed to fetch products: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")
```

### TypeScript (Frontend)

#### Style Guide

- **Line Length**: 80 characters
- **Indentation**: 2 spaces
- **Quotes**: Single quotes for strings
- **Semicolons**: Required
- **Type Annotations**: Explicit types for function parameters and returns
- **Comments**: JSDoc for exported functions/components

#### Linting & Formatting

- **ESLint**: JavaScript/TypeScript linter
- **Prettier**: Code formatter
- **TypeScript**: Type checker

```bash
# Run linters
npm run lint

# Format code
npm run format

# Type check
npm run type-check
```

#### Example

```typescript
/**
 * Props for the ProductGrid component.
 */
interface ProductGridProps {
  /** Array of products to display */
  products: Product[];
  /** Called when a product is selected */
  onProductSelect?: (product: Product) => void;
  /** Grid column configuration */
  columns?: number;
}

/**
 * ProductGrid component displays products in a responsive grid layout.
 *
 * @example
 * ```tsx
 * <ProductGrid
 *   products={products}
 *   onProductSelect={(product) => console.log(product)}
 *   columns={3}
 * />
 * ```
 */
export const ProductGrid: React.FC<ProductGridProps> = ({
  products,
  onProductSelect,
  columns = 4,
}) => {
  const handleClick = (product: Product): void => {
    onProductSelect?.(product);
  };

  return (
    <div className={`grid grid-cols-${columns} gap-4`}>
      {products.map((product) => (
        <ProductCard
          key={product.sku}
          product={product}
          onClick={() => handleClick(product)}
        />
      ))}
    </div>
  );
};
```

### Naming Conventions

#### Python

- **Variables/Functions**: `snake_case`
- **Classes**: `PascalCase`
- **Constants**: `UPPER_SNAKE_CASE`
- **Private**: `_leading_underscore`
- **Files**: `snake_case.py`

```python
# Good
MAX_RETRIES = 3
user_name = "John"

class ProductService:
    def get_products(self):
        pass

# Bad
maxRetries = 3
UserName = "John"

class product_service:
    def GetProducts(self):
        pass
```

#### TypeScript

- **Variables/Functions**: `camelCase`
- **Classes/Components**: `PascalCase`
- **Constants**: `UPPER_SNAKE_CASE`
- **Interfaces/Types**: `PascalCase`
- **Files**: `PascalCase.tsx` (components), `camelCase.ts` (utilities)

```typescript
// Good
const MAX_ITEMS = 100;
const userName = 'John';

interface ProductProps {
  name: string;
}

function getProduct(): Product {
  return {};
}

// Bad
const max_items = 100;
const UserName = 'John';

interface productProps {
  name: string;
}

function GetProduct(): Product {
  return {};
}
```

---

## Testing Strategy

### Backend Testing (pytest)

#### Test Structure

```
backend/tests/
├── conftest.py           # Shared fixtures
├── test_models.py        # Model tests
├── test_services.py      # Service tests
├── test_routes.py        # API endpoint tests
└── integration/          # Integration tests
    └── test_search_flow.py
```

#### Example Tests

```python
# backend/tests/test_services.py
import pytest
from app.services.product_service import ProductService
from app.schemas.product import ProductCreate

@pytest.mark.asyncio
async def test_create_product(db_session):
    """Test creating a new product."""
    service = ProductService(db_session)

    product_data = ProductCreate(
        sku="TEST-001",
        name="Test Product",
        description="Test description",
        price=19.99,
    )

    product = await service.create_product(product_data)

    assert product.id is not None
    assert product.sku == "TEST-001"
    assert product.name == "Test Product"
    assert product.price == 19.99

@pytest.mark.asyncio
async def test_get_product_by_sku(db_session, sample_product):
    """Test retrieving a product by SKU."""
    service = ProductService(db_session)

    product = await service.get_product_by_sku(sample_product.sku)

    assert product is not None
    assert product.sku == sample_product.sku
    assert product.name == sample_product.name

@pytest.mark.asyncio
async def test_get_nonexistent_product(db_session):
    """Test retrieving a non-existent product returns None."""
    service = ProductService(db_session)

    product = await service.get_product_by_sku("NONEXISTENT")

    assert product is None
```

#### Running Tests

```bash
# All tests
pytest backend/tests/

# Specific test file
pytest backend/tests/test_services.py

# Specific test
pytest backend/tests/test_services.py::test_create_product

# With coverage
pytest backend/tests/ --cov=app --cov-report=html

# Watch mode
pytest-watch backend/tests/
```

### Frontend Testing (Vitest + React Testing Library)

#### Test Structure

```
frontend/src/
├── components/
│   └── ProductCard/
│       ├── ProductCard.tsx
│       └── ProductCard.test.tsx
├── features/
│   └── search/
│       └── __tests__/
│           └── SearchBar.test.tsx
└── utils/
    └── __tests__/
        └── format.test.ts
```

#### Example Tests

```typescript
// frontend/src/components/ProductCard/ProductCard.test.tsx
import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { ProductCard } from './ProductCard';
import type { Product } from '../../types/product';

const mockProduct: Product = {
  sku: 'TEST-001',
  name: 'Test Product',
  description: 'Test description',
  price: 19.99,
  imageUrl: 'https://example.com/image.jpg',
};

describe('ProductCard', () => {
  it('renders product information correctly', () => {
    render(<ProductCard product={mockProduct} />);

    expect(screen.getByText('Test Product')).toBeInTheDocument();
    expect(screen.getByText('Test description')).toBeInTheDocument();
    expect(screen.getByText('$19.99')).toBeInTheDocument();
  });

  it('calls onAddToList when add button is clicked', () => {
    const onAddToList = vi.fn();
    render(<ProductCard product={mockProduct} onAddToList={onAddToList} />);

    const addButton = screen.getByText('Add to List');
    fireEvent.click(addButton);

    expect(onAddToList).toHaveBeenCalledWith(mockProduct);
    expect(onAddToList).toHaveBeenCalledTimes(1);
  });

  it('calls onView when card is clicked', () => {
    const onView = vi.fn();
    render(<ProductCard product={mockProduct} onView={onView} />);

    const card = screen.getByRole('article');
    fireEvent.click(card);

    expect(onView).toHaveBeenCalledWith(mockProduct);
  });
});
```

#### Running Tests

```bash
# All tests
npm run test

# Watch mode
npm run test:watch

# Coverage
npm run test:coverage

# UI mode
npm run test:ui
```

### Test Coverage Goals

- **Backend**: Minimum 80% coverage
- **Frontend**: Minimum 70% coverage
- **Critical paths**: 100% coverage (authentication, payment, etc.)

---

## Git Workflow

### Branch Strategy

- **main**: Production-ready code
- **develop**: Integration branch for features
- **feature/***: New features
- **bugfix/***: Bug fixes
- **hotfix/***: Emergency production fixes

### Branch Naming

```
feature/add-product-recommendations
bugfix/fix-search-pagination
hotfix/security-patch-jwt
```

### Commit Message Format

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `perf`: Performance improvements
- `test`: Adding/updating tests
- `chore`: Build process or auxiliary tool changes
- `ci`: CI/CD changes

**Examples**:

```
feat(search): add semantic search with Qdrant

Implement natural language product search using vector embeddings.
Includes caching layer and fallback to keyword search.

Closes #123
```

```
fix(api): handle null values in product description

Previous implementation crashed when description was null.
Now returns empty string for null descriptions.

Fixes #456
```

### Pull Request Process

1. **Create PR** from feature branch to develop
2. **Fill PR template** with description and checklist
3. **Request review** from 1-2 team members
4. **Pass CI checks** (tests, linting, type-checking)
5. **Address feedback** and make requested changes
6. **Squash and merge** once approved

### Pre-commit Hooks

Pre-commit hooks run automatically before each commit:

```bash
# Install pre-commit hooks
pre-commit install

# Run manually on all files
pre-commit run --all-files

# Skip hooks (not recommended)
git commit --no-verify
```

---

## Code Review Guidelines

### As a Reviewer

**Focus on**:
- ✅ Code correctness and logic
- ✅ Test coverage
- ✅ Performance implications
- ✅ Security concerns
- ✅ Code readability and maintainability
- ✅ Adherence to project patterns

**Avoid**:
- ❌ Nitpicking about style (let linters handle it)
- ❌ Rewriting code in your preferred style
- ❌ Requesting changes without explanation

**Review Checklist**:
- [ ] Code solves the stated problem
- [ ] Tests are comprehensive and pass
- [ ] No security vulnerabilities introduced
- [ ] Performance considerations addressed
- [ ] Documentation updated (if needed)
- [ ] No breaking changes (or properly documented)

### As an Author

**Before requesting review**:
- [ ] All tests pass locally
- [ ] Linting and formatting applied
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] PR description is clear and complete

**Responding to feedback**:
- Be open to suggestions
- Ask for clarification if needed
- Explain your reasoning
- Thank reviewers for their time

---

## Performance Best Practices

### Backend Performance

1. **Use async/await properly**:
   ```python
   # Good: Concurrent database queries
   products, reviews = await asyncio.gather(
       get_products(db),
       get_reviews(db),
   )

   # Bad: Sequential queries
   products = await get_products(db)
   reviews = await get_reviews(db)
   ```

2. **Implement caching**:
   ```python
   @lru_cache(maxsize=128)
   def get_settings():
       return Settings()

   # Redis caching
   cached = await redis.get(cache_key)
   if cached:
       return json.loads(cached)
   ```

3. **Use pagination**:
   ```python
   @router.get("/products")
   async def list_products(skip: int = 0, limit: int = 100):
       return await service.list_products(skip=skip, limit=limit)
   ```

4. **Optimize database queries**:
   ```python
   # Use eager loading to avoid N+1 queries
   products = await db.execute(
       select(Product).options(selectinload(Product.reviews))
   )
   ```

### Frontend Performance

1. **Lazy load routes**:
   ```typescript
   const ProductPage = React.lazy(() => import('./pages/ProductPage'));
   ```

2. **Memoize expensive computations**:
   ```typescript
   const sortedProducts = useMemo(
     () => products.sort((a, b) => a.price - b.price),
     [products]
   );
   ```

3. **Debounce user input**:
   ```typescript
   const debouncedQuery = useDebounce(query, 300);
   useEffect(() => {
     search(debouncedQuery);
   }, [debouncedQuery]);
   ```

4. **Optimize images**:
   ```tsx
   <img
     src={imageUrl}
     alt={alt}
     loading="lazy"
     width={400}
     height={300}
   />
   ```

---

## Troubleshooting

### Common Issues

#### Backend won't start

```bash
# Check if port 8000 is already in use
lsof -i :8000

# Kill process on port 8000
kill -9 $(lsof -t -i :8000)

# Check database connection
docker-compose ps postgres
docker-compose logs postgres
```

#### Frontend build fails

```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install

# Clear Vite cache
rm -rf node_modules/.vite
npm run dev
```

#### Database migration fails

```bash
# Check current migration status
cd backend
alembic current

# View migration history
alembic history

# Stamp database with current head (use with caution)
alembic stamp head

# Rollback and try again
alembic downgrade -1
alembic upgrade head
```

#### Tests failing

```bash
# Clear pytest cache
pytest --cache-clear

# Run tests with verbose output
pytest -vv

# Run specific failing test
pytest backend/tests/test_services.py::test_create_product -vv
```

### Getting Help

1. **Check documentation**: README.md, docs/
2. **Search issues**: GitHub issues
3. **Ask team**: Slack/Teams channel
4. **Create issue**: Detailed description with reproduction steps

---

## Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [SQLAlchemy 2.0 Documentation](https://docs.sqlalchemy.org/en/20/)
- [Pydantic V2 Documentation](https://docs.pydantic.dev/2.0/)
- [Celery Documentation](https://docs.celeryq.dev/)
- [Qdrant Documentation](https://qdrant.tech/documentation/)

---

**Happy coding! 🚀**
