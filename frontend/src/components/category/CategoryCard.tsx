// frontend/src/components/category/CategoryCard.tsx
import { Link } from 'react-router-dom';
import type { Category, CategoryWithProducts } from '@/types';

interface CategoryCardProps {
  category: Category | CategoryWithProducts;
}

function hasProductCount(
  category: Category | CategoryWithProducts
): category is CategoryWithProducts {
  return 'product_count' in category && typeof category.product_count === 'number';
}

export function CategoryCard({ category }: CategoryCardProps) {
  return (
    <Link
      to={`/category/${category.slug}`}
      className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 hover:shadow-md hover:border-primary-300 transition-all group"
    >
      <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center mb-4 group-hover:bg-primary-200 transition-colors">
        <svg
          className="w-6 h-6 text-primary-600"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"
          />
        </svg>
      </div>
      <h3 className="font-semibold text-gray-900 group-hover:text-primary-600 transition-colors">
        {category.name}
      </h3>
      {hasProductCount(category) && category.product_count > 0 && (
        <p className="text-sm text-gray-500 mt-1">
          {category.product_count} product{category.product_count !== 1 ? 's' : ''}
        </p>
      )}
    </Link>
  );
}
