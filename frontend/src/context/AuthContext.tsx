import React, { createContext, useContext, useState, useEffect } from 'react';
import { User } from '../types';
import { ApiClient } from '../api/client';

interface AuthContextType {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<User>;
  quickLogin: (role: 'ADMIN' | 'LMO' | 'TRADER') => Promise<User>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(() => {
    try {
      const stored = localStorage.getItem('legalmet_user');
      return stored ? JSON.parse(stored) : null;
    } catch {
      return null;
    }
  });
  const [token, setToken] = useState<string | null>(localStorage.getItem('legalmet_token'));
  const [isLoading, setIsLoading] = useState<boolean>(false);

  useEffect(() => {
    const initAuth = async () => {
      const storedToken = localStorage.getItem('legalmet_token');
      if (storedToken) {
        try {
          const userData = await ApiClient.getMe();
          localStorage.setItem('legalmet_user', JSON.stringify(userData));
          setUser(userData);
          setToken(storedToken);
        } catch (err) {
          ApiClient.clearToken();
          localStorage.removeItem('legalmet_user');
          setUser(null);
          setToken(null);
        }
      }
    };

    initAuth();
  }, []);

  const login = async (email: string, password: string): Promise<User> => {
    const res = await ApiClient.login({ email, password });
    ApiClient.setToken(res.access_token);
    localStorage.setItem('legalmet_user', JSON.stringify(res.user));
    setToken(res.access_token);
    setUser(res.user);
    return res.user;
  };

  const quickLogin = async (role: 'ADMIN' | 'LMO' | 'TRADER'): Promise<User> => {
    let email = 'admin@legalmet.gov.in';
    let pass = 'Admin@123';
    if (role === 'LMO') {
      email = 'lmo.sharma@legalmet.gov.in';
      pass = 'Lmo@123';
    } else if (role === 'TRADER') {
      email = 'trader.patel@agrotraders.in';
      pass = 'Trader@123';
    }
    return await login(email, pass);
  };

  const logout = () => {
    ApiClient.clearToken();
    localStorage.removeItem('legalmet_user');
    setToken(null);
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, token, isLoading, login, quickLogin, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
