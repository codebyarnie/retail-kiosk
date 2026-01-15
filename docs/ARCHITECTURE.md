# Architecture Documentation

## Table of Contents

1. [System Overview](#system-overview)
2. [Architecture Patterns](#architecture-patterns)
3. [Component Architecture](#component-architecture)
4. [Data Flow](#data-flow)
5. [Technology Stack](#technology-stack)
6. [Design Decisions](#design-decisions)
7. [Security Architecture](#security-architecture)
8. [Scalability & Performance](#scalability--performance)
9. [Deployment Architecture](#deployment-architecture)

---

## System Overview

The Retail Kiosk application is a modern, microservices-based product browser designed for hardware/DIY retail environments. It provides an intuitive self-service interface for customers to search, discover, and compile product lists that can be synced across devices and handed off to POS systems.

### Business Context

- **Domain**: Hardware/DIY retail (screws, tools, materials)
- **Primary Interface**: Android touchscreen kiosk in-store
- **Secondary Interface**: Web/mobile companion for home use
- **Business Model**: White-label SaaS for retail clients
- **Catalog Size**: ~100k products
- **Key Features**: Natural language search, semantic product discovery, session-based lists, QR code sync

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Client Layer                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Kiosk UI   │  │   Web App    │  │  Mobile PWA  │      │
│  │  (React/TS)  │  │  (React/TS)  │  │  (React/TS)  │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                              │
                    ┌─────────┴─────────┐
                    │   API Gateway     │
                    │   (FastAPI CORS)  │
                    └─────────┬─────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                     Application Layer                       │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              FastAPI Backend Service                 │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐          │   │
│  │  │  Routes  │  │ Services │  │  Models  │          │   │
│  │  └──────────┘  └──────────┘  └──────────┘          │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┼───────────────┐
              │               │               │
┌─────────────▼───┐  ┌────────▼────────┐  ┌──▼───────────┐
│  Message Queue  │  │  Cache Layer    │  │   Vector DB  │
│  (Redis/Celery) │  │    (Redis)      │  │   (Qdrant)   │
└─────────────────┘  └─────────────────┘  └──────────────┘
              │
┌─────────────▼───────────────────────────────────────────────┐
│                    Worker Layer                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │Product Sync  │  │Image Process │  │Vector Update │      │
│  │   Worker     │  │   Worker     │  │   Worker     │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
              │
┌─────────────▼───────────────────────────────────────────────┐
│                     Data Layer                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  PostgreSQL  │  │    Qdrant    │  │    Redis     │      │
│  │  (Primary)   │  │  (Vectors)   │  │  (Cache)     │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

---

## Architecture Patterns

### 1. Microservices Architecture

The application is decomposed into independently deployable services:

- **Frontend Service**: React SPA serving the user interface
- **Backend Service**: FastAPI REST API for business logic
- **Worker Service**: Celery workers for background processing
- **Data Services**: PostgreSQL, Redis, Qdrant

**Benefits**:
- Independent scaling of components
- Technology flexibility per service
- Fault isolation
- Easier development and deployment

### 2. Event-Driven Architecture

Background tasks are processed asynchronously using Celery with Redis as the message broker:

```
Backend API → Redis Queue → Celery Worker → Database/Qdrant
                    ↓
            Task Result Backend
```

**Use Cases**:
- Product data synchronization
- Image optimization
- Vector embedding generation
- Report generation
- Periodic cleanup tasks

### 3. Layered Architecture

Each service follows a clean layered architecture:

```
┌─────────────────────────────────────┐
│          Presentation Layer         │  ← Routes/Controllers
├─────────────────────────────────────┤
│          Service Layer              │  ← Business Logic
├─────────────────────────────────────┤
│          Data Access Layer          │  ← Models/Repositories
├─────────────────────────────────────┤
│          Infrastructure             │  ← Database, Cache, etc.
└─────────────────────────────────────┘
```

### 4. Hybrid Server-Client Architecture

**Central Server**:
- Single source of truth
- Embedding generation
- Analytics collection
- Data synchronization

**Local Cache** (Kiosk):
- Offline resilience
- Fast response times
- Reduced bandwidth usage
- Complete catalog cached locally

---

## Component Architecture

### Frontend (React + TypeScript + Vite)

**Directory Structure**:
```
frontend/
├── src/
│   ├── components/       # Reusable UI components
│   ├── features/         # Feature-specific modules
│   ├── hooks/            # Custom React hooks
│   ├── services/         # API clients and services
│   ├── stores/           # State management (Zustand)
│   ├── types/            # TypeScript type definitions
│   ├── utils/            # Utility functions
│   ├── App.tsx           # Root component
│   └── main.tsx          # Application entry point
├── public/               # Static assets
└── index.html            # HTML template
```

**Key Technologies**:
- **React 18**: UI library with concurrent features
- **TypeScript 5**: Static type checking
- **Vite 5**: Fast build tool and dev server
- **React Router**: Client-side routing
- **Zustand**: Lightweight state management
- **TanStack Query**: Server state management and caching
- **Axios**: HTTP client
- **Tailwind CSS**: Utility-first styling

**State Management Strategy**:
- **Local UI State**: React useState/useReducer
- **Global UI State**: Zustand stores
- **Server State**: TanStack Query with caching
- **Form State**: Controlled components

**Build Optimization**:
- Code splitting by route and vendor chunks
- Tree shaking for unused code elimination
- Asset optimization (images, fonts)
- Bundle size monitoring

### Backend (FastAPI + SQLAlchemy)

**Directory Structure**:
```
backend/
├── app/
│   ├── models/           # SQLAlchemy models
│   ├── routes/           # API endpoint handlers
│   ├── services/         # Business logic
│   ├── schemas/          # Pydantic schemas
│   ├── dependencies/     # Dependency injection
│   ├── middleware/       # Custom middleware
│   ├── config.py         # Configuration management
│   └── main.py           # Application entry point
├── alembic/              # Database migrations
├── tests/                # Test suite
└── requirements.txt      # Python dependencies
```

**Key Technologies**:
- **FastAPI**: Modern async web framework
- **SQLAlchemy 2.0**: ORM with async support
- **Alembic**: Database migrations
- **Pydantic**: Data validation and serialization
- **asyncpg**: Async PostgreSQL driver
- **Redis**: Caching and session management
- **Qdrant Client**: Vector database integration

**API Design Principles**:
- RESTful conventions
- OpenAPI documentation (Swagger UI)
- Versioned endpoints (/api/v1/...)
- Consistent error responses
- Request/response validation with Pydantic

**Database Access Pattern**:
- Async session management with FastAPI dependencies
- Repository pattern for data access
- Connection pooling for performance
- Transaction management

### Worker (Celery)

**Directory Structure**:
```
worker/
├── tasks/                # Task definitions
│   ├── product_sync.py   # Product synchronization
│   ├── image_processing.py
│   ├── vector_operations.py
│   └── reports.py
├── celery_app.py         # Celery configuration
├── config.py             # Worker settings
└── requirements.txt      # Python dependencies
```

**Task Queues**:
- `product_sync`: Product data synchronization
- `image_processing`: Image optimization and transformation
- `vector_db`: Vector embedding updates
- `reports`: Report generation
- `default`: General background tasks

**Task Management**:
- Automatic retry with exponential backoff
- Task result persistence in Redis
- Task routing by queue
- Worker monitoring and health checks
- Graceful shutdown handling

### Data Services

#### PostgreSQL (Primary Database)

**Purpose**: Persistent storage for application data

**Schema Design**:
- Products and inventory
- User sessions and lists
- Analytics events
- Task results and audit logs

**Configuration**:
- Connection pooling (10 connections, 20 overflow)
- Async driver (asyncpg)
- Read replicas for scalability (future)

#### Redis (Cache & Message Broker)

**Purpose**:
- Session cache
- API response cache
- Celery message broker
- Celery result backend
- Distributed locks

**Data Structures**:
- Strings: Simple cache values
- Hashes: Complex objects
- Lists: Task queues
- Sets: Session tracking
- Sorted Sets: Leaderboards/rankings

#### Qdrant (Vector Database)

**Purpose**: Semantic search and product discovery

**Collections**:
- Products: Vector embeddings for natural language search
- Future: User preferences, similar products

**Search Strategy**:
- Combined vector + filter search
- Similarity scoring
- Context-aware ranking
- Faceted navigation support

**Embedding Strategy**:
- Fields embedded: name + description + specifications
- Model: TBD (likely Sentence-BERT or similar)
- Dimensionality: TBD
- Update frequency: On product data sync

---

## Data Flow

### 1. Product Search Flow

```
User Query
    ↓
Frontend (React)
    ↓
[HTTP Request] → Backend API (/api/search)
    ↓
Service Layer
    ↓
┌─────────────────┐
│ Check Cache     │ → Redis (if cached)
└─────────────────┘
    ↓ (cache miss)
┌─────────────────┐
│ Vector Search   │ → Qdrant (semantic search)
└─────────────────┘
    ↓
┌─────────────────┐
│ Enrich Results  │ → PostgreSQL (product details)
└─────────────────┘
    ↓
[Cache Results] → Redis
    ↓
[JSON Response] → Frontend
    ↓
Display Results
```

### 2. Product Sync Flow

```
External Product Data (product.json)
    ↓
Backend API (/api/admin/sync)
    ↓
[Enqueue Task] → Celery (product_sync queue)
    ↓
Worker: sync_product_data
    ↓
┌─────────────────┐
│ Parse & Validate│
└─────────────────┘
    ↓
┌─────────────────┐
│ Update Database │ → PostgreSQL (upsert products)
└─────────────────┘
    ↓
┌─────────────────┐
│ Generate Embed. │ → ML Model (embeddings)
└─────────────────┘
    ↓
┌─────────────────┐
│ Update Vectors  │ → Qdrant (upsert vectors)
└─────────────────┘
    ↓
[Invalidate Cache] → Redis
    ↓
Task Complete → Result Backend
```

### 3. Session & List Management Flow

```
User adds product to list
    ↓
Frontend State Update (Zustand)
    ↓
[POST /api/lists/items] → Backend API
    ↓
Session Validation → Redis (check session)
    ↓
Update List → PostgreSQL (persist list)
    ↓
[Return List ID] → Frontend
    ↓
Generate QR Code
    ↓
User scans QR (mobile or kiosk)
    ↓
[GET /api/lists/{id}] → Backend API
    ↓
Retrieve List → PostgreSQL
    ↓
[JSON Response] → Frontend (new device)
```

### 4. Analytics Event Flow

```
User Action (search, view, add to list)
    ↓
Frontend Event Tracking
    ↓
[Batch POST /api/analytics/events] → Backend API
    ↓
[Enqueue Task] → Celery (default queue)
    ↓
Worker: process_analytics_batch
    ↓
Transform & Enrich
    ↓
Batch Insert → PostgreSQL (analytics tables)
    ↓
Update Metrics → Redis (real-time counters)
```

---

## Technology Stack

### Frontend Stack

| Technology | Version | Purpose |
|------------|---------|---------|
| React | 18.2+ | UI library |
| TypeScript | 5.3+ | Type safety |
| Vite | 5.0+ | Build tool |
| React Router | 6.x | Routing |
| Zustand | 4.x | State management |
| TanStack Query | 5.x | Server state |
| Axios | 1.x | HTTP client |
| Tailwind CSS | 3.x | Styling |
| Vitest | 1.x | Testing |

### Backend Stack

| Technology | Version | Purpose |
|------------|---------|---------|
| Python | 3.11+ | Language |
| FastAPI | 0.109+ | Web framework |
| SQLAlchemy | 2.0+ | ORM |
| Alembic | 1.13+ | Migrations |
| Pydantic | 2.5+ | Validation |
| asyncpg | 0.29+ | PostgreSQL driver |
| Redis | 5.0+ | Cache client |
| Qdrant Client | 1.7+ | Vector DB client |
| Celery | 5.3+ | Task queue |
| pytest | 7.4+ | Testing |
| Ruff | 0.1+ | Linting |
| Black | 23.12+ | Formatting |
| Mypy | 1.8+ | Type checking |

### Infrastructure Stack

| Technology | Version | Purpose |
|------------|---------|---------|
| PostgreSQL | 16+ | Primary database |
| Redis | 7+ | Cache & broker |
| Qdrant | Latest | Vector database |
| Docker | 20.10+ | Containerization |
| Docker Compose | 2.0+ | Orchestration |
| Nginx | 1.25+ | Reverse proxy |

---

## Design Decisions

### 1. Why FastAPI?

**Decision**: Use FastAPI over Django/Flask

**Rationale**:
- Native async/await support for high concurrency
- Automatic OpenAPI documentation
- Built-in request/response validation
- Modern Python 3.11+ type hints
- Performance comparable to Node.js and Go
- Easy dependency injection

### 2. Why Qdrant for Vector Search?

**Decision**: Use Qdrant over pgvector, Weaviate, or Pinecone

**Rationale**:
- Combined vector + filter search (faceted semantic search)
- Runs embedded (local on kiosk) or as server (hybrid model)
- Low resource footprint (Rust-based)
- Self-hostable, no vendor lock-in
- Excellent Python/JS SDKs
- Purpose-built for vector search

**Domain Fit**:
Hardware retail customers describe problems ("screws for outdoor decking") rather than exact product names, making semantic search essential.

### 3. Why Celery for Background Tasks?

**Decision**: Use Celery over custom task queue or cloud functions

**Rationale**:
- Mature and battle-tested
- Rich feature set (retries, scheduling, monitoring)
- Multiple broker options (Redis, RabbitMQ)
- Priority queues and routing
- Integration with Python ecosystem

**Use Cases**:
- Product data sync (long-running)
- Image processing (CPU-intensive)
- Vector embedding generation (ML workload)
- Report generation (scheduled)

### 4. Why Session-Based (No Login)?

**Decision**: Anonymous session-based lists instead of user accounts

**Rationale**:
- Reduces friction for quick in-store browsing
- No authentication complexity
- QR code sync provides cross-device functionality
- Aligns with kiosk use case (transient users)
- No GDPR concerns for anonymous sessions

### 5. Why Hybrid Architecture (Server + Local Cache)?

**Decision**: Central server with local kiosk caching

**Rationale**:
- **Offline resilience**: Kiosk remains functional without network
- **Performance**: Fast local search with cached catalog
- **Cost**: Reduced bandwidth and server load
- **Single source of truth**: Server handles updates and analytics
- **Flexibility**: Can operate in degraded mode

**Trade-offs**:
- Sync complexity
- Eventual consistency
- Larger local storage requirements

### 6. Why TypeScript over JavaScript?

**Decision**: TypeScript for frontend

**Rationale**:
- Catch errors at compile-time
- Better IDE support (autocomplete, refactoring)
- Self-documenting code (types as documentation)
- Safer refactoring
- Industry standard for large React applications

---

## Security Architecture

### 1. Authentication & Authorization

**Current State** (MVP):
- No user authentication required
- Session-based access control
- API endpoints secured with session tokens

**Future Enhancements**:
- Admin panel with JWT authentication
- Role-based access control (RBAC)
- Client-specific API keys (white-label)

### 2. Data Protection

**In Transit**:
- HTTPS/TLS for all API communication
- Secure WebSocket connections (future)

**At Rest**:
- Database encryption (PostgreSQL TDE)
- Encrypted backups
- No sensitive payment data stored

**Session Security**:
- HTTP-only cookies
- CSRF protection
- Session expiration
- Secure session ID generation

### 3. Input Validation

- Pydantic schemas for all API inputs
- SQL injection prevention (parameterized queries)
- XSS prevention (React automatic escaping)
- File upload validation (images only)
- Rate limiting on API endpoints

### 4. Dependency Security

- Automated vulnerability scanning (Dependabot)
- Regular dependency updates
- Security audits (npm audit, safety)
- Pre-commit hooks with secret detection

---

## Scalability & Performance

### Horizontal Scaling

**Frontend**:
- Static asset CDN
- Multiple nginx instances behind load balancer
- Edge caching for improved global performance

**Backend**:
- Stateless API servers (scale horizontally)
- Load balancer (Nginx/HAProxy)
- Connection pooling to database
- Shared cache (Redis) across instances

**Workers**:
- Multiple Celery worker instances
- Queue-based load distribution
- Auto-scaling based on queue depth

**Databases**:
- PostgreSQL read replicas
- Redis cluster mode
- Qdrant sharding (for large catalogs)

### Performance Optimization

**Caching Strategy**:
```
L1 Cache: Browser (service worker, local storage)
    ↓
L2 Cache: Redis (API responses, session data)
    ↓
L3 Cache: Database query cache
    ↓
Origin: PostgreSQL / Qdrant
```

**Query Optimization**:
- Database indexes on frequently queried fields
- Pagination for large result sets
- Eager loading for related data
- Vector search pre-filtering

**Asset Optimization**:
- Image lazy loading
- Code splitting by route
- Vendor chunk optimization
- Gzip/Brotli compression
- Asset versioning for cache busting

### Monitoring & Observability

**Metrics** (Future):
- Application metrics (Prometheus)
- Business metrics (analytics dashboard)
- Infrastructure metrics (Grafana)

**Logging**:
- Structured logging (Loguru)
- Centralized log aggregation
- Log levels by environment

**Tracing** (Future):
- Distributed tracing (OpenTelemetry)
- Request correlation IDs
- Performance profiling

---

## Deployment Architecture

### Development Environment

```
Developer Machine
├── Backend: uvicorn (hot reload)
├── Frontend: vite dev server (HMR)
├── Worker: celery worker (auto-reload)
└── Services: docker-compose (postgres, redis, qdrant)
```

### Production Environment

```
┌─────────────────────────────────────────────────┐
│                 Load Balancer                   │
│                  (Nginx/HAProxy)                │
└────────────┬────────────────────────────────────┘
             │
     ┌───────┴────────┐
     │                │
┌────▼─────┐    ┌────▼─────┐
│ Frontend │    │ Frontend │
│ Container│    │ Container│
└──────────┘    └──────────┘
     │
┌────▼──────────────────────┐
│    API Load Balancer      │
└────────────┬───────────────┘
     ┌───────┴────────┐
     │                │
┌────▼─────┐    ┌────▼─────┐
│ Backend  │    │ Backend  │
│ Container│    │ Container│
└──────────┘    └──────────┘
     │
┌────▼──────────────────────┐
│   Worker Load Balancer    │
└────────────┬───────────────┘
     ┌───────┴────────┐
     │                │
┌────▼─────┐    ┌────▼─────┐
│ Worker   │    │ Worker   │
│ Container│    │ Container│
└──────────┘    └──────────┘
     │
┌────▼──────────────────────┐
│     Data Layer            │
│  ┌────────────────────┐   │
│  │   PostgreSQL       │   │
│  │   (Managed/HA)     │   │
│  └────────────────────┘   │
│  ┌────────────────────┐   │
│  │   Redis Cluster    │   │
│  └────────────────────┘   │
│  ┌────────────────────┐   │
│  │   Qdrant Cluster   │   │
│  └────────────────────┘   │
└───────────────────────────┘
```

### Container Strategy

**Base Images**:
- Frontend: `node:18-alpine` (build) + `nginx:1.25-alpine` (serve)
- Backend: `python:3.11-slim`
- Worker: `python:3.11-slim`

**Multi-Stage Builds**:
- Smaller production images
- Build-time dependencies excluded
- Security vulnerability reduction

**Health Checks**:
- Frontend: HTTP GET /health
- Backend: HTTP GET /health
- Worker: Celery inspect ping
- Databases: Native health checks

---

## Future Architectural Considerations

### 1. GraphQL API

**When**: When frontend needs flexible data fetching

**Benefits**:
- Client-driven queries
- Reduced over-fetching
- Type safety with schema

### 2. Event Sourcing

**When**: For audit trail and time-travel debugging

**Use Cases**:
- Product change history
- User action replay
- Analytics replay

### 3. gRPC for Internal Services

**When**: For high-performance service-to-service communication

**Benefits**:
- Binary protocol (faster than JSON)
- Strong typing (protobuf)
- Streaming support

### 4. Kubernetes Orchestration

**When**: Scale beyond docker-compose

**Benefits**:
- Declarative configuration
- Self-healing
- Advanced scheduling
- Service mesh integration

### 5. Machine Learning Pipeline

**When**: For recommendation engine and category clustering

**Components**:
- Feature store
- Model serving
- A/B testing framework
- Feedback loop

---

## Conclusion

This architecture provides a solid foundation for the Retail Kiosk application with:

✅ **Scalability**: Horizontal scaling for all services
✅ **Performance**: Multi-layer caching and optimization
✅ **Reliability**: Fault isolation and graceful degradation
✅ **Maintainability**: Clean separation of concerns
✅ **Flexibility**: Pluggable components and modern patterns
✅ **Developer Experience**: Fast feedback loops and comprehensive tooling

The architecture is designed to evolve as the application grows, with clear paths for enhancement without major rewrites.
