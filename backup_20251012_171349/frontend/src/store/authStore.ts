import { create } from 'zustand';
import axios from 'axios';
import type { User } from '../types';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, fullName: string) => Promise<void>;
  logout: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  token: localStorage.getItem('token'),
  isAuthenticated: !!localStorage.getItem('token'),

  login: async (email, password) => {
    const response = await axios.post(`${API_URL}/api/auth/login`, { email, password });
    localStorage.setItem('token', response.data.access_token);
    axios.defaults.headers.common['Authorization'] = `Bearer ${response.data.access_token}`;
    set({
      user: response.data.user,
      token: response.data.access_token,
      isAuthenticated: true
    });
  },

  register: async (email, password, fullName) => {
    const response = await axios.post(`${API_URL}/api/auth/register`, {
      email,
      password,
      full_name: fullName
    });
    localStorage.setItem('token', response.data.access_token);
    axios.defaults.headers.common['Authorization'] = `Bearer ${response.data.access_token}`;
    set({
      user: response.data.user,
      token: response.data.access_token,
      isAuthenticated: true
    });
  },

  logout: () => {
    localStorage.removeItem('token');
    delete axios.defaults.headers.common['Authorization'];
    set({ user: null, token: null, isAuthenticated: false });
  }
}));
