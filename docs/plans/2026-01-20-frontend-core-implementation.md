# Frontend Core Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build the React frontend for the Retail Kiosk with search, browsing, and list management.

**Architecture:** Hybrid homepage with search + categories, floating mini-cart with session management, modal product details. Zustand for state, Axios for API, React Router for navigation.

**Tech Stack:** React 18, TypeScript, Vite, Tailwind CSS, Zustand, Axios, React Router v6

---

## Task 1: Configure Tailwind CSS

**Files:**
- Create: `frontend/tailwind.config.js`
- Create: `frontend/postcss.config.js`
- Modify: `frontend/src/index.css`

**Step 1: Create Tailwind config**

```javascript
// frontend/tailwind.config.js
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#eff6ff',
          100: '#dbeafe',
          200: '#bfdbfe',
          300: '#93c5fd',
          400: '#60a5fa',
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8',
          800: '#1e40af',
          900: '#1e3a8a',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      minHeight: {
        'touch': '44px',
      },
      minWidth: {
        'touch': '44px',
      },
    },
  },
  plugins: [],
}
```

**Step 2: Create PostCSS config**

```javascript
// frontend/postcss.config.js
export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
```

**Step 3: Update index.css with Tailwind directives**

Replace the entire content of `frontend/src/index.css` with:

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

/* Custom base styles */
@layer base {
  :root {
    font-family: Inter, system-ui, sans-serif;
  }

  body {
    @apply bg-gray-50 text-gray-900 min-h-screen;
  }

  #root {
    @apply min-h-screen w-full;
  }
}

/* Touch-friendly utilities */
@layer utilities {
  .touch-target {
    @apply min-h-touch min-w-touch;
  }
}
```

**Step 4: Verify Tailwind works**

Run: `cd frontend && npm run dev`
Expected: Dev server starts without errors

**Step 5: Commit**

```bash
git add frontend/tailwind.config.js frontend/postcss.config.js frontend/src/index.css
git commit -m "feat(frontend): configure Tailwind CSS"
```

---

## Task 2: Create TypeScript Types

**Files:**
- Create: `frontend/src/types/index.ts`

**Step 1: Create types file matching backend schemas**

```typescript
// frontend/src/types/index.ts

// Product types
export interface Product {
  id: number;
  sku: string;
  name: string;
  short_description: string | null;
  price: number;
  image_url: string | null;
  thumbnail_url: string | null;
  is_active: boolean;
  is_featured: boolean;
}

export interface ProductDetail extends Product {
  description: string | null;
  attributes: Record<string, unknown> | null;
  specifications: Record<string, unknown> | null;
  categories: Category[];
  created_at: string;
  updated_at: string;
}

export interface ProductListResponse {
  items: Product[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
}

// Category types
export interface Category {
  id: number;
  name: string;
  slug: string;
  description: string | null;
  parent_id: number | null;
  product_count: number;
}

export interface CategoryTree extends Category {
  children: CategoryTree[];
}

// Search types
export interface SearchResult {
  product: Product;
  score: number;
  highlights: Record<string, string> | null;
}

export interface SearchResponse {
  query: string;
  results: SearchResult[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
}

export interface SearchSuggestion {
  text: string;
  type: 'query' | 'category' | 'product' | 'attribute';
  metadata: Record<string, unknown> | null;
}

export interface SearchSuggestionsResponse {
  suggestions: SearchSuggestion[];
  recent_searches: string[];
  popular_searches: string[];
}

// List types
export interface ListItem {
  id: number;
  quantity: number;
  notes: string | null;
  price_at_add: number | null;
  product: Product;
  created_at: string;
}

export interface UserList {
  id: number;
  list_id: string;
  name: string;
  description: string | null;
  share_code: string | null;
  total_items: number;
  unique_items: number;
  created_at: string;
  updated_at: string;
}

export interface UserListDetail extends UserList {
  items: ListItem[];
}

export interface ListSyncResponse {
  list_id: string;
  share_code: string;
  sync_url: string;
}

// Session types
export interface Session {
  session_id: string;
  created_at: string;
  last_active: string;
  expires_at: string;
}

// API response wrapper
export interface ApiError {
  detail: string;
  status_code?: number;
}
```

**Step 2: Verify TypeScript compiles**

Run: `cd frontend && npm run type-check`
Expected: No errors

**Step 3: Commit**

```bash
git add frontend/src/types/index.ts
git commit -m "feat(frontend): add TypeScript types for API"
```

---

## Task 3: Create API Client

**Files:**
- Create: `frontend/src/services/api.ts`
- Create: `frontend/src/services/productService.ts`
- Create: `frontend/src/services/categoryService.ts`
- Create: `frontend/src/services/searchService.ts`
- Create: `frontend/src/services/listService.ts`

**Step 1: Create base API client**

```typescript
// frontend/src/services/api.ts
import axios, { AxiosError, AxiosInstance } from 'axios';
import type { ApiError } from '@/types';

const API_BASE_URL = '/api';

const api: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add session ID to requests
api.interceptors.request.use((config) => {
  const sessionId = localStorage.getItem('session_id');
  if (sessionId) {
    config.headers['X-Session-ID'] = sessionId;
  }
  return config;
});

// Handle errors
api.interceptors.response.use(
  (response) => response,
  (error: AxiosError<ApiError>) => {
    const message = error.response?.data?.detail || 'An error occurred';
    console.error('API Error:', message);
    return Promise.reject(error);
  }
);

export default api;
```

**Step 2: Create product service**

```typescript
// frontend/src/services/productService.ts
import api from './api';
import type { Product, ProductDetail, ProductListResponse } from '@/types';

export const productService = {
  async getProducts(page = 1, pageSize = 20): Promise<ProductListResponse> {
    const response = await api.get<ProductListResponse>('/products', {
      params: { page, page_size: pageSize },
    });
    return response.data;
  },

  async getProductBySku(sku: string): Promise<ProductDetail> {
    const response = await api.get<ProductDetail>(`/products/${sku}`);
    return response.data;
  },

  async getFeaturedProducts(): Promise<Product[]> {
    const response = await api.get<Product[]>('/products/featured');
    return response.data;
  },
};
```

**Step 3: Create category service**

```typescript
// frontend/src/services/categoryService.ts
import api from './api';
import type { Category, CategoryTree, ProductListResponse } from '@/types';

export const categoryService = {
  async getCategories(): Promise<Category[]> {
    const response = await api.get<Category[]>('/categories');
    return response.data;
  },

  async getCategoryTree(): Promise<CategoryTree[]> {
    const response = await api.get<CategoryTree[]>('/categories/tree');
    return response.data;
  },

  async getCategoryBySlug(slug: string): Promise<{ category: Category; products: ProductListResponse }> {
    const response = await api.get(`/categories/${slug}`);
    return response.data;
  },
};
```

**Step 4: Create search service**

```typescript
// frontend/src/services/searchService.ts
import api from './api';
import type { SearchResponse, SearchSuggestionsResponse } from '@/types';

export interface SearchParams {
  query: string;
  category_id?: number;
  min_price?: number;
  max_price?: number;
  page?: number;
  page_size?: number;
}

export const searchService = {
  async search(params: SearchParams): Promise<SearchResponse> {
    const response = await api.get<SearchResponse>('/search', {
      params: { q: params.query, ...params },
    });
    return response.data;
  },

  async getSuggestions(query: string): Promise<SearchSuggestionsResponse> {
    const response = await api.get<SearchSuggestionsResponse>('/search/suggestions', {
      params: { q: query },
    });
    return response.data;
  },
};
```

**Step 5: Create list service**

```typescript
// frontend/src/services/listService.ts
import api from './api';
import type { UserList, UserListDetail, ListSyncResponse } from '@/types';

export const listService = {
  async getLists(): Promise<UserList[]> {
    const response = await api.get<UserList[]>('/lists');
    return response.data;
  },

  async createList(name = 'My List'): Promise<UserListDetail> {
    const response = await api.post<UserListDetail>('/lists', { name });
    return response.data;
  },

  async getList(id: number): Promise<UserListDetail> {
    const response = await api.get<UserListDetail>(`/lists/${id}`);
    return response.data;
  },

  async addItem(listId: number, productSku: string, quantity = 1): Promise<UserListDetail> {
    const response = await api.post<UserListDetail>(`/lists/${listId}/items`, {
      product_sku: productSku,
      quantity,
    });
    return response.data;
  },

  async removeItem(listId: number, productSku: string): Promise<void> {
    await api.delete(`/lists/${listId}/items/${productSku}`);
  },

  async shareList(listId: number): Promise<ListSyncResponse> {
    const response = await api.post<ListSyncResponse>(`/lists/${listId}/share`);
    return response.data;
  },

  async syncFromCode(code: string): Promise<UserListDetail> {
    const response = await api.post<UserListDetail>(`/lists/sync/${code}`);
    return response.data;
  },
};
```

**Step 6: Create services barrel export**

```typescript
// frontend/src/services/index.ts
export { default as api } from './api';
export { productService } from './productService';
export { categoryService } from './categoryService';
export { searchService } from './searchService';
export { listService } from './listService';
```

**Step 7: Verify TypeScript compiles**

Run: `cd frontend && npm run type-check`
Expected: No errors

**Step 8: Commit**

```bash
git add frontend/src/services/
git commit -m "feat(frontend): add API service layer"
```

---

## Task 4: Create Zustand Stores

**Files:**
- Create: `frontend/src/store/sessionStore.ts`
- Create: `frontend/src/store/listStore.ts`
- Create: `frontend/src/store/searchStore.ts`
- Create: `frontend/src/store/index.ts`

**Step 1: Create session store**

```typescript
// frontend/src/store/sessionStore.ts
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

const SESSION_TIMEOUT_MS = 5 * 60 * 1000; // 5 minutes

interface SessionState {
  sessionId: string | null;
  listId: number | null;
  lastActive: number;
  showContinuePrompt: boolean;

