// frontend/src/components/list/SessionPrompt.tsx
import { useSessionStore, useListStore } from '@/store';
import { Modal, Button } from '@/components/ui';

export function SessionPrompt() {
  const { showContinuePrompt, setShowContinuePrompt, clearSession, listId } = useSessionStore();
  const { fetchList, createList, setList } = useListStore();
  const { setSession } = useSessionStore();

  const handleContinue = async () => {
    if (listId) {
      await fetchList(listId);
    }
    setShowContinuePrompt(false);
  };

  const handleStartFresh = async () => {
    clearSession();
    setList(null);
    try {
      const list = await createList();
      setSession(list.list_id, list.id);
    } catch (error) {
      console.error('Failed to create new list:', error);
    }
    setShowContinuePrompt(false);
  };

  return (
    <Modal
      isOpen={showContinuePrompt}
      onClose={() => setShowContinuePrompt(false)}
      title="Continue Previous Session?"
      size="sm"
    >
      <p className="text-gray-600 mb-6">
        You have items from a previous session. Would you like to continue where you left off?
      </p>

      <div className="flex gap-3">
        <Button
          variant="outline"
          onClick={handleStartFresh}
          className="flex-1"
        >
          Start Fresh
        </Button>
        <Button
          onClick={handleContinue}
          className="flex-1"
        >
          Continue
        </Button>
      </div>
    </Modal>
  );
}
