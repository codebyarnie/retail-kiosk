// frontend/src/pages/SearchResultsPage.tsx
import { useEffect, useState } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { SearchBar } from '@/components/search';
import { ProductGrid, ProductModal } from '@/components/product';
import { ErrorDisplay, EmptyState } from '@/components/ui';
import { useSearchStore, useListStore } from '@/store';
import type { Product, ProductDetail } from '@/types';

export function SearchResultsPage() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
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
            Results for &quot;{query}&quot;
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
        <ErrorDisplay
          message="Failed to load search results. Please try again."
          onRetry={() => search()}
        />
      )}

      {/* Empty state */}
      {!isLoading && !error && products.length === 0 && query && (
        <EmptyState
          icon={
            <svg
              className="w-24 h-24"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={1.5}
                d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
              />
            </svg>
          }
          title="No results found"
          description={`We couldn't find any products matching "${query}"`}
          action={{ label: 'Go Home', onClick: () => navigate('/') }}
        />
      )}

      {/* Results grid */}
      {!error && (products.length > 0 || isLoading) && (
        <ProductGrid
          products={products}
          onAddToList={handleAddToList}
          onProductClick={handleProductClick}
          isLoading={isLoading}
        />
      )}

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