  // Actions
  setSession: (sessionId: string, listId: number) => void;
  clearSession: () => void;
  updateLastActive: () => void;
  setShowContinuePrompt: (show: boolean) => void;
  isSessionExpired: () => boolean;
}

export const useSessionStore = create<SessionState>()(
  persist(
    (set, get) => ({
      sessionId: null,
      listId: null,
      lastActive: Date.now(),
      showContinuePrompt: false,

      setSession: (sessionId: string, listId: number) => {
        localStorage.setItem('session_id', sessionId);
        set({ sessionId, listId, lastActive: Date.now(), showContinuePrompt: false });
      },

      clearSession: () => {
        localStorage.removeItem('session_id');
        set({ sessionId: null, listId: null, showContinuePrompt: false });
      },

      updateLastActive: () => {
        set({ lastActive: Date.now() });
      },

      setShowContinuePrompt: (show: boolean) => {
        set({ showContinuePrompt: show });
      },

      isSessionExpired: () => {
        const { lastActive } = get();
        return Date.now() - lastActive > SESSION_TIMEOUT_MS;
      },
    }),
    {
      name: 'kiosk-session',
      partialize: (state) => ({
        sessionId: state.sessionId,
        listId: state.listId,
        lastActive: state.lastActive,
      }),
    }
  )
);
```

**Step 2: Create list store**

```typescript
// frontend/src/store/listStore.ts
import { create } from 'zustand';
import type { UserListDetail, ListItem } from '@/types';
import { listService } from '@/services';

interface ListState {
  currentList: UserListDetail | null;
  isLoading: boolean;
  error: string | null;
  isExpanded: boolean;

  // Actions
  setList: (list: UserListDetail | null) => void;
  createList: (name?: string) => Promise<UserListDetail>;
  fetchList: (id: number) => Promise<void>;
  addItem: (productSku: string, quantity?: number) => Promise<void>;
  removeItem: (productSku: string) => Promise<void>;
  setExpanded: (expanded: boolean) => void;
  toggleExpanded: () => void;
  clearError: () => void;
}

export const useListStore = create<ListState>((set, get) => ({
  currentList: null,
  isLoading: false,
  error: null,
  isExpanded: false,

  setList: (list) => set({ currentList: list }),

  createList: async (name = 'My List') => {
    set({ isLoading: true, error: null });
    try {
      const list = await listService.createList(name);
      set({ currentList: list, isLoading: false });
      return list;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to create list';
      set({ error: message, isLoading: false });
      throw err;
    }
  },

  fetchList: async (id: number) => {
    set({ isLoading: true, error: null });
    try {
      const list = await listService.getList(id);
      set({ currentList: list, isLoading: false });
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to fetch list';
      set({ error: message, isLoading: false });
    }
  },

  addItem: async (productSku: string, quantity = 1) => {
    const { currentList } = get();
    if (!currentList) return;

    set({ isLoading: true, error: null });
    try {
      const updatedList = await listService.addItem(currentList.id, productSku, quantity);
      set({ currentList: updatedList, isLoading: false });
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to add item';
      set({ error: message, isLoading: false });
    }
  },

  removeItem: async (productSku: string) => {
    const { currentList } = get();
    if (!currentList) return;

    set({ isLoading: true, error: null });
    try {
      await listService.removeItem(currentList.id, productSku);
      // Optimistically update the list
      set({
        currentList: {
          ...currentList,
          items: currentList.items.filter((item) => item.product.sku !== productSku),
          total_items: currentList.total_items - 1,
          unique_items: currentList.unique_items - 1,
        },
        isLoading: false,
      });
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to remove item';
      set({ error: message, isLoading: false });
    }
  },

  setExpanded: (expanded) => set({ isExpanded: expanded }),
  toggleExpanded: () => set((state) => ({ isExpanded: !state.isExpanded })),
  clearError: () => set({ error: null }),
}));
```

**Step 3: Create search store**

```typescript
// frontend/src/store/searchStore.ts
import { create } from 'zustand';
import type { SearchResponse, SearchSuggestion } from '@/types';
import { searchService, SearchParams } from '@/services/searchService';

interface SearchState {
  query: string;
  results: SearchResponse | null;
  suggestions: SearchSuggestion[];
  isLoading: boolean;
  error: string | null;
  filters: {
    categoryId?: number;
    minPrice?: number;
    maxPrice?: number;
  };

