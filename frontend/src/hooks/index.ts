/**
 * Custom Hooks
 * Reusable React hooks for the iHhashi app
 */

// Existing hooks
export { useCart } from './useCart';
export { useLoadShedding } from './useLoadShedding';
export { useDataSaver } from './useDataSaver';
export { usePostHog } from './usePostHog';

// WebSocket hooks
export {
  useWebSocket,
  useOrderTracking,
  useRiderTracking,
  useMerchantNotifications,
  useUserNotifications,
} from './useWebSocket';

export type {
  UseWebSocketOptions,
  UseWebSocketReturn,
  UseOrderTrackingOptions,
  UseOrderTrackingReturn,
  UseRiderTrackingOptions,
  UseRiderTrackingReturn,
  UseMerchantNotificationsOptions,
  UseMerchantNotificationsReturn,
  UseUserNotificationsOptions,
  UseUserNotificationsReturn,
} from './useWebSocket';
