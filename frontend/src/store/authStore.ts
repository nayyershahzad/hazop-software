import { create } from 'zustand';
import axios from 'axios';
import type { User } from '../types';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

interface Organization {
  id: string;
  name: string;
  slug: string;
  subscription_plan: string;
}

interface AuthState {
  user: User | null;
  organization: Organization | null;
  token: string | null;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, fullName: string, organizationName: string) => Promise<void>;
  logout: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  organization: null,
  token: localStorage.getItem('token'),
  isAuthenticated: !!localStorage.getItem('token'),

  login: async (email, password) => {
    const response = await axios.post(`${API_URL}/api/auth/login`, { email, password });
    localStorage.setItem('token', response.data.access_token);
    localStorage.setItem('user', JSON.stringify(response.data.user));
    localStorage.setItem('organization', JSON.stringify(response.data.organization));
    axios.defaults.headers.common['Authorization'] = `Bearer ${response.data.access_token}`;
    set({
      user: response.data.user,
      organization: response.data.organization,
      token: response.data.access_token,
      isAuthenticated: true
    });
  },

  register: async (email, password, fullName, organizationName) => {
    const response = await axios.post(`${API_URL}/api/auth/register`, {
      email,
      password,
      full_name: fullName,
      organization_name: organizationName
    });
    localStorage.setItem('token', response.data.access_token);
    localStorage.setItem('user', JSON.stringify(response.data.user));
    localStorage.setItem('organization', JSON.stringify(response.data.organization));
    axios.defaults.headers.common['Authorization'] = `Bearer ${response.data.access_token}`;
    set({
      user: response.data.user,
      organization: response.data.organization,
      token: response.data.access_token,
      isAuthenticated: true
    });
  },

  logout: () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    localStorage.removeItem('organization');
    delete axios.defaults.headers.common['Authorization'];
    set({ user: null, organization: null, token: null, isAuthenticated: false });
  }
}));