  // Actions
  setQuery: (query: string) => void;
  search: (params?: Partial<SearchParams>) => Promise<void>;
  fetchSuggestions: (query: string) => Promise<void>;
  setFilters: (filters: SearchState['filters']) => void;
  clearSearch: () => void;
  clearError: () => void;
}

export const useSearchStore = create<SearchState>((set, get) => ({
  query: '',
  results: null,
  suggestions: [],
  isLoading: false,
  error: null,
  filters: {},

  setQuery: (query) => set({ query }),

  search: async (params?: Partial<SearchParams>) => {
    const { query, filters } = get();
    if (!query.trim()) return;

    set({ isLoading: true, error: null });
    try {
      const results = await searchService.search({
        query,
        category_id: filters.categoryId,
        min_price: filters.minPrice,
        max_price: filters.maxPrice,
        ...params,
      });
      set({ results, isLoading: false });
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Search failed';
      set({ error: message, isLoading: false });
    }
  },

  fetchSuggestions: async (query: string) => {
    if (!query.trim()) {
      set({ suggestions: [] });
      return;
    }

    try {
      const response = await searchService.getSuggestions(query);
      set({ suggestions: response.suggestions });
    } catch {
      // Silently fail for suggestions
      set({ suggestions: [] });
    }
  },

  setFilters: (filters) => set({ filters }),

  clearSearch: () => set({ query: '', results: null, suggestions: [], filters: {} }),

  clearError: () => set({ error: null }),
}));
```

**Step 4: Create stores barrel export**

```typescript
// frontend/src/store/index.ts
export { useSessionStore } from './sessionStore';
export { useListStore } from './listStore';
export { useSearchStore } from './searchStore';
```

**Step 5: Verify TypeScript compiles**

Run: `cd frontend && npm run type-check`
Expected: No errors

**Step 6: Commit**

```bash
git add frontend/src/store/
git commit -m "feat(frontend): add Zustand state stores"
```

---

## Task 5: Create Test Setup

**Files:**
- Create: `frontend/src/test/setup.ts`

**Step 1: Create test setup file**

```typescript
// frontend/src/test/setup.ts
import '@testing-library/jest-dom';

// Mock localStorage
const localStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
};
Object.defineProperty(window, 'localStorage', { value: localStorageMock });

// Mock matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: vi.fn().mockImplementation((query: string) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(),
    removeListener: vi.fn(),
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })),
});

// Reset mocks between tests
beforeEach(() => {
  vi.clearAllMocks();
  localStorageMock.getItem.mockReturnValue(null);
});
```

**Step 2: Verify test setup works**

Run: `cd frontend && npm run test -- --run`
Expected: Test runner starts (may show 0 tests)

**Step 3: Commit**

```bash
git add frontend/src/test/setup.ts
git commit -m "feat(frontend): add test setup"
```

---

## Task 6: Create UI Components

**Files:**
- Create: `frontend/src/components/ui/Button.tsx`
- Create: `frontend/src/components/ui/Modal.tsx`
- Create: `frontend/src/components/ui/index.ts`

**Step 1: Create Button component**

```tsx
// frontend/src/components/ui/Button.tsx
import { ButtonHTMLAttributes, forwardRef } from 'react';
import classNames from 'classnames';

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = 'primary', size = 'md', children, ...props }, ref) => {
    const baseStyles = 'inline-flex items-center justify-center font-medium rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:pointer-events-none touch-target';

    const variants = {
      primary: 'bg-primary-600 text-white hover:bg-primary-700 focus:ring-primary-500',
      secondary: 'bg-gray-200 text-gray-900 hover:bg-gray-300 focus:ring-gray-500',
      outline: 'border-2 border-primary-600 text-primary-600 hover:bg-primary-50 focus:ring-primary-500',
      ghost: 'text-gray-700 hover:bg-gray-100 focus:ring-gray-500',
    };

    const sizes = {
      sm: 'px-3 py-1.5 text-sm',
      md: 'px-4 py-2 text-base',
      lg: 'px-6 py-3 text-lg',
    };

    return (
      <button
        ref={ref}
        className={classNames(baseStyles, variants[variant], sizes[size], className)}
        {...props}
      >
        {children}
      </button>
    );
  }
);

Button.displayName = 'Button';
```

**Step 2: Create Modal component**

```tsx
// frontend/src/components/ui/Modal.tsx
import { ReactNode, useEffect } from 'react';
import classNames from 'classnames';

interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title?: string;
  children: ReactNode;
  size?: 'sm' | 'md' | 'lg' | 'xl';
}

export function Modal({ isOpen, onClose, title, children, size = 'md' }: ModalProps) {
  // Close on escape key
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };

    if (isOpen) {
      document.addEventListener('keydown', handleEscape);
      document.body.style.overflow = 'hidden';
    }

    return () => {
      document.removeEventListener('keydown', handleEscape);
      document.body.style.overflow = '';
    };
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const sizes = {
    sm: 'max-w-sm',
    md: 'max-w-lg',
    lg: 'max-w-2xl',
    xl: 'max-w-4xl',
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/50 backdrop-blur-sm"
        onClick={onClose}
      />

      {/* Modal content */}
      <div className={classNames(
        'relative bg-white rounded-xl shadow-xl w-full mx-4 max-h-[90vh] overflow-auto',
        sizes[size]
      )}>
        {/* Header */}
        {title && (
          <div className="flex items-center justify-between p-4 border-b">
            <h2 className="text-xl font-semibold text-gray-900">{title}</h2>
            <button
              onClick={onClose}
              className="p-2 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100 touch-target"
              aria-label="Close"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        )}

        {/* Body */}
        <div className="p-4">
          {children}
        </div>
      </div>
    </div>
  );
}
```

**Step 3: Create barrel export**

```typescript
// frontend/src/components/ui/index.ts
export { Button } from './Button';
export { Modal } from './Modal';
```

**Step 4: Verify TypeScript compiles**

Run: `cd frontend && npm run type-check`
Expected: No errors

**Step 5: Commit**

```bash
git add frontend/src/components/ui/
git commit -m "feat(frontend): add UI components (Button, Modal)"
```

---

## Task 7: Create Layout Components

**Files:**
- Create: `frontend/src/components/layout/Header.tsx`
- Create: `frontend/src/components/layout/Layout.tsx`
- Create: `frontend/src/components/layout/index.ts`

**Step 1: Create Header component**

```tsx
// frontend/src/components/layout/Header.tsx
import { Link } from 'react-router-dom';

export function Header() {
  return (
    <header className="bg-white shadow-sm border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-2">
            <div className="w-10 h-10 bg-primary-600 rounded-lg flex items-center justify-center">
              <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
              </svg>
            </div>
            <span className="text-xl font-bold text-gray-900">Retail Kiosk</span>
          </Link>

          {/* Navigation hint */}
          <div className="text-sm text-gray-500">
            Touch to browse products
          </div>
        </div>
      </div>
    </header>
  );
}
```

**Step 2: Create Layout component**

```tsx
// frontend/src/components/layout/Layout.tsx
import { ReactNode } from 'react';
import { Header } from './Header';

