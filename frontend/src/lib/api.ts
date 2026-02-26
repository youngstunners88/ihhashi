import axios, { AxiosInstance, AxiosError } from 'axios';

// Environment-aware base URL
const getBaseURL = () => {
  if (import.meta.env.DEV) return 'http://localhost:8000/api/v1';
  if (import.meta.env.VITE_APP_ENV === 'staging') return 'https://staging-api.ihhashi.co.za/api/v1';
  return 'https://api.ihhashi.co.za/api/v1';
};

const api: AxiosInstance = axios.create({
  baseURL: getBaseURL(),
  headers: {
    'Content-Type': 'application/json',
    'Accept-Language': localStorage.getItem('language') || 'en',
  },
  timeout: 15000, // 15s timeout for spotty SA networks
});

// Request interceptor: Add auth token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  // Data-light mode: request compressed responses
  if (localStorage.getItem('data_saver') === 'true') {
    config.headers['Accept-Encoding'] = 'gzip, deflate';
  }
  return config;
});

// Response interceptor: Handle errors gracefully
api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    // Handle 401 - token expired
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token');
      window.location.href = '/login?expired=1';
      return Promise.reject(error);
    }
    
    // Handle offline mode for South African connectivity issues
    if (!navigator.onLine) {
      return Promise.reject({ 
        code: 'OFFLINE', 
        message: 'You appear to be offline. Orders will sync when connection is restored.' 
      });
    }
    
    // Generic error handling
    const message = (error.response?.data as any)?.detail || 'Something went wrong. Please try again.';
    return Promise.reject(new Error(message));
  }
);

// Auth API
export const authAPI = {
  login: (data: { email: string; password: string }) => 
    api.post('/auth/login', data),
  register: (data: any) => 
    api.post('/auth/register', data),
  refreshToken: () => 
    api.post('/auth/refresh'),
  logout: () => 
    api.post('/auth/logout'),
  me: () => 
    api.get('/auth/me'),
};

// Orders API
export const ordersAPI = {
  create: (data: any) => api.post('/orders', data),
  list: (params?: { status?: string; limit?: number }) => 
    api.get('/orders', { params }),
  get: (id: string) => api.get(`/orders/${id}`),
  update: (id: string, data: any) => api.patch(`/orders/${id}`, data),
  cancel: (id: string) => api.post(`/orders/${id}/cancel`),
};

// Merchants API
export const merchantsAPI = {
  list: (params?: { category?: string; lat?: number; lng?: number }) => 
    api.get('/merchants', { params }),
  get: (id: string) => api.get(`/merchants/${id}`),
  products: (id: string) => api.get(`/merchants/${id}/products`),
};

// Products API
export const productsAPI = {
  get: (id: string) => api.get(`/products/${id}`),
  search: (query: string) => api.get('/products/search', { params: { q: query } }),
};

// Trips/Delivery API
export const tripsAPI = {
  active: () => api.get('/trips/active'),
  history: (params?: { limit?: number }) => api.get('/trips/history', { params }),
  updateLocation: (lat: number, lng: number) => 
    api.post('/trips/location', { lat, lng }),
};

// Payments API
export const paymentsAPI = {
  initialize: (data: { amount: number; order_id: string }) => 
    api.post('/payments/initialize', data),
  verify: (reference: string) => api.get(`/payments/verify/${reference}`),
  banks: () => api.get('/payments/banks'),
};

// User API
export const usersAPI = {
  profile: () => api.get('/users/me'),
  updateProfile: (data: any) => api.patch('/users/me', data),
  updateLocation: (lat: number, lng: number, address?: string) => 
    api.patch('/users/location', { lat, lng, address }),
};

export default api;
