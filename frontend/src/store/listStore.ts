// frontend/src/store/listStore.ts
import { create } from 'zustand';
import type { UserListDetail } from '@/types';
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
      const message =
        err instanceof Error ? err.message : 'Failed to create list';
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
      const message =
        err instanceof Error ? err.message : 'Failed to fetch list';
      set({ error: message, isLoading: false });
    }
  },

  addItem: async (productSku: string, quantity = 1) => {
    const { currentList } = get();
    if (!currentList) {
      return;
    }

    set({ isLoading: true, error: null });
    try {
      const updatedList = await listService.addItem(
        currentList.id,
        productSku,
        quantity
      );
      set({ currentList: updatedList, isLoading: false });
    } catch (err) {
      const message =
        err instanceof Error ? err.message : 'Failed to add item';
      set({ error: message, isLoading: false });
    }
  },

  removeItem: async (productSku: string) => {
    const { currentList } = get();
    if (!currentList) {
      return;
    }

    set({ isLoading: true, error: null });
    try {
      await listService.removeItem(currentList.id, productSku);
      // Optimistically update the list
      set({
        currentList: {
          ...currentList,
          items: currentList.items.filter(
            (item) => item.product.sku !== productSku
          ),
          total_items: currentList.total_items - 1,
          unique_items: currentList.unique_items - 1,
        },
        isLoading: false,
      });
    } catch (err) {
      const message =
        err instanceof Error ? err.message : 'Failed to remove item';
      set({ error: message, isLoading: false });
    }
  },

  setExpanded: (expanded) => set({ isExpanded: expanded }),
  toggleExpanded: () => set((state) => ({ isExpanded: !state.isExpanded })),
  clearError: () => set({ error: null }),
}));