interface LayoutProps {
  children: ReactNode;
}

export function Layout({ children }: LayoutProps) {
  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <Header />
      <main className="flex-1">
        {children}
      </main>
    </div>
  );
}
```

**Step 3: Create barrel export**

```typescript
// frontend/src/components/layout/index.ts
export { Header } from './Header';
export { Layout } from './Layout';
```

**Step 4: Commit**

```bash
git add frontend/src/components/layout/
git commit -m "feat(frontend): add layout components"
```

---

## Task 8: Create Product Components

**Files:**
- Create: `frontend/src/components/product/ProductCard.tsx`
- Create: `frontend/src/components/product/ProductGrid.tsx`
- Create: `frontend/src/components/product/ProductModal.tsx`
- Create: `frontend/src/components/product/index.ts`

**Step 1: Create ProductCard component**

```tsx
// frontend/src/components/product/ProductCard.tsx
import type { Product } from '@/types';
import { Button } from '@/components/ui';

interface ProductCardProps {
  product: Product;
  onAddToList?: (product: Product) => void;
  onClick?: (product: Product) => void;
}

export function ProductCard({ product, onAddToList, onClick }: ProductCardProps) {
  const handleClick = () => onClick?.(product);
  const handleAddToList = (e: React.MouseEvent) => {
    e.stopPropagation();
    onAddToList?.(product);
  };

  return (
    <div
      className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden hover:shadow-md transition-shadow cursor-pointer"
      onClick={handleClick}
    >
      {/* Image */}
      <div className="aspect-square bg-gray-100 relative">
        {product.thumbnail_url || product.image_url ? (
          <img
            src={product.thumbnail_url || product.image_url || ''}
            alt={product.name}
            className="w-full h-full object-cover"
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center text-gray-400">
            <svg className="w-16 h-16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
          </div>
        )}

        {/* Featured badge */}
        {product.is_featured && (
          <span className="absolute top-2 left-2 bg-primary-600 text-white text-xs font-medium px-2 py-1 rounded">
            Featured
          </span>
        )}
      </div>

      {/* Content */}
      <div className="p-4">
        <h3 className="font-semibold text-gray-900 line-clamp-2 min-h-[3rem]">
          {product.name}
        </h3>

        {product.short_description && (
          <p className="text-sm text-gray-500 mt-1 line-clamp-2">
            {product.short_description}
          </p>
        )}

        <div className="mt-3 flex items-center justify-between gap-2">
          <span className="text-lg font-bold text-gray-900">
            ${product.price.toFixed(2)}
          </span>

          <Button
            size="sm"
            variant="outline"
            onClick={handleAddToList}
          >
            Add to List
          </Button>
        </div>
      </div>
    </div>
  );
}
```

**Step 2: Create ProductGrid component**

```tsx
// frontend/src/components/product/ProductGrid.tsx
import type { Product } from '@/types';
import { ProductCard } from './ProductCard';

interface ProductGridProps {
  products: Product[];
  onAddToList?: (product: Product) => void;
  onProductClick?: (product: Product) => void;
  isLoading?: boolean;
}

export function ProductGrid({ products, onAddToList, onProductClick, isLoading }: ProductGridProps) {
  if (isLoading) {
    return (
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
        {Array.from({ length: 8 }).map((_, i) => (
          <div key={i} className="bg-white rounded-xl border border-gray-200 overflow-hidden animate-pulse">
            <div className="aspect-square bg-gray-200" />
            <div className="p-4 space-y-3">
              <div className="h-4 bg-gray-200 rounded w-3/4" />
              <div className="h-4 bg-gray-200 rounded w-1/2" />
              <div className="h-8 bg-gray-200 rounded" />
            </div>
          </div>
        ))}
      </div>
    );
  }

  if (products.length === 0) {
    return (
      <div className="text-center py-12 text-gray-500">
        <svg className="w-16 h-16 mx-auto mb-4 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
        </svg>
        <p className="text-lg">No products found</p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
      {products.map((product) => (
        <ProductCard
          key={product.id}
          product={product}
          onAddToList={onAddToList}
          onClick={onProductClick}
        />
      ))}
    </div>
  );
}
```

**Step 3: Create ProductModal component**

```tsx
// frontend/src/components/product/ProductModal.tsx
import { useEffect, useState } from 'react';
import type { ProductDetail } from '@/types';
import { productService } from '@/services';
import { Modal, Button } from '@/components/ui';

interface ProductModalProps {
  sku: string | null;
  isOpen: boolean;
  onClose: () => void;
  onAddToList?: (product: ProductDetail) => void;
}

export function ProductModal({ sku, isOpen, onClose, onAddToList }: ProductModalProps) {
  const [product, setProduct] = useState<ProductDetail | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!sku || !isOpen) {
      setProduct(null);
      return;
    }

    const fetchProduct = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const data = await productService.getProductBySku(sku);
        setProduct(data);
      } catch {
        setError('Failed to load product details');
      } finally {
        setIsLoading(false);
      }
    };

    fetchProduct();
  }, [sku, isOpen]);

  return (
    <Modal isOpen={isOpen} onClose={onClose} size="lg">
      {isLoading && (
        <div className="py-12 text-center">
          <div className="w-8 h-8 border-4 border-primary-600 border-t-transparent rounded-full animate-spin mx-auto" />
          <p className="mt-4 text-gray-500">Loading product...</p>
        </div>
      )}

      {error && (
        <div className="py-12 text-center text-red-600">
          <p>{error}</p>
          <Button variant="outline" onClick={onClose} className="mt-4">
            Close
          </Button>
        </div>
      )}

      {product && !isLoading && !error && (
        <div className="flex flex-col md:flex-row gap-6">
          {/* Image */}
          <div className="md:w-1/2">
            <div className="aspect-square bg-gray-100 rounded-lg overflow-hidden">
              {product.image_url ? (
                <img
                  src={product.image_url}
                  alt={product.name}
                  className="w-full h-full object-cover"
                />
              ) : (
                <div className="w-full h-full flex items-center justify-center text-gray-400">
                  <svg className="w-24 h-24" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                  </svg>
                </div>
              )}
            </div>
          </div>

          {/* Details */}
          <div className="md:w-1/2">
            <h2 className="text-2xl font-bold text-gray-900">{product.name}</h2>
            <p className="text-sm text-gray-500 mt-1">SKU: {product.sku}</p>

            <div className="mt-4">
              <span className="text-3xl font-bold text-primary-600">
                ${product.price.toFixed(2)}
              </span>
            </div>

            {product.description && (
              <div className="mt-4">
                <h3 className="font-semibold text-gray-900 mb-2">Description</h3>
                <p className="text-gray-600">{product.description}</p>
              </div>
            )}

            {product.specifications && Object.keys(product.specifications).length > 0 && (
              <div className="mt-4">
                <h3 className="font-semibold text-gray-900 mb-2">Specifications</h3>
                <dl className="space-y-1">
                  {Object.entries(product.specifications).map(([key, value]) => (
                    <div key={key} className="flex">
                      <dt className="w-1/3 text-gray-500 text-sm">{key}:</dt>
                      <dd className="w-2/3 text-gray-900 text-sm">{String(value)}</dd>
                    </div>
                  ))}
                </dl>
              </div>
            )}

            <div className="mt-6">
              <Button
                size="lg"
                className="w-full"
                onClick={() => onAddToList?.(product)}
              >
                Add to List
              </Button>
            </div>
          </div>
        </div>
      )}
    </Modal>
  );
}
```

**Step 4: Create barrel export**

```typescript
// frontend/src/components/product/index.ts
export { ProductCard } from './ProductCard';
export { ProductGrid } from './ProductGrid';
export { ProductModal } from './ProductModal';
```

**Step 5: Commit**

```bash
git add frontend/src/components/product/
git commit -m "feat(frontend): add product components"
```

---

## Task 9: Create Search Components

**Files:**
- Create: `frontend/src/components/search/SearchBar.tsx`
- Create: `frontend/src/components/search/SearchHero.tsx`
- Create: `frontend/src/components/search/index.ts`
- Create: `frontend/src/hooks/useDebounce.ts`

**Step 1: Create useDebounce hook**

```typescript
// frontend/src/hooks/useDebounce.ts
import { useState, useEffect } from 'react';

