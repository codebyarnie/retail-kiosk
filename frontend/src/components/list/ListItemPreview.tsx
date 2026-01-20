// frontend/src/components/list/ListItemPreview.tsx
import type { ListItem } from '@/types';

interface ListItemPreviewProps {
  item: ListItem;
  onRemove?: (sku: string) => void;
}

export function ListItemPreview({ item, onRemove }: ListItemPreviewProps) {
  return (
    <div className="flex items-center gap-3 py-2">
      {/* Thumbnail */}
      <div className="w-12 h-12 bg-gray-100 rounded-lg overflow-hidden flex-shrink-0">
        {item.product.thumbnail_url ? (
          <img
            src={item.product.thumbnail_url}
            alt={item.product.name}
            className="w-full h-full object-cover"
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center text-gray-400">
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
            </svg>
          </div>
        )}
      </div>

      {/* Info */}
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium text-gray-900 truncate">
          {item.product.name}
        </p>
        <p className="text-xs text-gray-500">
          Qty: {item.quantity} · ${(item.product.price * item.quantity).toFixed(2)}
        </p>
      </div>

      {/* Remove button */}
      {onRemove && (
        <button
          onClick={() => onRemove(item.product.sku)}
          className="p-1 text-gray-400 hover:text-red-600 touch-target"
          aria-label="Remove item"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      )}
    </div>
  );
}
