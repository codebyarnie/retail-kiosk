# Retail Kiosk - Implementation TODO

Based on PRD analysis and current codebase state. Infrastructure is complete, business logic needs implementation.

## Phase 1: Database & Core Backend (Foundation) - COMPLETED

### 1.1 Database Models - DONE
- [x] Create Product model (SKU, name, description, price, image_url, metadata)
- [x] Create Category model (name, slug, parent_id for hierarchy)
- [x] Create ProductCategory junction table
- [x] Create UserSession model (session_id, created_at, last_active)
- [x] Create UserList model (session_id, name, created_at)
- [x] Create ListItem model (list_id, product_sku, quantity)
- [x] Create AnalyticsEvent model (session_id, event_type, data, timestamp)

### 1.2 Database Setup - DONE
- [x] Initialize Alembic migrations
- [x] Create initial migration with all models
- [x] Add database connection pooling in app lifespan
- [x] Test migrations with `make db-migrate`

### 1.3 Pydantic Schemas - DONE
- [x] ProductBase, ProductCreate, ProductResponse schemas
- [x] CategorySchema
- [x] UserSessionSchema
- [x] ListSchema, ListItemSchema
- [x] SearchRequestSchema, SearchResponseSchema
- [x] AnalyticsEventSchema

## Phase 2: Core Services & Routes - COMPLETED

### 2.1 Product Service & Routes - DONE
- [x] ProductService: get_by_sku, list_products, filter_products
- [x] GET /api/products - list with pagination
- [x] GET /api/products/{sku} - product detail
- [x] GET /api/categories - category list

### 2.2 Search Service & Routes - DONE
- [x] SearchService: semantic_search, keyword_fallback
- [x] GET /api/search?q={query} - search endpoint (keyword mode)
- [x] Implement search result grouping
- [x] Qdrant client initialization (semantic search)
- [x] Create products collection in Qdrant
- [x] Implement semantic search with Qdrant vector database

### 2.3 List Service & Routes - DONE
- [x] ListService: create_list, add_item, remove_item, get_list
- [x] Session middleware for anonymous users
- [x] POST /api/lists - create list
- [x] GET /api/lists/{id} - get list
- [x] POST /api/lists/{id}/items - add item
- [x] DELETE /api/lists/{id}/items/{sku} - remove item

### 2.4 Analytics Service & Routes - DONE
- [x] AnalyticsService: track_event, get_session_events
- [x] POST /api/analytics/events - track event batch
- [x] Event types: search, view_product, add_to_list

## Phase 3: Vector Search & Embeddings - COMPLETED

### 3.1 Embedding Service - DONE
- [x] Select embedding model (sentence-transformers)
- [x] EmbeddingService: generate_embedding, batch_embeddings
- [x] Integrate with Qdrant upsert (via QdrantService)

### 3.2 Worker Tasks Implementation - DONE
- [x] Implement sync_product_data task (from JSON file)
- [x] Implement update_vector_embeddings task
- [x] Implement cleanup_old_data task
- [x] Add sample seed data script for testing
- [x] Add admin API endpoints for triggering tasks

## Phase 4: Frontend Core - COMPLETED

### 4.1 Setup & Routing - DONE
- [x] Configure React Router with routes (/, /search, /category/:slug, /list)
- [x] Create layout components (Header, Layout)
- [x] Setup API client with Axios (session ID interceptor)
- [x] Configure Tailwind CSS with custom theme (primary colors, touch-friendly)
- [x] TypeScript types matching backend schemas

### 4.2 State Management - DONE
- [x] Create listStore (Zustand) for shopping list
- [x] Create sessionStore for user session (5-min auto-expire, persist middleware)
- [x] Create searchStore for search state

### 4.3 Core Pages - DONE
- [x] HomePage with search bar and featured categories
- [x] SearchResultsPage with product grid
- [x] CategoryPage with products (replaces ProductDetailPage)
- [x] ListPage showing user's list

### 4.4 Core Components - DONE
- [x] Button component (variants: primary, secondary, outline, ghost; sizes: sm, md, lg)
- [x] Modal component (accessible with escape key, backdrop click, responsive sizes)
- [x] SearchBar with debounced input
- [x] SearchHero for home page
- [x] ProductCard for grid display
- [x] ProductGrid responsive layout
- [x] CategoryCard and CategoryGrid components
- [x] ListItemPreview component
- [x] FloatingCart component (fixed position, expandable mini-list panel)
- [x] SessionPrompt modal (Continue/Start Fresh session handling)
- [x] ProductModal for product details (configurable architecture)

