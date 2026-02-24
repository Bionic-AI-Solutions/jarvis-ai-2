/**
 * JARVIS AI — Auth store (Zustand).
 */

import { create } from 'zustand';
import { api } from '../services/api';

interface AuthStore {
  isLocked: boolean;
  hasPassphrase: boolean;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;

  checkStatus: () => Promise<void>;
  login: (passphrase: string) => Promise<boolean>;
  lock: () => Promise<void>;
  setPassphrase: (passphrase: string) => Promise<void>;
}

export const useAuthStore = create<AuthStore>((set) => ({
  isLocked: true,
  hasPassphrase: false,
  isAuthenticated: false,
  isLoading: false,
  error: null,

  checkStatus: async () => {
    try {
      const status = await api.getAuthStatus();
      set({
        isLocked: status.is_locked,
        hasPassphrase: status.has_passphrase,
        isAuthenticated: !status.is_locked && status.has_passphrase,
      });
    } catch {
      set({ error: 'Failed to check auth status' });
    }
  },

  login: async (passphrase) => {
    set({ isLoading: true, error: null });
    try {
      const response = await api.verifyPassphrase(passphrase);
      if (response.authenticated && response.token) {
        api.setToken(response.token);
        set({ isAuthenticated: true, isLocked: false, isLoading: false });
        return true;
      }
      set({ error: 'Invalid passphrase', isLoading: false });
      return false;
    } catch (err) {
      set({ error: (err as Error).message, isLoading: false });
      return false;
    }
  },

  lock: async () => {
    try {
      await api.lock();
      api.setToken(null);
      set({ isLocked: true, isAuthenticated: false });
    } catch (err) {
      set({ error: (err as Error).message });
    }
  },

  setPassphrase: async (passphrase) => {
    set({ isLoading: true, error: null });
    try {
      await api.setPassphrase(passphrase);
      set({ hasPassphrase: true, isLoading: false });
    } catch (err) {
      set({ error: (err as Error).message, isLoading: false });
    }
  },
}));
