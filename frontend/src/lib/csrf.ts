/**
 * CSRF Token Management
 * 
 * Handles CSRF token fetching, storage, and injection for state-changing requests.
 * The backend should provide a CSRF token via httpOnly cookie, and this module
 * fetches a reference token from the server to include in request headers.
 */

interface CSRFTokenResponse {
  csrf_token: string;
  expires_at?: string;
}

// In-memory token cache (cleared on page refresh)
let cachedToken: string | null = null;
let tokenExpiry: number | null = null;
let fetchPromise: Promise<string> | null = null;

/**
 * Get the API base URL from environment
 */
const getApiBaseUrl = (): string => {
  const baseUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
  return baseUrl.endsWith('/api/v1') ? baseUrl : `${baseUrl}/api/v1`;
};

/**
 * Check if the cached token is still valid
 */
const isTokenValid = (): boolean => {
  if (!cachedToken || !tokenExpiry) return false;
  // Consider token invalid 30 seconds before actual expiry
  return Date.now() < (tokenExpiry - 30000);
};

/**
 * Fetch a fresh CSRF token from the backend
 * 
 * The backend should:
 * 1. Generate a CSRF token
 * 2. Set it as an httpOnly cookie (for server validation)
 * 3. Return a reference token in the response (for client to send in headers)
 */
export const fetchCSRFToken = async (): Promise<string> => {
  // Return existing valid token if available
  if (isTokenValid() && cachedToken) {
    return cachedToken;
  }

  // Dedupe concurrent fetches
  if (fetchPromise) {
    return fetchPromise;
  }

  fetchPromise = (async () => {
    try {
      const response = await fetch(`${getApiBaseUrl()}/auth/csrf-token`, {
        method: 'GET',
        credentials: 'include', // Include cookies for session
        headers: {
          'Accept': 'application/json',
        },
      });

      if (!response.ok) {
        // If CSRF endpoint doesn't exist yet (backend not updated), 
        // return empty string - backend should allow this during transition
        if (response.status === 404) {
          console.warn('CSRF endpoint not found - backend may need update');
          return '';
        }
        throw new Error(`Failed to fetch CSRF token: ${response.status}`);
      }

      const data: CSRFTokenResponse = await response.json();
      
      cachedToken = data.csrf_token;
      tokenExpiry = data.expires_at 
        ? new Date(data.expires_at).getTime()
        : Date.now() + (60 * 60 * 1000); // Default 1 hour expiry

      return cachedToken;
    } catch (error) {
      console.error('Error fetching CSRF token:', error);
      // Return empty string to allow requests to proceed
      // Backend should handle missing CSRF gracefully during transition
      return '';
    } finally {
      fetchPromise = null;
    }
  })();

  return fetchPromise;
};

/**
 * Get the current CSRF token, fetching a new one if necessary
 */
export const getCSRFToken = async (): Promise<string> => {
  if (isTokenValid() && cachedToken) {
    return cachedToken;
  }
  return fetchCSRFToken();
};

/**
 * Clear the cached CSRF token (call on logout or auth error)
 */
export const clearCSRFToken = (): void => {
  cachedToken = null;
  tokenExpiry = null;
  fetchPromise = null;
};

/**
 * Refresh the CSRF token (call periodically for long-lived sessions)
 */
export const refreshCSRFToken = async (): Promise<string> => {
  clearCSRFToken();
  return fetchCSRFToken();
};

/**
 * Initialize CSRF protection on app load
 * Call this early in the application bootstrap
 */
export const initCSRF = async (): Promise<void> => {
  try {
    await fetchCSRFToken();
  } catch (error) {
    console.warn('CSRF initialization failed - will retry on first request');
  }
};

/**
 * The header name used for CSRF token in requests
 * Backend should look for this header and validate against the cookie
 */
export const CSRF_HEADER_NAME = 'X-CSRF-Token';

export default {
  fetchCSRFToken,
  getCSRFToken,
  clearCSRFToken,
  refreshCSRFToken,
  initCSRF,
  CSRF_HEADER_NAME,
};