## Phase 5: QR Sync & Polish - COMPLETED

### 5.1 QR Code Features - DONE
- [x] QR code sync endpoints (POST /api/lists/{id}/share, POST /api/lists/sync/{code})
- [x] QR code generation library (frontend) - QRCodeDisplay and ShareListModal components
- [x] QR code scanning (camera access) - QRScanner component with html5-qrcode
- [x] SyncPage for QR scanning and manual code entry

### 5.2 UI Polish - DONE
- [x] Touch-friendly UI for kiosk (44px min touch targets via Tailwind, responsive design)
- [x] Loading states and skeletons (ProductCardSkeleton, ListItemSkeleton)
- [x] Error handling UI (ErrorDisplay component)
- [x] Empty states (EmptyState component)

## Phase 6: Testing & Documentation

### 6.1 Backend Tests
- [ ] Unit tests for services
- [x] Integration tests for vector search (EmbeddingService, QdrantService)
- [ ] Integration tests for routes
- [ ] Test database fixtures

### 6.2 Frontend Tests
- [x] Test setup infrastructure (vitest, jsdom, jest-dom matchers)
- [x] Browser API mocks (localStorage, matchMedia)
- [ ] Component unit tests
- [ ] E2E tests with Playwright

---

## Current Progress

**Started:** 2026-01-20
**Last Updated:** 2026-01-20
**Status:** Phase 1-5 Complete (Full-stack application functional with QR sync)

### Completed:
- All database models (Product, Category, Session, List, Analytics)
- Alembic migrations setup and initial migration
- All Pydantic schemas for request/response validation
- All services (ProductService, CategoryService, ListService, SearchService, SessionService, AnalyticsService)
- All API routes with full CRUD operations
- Session-based anonymous user tracking
- QR code sync endpoints for list sharing
- Sample data seeding script with 8 products and 12 categories

### Phase 5 - QR Sync & Polish:
- QR code generation (react-qr-code) - QRCodeDisplay component
- QR code scanning (html5-qrcode) - QRScanner component
- ShareListModal for generating and displaying share QR codes
- SyncPage for scanning QR codes and manual code entry
- UI polish components (LoadingSkeleton, ErrorDisplay, EmptyState)
- Loading skeletons on product pages
- Error and empty states on all pages

### Frontend Core (Phase 4):
- TypeScript types matching all backend schemas
- Axios API client with session ID interceptor
- Zustand stores (sessionStore, listStore, searchStore)
- Session management with 5-min auto-expire and "Continue previous?" prompt
- All UI components (Button, Modal, ProductCard, ProductGrid, ProductModal)
- Search components (SearchBar, SearchHero with debounce)
- Category components (CategoryCard, CategoryGrid)
- List components (ListItemPreview, FloatingCart, SessionPrompt)
- All pages (HomePage, SearchResultsPage, CategoryPage, ListPage)
- React Router configuration
- Tailwind CSS with custom theme and touch-friendly utilities
- Test setup infrastructure (vitest, jsdom, jest-dom matchers)

### Backend API Endpoints:
- `GET /health` - Health check
- `GET /api/products` - List products with pagination
- `GET /api/products/featured` - Featured products
- `GET /api/products/{sku}` - Product detail
- `GET /api/categories` - List categories
- `GET /api/categories/tree` - Category hierarchy
- `GET /api/categories/{slug}` - Category with products
- `GET /api/search?q=...` - Search products
- `GET /api/search/suggestions?q=...` - Search autocomplete
- `GET /api/lists` - User's lists
- `POST /api/lists` - Create list
- `GET /api/lists/{id}` - Get list detail
- `POST /api/lists/{id}/items` - Add item
- `DELETE /api/lists/{id}/items/{sku}` - Remove item
- `POST /api/lists/{id}/share` - Generate share code
- `POST /api/lists/sync/{code}` - Sync from code
- `POST /api/analytics/events` - Track events
- `GET /api/analytics/summary` - Session summary
- `POST /api/admin/sync-products` - Trigger product sync from JSON
- `POST /api/admin/update-embeddings` - Trigger embedding updates
- `POST /api/admin/cleanup-vectors` - Trigger stale vector cleanup

## Quick Reference

```bash
# Start infrastructure services
docker-compose up -d

# Run migrations
cd backend && alembic upgrade head

# Seed sample data
cd backend && python scripts/seed_data.py

# Run backend (from project root)
cd backend && uvicorn app.main:app --reload --port 8000

# Run frontend
cd frontend && npm run dev

# Run tests
make test
```
