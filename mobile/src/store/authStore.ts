import { create } from 'zustand';
import * as SecureStore from 'expo-secure-store';

interface User {
  id: string;
  email: string;
  full_name: string;
}

interface AuthState {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  initializeAuth: () => Promise<void>;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  token: null,
  isLoading: true,

  initializeAuth: async () => {
    const token = await SecureStore.getItemAsync('token');
    set({ token, isLoading: false });
  },

  login: async (email: string, password: string) => {
    // API call implementation
    const token = 'dummy-token';
    await SecureStore.setItemAsync('token', token);
    set({ token, user: { id: '1', email, full_name: 'User' } });
  },

  logout: async () => {
    await SecureStore.deleteItemAsync('token');
    set({ user: null, token: null });
  },
}));
