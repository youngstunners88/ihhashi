/**
 * Firebase Cloud Messaging (FCM) setup for iHhashi
 *
 * Initialises the Firebase app using VITE_FIREBASE_* env vars and exposes a
 * helper that requests notification permission and returns the FCM device token.
 *
 * Required env vars (add to .env):
 *   VITE_FIREBASE_API_KEY
 *   VITE_FIREBASE_AUTH_DOMAIN
 *   VITE_FIREBASE_PROJECT_ID
 *   VITE_FIREBASE_MESSAGING_SENDER_ID
 *   VITE_FIREBASE_APP_ID
 *   VITE_FIREBASE_VAPID_KEY   ← Web Push certificate key from Firebase console
 *
 * Run `npm install firebase` to add the Firebase JS SDK.
 */

// Dynamic import so the app doesn't crash if the firebase package is absent
// (e.g. before `npm install` has been run after adding the dependency).
async function getFirebaseModules() {
  const { initializeApp, getApps } = await import('firebase/app');
  const { getMessaging, getToken, onMessage } = await import('firebase/messaging');
  return { initializeApp, getApps, getMessaging, getToken, onMessage };
}

const firebaseConfig = {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY,
  authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN,
  projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID,
  messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID,
  appId: import.meta.env.VITE_FIREBASE_APP_ID,
};

const VAPID_KEY = import.meta.env.VITE_FIREBASE_VAPID_KEY as string | undefined;

/**
 * Request notification permission, register the service worker, and return
 * the FCM registration token.
 *
 * Returns `null` when:
 * - Firebase env vars are not configured
 * - The user denies notification permission
 * - The browser does not support service workers / FCM
 */
export async function getFCMToken(): Promise<string | null> {
  if (!firebaseConfig.apiKey || !firebaseConfig.projectId) {
    console.warn('[FCM] Firebase env vars not configured. Skipping push setup.');
    return null;
  }

  if (!('serviceWorker' in navigator) || !('Notification' in window)) {
    console.warn('[FCM] Push notifications not supported in this browser.');
    return null;
  }

  try {
    const { initializeApp, getApps, getMessaging, getToken } =
      await getFirebaseModules();

    const app =
      getApps().length === 0 ? initializeApp(firebaseConfig) : getApps()[0];

    const permission = await Notification.requestPermission();
    if (permission !== 'granted') {
      console.info('[FCM] Notification permission denied by user.');
      return null;
    }

    // Register the FCM service worker
    const swRegistration = await navigator.serviceWorker.register(
      '/firebase-messaging-sw.js'
    );

    const messaging = getMessaging(app);
    const token = await getToken(messaging, {
      vapidKey: VAPID_KEY,
      serviceWorkerRegistration: swRegistration,
    });

    return token || null;
  } catch (err) {
    console.error('[FCM] Failed to get FCM token:', err);
    return null;
  }
}

/**
 * Subscribe to foreground push messages while the app tab is active.
 * Returns an unsubscribe function.
 */
export async function onForegroundMessage(
  handler: (payload: { title?: string; body?: string; data?: Record<string, string> }) => void
): Promise<() => void> {
  if (!firebaseConfig.apiKey) return () => {};

  try {
    const { initializeApp, getApps, getMessaging, onMessage } =
      await getFirebaseModules();

    const app =
      getApps().length === 0 ? initializeApp(firebaseConfig) : getApps()[0];
    const messaging = getMessaging(app);

    const unsubscribe = onMessage(messaging, (payload) => {
      handler({
        title: payload.notification?.title,
        body: payload.notification?.body,
        data: payload.data as Record<string, string> | undefined,
      });
    });

    return unsubscribe;
  } catch (err) {
    console.error('[FCM] onForegroundMessage setup failed:', err);
    return () => {};
  }
}
