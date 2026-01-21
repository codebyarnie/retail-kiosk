# Phase 6: Testing Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Comprehensive test coverage for backend services, routes, and frontend components with E2E tests.

**Architecture:** pytest for backend, vitest for frontend, Playwright for E2E

**Tech Stack:** pytest, pytest-asyncio, httpx, vitest, @testing-library/react, Playwright

---

## Task 1: Create Backend Test Fixtures

**Files:**
- Create: `backend/tests/conftest.py`
- Create: `backend/tests/factories.py`

**Step 1: Create conftest.py with fixtures**

```python
# backend/tests/conftest.py
"""Shared test fixtures for backend tests."""

import asyncio
from collections.abc import AsyncGenerator
from typing import Any

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.dependencies.database import get_db
from app.main import app
from app.models.base import Base


# Use in-memory SQLite for tests
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def db_engine():
    """Create a test database engine."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def db_session(db_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session."""
    async_session_factory = async_sessionmaker(
        db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with async_session_factory() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture(scope="function")
async def test_client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create an async test client with database override."""

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()


# Sample data fixtures
@pytest.fixture
def sample_product_data() -> dict[str, Any]:
    """Sample product data for testing."""
    return {
        "sku": "TEST-001",
        "name": "Test Product",
        "description": "A test product description",
        "short_description": "Test product",
        "price": 29.99,
        "image_url": "/images/test.jpg",
        "is_active": True,
        "is_featured": False,
    }


@pytest.fixture
def sample_category_data() -> dict[str, Any]:
    """Sample category data for testing."""
    return {
        "name": "Test Category",
        "slug": "test-category",
        "description": "A test category",
        "display_order": 1,
        "is_active": True,
    }


@pytest.fixture
def sample_list_data() -> dict[str, Any]:
    """Sample list data for testing."""
    return {
        "name": "My Shopping List",
        "description": "Items to buy",
    }
```

**Step 2: Create factories.py**

```python
# backend/tests/factories.py
"""Factory functions for creating test data."""

from datetime import datetime, timezone
from typing import Any

from app.models.product import Category, Product
from app.models.session import UserSession
from app.models.list import UserList, ListItem


def create_product(**kwargs) -> Product:
    """Create a Product model instance."""
    defaults = {
        "sku": "TEST-001",
        "name": "Test Product",
        "description": "Test description",
        "short_description": "Test",
        "price": 19.99,
        "is_active": True,
        "is_featured": False,
    }
    defaults.update(kwargs)
    return Product(**defaults)


def create_category(**kwargs) -> Category:
    """Create a Category model instance."""
    defaults = {
        "name": "Test Category",
        "slug": "test-category",
        "description": "Test category description",
        "display_order": 1,
        "is_active": True,
    }
    defaults.update(kwargs)
    return Category(**defaults)


def create_session(**kwargs) -> UserSession:
    """Create a UserSession model instance."""
    defaults = {
        "session_id": "test-session-123",
        "device_type": "desktop",
    }
    defaults.update(kwargs)
    return UserSession(**defaults)


def create_user_list(session_id: int, **kwargs) -> UserList:
    """Create a UserList model instance."""
    defaults = {
        "session_id": session_id,
        "list_id": "list-test-123",
        "name": "Test List",
    }
    defaults.update(kwargs)
    return UserList(**defaults)
```

**Step 3: Run tests to verify fixtures work**

Run: `cd backend && python -m pytest tests/conftest.py -v`
Expected: No errors (conftest loads)

**Step 4: Commit**

```bash
git add backend/tests/
git commit -m "test(backend): add test fixtures and factories"
```

---

## Task 2: Create ProductService Tests

**Files:**
- Create: `backend/tests/services/test_product_service.py`

**Step 1: Write tests**

