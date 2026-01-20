// frontend/src/components/list/FloatingCart.tsx
import { Link } from 'react-router-dom';
import { useListStore, useSessionStore } from '@/store';
import { Button } from '@/components/ui';
import { ListItemPreview } from './ListItemPreview';

export function FloatingCart() {
  const { currentList, isExpanded, toggleExpanded, removeItem, createList } = useListStore();
  const { sessionId, setSession } = useSessionStore();

  const itemCount = currentList?.total_items ?? 0;
  const displayItems = currentList?.items.slice(0, 5) ?? [];

  const handleStartCart = async () => {
    try {
      const list = await createList();
      setSession(list.list_id, list.id);
    } catch (error) {
      console.error('Failed to create list:', error);
    }
  };

  // No session - show Start Cart button
  if (!sessionId || !currentList) {
    return (
      <div className="fixed bottom-6 right-6 z-40">
        <Button
          size="lg"
          onClick={handleStartCart}
          className="shadow-lg"
        >
          <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
          Start Cart
        </Button>
      </div>
    );
  }

  return (
    <div className="fixed bottom-6 right-6 z-40">
      {/* Expanded panel */}
      {isExpanded && (
        <div className="absolute bottom-16 right-0 w-80 bg-white rounded-xl shadow-xl border border-gray-200 overflow-hidden mb-2">
          <div className="p-4 border-b border-gray-100">
            <h3 className="font-semibold text-gray-900">Your List</h3>
            <p className="text-sm text-gray-500">{itemCount} item{itemCount !== 1 ? 's' : ''}</p>
          </div>

          <div className="max-h-64 overflow-auto p-4">
            {displayItems.length === 0 ? (
              <p className="text-sm text-gray-500 text-center py-4">
                Your list is empty
              </p>
            ) : (
              <div className="space-y-2">
                {displayItems.map((item) => (
                  <ListItemPreview
                    key={item.id}
                    item={item}
                    onRemove={removeItem}
                  />
                ))}
                {currentList.items.length > 5 && (
                  <p className="text-xs text-gray-500 text-center pt-2">
                    +{currentList.items.length - 5} more items
                  </p>
                )}
              </div>
            )}
          </div>

          <div className="p-4 border-t border-gray-100">
            <Link to="/list">
              <Button variant="outline" className="w-full">
                View Full List
              </Button>
            </Link>
          </div>
        </div>
      )}

      {/* Floating button */}
      <button
        onClick={toggleExpanded}
        className="w-14 h-14 bg-primary-600 text-white rounded-full shadow-lg hover:bg-primary-700 transition-colors flex items-center justify-center relative"
      >
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
        </svg>

        {/* Badge */}
        {itemCount > 0 && (
          <span className="absolute -top-1 -right-1 w-6 h-6 bg-red-500 text-white text-xs font-bold rounded-full flex items-center justify-center">
            {itemCount > 99 ? '99+' : itemCount}
          </span>
        )}
      </button>
    </div>
  );
}
