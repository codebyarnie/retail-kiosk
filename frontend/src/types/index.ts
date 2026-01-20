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
  image_url: string | null;
  parent_id: number | null;
  display_order: number;
  is_active: boolean;
}

export interface CategoryTree extends Category {
  children: CategoryTree[];
}

export interface CategoryWithProducts extends Category {
  products: Product[];
  product_count: number;
}

// Search types
export interface SearchResult {
  product: Product;
  score: number;
  highlights: Record<string, string> | null;
}

export interface SearchGrouping {
  group_name: string;
  results: SearchResult[];
  total_in_group: number;
}

export interface SearchResponse {
  query: string;
  results: SearchResult[];
  groupings: SearchGrouping[] | null;
  total: number;
  page: number;
  page_size: number;
  pages: number;
  best_match: SearchResult | null;
  best_match_reason: string | null;
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

export interface FilterOption {
  value: string;
  label: string;
  count: number;
}

export interface FilterFacet {
  name: string;
  display_name: string;
  type: 'checkbox' | 'range' | 'single_select';
  options: FilterOption[];
}

export interface SearchFiltersResponse {
  facets: FilterFacet[];
  price_range: { min: number; max: number } | null;
  categories: Category[];
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
  device_type: string | null;
  created_at: string;
  last_active_at: string;
  expires_at: string | null;
}

// API response wrapper
export interface ApiError {
  detail: string;
  status_code?: number;
}

// Request types for creating/updating resources
export interface ProductCreate {
  sku: string;
  name: string;
  description?: string | null;
  short_description?: string | null;
  price: number;
  image_url?: string | null;
  thumbnail_url?: string | null;
  attributes?: Record<string, unknown>;
  specifications?: Record<string, unknown>;
  is_active?: boolean;
  is_featured?: boolean;
  category_ids?: number[] | null;
}

export interface ProductUpdate {
  name?: string | null;
  description?: string | null;
  short_description?: string | null;
  price?: number | null;
  image_url?: string | null;
  thumbnail_url?: string | null;
  attributes?: Record<string, unknown> | null;
  specifications?: Record<string, unknown> | null;
  is_active?: boolean | null;
  is_featured?: boolean | null;
  category_ids?: number[] | null;
}

export interface SearchRequest {
  query: string;
  category_id?: number | null;
  min_price?: number | null;
  max_price?: number | null;
  attributes?: Record<string, unknown> | null;
  page?: number;
  page_size?: number;
}

export interface ListItemCreate {
  product_sku: string;
  quantity?: number;
  notes?: string | null;
}

export interface ListItemUpdate {
  quantity?: number | null;
  notes?: string | null;
}

export interface UserListCreate {
  name?: string;
  description?: string | null;
}

export interface UserListUpdate {
  name?: string | null;
  description?: string | null;
}