```python
# backend/tests/services/test_product_service.py
"""Tests for ProductService."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.product import Product, Category
from app.services.product_service import ProductService
from tests.factories import create_product, create_category


@pytest.mark.asyncio
class TestProductService:
    """Tests for ProductService."""

    async def test_get_by_sku_found(self, db_session: AsyncSession):
        """Test getting a product by SKU that exists."""
        product = create_product(sku="FOUND-001")
        db_session.add(product)
        await db_session.commit()

        service = ProductService(db_session)
        result = await service.get_by_sku("FOUND-001")

        assert result is not None
        assert result.sku == "FOUND-001"

    async def test_get_by_sku_not_found(self, db_session: AsyncSession):
        """Test getting a product by SKU that doesn't exist."""
        service = ProductService(db_session)
        result = await service.get_by_sku("NONEXISTENT")

        assert result is None

    async def test_list_products_empty(self, db_session: AsyncSession):
        """Test listing products when none exist."""
        service = ProductService(db_session)
        result = await service.list_products()

        assert result.items == []
        assert result.total == 0

    async def test_list_products_with_pagination(self, db_session: AsyncSession):
        """Test listing products with pagination."""
        for i in range(5):
            product = create_product(sku=f"PROD-{i:03d}", name=f"Product {i}")
            db_session.add(product)
        await db_session.commit()

        service = ProductService(db_session)
        result = await service.list_products(page=1, page_size=2)

        assert len(result.items) == 2
        assert result.total == 5
        assert result.pages == 3

    async def test_get_featured_products(self, db_session: AsyncSession):
        """Test getting featured products."""
        featured = create_product(sku="FEATURED-001", is_featured=True)
        regular = create_product(sku="REGULAR-001", is_featured=False)
        db_session.add_all([featured, regular])
        await db_session.commit()

        service = ProductService(db_session)
        result = await service.get_featured(limit=10)

        assert len(result) == 1
        assert result[0].sku == "FEATURED-001"

    async def test_get_by_category(self, db_session: AsyncSession):
        """Test getting products by category."""
        category = create_category(slug="tools")
        product = create_product(sku="TOOL-001")
        product.categories.append(category)
        db_session.add_all([category, product])
        await db_session.commit()

        service = ProductService(db_session)
        result = await service.get_by_category(category.id)

        assert len(result.items) == 1
        assert result.items[0].sku == "TOOL-001"
```

**Step 2: Run tests**

Run: `cd backend && python -m pytest tests/services/test_product_service.py -v`
Expected: All tests pass

**Step 3: Commit**

```bash
git add backend/tests/services/test_product_service.py
git commit -m "test(backend): add ProductService tests"
```

---

## Task 3: Create CategoryService Tests

**Files:**
- Create: `backend/tests/services/test_category_service.py`

**Step 1: Write tests**

```python
# backend/tests/services/test_category_service.py
"""Tests for CategoryService."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.category_service import CategoryService
from tests.factories import create_category, create_product


@pytest.mark.asyncio
class TestCategoryService:
    """Tests for CategoryService."""

    async def test_get_by_slug_found(self, db_session: AsyncSession):
        """Test getting a category by slug that exists."""
        category = create_category(slug="power-tools")
        db_session.add(category)
        await db_session.commit()

        service = CategoryService(db_session)
        result = await service.get_by_slug("power-tools")

        assert result is not None
        assert result.slug == "power-tools"

    async def test_get_by_slug_not_found(self, db_session: AsyncSession):
        """Test getting a category by slug that doesn't exist."""
        service = CategoryService(db_session)
        result = await service.get_by_slug("nonexistent")

        assert result is None

    async def test_list_categories(self, db_session: AsyncSession):
        """Test listing all categories."""
        cat1 = create_category(slug="cat-1", display_order=1)
        cat2 = create_category(slug="cat-2", display_order=2)
        db_session.add_all([cat1, cat2])
        await db_session.commit()

        service = CategoryService(db_session)
        result = await service.list_categories()

        assert len(result) == 2

    async def test_get_tree(self, db_session: AsyncSession):
        """Test getting category tree with parent/child relationships."""
        parent = create_category(slug="parent", name="Parent")
        db_session.add(parent)
        await db_session.flush()

        child = create_category(slug="child", name="Child", parent_id=parent.id)
        db_session.add(child)
        await db_session.commit()

        service = CategoryService(db_session)
        result = await service.get_tree()

        # Should return only root categories
        root_cats = [c for c in result if c.parent_id is None]
        assert len(root_cats) == 1
        assert root_cats[0].slug == "parent"

    async def test_get_with_products(self, db_session: AsyncSession):
        """Test getting a category with its products."""
        category = create_category(slug="drills")
        product = create_product(sku="DRILL-001")
        product.categories.append(category)
        db_session.add_all([category, product])
        await db_session.commit()

        service = CategoryService(db_session)
        result = await service.get_with_products("drills")

        assert result is not None
        assert result.slug == "drills"
```

**Step 2: Run tests**

Run: `cd backend && python -m pytest tests/services/test_category_service.py -v`
Expected: All tests pass

