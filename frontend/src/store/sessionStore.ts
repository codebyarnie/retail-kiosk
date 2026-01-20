// frontend/src/store/sessionStore.ts
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

const SESSION_TIMEOUT_MS = 5 * 60 * 1000; // 5 minutes

interface SessionState {
  sessionId: string | null;
  listId: number | null;
  lastActive: number;
  showContinuePrompt: boolean;

  // Actions
  setSession: (sessionId: string, listId: number) => void;
  clearSession: () => void;
  updateLastActive: () => void;
  setShowContinuePrompt: (show: boolean) => void;
  isSessionExpired: () => boolean;
}

export const useSessionStore = create<SessionState>()(
  persist(
    (set, get) => ({
      sessionId: null,
      listId: null,
      lastActive: Date.now(),
      showContinuePrompt: false,

      setSession: (sessionId: string, listId: number) => {
        localStorage.setItem('session_id', sessionId);
        set({
          sessionId,
          listId,
          lastActive: Date.now(),
          showContinuePrompt: false,
        });
      },

      clearSession: () => {
        localStorage.removeItem('session_id');
        set({ sessionId: null, listId: null, showContinuePrompt: false });
      },

      updateLastActive: () => {
        set({ lastActive: Date.now() });
      },

      setShowContinuePrompt: (show: boolean) => {
        set({ showContinuePrompt: show });
      },

      isSessionExpired: () => {
        const { lastActive } = get();
        return Date.now() - lastActive > SESSION_TIMEOUT_MS;
      },
    }),
    {
      name: 'kiosk-session',
      partialize: (state) => ({
        sessionId: state.sessionId,
        listId: state.listId,
        lastActive: state.lastActive,
      }),
    }
  )
);
