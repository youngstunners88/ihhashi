import axios, { AxiosInstance, AxiosError, InternalAxiosRequestConfig } from 'axios';
import { getCSRFToken, clearCSRFToken, CSRF_HEADER_NAME, initCSRF } from './csrf';

// Methods that require CSRF protection (state-changing operations)
const CSRF_PROTECTED_METHODS = ['post', 'put', 'patch', 'delete'];

/**
 * Get the API base URL from environment variable
 * Single source of truth - VITE_API_URL
 */
const getBaseURL = (): string => {
  const baseUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
  // Ensure consistent URL format
  return baseUrl.endsWith('/api/v1') ? baseUrl : `${baseUrl}/api/v1`;
};

/**
 * Create axios instance with default configuration
 */
const api: AxiosInstance = axios.create({
  baseURL: getBaseURL(),
  headers: {
    'Content-Type': 'application/json',
    'Accept-Language': localStorage.getItem('language') || 'en',
  },
  timeout: 15000, // 15s timeout for spotty SA networks
  withCredentials: true, // Essential for cookie-based auth
});

/**
 * Request interceptor
 * - Adds CSRF token for state-changing requests
 * - Handles data-saver mode
 * - No localStorage token management (cookies only)
 */
api.interceptors.request.use(
  async (config: InternalAxiosRequestConfig) => {
    // Add CSRF token for state-changing methods
    if (config.method && CSRF_PROTECTED_METHODS.includes(config.method.toLowerCase())) {
      try {
        const csrfToken = await getCSRFToken();
        if (csrfToken) {
          config.headers[CSRF_HEADER_NAME] = csrfToken;
        }
      } catch (error) {
        console.warn('Failed to get CSRF token, proceeding without it');
      }
    }

    // Data-light mode: request compressed responses
    if (localStorage.getItem('data_saver') === 'true') {
      config.headers['Accept-Encoding'] = 'gzip, deflate';
    }

    // Language preference
    const language = localStorage.getItem('language');
    if (language) {
      config.headers['Accept-Language'] = language;
    }

    return config;
  },
  (error) => Promise.reject(error)
);

/**
 * Response interceptor
 * - Handles authentication errors (clear CSRF, redirect to login)
 * - Handles offline mode gracefully
 * - Provides user-friendly error messages
 */
api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    // Handle 401 - unauthorized/session expired
    if (error.response?.status === 401) {
      // Clear CSRF token on auth failure
      clearCSRFToken();
      
      // Only redirect if not already on auth pages
      const currentPath = window.location.pathname;
      if (!currentPath.startsWith('/login') && !currentPath.startsWith('/register')) {
        const returnUrl = encodeURIComponent(window.location.pathname + window.location.search);
        window.location.href = `/login?session_expired=1&return=${returnUrl}`;
      }
      return Promise.reject(error);
    }

    // Handle 403 - CSRF validation failed
    if (error.response?.status === 403) {
      const errorData = error.response?.data as any;
      if (errorData?.detail?.toLowerCase().includes('csrf')) {
        // Clear invalid CSRF token and retry once
        clearCSRFToken();
        // The user can retry their action
        return Promise.reject(new Error('Security token expired. Please try again.'));
      }
    }

    // Handle offline mode for South African connectivity issues
    if (!navigator.onLine) {
      return Promise.reject({
        code: 'OFFLINE',
        message: 'You appear to be offline. Orders will sync when connection is restored.',
      });
    }

    // Handle network errors (server unreachable)
    if (error.code === 'ERR_NETWORK' || error.code === 'ECONNABORTED') {
      return Promise.reject({
        code: 'NETWORK_ERROR',
        message: 'Unable to connect to server. Please check your connection.',
      });
    }

    // Generic error handling with user-friendly message
    const message = 
      (error.response?.data as any)?.detail || 
      (error.response?.data as any)?.message ||
      'Something went wrong. Please try again.';
    
    return Promise.reject(new Error(message));
  }
);

// ============================================================================
// Auth API - Cookie-based authentication
// ============================================================================
export const authAPI = {
  /**
   * Login with email/password
   * Backend sets httpOnly cookie with session/token
   */
  login: (data: { email: string; password: string }) =>
    api.post('/auth/login', data),

  /**
   * Register new user
   * Backend sets httpOnly cookie with session/token
   */
  register: (data: { 
    email: string; 
    password: string; 
    name?: string;
    phone?: string;
    role?: string;
  }) =>
    api.post('/auth/register', data),

  /**
   * Refresh session
   * Backend refreshes httpOnly cookie
   */
  refreshToken: () =>
    api.post('/auth/refresh'),

  /**
   * Logout - clears server session
   * Backend clears httpOnly cookie
   */
  logout: async () => {
    try {
      await api.post('/auth/logout');
    } finally {
      // Always clear local state
      clearCSRFToken();
    }
  },

  /**
   * Get current user profile
   * Requires valid session cookie
   */
  me: () =>
    api.get('/auth/me'),

  /**
   * Request password reset
   */
  requestPasswordReset: (email: string) =>
    api.post('/auth/password-reset/request', { email }),

  /**
   * Confirm password reset with token
   */
  confirmPasswordReset: (token: string, newPassword: string) =>
    api.post('/auth/password-reset/confirm', { token, new_password: newPassword }),

  /**
   * Change password (authenticated)
   */
  changePassword: (currentPassword: string, newPassword: string) =>
    api.post('/auth/password/change', { 
      current_password: currentPassword, 
      new_password: newPassword 
    }),
};