**Step 3: Commit**

```bash
git add backend/tests/services/test_category_service.py
git commit -m "test(backend): add CategoryService tests"
```

---

## Task 4: Create ListService Tests

**Files:**
- Create: `backend/tests/services/test_list_service.py`

**Step 1: Write tests**

```python
# backend/tests/services/test_list_service.py
"""Tests for ListService."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.list import UserListCreate, ListItemCreate
from app.services.list_service import ListService
from tests.factories import create_session, create_product


@pytest.mark.asyncio
class TestListService:
    """Tests for ListService."""

    async def test_create_list(self, db_session: AsyncSession):
        """Test creating a new list."""
        session = create_session()
        db_session.add(session)
        await db_session.commit()

        service = ListService(db_session)
        list_data = UserListCreate(name="My List")
        result = await service.create_list(session.id, list_data)

        assert result is not None
        assert result.name == "My List"
        assert result.session_id == session.id

    async def test_get_list_by_id(self, db_session: AsyncSession):
        """Test getting a list by its ID."""
        session = create_session()
        db_session.add(session)
        await db_session.commit()

        service = ListService(db_session)
        created = await service.create_list(session.id, UserListCreate(name="Test"))
        result = await service.get_list_by_id(created.list_id)

        assert result is not None
        assert result.name == "Test"

    async def test_add_item_to_list(self, db_session: AsyncSession):
        """Test adding an item to a list."""
        session = create_session()
        product = create_product(sku="ADD-001", price=10.00)
        db_session.add_all([session, product])
        await db_session.commit()

        service = ListService(db_session)
        user_list = await service.create_list(session.id, UserListCreate(name="Test"))

        item_data = ListItemCreate(product_sku="ADD-001", quantity=2)
        result = await service.add_item(user_list.list_id, item_data)

        assert result is not None
        assert result.quantity == 2
        assert result.product.sku == "ADD-001"

    async def test_remove_item_from_list(self, db_session: AsyncSession):
        """Test removing an item from a list."""
        session = create_session()
        product = create_product(sku="REM-001")
        db_session.add_all([session, product])
        await db_session.commit()

        service = ListService(db_session)
        user_list = await service.create_list(session.id, UserListCreate(name="Test"))
        await service.add_item(user_list.list_id, ListItemCreate(product_sku="REM-001"))

        result = await service.remove_item(user_list.list_id, "REM-001")

        assert result is True

        # Verify item was removed
        updated_list = await service.get_list_by_id(user_list.list_id)
        assert len(updated_list.items) == 0

    async def test_generate_share_code(self, db_session: AsyncSession):
        """Test generating a share code for a list."""
        session = create_session()
        db_session.add(session)
        await db_session.commit()

        service = ListService(db_session)
        user_list = await service.create_list(session.id, UserListCreate(name="Shareable"))

        share_code = await service.generate_share_code(user_list.list_id)

        assert share_code is not None
        assert len(share_code) > 0

    async def test_clone_list_to_session(self, db_session: AsyncSession):
        """Test cloning a list to another session via share code."""
        session1 = create_session(session_id="session-1")
        session2 = create_session(session_id="session-2")
        product = create_product(sku="CLONE-001")
        db_session.add_all([session1, session2, product])
        await db_session.commit()

        service = ListService(db_session)
        original = await service.create_list(session1.id, UserListCreate(name="Original"))
        await service.add_item(original.list_id, ListItemCreate(product_sku="CLONE-001"))
        share_code = await service.generate_share_code(original.list_id)

        # Clone to session2
        cloned = await service.clone_list_to_session(share_code, session2.id)

        assert cloned is not None
        assert cloned.session_id == session2.id
```

**Step 2: Run tests**

Run: `cd backend && python -m pytest tests/services/test_list_service.py -v`
Expected: All tests pass

**Step 3: Commit**

```bash
git add backend/tests/services/test_list_service.py
git commit -m "test(backend): add ListService tests"
```

---

## Task 5: Create Route Integration Tests

**Files:**
- Create: `backend/tests/routes/test_products.py`
- Create: `backend/tests/routes/test_categories.py`
- Create: `backend/tests/routes/test_lists.py`
- Create: `backend/tests/routes/__init__.py`

**Step 1: Create products route tests**