export function useDebounce<T>(value: T, delay: number): T {
  const [debouncedValue, setDebouncedValue] = useState<T>(value);

  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => {
      clearTimeout(timer);
    };
  }, [value, delay]);

  return debouncedValue;
}
```

**Step 2: Create SearchBar component**

```tsx
// frontend/src/components/search/SearchBar.tsx
import { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useSearchStore } from '@/store';
import { useDebounce } from '@/hooks/useDebounce';

interface SearchBarProps {
  size?: 'default' | 'large';
  autoFocus?: boolean;
}

export function SearchBar({ size = 'default', autoFocus = false }: SearchBarProps) {
  const navigate = useNavigate();
  const inputRef = useRef<HTMLInputElement>(null);
  const { query, setQuery, suggestions, fetchSuggestions } = useSearchStore();
  const [localQuery, setLocalQuery] = useState(query);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const debouncedQuery = useDebounce(localQuery, 300);

  useEffect(() => {
    if (autoFocus && inputRef.current) {
      inputRef.current.focus();
    }
  }, [autoFocus]);

  useEffect(() => {
    if (debouncedQuery) {
      fetchSuggestions(debouncedQuery);
    }
  }, [debouncedQuery, fetchSuggestions]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (localQuery.trim()) {
      setQuery(localQuery);
      setShowSuggestions(false);
      navigate(`/search?q=${encodeURIComponent(localQuery)}`);
    }
  };

  const handleSuggestionClick = (text: string) => {
    setLocalQuery(text);
    setQuery(text);
    setShowSuggestions(false);
    navigate(`/search?q=${encodeURIComponent(text)}`);
  };

  const inputClasses = size === 'large'
    ? 'text-xl py-4 px-6'
    : 'text-base py-2 px-4';

  return (
    <form onSubmit={handleSubmit} className="relative w-full">
      <div className="relative">
        <input
          ref={inputRef}
          type="text"
          value={localQuery}
          onChange={(e) => {
            setLocalQuery(e.target.value);
            setShowSuggestions(true);
          }}
          onFocus={() => setShowSuggestions(true)}
          onBlur={() => setTimeout(() => setShowSuggestions(false), 200)}
          placeholder="Search for products..."
          className={`w-full bg-white border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-primary-500 outline-none ${inputClasses}`}
        />
        <button
          type="submit"
          className="absolute right-2 top-1/2 -translate-y-1/2 p-2 text-gray-400 hover:text-primary-600 touch-target"
        >
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
        </button>
      </div>

      {/* Suggestions dropdown */}
      {showSuggestions && suggestions.length > 0 && (
        <div className="absolute top-full left-0 right-0 mt-1 bg-white border border-gray-200 rounded-xl shadow-lg z-10 overflow-hidden">
          {suggestions.map((suggestion, index) => (
            <button
              key={index}
              type="button"
              className="w-full px-4 py-3 text-left hover:bg-gray-50 flex items-center gap-3 touch-target"
              onClick={() => handleSuggestionClick(suggestion.text)}
            >
              <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
              <span className="text-gray-700">{suggestion.text}</span>
              <span className="ml-auto text-xs text-gray-400 capitalize">{suggestion.type}</span>
            </button>
          ))}
        </div>
      )}
    </form>
  );
}
```

**Step 3: Create SearchHero component**

```tsx
// frontend/src/components/search/SearchHero.tsx
import { SearchBar } from './SearchBar';

export function SearchHero() {
  return (
    <div className="bg-gradient-to-br from-primary-600 to-primary-800 text-white py-16 px-4">
      <div className="max-w-3xl mx-auto text-center">
        <h1 className="text-4xl font-bold mb-4">
          Find What You Need
        </h1>
        <p className="text-primary-100 text-lg mb-8">
          Search thousands of products or browse by category
        </p>
        <div className="max-w-xl mx-auto">
          <SearchBar size="large" autoFocus />
        </div>
      </div>
    </div>
  );
}
```

**Step 4: Create barrel export and hooks index**

```typescript
// frontend/src/components/search/index.ts
export { SearchBar } from './SearchBar';
export { SearchHero } from './SearchHero';
```

```typescript
// frontend/src/hooks/index.ts
export { useDebounce } from './useDebounce';
```

**Step 5: Commit**

```bash
git add frontend/src/components/search/ frontend/src/hooks/
git commit -m "feat(frontend): add search components and hooks"
```

---

## Task 10: Create Category Components

**Files:**
- Create: `frontend/src/components/category/CategoryCard.tsx`
- Create: `frontend/src/components/category/CategoryGrid.tsx`
- Create: `frontend/src/components/category/index.ts`

**Step 1: Create CategoryCard component**

```tsx
// frontend/src/components/category/CategoryCard.tsx
import { Link } from 'react-router-dom';
import type { Category } from '@/types';

interface CategoryCardProps {
  category: Category;
}

export function CategoryCard({ category }: CategoryCardProps) {
  return (
    <Link
      to={`/category/${category.slug}`}
      className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 hover:shadow-md hover:border-primary-300 transition-all group"
    >
      <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center mb-4 group-hover:bg-primary-200 transition-colors">
        <svg className="w-6 h-6 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
        </svg>
      </div>
      <h3 className="font-semibold text-gray-900 group-hover:text-primary-600 transition-colors">
        {category.name}
      </h3>
      {category.product_count > 0 && (
        <p className="text-sm text-gray-500 mt-1">
          {category.product_count} product{category.product_count !== 1 ? 's' : ''}
        </p>
      )}
    </Link>
  );
}
```

**Step 2: Create CategoryGrid component**

```tsx
// frontend/src/components/category/CategoryGrid.tsx
import type { Category } from '@/types';
import { CategoryCard } from './CategoryCard';

interface CategoryGridProps {
  categories: Category[];
  isLoading?: boolean;
}

