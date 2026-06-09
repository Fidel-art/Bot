import axios from 'axios';

const normalizeApiBaseUrl = (url) => {
  if (!url) return 'http://127.0.0.1:8000';
  return url.replace('://localhost', '://127.0.0.1');
};

const API_BASE_URL = import.meta.env.DEV
  ? ''
  : normalizeApiBaseUrl(import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000');

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Handle token expiration
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // Token expired, try refresh
      const refreshToken = localStorage.getItem('refresh_token');
      if (refreshToken) {
        try {
          const response = await axios.post(`${API_BASE_URL}/api/auth/refresh`, {
            refresh_token: refreshToken,
          });
          localStorage.setItem('access_token', response.data.access_token);
          // Retry original request
          error.config.headers.Authorization = `Bearer ${response.data.access_token}`;
          return axios(error.config);
        } catch {
          // Refresh failed, logout
          localStorage.clear();
          window.location.href = '/login';
        }
      } else {
        localStorage.clear();
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  login: (email, password) => api.post('/api/auth/login', { email, password }),
  register: (data) => api.post('/api/auth/register', data),
  logout: () => api.post('/api/auth/logout'),
};

// Profile API
export const profileAPI = {
  getProfile: () => api.get('/api/profile'),
};

// Subscription API
export const subscriptionAPI = {
  getSubscription: () => api.get('/api/subscription'),
  createSubscription: (plan, paymentMethod) => 
    api.post('/api/subscription/create', { plan, payment_method: paymentMethod }),
  processPayment: (plan, paymentMethod, paymentDetails) =>
    api.post('/api/subscription/pay', { plan, payment_method: paymentMethod, payment_details: paymentDetails }),
};

// Bot Control API
export const botAPI = {
  startBot: (config = null) => api.post('/api/bot/start', config),
  stopBot: () => api.post('/api/bot/stop'),
  pauseBot: () => api.post('/api/bot/pause'),
  resumeBot: () => api.post('/api/bot/resume'),
  getStatus: () => api.get('/api/bot/status'),
  instantTrade: (payload) => api.post('/api/bot/instant-trade', payload, { timeout: 45000 }),
};

// Config API
export const configAPI = {
  getConfig: () => api.get('/api/config'),
  saveConfig: (config) => api.post('/api/config/save', config),
};

// Trades API
export const tradesAPI = {
  getHistory: (limit = 100) => api.get(`/api/trades/history?limit=${limit}`),
  getStatistics: () => api.get('/api/trades/statistics'),
};

// System API
export const systemAPI = {
  getHealth: () => api.get('/api/system/health'),
  getMT5Status: () => api.get('/api/system/mt5-status'),
  launchMT5: () => api.post('/api/system/launch-mt5'),
  openMT5Charts: (symbol = 'EURUSD', timeframe = 'H1') => 
    api.post(`/api/system/open-mt5-charts?symbol=${symbol}&timeframe=${timeframe}`),
};

export default api;
