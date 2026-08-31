import axios from 'axios';

// Falls back to the local dev API if VITE_API_URL isn't set, so a fresh
// checkout still works out of the box -- but any environment (a teammate's
// machine, staging, production) can override it via .env without touching
// source code.
const BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api';

const api = axios.create({
  baseURL: BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Separate, interceptor-free client used only for the refresh call itself --
// keeps it from ever being caught by api's own response interceptor below.
const refreshClient = axios.create({ baseURL: BASE_URL });

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

// --- Token refresh on 401 -------------------------------------------------
// Access tokens are short-lived (see SIMPLE_JWT.ACCESS_TOKEN_LIFETIME in
// devflow-api/config/settings.py). Without this, every request made after
// the token expires would fail with 401 even though a valid refresh token
// is sitting in localStorage, forcing a full logout/login to recover.
//
// isRefreshing/queue below coalesce concurrent 401s (e.g. several requests
// firing at once when the token expires) into a single refresh call instead
// of racing multiple refresh requests against each other.
let isRefreshing = false;
let queue = [];

const resolveQueue = (error, token = null) => {
  queue.forEach(({ resolve, reject }) => {
    if (error) reject(error);
    else resolve(token);
  });
  queue = [];
};

const clearSessionAndRedirect = () => {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
  if (window.location.pathname !== '/login') {
    window.location.href = '/login';
  }
};

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const { config, response } = error;

    // Not a 401, or there's no request config to retry (e.g. network error) -> bail out.
    if (!response || response.status !== 401 || !config) {
      return Promise.reject(error);
    }

    // The login/refresh endpoints themselves returning 401 means the
    // credentials/refresh token are genuinely invalid -- don't try to
    // "refresh" our way out of that.
    if (config.url?.includes('/auth/login/') || config.url?.includes('/auth/token/refresh/')) {
      return Promise.reject(error);
    }

    // Already retried once for this request -- refreshing again won't help.
    if (config._retry) {
      return Promise.reject(error);
    }

    const refreshToken = localStorage.getItem('refresh_token');
    if (!refreshToken) {
      clearSessionAndRedirect();
      return Promise.reject(error);
    }

    if (isRefreshing) {
      // A refresh is already in flight -- queue this request and retry it
      // once that refresh resolves, instead of firing a second refresh call.
      return new Promise((resolve, reject) => {
        queue.push({ resolve, reject });
      }).then((newToken) => {
        config.headers.Authorization = `Bearer ${newToken}`;
        config._retry = true;
        return api(config);
      });
    }

    config._retry = true;
    isRefreshing = true;

    try {
      const { data } = await refreshClient.post('/auth/token/refresh/', { refresh: refreshToken });
      localStorage.setItem('access_token', data.access);
      // ROTATE_REFRESH_TOKENS is on server-side, so a new refresh token
      // comes back with each refresh -- store it or the *next* refresh
      // will be rejected as reusing a rotated-out token.
      if (data.refresh) {
        localStorage.setItem('refresh_token', data.refresh);
      }

      resolveQueue(null, data.access);
      config.headers.Authorization = `Bearer ${data.access}`;
      return api(config);
    } catch (refreshError) {
      resolveQueue(refreshError, null);
      clearSessionAndRedirect();
      return Promise.reject(refreshError);
    } finally {
      isRefreshing = false;
    }
  }
);

export default api;