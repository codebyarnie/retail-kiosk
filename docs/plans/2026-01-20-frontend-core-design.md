# Frontend Core Design

**Date:** 2026-01-20
**Status:** Approved
**Phase:** 4 (Frontend Core)

## Overview

Design for the React frontend of the Retail Kiosk application - a touch-friendly product browser for hardware/DIY retail.

## Key Design Decisions

1. **Hybrid homepage** - Prominent search bar + category grid (serves both search-first and browse-first customers)
2. **Floating mini-cart** - Bottom-right floating button with item count, expands to mini-list
3. **Prominent "Start Cart"** - Clear action for new customers, avoids confusion with previous sessions
4. **Session auto-expire** - 5 min inactivity timeout with "Continue previous?" prompt for recovery
5. **Modal product detail** - Configurable, defaults to modal overlay to preserve browsing context

## Route Structure

```
/                    → HomePage (search bar + category grid)
/search?q=...        → SearchResultsPage
/category/:slug      → CategoryPage (filtered product grid)
/list                → ListPage (full list view, for QR sharing)
```

## Component Architecture

```
App
├── Layout
│   ├── Header (logo, mini search, session indicator)
│   ├── main content (routes)
│   └── FloatingCart (mini-cart button + "Start Cart")
├── ProductModal (configurable detail view)
└── SessionPrompt (continue previous? dialog)
```

## State Management (Zustand)

- `sessionStore` - session ID, expiry timer, "continue previous" state
- `listStore` - current list, items, add/remove actions
- `searchStore` - query, filters, results cache

## Component Details

### HomePage

```
HomePage
├── SearchHero
│   ├── Large search input (auto-focus on kiosk)
│   └── SearchSuggestions dropdown (recent + popular)
├── CategoryGrid
│   ├── CategoryCard (icon, name, product count)
│   └── Responsive: 3 cols desktop, 2 cols tablet
└── FeaturedProducts (horizontal scroll carousel)
```

### SearchResultsPage

```
SearchResultsPage
├── SearchBar (smaller, in-page)
├── FilterPanel (left sidebar)
│   ├── CategoryFilter
│   ├── PriceRangeSlider
│   └── AttributeFilters (dynamic from API)
├── ProductGrid
│   ├── ProductCard (image, name, price, add-to-list)
│   └── Responsive: 4/3/2 cols by breakpoint
└── Pagination
```

### FloatingCart

```
FloatingCart (bottom-right, fixed position)
├── Collapsed: circular button with item count badge
├── Expanded: mini-list panel (max 5 items shown)
│   ├── ListItemPreview (thumbnail, name, qty, remove)
│   ├── "View Full List" link
│   └── Total item count
└── "Start Cart" button (prominent when no session)
```

## File Structure

```
src/
├── components/
│   ├── layout/
│   │   ├── Header.tsx
│   │   ├── Layout.tsx
│   │   └── FloatingCart.tsx
│   ├── product/
│   │   ├── ProductCard.tsx
│   │   ├── ProductGrid.tsx
│   │   └── ProductModal.tsx
│   ├── search/
│   │   ├── SearchBar.tsx
│   │   ├── SearchHero.tsx
│   │   └── SearchSuggestions.tsx
│   ├── category/
│   │   └── CategoryCard.tsx
│   ├── list/
│   │   ├── ListItemPreview.tsx
│   │   └── SessionPrompt.tsx
│   └── ui/
│       ├── Button.tsx
│       ├── Modal.tsx
│       └── Toast.tsx
├── pages/
│   ├── HomePage.tsx
│   ├── SearchResultsPage.tsx
│   ├── CategoryPage.tsx
│   └── ListPage.tsx
├── stores/
│   ├── sessionStore.ts
│   ├── listStore.ts
│   └── searchStore.ts
├── services/
│   ├── api.ts
│   ├── productService.ts
│   ├── categoryService.ts
│   ├── searchService.ts
│   ├── listService.ts
│   └── analyticsService.ts
├── hooks/
│   ├── useInactivityTimer.ts
│   └── useDebounce.ts
└── types/
    └── index.ts
```

## API Integration

### Session Flow

1. App loads → check localStorage for session_id
2. If exists + not expired → show "Continue previous?" prompt
3. User taps "Start Cart" → POST /api/lists → new session_id
4. Session ID stored in localStorage + Zustand
5. All API requests include X-Session-ID header
6. Inactivity timer (5 min) → auto-clear session
7. Any user interaction → reset timer

### List Sync Flow (QR sharing)

1. User taps "Share List" → POST /api/lists/{id}/share
2. Response: { share_code, sync_url }
3. Display QR code encoding sync_url
4. On phone: scan QR → open sync_url → list loads

### Analytics Events

- `search` - query, results count
- `view_product` - SKU, source (search/category/featured)
- `add_to_list` - SKU, quantity
- `remove_from_list` - SKU

## Error Handling

- API errors → toast notification
- Network offline → show banner, queue actions
- 404 product → redirect to search with message

## Touch-Friendly Guidelines

- Minimum tap target: 44x44px
- Generous padding on interactive elements
- Swipe gestures for carousel/list items
- Large, readable fonts (16px minimum)

## Implementation Order

1. Types + API client setup
2. Zustand stores
3. Layout + routing shell
4. HomePage (search + categories)
5. SearchResultsPage + ProductCard
6. FloatingCart + list interactions
7. ProductModal
8. Polish (loading states, errors, toast)
