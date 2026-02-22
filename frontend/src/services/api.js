import axios from 'axios';

// ── Base Axios Instance ──────────────────────────────────────────
const API = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
});

// ── Request Interceptor — attach JWT token to every request ──────
API.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// ── Response Interceptor — auto-logout on 401 ────────────────────
API.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/';
    }
    return Promise.reject(error);
  }
);

// ════════════════════════════════════════════════════════════════
// AUTH ENDPOINTS
// ════════════════════════════════════════════════════════════════

export const authAPI = {
  signup: (data) =>
    API.post('/auth/signup', data),

  login: (data) =>
    API.post('/auth/login', data),

  me: () =>
    API.get('/auth/me'),

  logout: () =>
    API.post('/auth/logout'),
};

// ════════════════════════════════════════════════════════════════
// SUPPLIERS ENDPOINTS
// ════════════════════════════════════════════════════════════════

export const suppliersAPI = {
  getAll: () =>
    API.get('/api/suppliers/'),

  getOne: (supplierId) =>
    API.get(`/api/suppliers/${supplierId}`),

  create: (data) =>
    API.post('/api/suppliers/', data),

  update: (supplierId, data) =>
    API.put(`/api/suppliers/${supplierId}`, data),

  delete: (supplierId) =>
    API.delete(`/api/suppliers/${supplierId}`),
};

// ════════════════════════════════════════════════════════════════
// EVALUATIONS ENDPOINTS
// ════════════════════════════════════════════════════════════════

export const evaluationsAPI = {
  getAll: (params) =>
    API.get('/api/evaluations/', { params }),

  getOne: (evaluationId) =>
    API.get(`/api/evaluations/${evaluationId}`),

  create: (data) =>
    API.post('/api/evaluations/', data),
};

// ════════════════════════════════════════════════════════════════
// DOCUMENTS ENDPOINTS
// ════════════════════════════════════════════════════════════════

export const documentsAPI = {
  getBySupplier: (supplierId) =>
    API.get(`/api/documents/`, { params: { supplier_id: supplierId } }),

  upload: (formData) =>
    API.post('/api/documents/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),
};

// ════════════════════════════════════════════════════════════════
// USERS ENDPOINTS (Admin only)
// ════════════════════════════════════════════════════════════════

export const usersAPI = {
  create: (data) =>
    API.post('/api/users/', data),

  getAll: () =>
    API.get('/api/users/'),
};

// ════════════════════════════════════════════════════════════════
// ADMIN ENDPOINTS (Super Admin only)
// ════════════════════════════════════════════════════════════════

export const adminAPI = {
  getUsageSummary: () =>
    API.get('/api/admin/usage-summary'),

  getCompanyUsage: () =>
    API.get('/api/admin/company-usage'),

  getMonthlyCost: () =>
    API.get('/api/admin/monthly-cost'),

  getTopExpensive: () =>
    API.get('/api/admin/top-expensive-evaluations'),

  getCompanies: () =>
    API.get('/api/admin/companies'),

  deactivateCompany: (companyId) =>
    API.patch(`/api/admin/companies/${companyId}/deactivate`),

  reactivateCompany: (companyId) =>
    API.patch(`/api/admin/companies/${companyId}/reactivate`),

  deleteCompany: (companyId) =>
    API.delete(`/api/admin/companies/${companyId}/permanent-delete`, {
      params: { confirm: 'DELETE_COMPANY_PERMANENTLY' },
    }),
};

export default API;