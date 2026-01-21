// frontend/src/services/categoryService.ts
import api from './api';
import type { Category, CategoryTree, CategoryWithProducts } from '@/types';

export const categoryService = {
  async getCategories(): Promise<Category[]> {
    const response = await api.get<Category[]>('/categories');
    return response.data;
  },

  async getCategoryTree(): Promise<CategoryTree[]> {
    const response = await api.get<CategoryTree[]>('/categories/tree');
    return response.data;
  },

  async getCategoryBySlug(slug: string): Promise<CategoryWithProducts> {
    const response = await api.get<CategoryWithProducts>(`/categories/${slug}`);
    return response.data;
  },
};
