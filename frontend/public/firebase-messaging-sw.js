/**
 * Firebase Cloud Messaging Service Worker — iHhashi
 *
 * Handles background push notifications when the app tab is not focused.
 * Must live at /firebase-messaging-sw.js (root of the public directory).
 *
 * NOTE: The Firebase SDK version here should match the version installed
 * via `npm install firebase`.
 */

importScripts('https://www.gstatic.com/firebasejs/10.12.0/firebase-app-compat.js');
importScripts('https://www.gstatic.com/firebasejs/10.12.0/firebase-messaging-compat.js');

// These values are baked in at runtime by the main app via postMessage,
// or you can hard-code them here if you don't mind them being public
// (they are safe to expose — see Firebase docs).
// Alternatively, use a build-time replacement.
self.__WB_FIREBASE_CONFIG = self.__WB_FIREBASE_CONFIG || {};

firebase.initializeApp(self.__WB_FIREBASE_CONFIG);

const messaging = firebase.messaging();

// Handle background messages
messaging.onBackgroundMessage((payload) => {
  const { title = 'iHhashi', body = '' } = payload.notification || {};
  const data = payload.data || {};

  self.registration.showNotification(title, {
    body,
    icon: '/icons/icon-192.png',
    badge: '/icons/badge-72.png',
    data,
    // Vibrate pattern for Android
    vibrate: [200, 100, 200],
    actions: [
      { action: 'view', title: 'View' },
      { action: 'dismiss', title: 'Dismiss' },
    ],
  });
});

// Notification click handler
self.addEventListener('notificationclick', (event) => {
  event.notification.close();

  if (event.action === 'dismiss') return;

  const data = event.notification.data || {};
  let url = '/';

  if (data.order_id) url = `/orders/${data.order_id}`;
  else if (data.delivery_id) url = `/orders?delivery=${data.delivery_id}`;

  event.waitUntil(
    clients
      .matchAll({ type: 'window', includeUncontrolled: true })
      .then((clientList) => {
        for (const client of clientList) {
          if (client.url.includes(self.location.origin) && 'focus' in client) {
            client.navigate(url);
            return client.focus();
          }
        }
        if (clients.openWindow) return clients.openWindow(url);
      })
  );
});