export function CategoryGrid({ categories, isLoading }: CategoryGridProps) {
  if (isLoading) {
    return (
      <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
        {Array.from({ length: 6 }).map((_, i) => (
          <div key={i} className="bg-white rounded-xl border border-gray-200 p-6 animate-pulse">
            <div className="w-12 h-12 bg-gray-200 rounded-lg mb-4" />
            <div className="h-4 bg-gray-200 rounded w-2/3 mb-2" />
            <div className="h-3 bg-gray-200 rounded w-1/3" />
          </div>
        ))}
      </div>
    );
  }

  if (categories.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        No categories available
      </div>
    );
  }

  return (
    <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
      {categories.map((category) => (
        <CategoryCard key={category.id} category={category} />
      ))}
    </div>
  );
}
```

**Step 3: Create barrel export**

```typescript
// frontend/src/components/category/index.ts
export { CategoryCard } from './CategoryCard';
export { CategoryGrid } from './CategoryGrid';
```

**Step 4: Commit**

```bash
git add frontend/src/components/category/
git commit -m "feat(frontend): add category components"
```

---

## Task 11: Create List Components

**Files:**
- Create: `frontend/src/components/list/ListItemPreview.tsx`
- Create: `frontend/src/components/list/FloatingCart.tsx`
- Create: `frontend/src/components/list/SessionPrompt.tsx`
- Create: `frontend/src/components/list/index.ts`

**Step 1: Create ListItemPreview component**

```tsx
// frontend/src/components/list/ListItemPreview.tsx
import type { ListItem } from '@/types';

interface ListItemPreviewProps {
  item: ListItem;
  onRemove?: (sku: string) => void;
}

export function ListItemPreview({ item, onRemove }: ListItemPreviewProps) {
  return (
    <div className="flex items-center gap-3 py-2">
      {/* Thumbnail */}
      <div className="w-12 h-12 bg-gray-100 rounded-lg overflow-hidden flex-shrink-0">
        {item.product.thumbnail_url ? (
          <img
            src={item.product.thumbnail_url}
            alt={item.product.name}
            className="w-full h-full object-cover"
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center text-gray-400">
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
            </svg>
          </div>
        )}
      </div>

      {/* Info */}
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium text-gray-900 truncate">
          {item.product.name}
        </p>
        <p className="text-xs text-gray-500">
          Qty: {item.quantity} · ${(item.product.price * item.quantity).toFixed(2)}
        </p>
      </div>

      {/* Remove button */}
      {onRemove && (
        <button
          onClick={() => onRemove(item.product.sku)}
          className="p-1 text-gray-400 hover:text-red-600 touch-target"
          aria-label="Remove item"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      )}
    </div>
  );
}
```

**Step 2: Create FloatingCart component**

```tsx
// frontend/src/components/list/FloatingCart.tsx
import { Link } from 'react-router-dom';
import { useListStore, useSessionStore } from '@/store';
import { Button } from '@/components/ui';
import { ListItemPreview } from './ListItemPreview';

export function FloatingCart() {
  const { currentList, isExpanded, toggleExpanded, removeItem, createList } = useListStore();
  const { sessionId, setSession } = useSessionStore();

  const itemCount = currentList?.total_items ?? 0;
  const displayItems = currentList?.items.slice(0, 5) ?? [];

  const handleStartCart = async () => {
    try {
      const list = await createList();
      setSession(list.list_id, list.id);
    } catch (error) {
      console.error('Failed to create list:', error);
    }
  };

  // No session - show Start Cart button
  if (!sessionId || !currentList) {
    return (
      <div className="fixed bottom-6 right-6 z-40">
        <Button
          size="lg"
          onClick={handleStartCart}
          className="shadow-lg"
        >
          <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
          Start Cart
        </Button>
      </div>
    );
  }

  return (
    <div className="fixed bottom-6 right-6 z-40">
      {/* Expanded panel */}
      {isExpanded && (
        <div className="absolute bottom-16 right-0 w-80 bg-white rounded-xl shadow-xl border border-gray-200 overflow-hidden mb-2">
          <div className="p-4 border-b border-gray-100">
            <h3 className="font-semibold text-gray-900">Your List</h3>
            <p className="text-sm text-gray-500">{itemCount} item{itemCount !== 1 ? 's' : ''}</p>
          </div>

          <div className="max-h-64 overflow-auto p-4">
            {displayItems.length === 0 ? (
              <p className="text-sm text-gray-500 text-center py-4">
                Your list is empty
              </p>
            ) : (
              <div className="space-y-2">
                {displayItems.map((item) => (
                  <ListItemPreview
                    key={item.id}
                    item={item}
                    onRemove={removeItem}
                  />
                ))}
                {currentList.items.length > 5 && (
                  <p className="text-xs text-gray-500 text-center pt-2">
                    +{currentList.items.length - 5} more items
                  </p>
                )}
              </div>
            )}
          </div>

          <div className="p-4 border-t border-gray-100">
            <Link to="/list">
              <Button variant="outline" className="w-full">
                View Full List
              </Button>
            </Link>
          </div>
        </div>
      )}

      {/* Floating button */}
      <button
        onClick={toggleExpanded}
        className="w-14 h-14 bg-primary-600 text-white rounded-full shadow-lg hover:bg-primary-700 transition-colors flex items-center justify-center relative"
      >
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
        </svg>

        {/* Badge */}
        {itemCount > 0 && (
          <span className="absolute -top-1 -right-1 w-6 h-6 bg-red-500 text-white text-xs font-bold rounded-full flex items-center justify-center">
            {itemCount > 99 ? '99+' : itemCount}
          </span>
        )}
      </button>
    </div>
  );
}
```

**Step 3: Create SessionPrompt component**

```tsx
// frontend/src/components/list/SessionPrompt.tsx
import { useSessionStore, useListStore } from '@/store';
import { Modal, Button } from '@/components/ui';

export function SessionPrompt() {
  const { showContinuePrompt, setShowContinuePrompt, clearSession, listId } = useSessionStore();
  const { fetchList, createList, setList } = useListStore();
  const { setSession } = useSessionStore();

  const handleContinue = async () => {
    if (listId) {
      await fetchList(listId);
    }
    setShowContinuePrompt(false);
  };

  const handleStartFresh = async () => {
    clearSession();
    setList(null);
    try {
      const list = await createList();
      setSession(list.list_id, list.id);
    } catch (error) {
      console.error('Failed to create new list:', error);
    }
    setShowContinuePrompt(false);
  };

  return (
    <Modal
      isOpen={showContinuePrompt}
      onClose={() => setShowContinuePrompt(false)}
      title="Continue Previous Session?"
      size="sm"
    >
      <p className="text-gray-600 mb-6">
        You have items from a previous session. Would you like to continue where you left off?
      </p>

      <div className="flex gap-3">
        <Button
          variant="outline"
          onClick={handleStartFresh}
          className="flex-1"
        >
          Start Fresh
        </Button>
        <Button
          onClick={handleContinue}
          className="flex-1"
        >
          Continue
        </Button>
      </div>
    </Modal>
  );
}
```

**Step 4: Create barrel export**

```typescript
// frontend/src/components/list/index.ts
export { ListItemPreview } from './ListItemPreview';
export { FloatingCart } from './FloatingCart';
export { SessionPrompt } from './SessionPrompt';
```

**Step 5: Commit**

```bash
git add frontend/src/components/list/
git commit -m "feat(frontend): add list and cart components"
```

---

## Task 12: Create Pages

**Files:**
- Create: `frontend/src/pages/HomePage.tsx`
- Create: `frontend/src/pages/SearchResultsPage.tsx`
- Create: `frontend/src/pages/CategoryPage.tsx`
- Create: `frontend/src/pages/ListPage.tsx`
- Create: `frontend/src/pages/index.ts`

**Step 1: Create HomePage**

```tsx
// frontend/src/pages/HomePage.tsx
import { useEffect, useState } from 'react';
import { SearchHero } from '@/components/search';
import { CategoryGrid } from '@/components/category';
import { ProductGrid } from '@/components/product';
import { categoryService, productService } from '@/services';
import { useListStore } from '@/store';
import type { Category, Product } from '@/types';

