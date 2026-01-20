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
