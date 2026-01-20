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

  async addItem(
    listId: number,
    productSku: string,
    quantity = 1
  ): Promise<UserListDetail> {
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
    const response = await api.post<ListSyncResponse>(
      `/lists/${listId}/share`
    );
    return response.data;
  },

  async syncFromCode(code: string): Promise<UserListDetail> {
    const response = await api.post<UserListDetail>(`/lists/sync/${code}`);
    return response.data;
  },
};
