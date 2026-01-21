# Phase 6: Testing & Documentation Design

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Achieve comprehensive test coverage for both backend and frontend, ensuring reliability before production deployment.

**Architecture:** pytest + pytest-asyncio for backend, vitest for frontend unit tests, Playwright for E2E.

**Tech Stack:** pytest, pytest-asyncio, pytest-mock, httpx (async test client), vitest, @testing-library/react, Playwright

---

## 1. Backend Test Strategy

### 1.1 Test Fixtures (conftest.py)

Create reusable fixtures for:
- **Async database session** - In-memory SQLite for unit tests, or test PostgreSQL
- **Test client** - httpx.AsyncClient with FastAPI TestClient
- **Sample data factories** - Products, categories, sessions, lists
- **Mock services** - For isolating unit tests

**Key fixtures:**
```python
@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    # Create test database session

@pytest.fixture
async def test_client(db_session) -> AsyncGenerator[AsyncClient, None]:
    # Create async test client with dependency overrides

@pytest.fixture
def sample_product() -> dict:
    # Return sample product data

@pytest.fixture
def sample_category() -> dict:
    # Return sample category data
```

### 1.2 Service Unit Tests

**Services to test:**
| Service | Priority | Key Methods |
|---------|----------|-------------|
| ProductService | High | get_by_sku, list_products, get_featured |
| CategoryService | High | get_by_slug, get_tree, get_with_products |
| ListService | High | create_list, add_item, remove_item, share |
| SessionService | Medium | get_or_create, touch, cleanup_expired |
| AnalyticsService | Medium | track_event, get_summary |

**Test patterns:**
- Mock database session with AsyncMock
- Test happy paths and error cases
- Verify correct SQL queries via mock assertions

### 1.3 Route Integration Tests

**Routes to test:**
| Route Group | Endpoints | Test Focus |
|-------------|-----------|------------|
| Products | GET /products, GET /products/{sku} | Pagination, 404 handling |
| Categories | GET /categories, GET /categories/{slug} | Tree structure, products |
| Search | GET /search?q= | Results, empty, semantic |
| Lists | POST /lists, POST /lists/{id}/items | CRUD, session handling |
| Analytics | POST /events | Event batching |

**Test patterns:**
- Use httpx.AsyncClient with app
- Override database dependency with test session
- Test request/response schemas
- Test authentication/session headers

---

## 2. Frontend Test Strategy

### 2.1 Component Unit Tests

**Components to test (priority order):**

**High Priority (user-facing):**
- Button - variants, sizes, disabled state
- Modal - open/close, escape key, backdrop click
- ProductCard - rendering, add to list click
- SearchBar - input, debounce, submit
- FloatingCart - badge count, expand/collapse

**Medium Priority:**
- LoadingSkeleton variants
- ErrorDisplay with retry
- EmptyState with action
- CategoryCard, CategoryGrid
- ListItemPreview

**Test patterns:**
- Use @testing-library/react
- Test rendering, user interactions, accessibility
- Mock stores with vi.mock

### 2.2 Store Tests

**Stores to test:**
- sessionStore - session creation, expiry, persistence
- listStore - CRUD operations, API integration
- searchStore - search state, loading, results

### 2.3 Page Tests

**Pages to test:**
- HomePage - renders, search works
- SearchResultsPage - loading, results, empty
- CategoryPage - products load, error state
- ListPage - items display, share button
- SyncPage - scanner toggle, manual entry

---

## 3. E2E Test Strategy (Playwright)

### 3.1 Critical User Flows

**Flow 1: Search and Browse**
1. Open home page
2. Enter search query
3. View results
4. Click product to view details

**Flow 2: Category Navigation**
1. Open home page
2. Click category
3. View products in category
4. Navigate between categories

**Flow 3: Shopping List**
1. Start a new cart
2. Add products to list
3. View list page
4. Update quantities
5. Remove items

**Flow 4: QR Share (mock camera)**
1. Go to list page
2. Click share
3. Verify QR code displays
4. Copy link
5. Navigate to sync page
6. Enter code manually
7. Verify list synced

### 3.2 Playwright Configuration

```typescript
// playwright.config.ts
export default defineConfig({
  testDir: './e2e',
  use: {
    baseURL: 'http://localhost:5173',
    trace: 'on-first-retry',
  },
  webServer: {
    command: 'npm run dev',
    port: 5173,
    reuseExistingServer: !process.env.CI,
  },
});
```

---

## 4. File Structure

```
backend/tests/
├── conftest.py              # Shared fixtures
├── factories.py             # Data factories
├── services/
│   ├── test_product_service.py
│   ├── test_category_service.py
│   ├── test_list_service.py
│   ├── test_session_service.py
│   └── test_analytics_service.py
├── routes/
│   ├── test_products.py
│   ├── test_categories.py
│   ├── test_search.py
│   ├── test_lists.py
│   └── test_analytics.py
└── integration/
    └── test_vector_search.py  (existing)

frontend/
├── src/
│   ├── components/
│   │   ├── ui/__tests__/
│   │   │   ├── Button.test.tsx
│   │   │   ├── Modal.test.tsx
│   │   │   └── ...
│   │   ├── product/__tests__/
│   │   └── ...
│   ├── stores/__tests__/
│   └── pages/__tests__/
└── e2e/
    ├── search.spec.ts
    ├── category.spec.ts
    ├── list.spec.ts
    └── sync.spec.ts
```

---

## 5. Coverage Goals

| Component | Target Coverage |
|-----------|----------------|
| Backend Services | 80%+ |
| Backend Routes | 70%+ |
| Frontend Components | 70%+ |
| Frontend Stores | 80%+ |
| E2E Critical Flows | 100% |

---

## 6. Implementation Order

1. **Backend fixtures** - Create conftest.py with db, client, factories
2. **Backend service tests** - Test core business logic
3. **Backend route tests** - Test API contracts
4. **Frontend component tests** - Test UI components
5. **Frontend store tests** - Test state management
6. **E2E tests** - Test user flows end-to-end
