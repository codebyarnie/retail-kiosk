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
    if (!query.trim()) {
      return;
    }

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

  clearSearch: () =>
    set({ query: '', results: null, suggestions: [], filters: {} }),

  clearError: () => set({ error: null }),
}));
