// frontend/src/components/product/ProductCard.tsx
import type { Product } from '@/types';
import { Button } from '@/components/ui';

interface ProductCardProps {
  product: Product;
  onAddToList?: (product: Product) => void;
  onClick?: (product: Product) => void;
}

export function ProductCard({ product, onAddToList, onClick }: ProductCardProps) {
  const handleClick = () => onClick?.(product);
  const handleAddToList = (e: React.MouseEvent) => {
    e.stopPropagation();
    onAddToList?.(product);
  };

  return (
    <div
      className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden hover:shadow-md transition-shadow cursor-pointer"
      onClick={handleClick}
    >
      {/* Image */}
      <div className="aspect-square bg-gray-100 relative">
        {product.thumbnail_url || product.image_url ? (
          <img
            src={product.thumbnail_url || product.image_url || ''}
            alt={product.name}
            className="w-full h-full object-cover"
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center text-gray-400">
            <svg className="w-16 h-16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
          </div>
        )}

        {/* Featured badge */}
        {product.is_featured && (
          <span className="absolute top-2 left-2 bg-primary-600 text-white text-xs font-medium px-2 py-1 rounded">
            Featured
          </span>
        )}
      </div>

      {/* Content */}
      <div className="p-4">
        <h3 className="font-semibold text-gray-900 line-clamp-2 min-h-[3rem]">
          {product.name}
        </h3>

        {product.short_description && (
          <p className="text-sm text-gray-500 mt-1 line-clamp-2">
            {product.short_description}
          </p>
        )}

        <div className="mt-3 flex items-center justify-between gap-2">
          <span className="text-lg font-bold text-gray-900">
            ${product.price.toFixed(2)}
          </span>

          <Button
            size="sm"
            variant="outline"
            onClick={handleAddToList}
          >
            Add to List
          </Button>
        </div>
      </div>
    </div>
  );
}