```python
# backend/tests/routes/test_products.py
"""Tests for product API routes."""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.factories import create_product, create_category


@pytest.mark.asyncio
class TestProductRoutes:
    """Tests for /api/products endpoints."""

    async def test_list_products_empty(self, test_client: AsyncClient):
        """Test listing products when none exist."""
        response = await test_client.get("/api/products")

        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0

    async def test_list_products(
        self, test_client: AsyncClient, db_session: AsyncSession
    ):
        """Test listing products."""
        product = create_product()
        db_session.add(product)
        await db_session.commit()

        response = await test_client.get("/api/products")

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["sku"] == product.sku

    async def test_get_product_by_sku(
        self, test_client: AsyncClient, db_session: AsyncSession
    ):
        """Test getting a specific product by SKU."""
        product = create_product(sku="GET-001")
        db_session.add(product)
        await db_session.commit()

        response = await test_client.get("/api/products/GET-001")

        assert response.status_code == 200
        data = response.json()
        assert data["sku"] == "GET-001"

    async def test_get_product_not_found(self, test_client: AsyncClient):
        """Test getting a product that doesn't exist."""
        response = await test_client.get("/api/products/NONEXISTENT")

        assert response.status_code == 404

    async def test_get_featured_products(
        self, test_client: AsyncClient, db_session: AsyncSession
    ):
        """Test getting featured products."""
        featured = create_product(sku="FEAT-001", is_featured=True)
        db_session.add(featured)
        await db_session.commit()

        response = await test_client.get("/api/products/featured")

        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
```

**Step 2: Create categories route tests**

```python
# backend/tests/routes/test_categories.py
"""Tests for category API routes."""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.factories import create_category


@pytest.mark.asyncio
class TestCategoryRoutes:
    """Tests for /api/categories endpoints."""

    async def test_list_categories(
        self, test_client: AsyncClient, db_session: AsyncSession
    ):
        """Test listing categories."""
        category = create_category()
        db_session.add(category)
        await db_session.commit()

        response = await test_client.get("/api/categories")

        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1

    async def test_get_category_tree(
        self, test_client: AsyncClient, db_session: AsyncSession
    ):
        """Test getting category tree."""
        parent = create_category(slug="parent")
        db_session.add(parent)
        await db_session.commit()

        response = await test_client.get("/api/categories/tree")

        assert response.status_code == 200

    async def test_get_category_by_slug(
        self, test_client: AsyncClient, db_session: AsyncSession
    ):
        """Test getting a category by slug."""
        category = create_category(slug="test-slug")
        db_session.add(category)
        await db_session.commit()

        response = await test_client.get("/api/categories/test-slug")

        assert response.status_code == 200
        data = response.json()
        assert data["slug"] == "test-slug"

    async def test_get_category_not_found(self, test_client: AsyncClient):
        """Test getting a category that doesn't exist."""
        response = await test_client.get("/api/categories/nonexistent")

        assert response.status_code == 404
```

**Step 3: Create lists route tests**

```python
# backend/tests/routes/test_lists.py
"""Tests for list API routes."""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.factories import create_session, create_product


@pytest.mark.asyncio
class TestListRoutes:
    """Tests for /api/lists endpoints."""

    async def test_create_list(
        self, test_client: AsyncClient, db_session: AsyncSession
    ):
        """Test creating a new list."""
        response = await test_client.post(
            "/api/lists",
            json={"name": "Test List"}
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test List"
        assert "list_id" in data

    async def test_get_list(
        self, test_client: AsyncClient, db_session: AsyncSession
    ):
        """Test getting a list by ID."""
        # First create a list
        create_response = await test_client.post(
            "/api/lists",
            json={"name": "Get Test"}
        )
        list_id = create_response.json()["list_id"]

        response = await test_client.get(f"/api/lists/{list_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Get Test"

    async def test_add_item_to_list(
        self, test_client: AsyncClient, db_session: AsyncSession
    ):
        """Test adding an item to a list."""
        product = create_product(sku="ITEM-001")
        db_session.add(product)
        await db_session.commit()

        # Create list
        create_response = await test_client.post(
            "/api/lists",
            json={"name": "Item Test"}
        )
        list_id = create_response.json()["list_id"]

        # Add item
        response = await test_client.post(
            f"/api/lists/{list_id}/items",
            json={"product_sku": "ITEM-001", "quantity": 2}
        )

        assert response.status_code == 201
        data = response.json()
        assert data["quantity"] == 2

    async def test_remove_item_from_list(
        self, test_client: AsyncClient, db_session: AsyncSession
    ):
        """Test removing an item from a list."""
        product = create_product(sku="DEL-001")
        db_session.add(product)
        await db_session.commit()

        # Create list and add item
        create_response = await test_client.post(
            "/api/lists",
            json={"name": "Delete Test"}
        )
        list_id = create_response.json()["list_id"]
        await test_client.post(
            f"/api/lists/{list_id}/items",
            json={"product_sku": "DEL-001"}
        )

        # Remove item
        response = await test_client.delete(f"/api/lists/{list_id}/items/DEL-001")

        assert response.status_code == 204

    async def test_share_list(
        self, test_client: AsyncClient, db_session: AsyncSession
    ):
        """Test generating a share code for a list."""
        create_response = await test_client.post(
            "/api/lists",
            json={"name": "Share Test"}
        )
        list_id = create_response.json()["list_id"]

        response = await test_client.post(f"/api/lists/{list_id}/share")

        assert response.status_code == 200
        data = response.json()
        assert "share_code" in data
```

