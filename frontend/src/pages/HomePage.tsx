// frontend/src/pages/HomePage.tsx
import { useEffect, useState } from 'react';
import { SearchHero } from '@/components/search';
import { CategoryGrid } from '@/components/category';
import { ProductGrid } from '@/components/product';
import { categoryService, productService } from '@/services';
import { useListStore } from '@/store';
import type { Category, Product } from '@/types';

export function HomePage() {
  const [categories, setCategories] = useState<Category[]>([]);
  const [featuredProducts, setFeaturedProducts] = useState<Product[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const { addItem, currentList } = useListStore();

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [cats, featured] = await Promise.all([
          categoryService.getCategories(),
          productService.getFeaturedProducts(),
        ]);
        setCategories(cats);
        setFeaturedProducts(featured);
      } catch (error) {
        console.error('Failed to load homepage data:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
  }, []);

  const handleAddToList = (product: Product) => {
    if (currentList) {
      addItem(product.sku);
    }
  };

  return (
    <div>
      <SearchHero />

      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Categories Section */}
        <section className="mb-12">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">
            Browse Categories
          </h2>
          <CategoryGrid categories={categories} isLoading={isLoading} />
        </section>

        {/* Featured Products Section */}
        {featuredProducts.length > 0 && (
          <section>
            <h2 className="text-2xl font-bold text-gray-900 mb-6">
              Featured Products
            </h2>
            <ProductGrid
              products={featuredProducts}
              onAddToList={handleAddToList}
              isLoading={isLoading}
            />
          </section>
        )}
      </div>
    </div>
  );
}
