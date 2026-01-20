// frontend/src/pages/ListPage.tsx
import { useListStore, useSessionStore } from '@/store';
import { Button } from '@/components/ui';
import { ListItemPreview } from '@/components/list';

export function ListPage() {
  const { currentList, removeItem, isLoading } = useListStore();
  const { clearSession } = useSessionStore();

  const handleClearList = () => {
    clearSession();
  };

  if (!currentList) {
    return (
      <div className="max-w-2xl mx-auto px-4 py-12 text-center">
        <svg className="w-24 h-24 text-gray-300 mx-auto mb-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
        </svg>
        <h1 className="text-2xl font-bold text-gray-900 mb-2">No Active List</h1>
        <p className="text-gray-500">
          Start a new cart to begin adding products to your list.
        </p>
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
        <Button variant="outline" onClick={handleClearList}>
          Clear List
        </Button>
      </div>

      {currentList.items.length === 0 ? (
        <div className="text-center py-12 text-gray-500">
          <p>Your list is empty. Start browsing to add products!</p>
        </div>
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
    </div>
  );
}