export function HomePage() {
  const [categories, setCategories] = useState<Category[]>([]);
  const [featuredProducts, setFeaturedProducts] = useState<Product[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const { addItem, currentList } = useListStore();

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [cats, featured] = await Promise.all([
          categoryService.getCategories(),
          productService.getFeaturedProducts(),
        ]);
        setCategories(cats);
        setFeaturedProducts(featured);
      } catch (error) {
        console.error('Failed to load homepage data:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
  }, []);

  const handleAddToList = (product: Product) => {
    if (currentList) {
      addItem(product.sku);
    }
  };

  return (
    <div>
      <SearchHero />

      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Categories Section */}
        <section className="mb-12">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">
            Browse Categories
          </h2>
          <CategoryGrid categories={categories} isLoading={isLoading} />
        </section>

        {/* Featured Products Section */}
        {featuredProducts.length > 0 && (
          <section>
            <h2 className="text-2xl font-bold text-gray-900 mb-6">
              Featured Products
            </h2>
            <ProductGrid
              products={featuredProducts}
              onAddToList={handleAddToList}
              isLoading={isLoading}
            />
          </section>
        )}
      </div>
    </div>
  );
}
```

**Step 2: Create SearchResultsPage**

```tsx
// frontend/src/pages/SearchResultsPage.tsx
import { useEffect, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { SearchBar } from '@/components/search';
import { ProductGrid, ProductModal } from '@/components/product';
import { useSearchStore, useListStore } from '@/store';
import type { Product, ProductDetail } from '@/types';

export function SearchResultsPage() {
  const [searchParams] = useSearchParams();
  const query = searchParams.get('q') || '';
  const { results, isLoading, error, setQuery, search } = useSearchStore();
  const { addItem, currentList } = useListStore();
  const [selectedSku, setSelectedSku] = useState<string | null>(null);

  useEffect(() => {
    if (query) {
      setQuery(query);
      search();
    }
  }, [query, setQuery, search]);

  const handleAddToList = (product: Product | ProductDetail) => {
    if (currentList) {
      addItem(product.sku);
    }
  };

  const handleProductClick = (product: Product) => {
    setSelectedSku(product.sku);
  };

  const products = results?.results.map((r) => r.product) ?? [];

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      {/* Search bar */}
      <div className="max-w-2xl mb-8">
        <SearchBar />
      </div>

      {/* Results header */}
      <div className="mb-6">
        {query && (
          <h1 className="text-2xl font-bold text-gray-900">
            Results for "{query}"
          </h1>
        )}
        {results && (
          <p className="text-gray-500 mt-1">
            {results.total} product{results.total !== 1 ? 's' : ''} found
          </p>
        )}
      </div>

      {/* Error state */}
      {error && (
        <div className="bg-red-50 text-red-600 p-4 rounded-lg mb-6">
          {error}
        </div>
      )}

      {/* Results grid */}
      <ProductGrid
        products={products}
        onAddToList={handleAddToList}
        onProductClick={handleProductClick}
        isLoading={isLoading}
      />

      {/* Product modal */}
      <ProductModal
        sku={selectedSku}
        isOpen={!!selectedSku}
        onClose={() => setSelectedSku(null)}
        onAddToList={handleAddToList}
      />
    </div>
  );
}
```

**Step 3: Create CategoryPage**

```tsx
// frontend/src/pages/CategoryPage.tsx
import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { ProductGrid, ProductModal } from '@/components/product';
import { categoryService } from '@/services';
import { useListStore } from '@/store';
import type { Category, Product, ProductDetail } from '@/types';

export function CategoryPage() {
  const { slug } = useParams<{ slug: string }>();
  const [category, setCategory] = useState<Category | null>(null);
  const [products, setProducts] = useState<Product[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { addItem, currentList } = useListStore();
  const [selectedSku, setSelectedSku] = useState<string | null>(null);

  useEffect(() => {
    if (!slug) return;

    const fetchCategory = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const data = await categoryService.getCategoryBySlug(slug);
        setCategory(data.category);
        setProducts(data.products.items);
      } catch {
        setError('Failed to load category');
      } finally {
        setIsLoading(false);
      }
    };

    fetchCategory();
  }, [slug]);

  const handleAddToList = (product: Product | ProductDetail) => {
    if (currentList) {
      addItem(product.sku);
    }
  };

  const handleProductClick = (product: Product) => {
    setSelectedSku(product.sku);
  };

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      {/* Header */}
      {category && (
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">{category.name}</h1>
          {category.description && (
            <p className="text-gray-600 mt-2">{category.description}</p>
          )}
        </div>
      )}

      {/* Error state */}
      {error && (
        <div className="bg-red-50 text-red-600 p-4 rounded-lg mb-6">
          {error}
        </div>
      )}

      {/* Products grid */}
      <ProductGrid
        products={products}
        onAddToList={handleAddToList}
        onProductClick={handleProductClick}
        isLoading={isLoading}
      />

      {/* Product modal */}
      <ProductModal
        sku={selectedSku}
        isOpen={!!selectedSku}
        onClose={() => setSelectedSku(null)}
        onAddToList={handleAddToList}
      />
    </div>
  );
}
```

**Step 4: Create ListPage**

```tsx
// frontend/src/pages/ListPage.tsx
import { useListStore, useSessionStore } from '@/store';
import { Button } from '@/components/ui';
import { ListItemPreview } from '@/components/list';

