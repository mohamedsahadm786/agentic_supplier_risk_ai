import { useState, useEffect } from 'react';
import { getUser, getToken, setToken, removeToken } from '../utils/auth';
import { authAPI } from '../services/api';

export function useAuth() {
  const [user,    setUser]    = useState(getUser());
  const [loading, setLoading] = useState(false);
  const [error,   setError]   = useState(null);

  // Re-read user from token whenever token changes
  useEffect(() => {
    setUser(getUser());
  }, []);

  // ── Login ──────────────────────────────────────────────────────
  const login = async (email, password) => {
    setLoading(true);
    setError(null);
    try {
      const response = await authAPI.login({ email, password });
      const { access_token } = response.data;
      setToken(access_token);
      const decoded = getUser();
      setUser(decoded);
      return decoded; // caller uses role to redirect
    } catch (err) {
      const msg = err.response?.data?.detail || 'Login failed. Please try again.';
      setError(msg);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  // ── Signup ─────────────────────────────────────────────────────
  const signup = async (formData) => {
    setLoading(true);
    setError(null);
    try {
      const response = await authAPI.signup(formData);
      const { access_token } = response.data;
      setToken(access_token);
      const decoded = getUser();
      setUser(decoded);
      return decoded;
    } catch (err) {
      const msg = err.response?.data?.detail || 'Signup failed. Please try again.';
      setError(msg);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  // ── Logout ─────────────────────────────────────────────────────
  const logout = async () => {
    try {
      await authAPI.logout();
    } catch {
      // Even if logout API fails, clear local token
    } finally {
      removeToken();
      setUser(null);
      window.location.href = '/';
    }
  };

  return { user, loading, error, login, signup, logout };
}