// ============================================================================
// Orders API
// ============================================================================
export const ordersAPI = {
  create: (data: any) => api.post('/orders', data),
  list: (params?: { status?: string; limit?: number; offset?: number }) =>
    api.get('/orders', { params }),
  get: (id: string) => api.get(`/orders/${id}`),
  update: (id: string, data: any) => api.patch(`/orders/${id}`, data),
  cancel: (id: string) => api.post(`/orders/${id}/cancel`),
  rate: (id: string, rating: number, comment?: string) =>
    api.post(`/orders/${id}/rate`, { rating, comment }),
};

// ============================================================================
// Merchants API
// ============================================================================
export const merchantsAPI = {
  list: (params?: { 
    category?: string; 
    lat?: number; 
    lng?: number;
    radius?: number;
    search?: string;
  }) =>
    api.get('/merchants', { params }),
  get: (id: string) => api.get(`/merchants/${id}`),
  products: (id: string, params?: { category?: string }) =>
    api.get(`/merchants/${id}/products`, { params }),
  categories: () => api.get('/merchants/categories'),
  nearby: (lat: number, lng: number, radius?: number) =>
    api.get('/merchants/nearby', { params: { lat, lng, radius } }),
};

// ============================================================================
// Products API
// ============================================================================
export const productsAPI = {
  get: (id: string) => api.get(`/products/${id}`),
  search: (query: string, params?: { merchant_id?: string }) =>
    api.get('/products/search', { params: { q: query, ...params } }),
  categories: (merchantId?: string) =>
    api.get('/products/categories', { params: { merchant_id: merchantId } }),
};

// ============================================================================
// Trips/Delivery API
// ============================================================================
export const tripsAPI = {
  active: () => api.get('/trips/active'),
  history: (params?: { limit?: number; offset?: number }) =>
    api.get('/trips/history', { params }),
  updateLocation: (lat: number, lng: number) =>
    api.post('/trips/location', { lat, lng }),
  accept: (orderId: string) => api.post(`/trips/accept/${orderId}`),
  complete: (tripId: string) => api.post(`/trips/${tripId}/complete`),
};

// ============================================================================
// Payments API
// ============================================================================
export const paymentsAPI = {
  initialize: (data: { amount: number; order_id: string }) =>
    api.post('/payments/initialize', data),
  verify: (reference: string) => api.get(`/payments/verify/${reference}`),
  banks: () => api.get('/payments/banks'),
  methods: () => api.get('/payments/methods'),
};

// ============================================================================
// User API
// ============================================================================
export const usersAPI = {
  profile: () => api.get('/users/me'),
  updateProfile: (data: any) => api.patch('/users/me', data),
  updateLocation: (lat: number, lng: number, address?: string) =>
    api.patch('/users/location', { lat, lng, address }),
  updateLanguage: (language: string) =>
    api.patch('/users/language', { language }),
  deleteAccount: () => api.delete('/users/me'),
};

// ============================================================================
// Address API
// ============================================================================
export const addressesAPI = {
  list: () => api.get('/addresses'),
  get: (id: string) => api.get(`/addresses/${id}`),
  create: (data: { 
    label: string; 
    address: string; 
    lat: number; 
    lng: number;
    instructions?: string;
  }) => api.post('/addresses', data),
  update: (id: string, data: any) => api.patch(`/addresses/${id}`, data),
  delete: (id: string) => api.delete(`/addresses/${id}`),
  setDefault: (id: string) => api.post(`/addresses/${id}/default`),
};

// ============================================================================
// Vendor/Merchant Dashboard API
// ============================================================================
export const vendorAPI = {
  dashboard: () => api.get('/vendors/dashboard'),
  orders: (params?: { status?: string }) =>
    api.get('/vendors/orders', { params }),
  products: () => api.get('/vendors/products'),
  createProduct: (data: any) => api.post('/vendors/products', data),
  updateProduct: (id: string, data: any) =>
    api.patch(`/vendors/products/${id}`, data),
  deleteProduct: (id: string) => api.delete(`/vendors/products/${id}`),
  updateStatus: (isOpen: boolean) =>
    api.patch('/vendors/status', { is_open: isOpen }),
  analytics: (period?: string) =>
    api.get('/vendors/analytics', { params: { period } }),
};

// ============================================================================
// Delivery Serviceman/Rider API
// ============================================================================
export const riderAPI = {
  profile: () => api.get('/riders/me'),
  updateProfile: (data: any) => api.patch('/riders/me', data),
  status: (status: 'online' | 'offline' | 'busy') =>
    api.patch('/riders/status', { status }),
  earnings: (period?: string) =>
    api.get('/riders/earnings', { params: { period } }),
  availableOrders: (lat: number, lng: number) =>
    api.get('/riders/orders/available', { params: { lat, lng } }),
  acceptOrder: (orderId: string) => api.post(`/riders/orders/${orderId}/accept`),
  updateOrderStatus: (orderId: string, status: string) =>
    api.patch(`/riders/orders/${orderId}/status`, { status }),
};

// ============================================================================
// Initialize CSRF on module load
// This ensures CSRF token is ready before any API calls
// ============================================================================
let csrfInitialized = false;

export const initializeApi = async (): Promise<void> => {
  if (!csrfInitialized) {
    await initCSRF();
    csrfInitialized = true;
  }
};

// Auto-initialize when this module is imported (non-blocking)
initializeApi().catch(() => {
  // Silently fail - will retry on first API call
});

export default api;