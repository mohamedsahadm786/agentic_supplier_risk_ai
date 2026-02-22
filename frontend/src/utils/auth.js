import { jwtDecode } from 'jwt-decode';

// ── Token Storage ────────────────────────────────────────────────
export const getToken = () => localStorage.getItem('token');

export const setToken = (token) => localStorage.setItem('token', token);

export const removeToken = () => localStorage.removeItem('token');

// ── Decode JWT and return user payload ───────────────────────────
export const getUser = () => {
  const token = getToken();
  if (!token) return null;
  try {
    const decoded = jwtDecode(token);
    // Check if token is expired
    const now = Date.now() / 1000;
    if (decoded.exp && decoded.exp < now) {
      removeToken();
      return null;
    }
    return decoded; // { user_id, email, company_id, role, exp }
  } catch {
    removeToken();
    return null;
  }
};

// ── Role Helpers ─────────────────────────────────────────────────
export const getRole = () => getUser()?.role || null;

export const isLoggedIn = () => !!getUser();

export const isSuperAdmin = () => getRole() === 'super_admin';

export const isAdmin = () => getRole() === 'admin';

export const isAnalyst = () => getRole() === 'analyst';

export const isViewer = () => getRole() === 'viewer';

export const canEdit = () => ['admin', 'analyst'].includes(getRole());

export const canAdminManage = () => getRole() === 'admin';

// ── Role-based redirect path after login ─────────────────────────
export const getRedirectPath = (role) => {
  if (role === 'super_admin') return '/platform-admin';
  return '/dashboard';
};