export function ListPage() {
  const { currentList, removeItem, isLoading } = useListStore();
  const { clearSession } = useSessionStore();

  const handleClearList = () => {
    clearSession();
  };

  if (!currentList) {
    return (
      <div className="max-w-2xl mx-auto px-4 py-12 text-center">
        <svg className="w-24 h-24 text-gray-300 mx-auto mb-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
        </svg>
        <h1 className="text-2xl font-bold text-gray-900 mb-2">No Active List</h1>
        <p className="text-gray-500">
          Start a new cart to begin adding products to your list.
        </p>
      </div>
    );
  }

  const totalValue = currentList.items.reduce(
    (sum, item) => sum + item.product.price * item.quantity,
    0
  );

  return (
    <div className="max-w-2xl mx-auto px-4 py-8">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">{currentList.name}</h1>
          <p className="text-gray-500">
            {currentList.total_items} item{currentList.total_items !== 1 ? 's' : ''}
          </p>
        </div>
        <Button variant="outline" onClick={handleClearList}>
          Clear List
        </Button>
      </div>

      {currentList.items.length === 0 ? (
        <div className="text-center py-12 text-gray-500">
          <p>Your list is empty. Start browsing to add products!</p>
        </div>
      ) : (
        <>
          <div className="bg-white rounded-xl border border-gray-200 divide-y divide-gray-100">
            {currentList.items.map((item) => (
              <div key={item.id} className="px-4">
                <ListItemPreview item={item} onRemove={removeItem} />
              </div>
            ))}
          </div>

          {/* Total */}
          <div className="mt-6 p-4 bg-gray-50 rounded-xl">
            <div className="flex justify-between text-lg font-semibold">
              <span>Estimated Total</span>
              <span>${totalValue.toFixed(2)}</span>
            </div>
            <p className="text-sm text-gray-500 mt-1">
              Prices may vary. See store associate for final pricing.
            </p>
          </div>
        </>
      )}

      {isLoading && (
        <div className="fixed inset-0 bg-black/20 flex items-center justify-center">
          <div className="w-8 h-8 border-4 border-primary-600 border-t-transparent rounded-full animate-spin" />
        </div>
      )}
    </div>
  );
}
```

**Step 5: Create barrel export**

```typescript
// frontend/src/pages/index.ts
export { HomePage } from './HomePage';
export { SearchResultsPage } from './SearchResultsPage';
export { CategoryPage } from './CategoryPage';
export { ListPage } from './ListPage';
```

**Step 6: Commit**

```bash
git add frontend/src/pages/
git commit -m "feat(frontend): add page components"
```

---

## Task 13: Wire Up Router and App

**Files:**
- Modify: `frontend/src/App.tsx`
- Modify: `frontend/src/main.tsx`

**Step 1: Update App.tsx with routing**

Replace entire content of `frontend/src/App.tsx`:

```tsx
// frontend/src/App.tsx
import { useEffect } from 'react';
import { Routes, Route } from 'react-router-dom';
import { Layout } from '@/components/layout';
import { FloatingCart, SessionPrompt } from '@/components/list';
import { HomePage, SearchResultsPage, CategoryPage, ListPage } from '@/pages';
import { useSessionStore, useListStore } from '@/store';

function App() {
  const { sessionId, listId, isSessionExpired, setShowContinuePrompt, updateLastActive } = useSessionStore();
  const { fetchList } = useListStore();

  // Check for existing session on mount
  useEffect(() => {
    if (sessionId && listId) {
      if (isSessionExpired()) {
        setShowContinuePrompt(true);
      } else {
        fetchList(listId);
      }
    }
  }, [sessionId, listId, isSessionExpired, setShowContinuePrompt, fetchList]);

  // Update last active on user interaction
  useEffect(() => {
    const handleActivity = () => updateLastActive();

    window.addEventListener('click', handleActivity);
    window.addEventListener('keydown', handleActivity);
    window.addEventListener('touchstart', handleActivity);

    return () => {
      window.removeEventListener('click', handleActivity);
      window.removeEventListener('keydown', handleActivity);
      window.removeEventListener('touchstart', handleActivity);
    };
  }, [updateLastActive]);

  return (
    <>
      <Layout>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/search" element={<SearchResultsPage />} />
          <Route path="/category/:slug" element={<CategoryPage />} />
          <Route path="/list" element={<ListPage />} />
        </Routes>
      </Layout>

      <FloatingCart />
      <SessionPrompt />
    </>
  );
}

export default App;
```

**Step 2: Update main.tsx with BrowserRouter**

Replace entire content of `frontend/src/main.tsx`:

```tsx
// frontend/src/main.tsx
import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import App from './App';
import './index.css';

const rootElement = document.getElementById('root');

if (!rootElement) {
  throw new Error('Failed to find the root element.');
}

ReactDOM.createRoot(rootElement).render(
  <React.StrictMode>
    <BrowserRouter>
      <App />
    </BrowserRouter>
  </React.StrictMode>
);
```

**Step 3: Delete old App.css (no longer needed)**

```bash
rm frontend/src/App.css
```

**Step 4: Verify TypeScript compiles**

Run: `cd frontend && npm run type-check`
Expected: No errors

**Step 5: Commit**

```bash
git add frontend/src/App.tsx frontend/src/main.tsx
git rm frontend/src/App.css
git commit -m "feat(frontend): wire up routing and app shell"
```

---

## Task 14: Create Component Barrel Exports

**Files:**
- Create: `frontend/src/components/index.ts`

**Step 1: Create main components barrel export**

```typescript
// frontend/src/components/index.ts
export * from './ui';
export * from './layout';
export * from './product';
export * from './search';
export * from './category';
export * from './list';
```

**Step 2: Commit**

```bash
git add frontend/src/components/index.ts
git commit -m "feat(frontend): add component barrel exports"
```

---

## Task 15: Build and Test in Docker

**Step 1: Start Docker services**

Run: `docker-compose up -d`
Expected: All services start successfully

**Step 2: Run database migrations**

Run: `cd backend && alembic upgrade head`
Expected: Migrations applied

**Step 3: Seed sample data**

Run: `cd backend && python scripts/seed_data.py`
Expected: Sample data seeded

**Step 4: Build frontend**

Run: `cd frontend && npm run build`
Expected: Build completes without errors

**Step 5: Run frontend type check**

Run: `cd frontend && npm run type-check`
Expected: No type errors

**Step 6: Run frontend lint**

Run: `cd frontend && npm run lint`
Expected: No lint errors (or only warnings)

**Step 7: Start services and test manually**

Run in terminal 1: `cd backend && uvicorn app.main:app --reload --port 8000`
Run in terminal 2: `cd frontend && npm run dev`

Test in browser at http://localhost:5173:
- [ ] Homepage loads with search and categories
- [ ] Search works and shows results
- [ ] Category pages load with products
- [ ] "Start Cart" creates a new list
- [ ] Add to list works
- [ ] Floating cart shows items
- [ ] List page displays items

**Step 8: Final commit**

```bash
git add -A
git commit -m "feat(frontend): complete Phase 4 frontend core implementation"
```

---

## Summary

This plan implements the complete frontend core for the Retail Kiosk:

1. **Tailwind CSS** - Configured with touch-friendly utilities
2. **TypeScript Types** - Matching backend API schemas
3. **API Services** - Axios client with session handling
4. **Zustand Stores** - Session, list, and search state
5. **UI Components** - Button, Modal
6. **Layout Components** - Header, Layout
7. **Product Components** - ProductCard, ProductGrid, ProductModal
8. **Search Components** - SearchBar, SearchHero
9. **Category Components** - CategoryCard, CategoryGrid
10. **List Components** - ListItemPreview, FloatingCart, SessionPrompt
11. **Pages** - Home, Search, Category, List
12. **App Routing** - React Router v6 setup

Total: ~15 tasks with incremental commits