**Step 4: Create __init__.py**

```python
# backend/tests/routes/__init__.py
"""Route tests package."""
```

**Step 5: Run route tests**

Run: `cd backend && python -m pytest tests/routes/ -v`
Expected: All tests pass

**Step 6: Commit**

```bash
git add backend/tests/routes/
git commit -m "test(backend): add route integration tests"
```

---

## Task 6: Create Frontend Component Tests

**Files:**
- Create: `frontend/src/components/ui/__tests__/Button.test.tsx`
- Create: `frontend/src/components/ui/__tests__/Modal.test.tsx`
- Create: `frontend/src/components/ui/__tests__/LoadingSkeleton.test.tsx`

**Step 1: Create Button tests**

```tsx
// frontend/src/components/ui/__tests__/Button.test.tsx
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Button } from '../Button';

describe('Button', () => {
  it('renders with children', () => {
    render(<Button>Click me</Button>);
    expect(screen.getByRole('button', { name: /click me/i })).toBeInTheDocument();
  });

  it('calls onClick when clicked', async () => {
    const handleClick = vi.fn();
    render(<Button onClick={handleClick}>Click</Button>);

    await userEvent.click(screen.getByRole('button'));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it('is disabled when disabled prop is true', () => {
    render(<Button disabled>Disabled</Button>);
    expect(screen.getByRole('button')).toBeDisabled();
  });

  it('applies variant classes', () => {
    const { rerender } = render(<Button variant="primary">Primary</Button>);
    expect(screen.getByRole('button')).toHaveClass('bg-primary-600');

    rerender(<Button variant="outline">Outline</Button>);
    expect(screen.getByRole('button')).toHaveClass('border');
  });

  it('applies size classes', () => {
    const { rerender } = render(<Button size="sm">Small</Button>);
    expect(screen.getByRole('button')).toHaveClass('px-3');

    rerender(<Button size="lg">Large</Button>);
    expect(screen.getByRole('button')).toHaveClass('px-6');
  });
});
```

**Step 2: Create Modal tests**

```tsx
// frontend/src/components/ui/__tests__/Modal.test.tsx
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Modal } from '../Modal';

describe('Modal', () => {
  it('renders when open', () => {
    render(
      <Modal isOpen={true} onClose={vi.fn()} title="Test Modal">
        Modal content
      </Modal>
    );
    expect(screen.getByText('Test Modal')).toBeInTheDocument();
    expect(screen.getByText('Modal content')).toBeInTheDocument();
  });

  it('does not render when closed', () => {
    render(
      <Modal isOpen={false} onClose={vi.fn()} title="Test Modal">
        Modal content
      </Modal>
    );
    expect(screen.queryByText('Test Modal')).not.toBeInTheDocument();
  });

  it('calls onClose when close button clicked', async () => {
    const onClose = vi.fn();
    render(
      <Modal isOpen={true} onClose={onClose} title="Test">
        Content
      </Modal>
    );

    await userEvent.click(screen.getByRole('button', { name: /close/i }));
    expect(onClose).toHaveBeenCalled();
  });

  it('calls onClose when escape key pressed', async () => {
    const onClose = vi.fn();
    render(
      <Modal isOpen={true} onClose={onClose} title="Test">
        Content
      </Modal>
    );

    await userEvent.keyboard('{Escape}');
    expect(onClose).toHaveBeenCalled();
  });
});
```

**Step 3: Create LoadingSkeleton tests**

