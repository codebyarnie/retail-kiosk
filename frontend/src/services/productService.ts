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
