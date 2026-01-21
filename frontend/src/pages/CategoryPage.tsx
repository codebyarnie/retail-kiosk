// frontend/src/pages/CategoryPage.tsx
import { useEffect, useState, useCallback } from 'react';
import { useParams } from 'react-router-dom';
import { ProductGrid, ProductModal } from '@/components/product';
import { ErrorDisplay } from '@/components/ui';
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

  const fetchCategory = useCallback(async () => {
    if (!slug) {
      return;
    }
    setIsLoading(true);
    setError(null);
    try {
      const data = await categoryService.getCategoryBySlug(slug);
      setCategory(data);
      setProducts(data.products);
    } catch {
      setError('Failed to load category');
    } finally {
      setIsLoading(false);
    }
  }, [slug]);

  useEffect(() => {
    fetchCategory();
  }, [fetchCategory]);

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
        <ErrorDisplay
          title="Category Not Found"
          message="We couldn't load this category. Please try again."
          onRetry={fetchCategory}
        />
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