```tsx
// frontend/src/components/ui/__tests__/LoadingSkeleton.test.tsx
import { render } from '@testing-library/react';
import { Skeleton, ProductCardSkeleton, ListItemSkeleton } from '../LoadingSkeleton';

describe('LoadingSkeleton', () => {
  describe('Skeleton', () => {
    it('renders with pulse animation', () => {
      const { container } = render(<Skeleton />);
      expect(container.firstChild).toHaveClass('animate-pulse');
    });

    it('applies custom className', () => {
      const { container } = render(<Skeleton className="h-10 w-20" />);
      expect(container.firstChild).toHaveClass('h-10', 'w-20');
    });
  });

  describe('ProductCardSkeleton', () => {
    it('renders skeleton structure', () => {
      const { container } = render(<ProductCardSkeleton />);
      const skeletons = container.querySelectorAll('.animate-pulse');
      expect(skeletons.length).toBeGreaterThan(0);
    });
  });

  describe('ListItemSkeleton', () => {
    it('renders skeleton structure', () => {
      const { container } = render(<ListItemSkeleton />);
      const skeletons = container.querySelectorAll('.animate-pulse');
      expect(skeletons.length).toBeGreaterThan(0);
    });
  });
});
```

**Step 4: Run frontend tests**

Run: `cd frontend && npm test -- --run`
Expected: All tests pass

**Step 5: Commit**

```bash
git add frontend/src/components/ui/__tests__/
git commit -m "test(frontend): add UI component tests"
```

---

## Task 7: Setup Playwright and Create E2E Tests

**Files:**
- Create: `frontend/playwright.config.ts`
- Create: `frontend/e2e/search.spec.ts`
- Create: `frontend/e2e/list.spec.ts`

**Step 1: Install Playwright**

```bash
cd frontend && npm install -D @playwright/test && npx playwright install chromium
```

**Step 2: Create Playwright config**

```typescript
// frontend/playwright.config.ts
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  use: {
    baseURL: 'http://localhost:5173',
    trace: 'on-first-retry',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:5173',
    reuseExistingServer: !process.env.CI,
  },
});
```

**Step 3: Create search E2E test**

```typescript
// frontend/e2e/search.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Search Flow', () => {
  test('can search for products', async ({ page }) => {
    await page.goto('/');

    // Find and use search bar
    const searchInput = page.getByPlaceholder(/search/i);
    await expect(searchInput).toBeVisible();

    await searchInput.fill('drill');
    await searchInput.press('Enter');

    // Should navigate to search results
    await expect(page).toHaveURL(/\/search\?q=drill/);
  });

  test('shows empty state for no results', async ({ page }) => {
    await page.goto('/search?q=xyznonexistent123');

    // Should show empty state
    await expect(page.getByText(/no results/i)).toBeVisible();
  });
});
```

**Step 4: Create list E2E test**

```typescript
// frontend/e2e/list.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Shopping List Flow', () => {
  test('can start a new cart', async ({ page }) => {
    await page.goto('/');

    // Click Start Cart button
    const startCartButton = page.getByRole('button', { name: /start cart/i });
    await expect(startCartButton).toBeVisible();
    await startCartButton.click();

    // Cart icon should now show
    await expect(page.locator('[data-testid="cart-button"]')).toBeVisible();
  });

  test('can view list page', async ({ page }) => {
    await page.goto('/list');

    // Should show list page
    await expect(page.getByText(/list/i)).toBeVisible();
  });
});
```

**Step 5: Add E2E script to package.json**

Add to scripts:
```json
"test:e2e": "playwright test",
"test:e2e:ui": "playwright test --ui"
```

**Step 6: Run E2E tests**

Note: Requires backend and frontend running. For CI, use docker-compose.

Run: `cd frontend && npm run test:e2e`

**Step 7: Commit**

```bash
git add frontend/playwright.config.ts frontend/e2e/ frontend/package.json
git commit -m "test(frontend): add Playwright E2E tests"
```

---

## Task 8: Run Full Test Suite and Update Coverage

**Step 1: Run all backend tests**

```bash
cd backend && python -m pytest -v --cov=app --cov-report=term-missing
```

**Step 2: Run all frontend tests**

```bash
cd frontend && npm test -- --run --coverage
```

**Step 3: Update TODO.md to mark Phase 6 complete**

**Step 4: Final commit**

```bash
git add .
git commit -m "test: complete Phase 6 testing implementation"
```
