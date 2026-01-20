// frontend/src/App.tsx
import { useEffect } from 'react';
import { Routes, Route } from 'react-router-dom';
import { Layout } from '@/components/layout';
import { FloatingCart, SessionPrompt } from '@/components/list';
import {
  HomePage,
  SearchResultsPage,
  CategoryPage,
  ListPage,
  SyncPage,
} from '@/pages';
import { useSessionStore, useListStore } from '@/store';

function App() {
  const { sessionId, listId, isSessionExpired, setShowContinuePrompt, updateLastActive } = useSessionStore();
  const { fetchList } = useListStore();

  // Check for existing session on mount
  useEffect(() => {
    if (sessionId && listId) {
      if (isSessionExpired()) {
        setShowContinuePrompt(true);
      } else {
        fetchList(listId);
      }
    }
  }, [sessionId, listId, isSessionExpired, setShowContinuePrompt, fetchList]);

  // Update last active on user interaction
  useEffect(() => {
    const handleActivity = () => updateLastActive();

    window.addEventListener('click', handleActivity);
    window.addEventListener('keydown', handleActivity);
    window.addEventListener('touchstart', handleActivity);

    return () => {
      window.removeEventListener('click', handleActivity);
      window.removeEventListener('keydown', handleActivity);
      window.removeEventListener('touchstart', handleActivity);
    };
  }, [updateLastActive]);

  return (
    <>
      <Layout>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/search" element={<SearchResultsPage />} />
          <Route path="/category/:slug" element={<CategoryPage />} />
          <Route path="/list" element={<ListPage />} />
          <Route path="/sync/:code?" element={<SyncPage />} />
        </Routes>
      </Layout>

      <FloatingCart />
      <SessionPrompt />
    </>
  );
}

export default App;
