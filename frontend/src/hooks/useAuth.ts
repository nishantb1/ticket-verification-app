import { useState, useEffect } from 'react';
import apiService from '../services/api';

// Custom event for auth state changes
const AUTH_EVENT = 'authStateChanged';

export const useAuth = () => {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  const checkAuthStatus = async () => {
    try {
      const response = await apiService.validateSession();
      setIsAuthenticated(response.authenticated);
    } catch (error) {
      console.error('Error validating session:', error);
      setIsAuthenticated(false);
    }
  };

  useEffect(() => {
    // Clear any old localStorage auth data
    localStorage.removeItem('authToken');
    
    checkAuthStatus().finally(() => {
      setIsLoading(false);
    });

    // Listen for custom auth events (same tab)
    const handleAuthChange = () => {
      checkAuthStatus();
    };

    window.addEventListener(AUTH_EVENT, handleAuthChange);
    
    return () => {
      window.removeEventListener(AUTH_EVENT, handleAuthChange);
    };
  }, []);

  const login = async (username: string, password: string) => {
    try {
      const response = await apiService.login({ username, password });
      if (response.success) {
        setIsAuthenticated(true);
        // Dispatch custom event
        window.dispatchEvent(new Event(AUTH_EVENT));
        return { success: true };
      } else {
        return { success: false, message: response.message };
      }
    } catch (error) {
      return { success: false, message: 'Login failed' };
    }
  };

  const logout = async () => {
    try {
      await apiService.logout();
    } catch (error) {
      // Ignore logout errors
    } finally {
      setIsAuthenticated(false);
      // Dispatch custom event
      window.dispatchEvent(new Event(AUTH_EVENT));
    }
  };

  return {
    isAuthenticated,
    isLoading,
    login,
    logout,
  };
}; 