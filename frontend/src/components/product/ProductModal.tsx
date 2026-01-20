// frontend/src/components/product/ProductModal.tsx
import { useEffect, useState } from 'react';
import type { ProductDetail } from '@/types';
import { productService } from '@/services';
import { Modal, Button } from '@/components/ui';

interface ProductModalProps {
  sku: string | null;
  isOpen: boolean;
  onClose: () => void;
  onAddToList?: (product: ProductDetail) => void;
}

export function ProductModal({
  sku,
  isOpen,
  onClose,
  onAddToList,
}: ProductModalProps) {
  const [product, setProduct] = useState<ProductDetail | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!sku || !isOpen) {
      setProduct(null);
      return;
    }

    const fetchProduct = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const data = await productService.getProductBySku(sku);
        setProduct(data);
      } catch {
        setError('Failed to load product details');
      } finally {
        setIsLoading(false);
      }
    };

    fetchProduct();
  }, [sku, isOpen]);

  return (
    <Modal isOpen={isOpen} onClose={onClose} size="lg">
      {isLoading && (
        <div className="py-12 text-center">
          <div className="w-8 h-8 border-4 border-primary-600 border-t-transparent rounded-full animate-spin mx-auto" />
          <p className="mt-4 text-gray-500">Loading product...</p>
        </div>
      )}

      {error && (
        <div className="py-12 text-center text-red-600">
          <p>{error}</p>
          <Button variant="outline" onClick={onClose} className="mt-4">
            Close
          </Button>
        </div>
      )}

      {product && !isLoading && !error && (
        <div className="flex flex-col md:flex-row gap-6">
          {/* Image */}
          <div className="md:w-1/2">
            <div className="aspect-square bg-gray-100 rounded-lg overflow-hidden">
              {product.image_url ? (
                <img
                  src={product.image_url}
                  alt={product.name}
                  className="w-full h-full object-cover"
                />
              ) : (
                <div className="w-full h-full flex items-center justify-center text-gray-400">
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
                      d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
                    />
                  </svg>
                </div>
              )}
            </div>
          </div>

          {/* Details */}
          <div className="md:w-1/2">
            <h2 className="text-2xl font-bold text-gray-900">{product.name}</h2>
            <p className="text-sm text-gray-500 mt-1">SKU: {product.sku}</p>

            <div className="mt-4">
              <span className="text-3xl font-bold text-primary-600">
                ${product.price.toFixed(2)}
              </span>
            </div>

            {product.description && (
              <div className="mt-4">
                <h3 className="font-semibold text-gray-900 mb-2">Description</h3>
                <p className="text-gray-600">{product.description}</p>
              </div>
            )}

            {product.specifications &&
              Object.keys(product.specifications).length > 0 && (
                <div className="mt-4">
                  <h3 className="font-semibold text-gray-900 mb-2">
                    Specifications
                  </h3>
                  <dl className="space-y-1">
                    {Object.entries(product.specifications).map(
                      ([key, value]) => (
                        <div key={key} className="flex">
                          <dt className="w-1/3 text-gray-500 text-sm">{key}:</dt>
                          <dd className="w-2/3 text-gray-900 text-sm">
                            {String(value)}
                          </dd>
                        </div>
                      )
                    )}
                  </dl>
                </div>
              )}

            <div className="mt-6">
              <Button
                size="lg"
                className="w-full"
                onClick={() => onAddToList?.(product)}
              >
                Add to List
              </Button>
            </div>
          </div>
        </div>
      )}
    </Modal>
  );
}
