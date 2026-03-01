/**
 * useNotifications — registers this device for FCM push notifications and
 * keeps the backend token in sync.
 *
 * Call once near the top of the app after the user authenticates.
 *
 * Behaviour:
 * - Skipped when VITE_ENABLE_NOTIFICATIONS !== "true"
 * - Requests permission, gets an FCM token, POSTs it to /api/v1/users/fcm-token
 * - Re-registers on token refresh (browser may rotate tokens)
 * - Handles foreground messages (shows a minimal in-app toast)
 */

import { useEffect } from 'react';
import { getFCMToken, onForegroundMessage } from '../lib/firebase';
import api from '../lib/api';

const NOTIFICATIONS_ENABLED =
  import.meta.env.VITE_ENABLE_NOTIFICATIONS === 'true';

const FCM_TOKEN_KEY = 'fcm_token';

async function registerToken(): Promise<void> {
  const token = await getFCMToken();
  if (!token) return;

  // Avoid re-uploading the same token on every mount
  const cached = localStorage.getItem(FCM_TOKEN_KEY);
  if (cached === token) return;

  try {
    await api.post('/users/fcm-token', { token });
    localStorage.setItem(FCM_TOKEN_KEY, token);
  } catch (err) {
    console.warn('[Notifications] Failed to register FCM token with backend:', err);
  }
}

function showForegroundToast(title?: string, body?: string): void {
  // Minimal in-app notification — replace with your toast library if available
  if (!title && !body) return;
  const msg = [title, body].filter(Boolean).join(' — ');
  console.info('[Notification]', msg);
  // If you have a toast system, call it here:
  // toast.info(msg);
}

export function useNotifications(isAuthenticated: boolean): void {
  useEffect(() => {
    if (!isAuthenticated || !NOTIFICATIONS_ENABLED) return;

    // Register FCM token
    registerToken();

    // Handle messages when the app is in the foreground
    let unsubscribe: (() => void) | null = null;
    onForegroundMessage(({ title, body, data }) => {
      showForegroundToast(title, body);
      // Emit a custom DOM event so any component can react to push messages
      window.dispatchEvent(
        new CustomEvent('ihhashi:push', { detail: { title, body, data } })
      );
    }).then((fn) => {
      unsubscribe = fn;
    });

    return () => {
      unsubscribe?.();
    };
  }, [isAuthenticated]);
}
