'use client';

import React, { createContext, useContext, useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';

interface User {
  id: string;
  email: string;
  name: string;
  role_id?: string;
  role_name?: string;
  is_active: boolean;
}

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, name?: string) => Promise<void>;
  logout: () => void;
  isAuthenticated: boolean;
  isAdmin: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  // API Base URL
  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    const token = localStorage.getItem('access_token');
    
    if (!token) {
      setLoading(false);
      return;
    }

    try {
      const response = await fetch(`${API_URL}/auth/me`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const userData = await response.json();
        // Ensure user object has proper structure
        if (userData && typeof userData === 'object') {
          setUser({
            id: userData.id || '',
            email: userData.email || '',
            name: userData.full_name || userData.name || 'User',
            role_id: userData.role_id || undefined,
            role_name: (userData.role && userData.role.name) || userData.role_name || undefined,
            is_active: userData.is_active !== false,
          });
        }
      } else {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
      }
    } catch (error) {
      console.error('Auth check failed:', error);
    } finally {
      setLoading(false);
    }
  };

  const login = async (email: string, password: string) => {
    // 🔧 Fixed: Changed from /api/v1/auth/login to /auth/login
    const response = await fetch(`${API_URL}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Login failed');
    }

    const data = await response.json();
    
    localStorage.setItem('access_token', data.access_token);
    localStorage.setItem('refresh_token', data.refresh_token);
    
    // Ensure user object has proper structure
    const userData: User = {
      id: data.user?.id || '',
      email: data.user?.email || email,
      name: data.user?.full_name || data.user?.name || 'User',
      role_id: data.user?.role_id || undefined,
      role_name: (data.user?.role && data.user.role.name) || data.user?.role_name || undefined,
      is_active: data.user?.is_active !== false,
    };
    
    setUser(userData);
    
    // Check if user is admin by role_id or role object
    const isAdmin = data.user?.role?.name === 'admin' || 
                   (data.user?.role_id && data.user.role_id.includes('admin'));
    
    if (isAdmin) {
      router.push('/admin');
    } else {
      router.push('/home');
    }
  };

  const register = async (email: string, password: string, name?: string) => {
    // 🔧 Fixed: Changed from /api/v1/auth/register to /auth/register
    const response = await fetch(`${API_URL}/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password, full_name: name || email })
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Registration failed');
    }

    const data = await response.json();
    
    localStorage.setItem('access_token', data.access_token);
    localStorage.setItem('refresh_token', data.refresh_token);
    
    // Ensure user object has proper structure
    const userData: User = {
      id: data.user?.id || '',
      email: data.user?.email || email,
      name: data.user?.full_name || data.user?.name || name || 'User',
      role_id: data.user?.role_id || undefined,
      is_active: data.user?.is_active !== false,
    };
    
    setUser(userData);
    router.push('/home');
  };

  const logout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    setUser(null);
    router.push('/login');
  };

  // Check if user is admin
  const isAdmin = Boolean(
    user?.role_id?.toString().toLowerCase().includes('admin') ||
    (user?.role_name && user.role_name.toLowerCase() === 'admin')
  );

  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        login,
        register,
        logout,
        isAuthenticated: !!user,
        isAdmin
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
}
