/**
 * JARVIS AI — Chat store (Zustand).
 */

import { create } from 'zustand';
import { api, type ChatSession, type ChatMessage } from '../services/api';

interface ChatStore {
  sessions: ChatSession[];
  activeSessionId: string | null;
  isLoading: boolean;
  error: string | null;

  loadSessions: () => Promise<void>;
  createSession: (title?: string) => Promise<ChatSession>;
  selectSession: (id: string | null) => void;
  sendMessage: (content: string) => Promise<void>;
  activeMessages: () => ChatMessage[];
}

export const useChatStore = create<ChatStore>((set, get) => ({
  sessions: [],
  activeSessionId: null,
  isLoading: false,
  error: null,

  loadSessions: async () => {
    set({ isLoading: true, error: null });
    try {
      const sessions = await api.listChats();
      set({ sessions, isLoading: false });
    } catch (err) {
      set({ error: (err as Error).message, isLoading: false });
    }
  },

  createSession: async (title) => {
    const session = await api.createChat({ title: title || 'New Chat' });
    set((state) => ({
      sessions: [session, ...state.sessions],
      activeSessionId: session.id,
    }));
    return session;
  },

  selectSession: (id) => {
    set({ activeSessionId: id });
  },

  sendMessage: async (content) => {
    const { activeSessionId } = get();
    if (!activeSessionId) return;

    set({ isLoading: true });
    try {
      await api.sendMessage(activeSessionId, content);
      // Refresh the session to get the new messages
      const session = await api.getChat(activeSessionId);
      set((state) => ({
        sessions: state.sessions.map((s) => (s.id === activeSessionId ? session : s)),
        isLoading: false,
      }));
    } catch (err) {
      set({ error: (err as Error).message, isLoading: false });
    }
  },

  activeMessages: () => {
    const { sessions, activeSessionId } = get();
    const session = sessions.find((s) => s.id === activeSessionId);
    return session?.messages || [];
  },
}));
