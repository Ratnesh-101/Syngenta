import React, { createContext, useContext, useEffect, useState, useCallback } from 'react';
import type { Rep } from '../types';
import { getMe } from '../api/auth';

interface AuthContextValue {
  rep: Rep | null;
  token: string | null;
  isLoading: boolean;
  login: (token: string, rep: Rep) => void;
  logout: () => void;
  refreshMe: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [rep, setRep] = useState<Rep | null>(() => {
    try {
      const stored = localStorage.getItem('rep');
      return stored ? (JSON.parse(stored) as Rep) : null;
    } catch {
      return null;
    }
  });
  const [token, setToken] = useState<string | null>(() => localStorage.getItem('access_token'));
  const [isLoading, setIsLoading] = useState(true);

  // On mount — verify token is still valid
  useEffect(() => {
    if (!token) {
      setIsLoading(false);
      return;
    }
    getMe()
      .then((me) => {
        setRep(me);
        localStorage.setItem('rep', JSON.stringify(me));
      })
      .catch(() => {
        // Token invalid — clear everything
        setToken(null);
        setRep(null);
        localStorage.removeItem('access_token');
        localStorage.removeItem('rep');
      })
      .finally(() => setIsLoading(false));
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  const login = useCallback((newToken: string, newRep: Rep) => {
    localStorage.setItem('access_token', newToken);
    localStorage.setItem('rep', JSON.stringify(newRep));
    setToken(newToken);
    setRep(newRep);
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('rep');
    setToken(null);
    setRep(null);
  }, []);

  const refreshMe = useCallback(async () => {
    const me = await getMe();
    setRep(me);
    localStorage.setItem('rep', JSON.stringify(me));
  }, []);

  return (
    <AuthContext.Provider value={{ rep, token, isLoading, login, logout, refreshMe }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within <AuthProvider>');
  return ctx;
}
