// frontend/src/pages/ListPage.tsx
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useListStore, useSessionStore } from '@/store';
import { Button, EmptyState } from '@/components/ui';
import { ListItemPreview } from '@/components/list';
import { ShareListModal } from '@/components/qr';

export function ListPage() {
  const navigate = useNavigate();
  const { currentList, removeItem, isLoading } = useListStore();
  const { clearSession } = useSessionStore();
  const [showShareModal, setShowShareModal] = useState(false);

  const handleClearList = () => {
    clearSession();
  };

  if (!currentList) {
    return (
      <div className="max-w-2xl mx-auto px-4 py-12">
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
                d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
              />
            </svg>
          }
          title="No Active List"
          description="Start a new cart to begin adding products to your list."
          action={{ label: 'Browse Products', onClick: () => navigate('/') }}
        />
      </div>
    );
  }

  const totalValue = currentList.items.reduce(
    (sum, item) => sum + item.product.price * item.quantity,
    0
  );

  return (
    <div className="max-w-2xl mx-auto px-4 py-8">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">{currentList.name}</h1>
          <p className="text-gray-500">
            {currentList.total_items} item{currentList.total_items !== 1 ? 's' : ''}
          </p>
        </div>
        <div className="flex gap-2">
          {currentList.items.length > 0 && (
            <Button variant="secondary" onClick={() => setShowShareModal(true)}>
              <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z" />
              </svg>
              Share List
            </Button>
          )}
          <Button variant="outline" onClick={handleClearList}>
            Clear List
          </Button>
        </div>
      </div>

      {currentList.items.length === 0 ? (
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
                d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
              />
            </svg>
          }
          title="Your list is empty"
          description="Start browsing to add products to your list!"
          action={{ label: 'Browse Products', onClick: () => navigate('/') }}
        />
      ) : (
        <>
          <div className="bg-white rounded-xl border border-gray-200 divide-y divide-gray-100">
            {currentList.items.map((item) => (
              <div key={item.id} className="px-4">
                <ListItemPreview item={item} onRemove={removeItem} />
              </div>
            ))}
          </div>

          {/* Total */}
          <div className="mt-6 p-4 bg-gray-50 rounded-xl">
            <div className="flex justify-between text-lg font-semibold">
              <span>Estimated Total</span>
              <span>${totalValue.toFixed(2)}</span>
            </div>
            <p className="text-sm text-gray-500 mt-1">
              Prices may vary. See store associate for final pricing.
            </p>
          </div>
        </>
      )}

      {isLoading && (
        <div className="fixed inset-0 bg-black/20 flex items-center justify-center">
          <div className="w-8 h-8 border-4 border-primary-600 border-t-transparent rounded-full animate-spin" />
        </div>
      )}

      {currentList && (
        <ShareListModal
          isOpen={showShareModal}
          onClose={() => setShowShareModal(false)}
          listId={currentList.list_id}
        />
      )}
    </div>
  );
}
