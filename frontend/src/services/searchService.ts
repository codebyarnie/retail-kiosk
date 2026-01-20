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
    const response = await api.get<SearchSuggestionsResponse>(
      '/search/suggestions',
      {
        params: { q: query },
      }
    );
    return response.data;
  },
};
