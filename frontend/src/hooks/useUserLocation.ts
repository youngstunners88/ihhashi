/**
 * useUserLocation — resolves the user's current coordinates via the browser
 * Geolocation API and keeps them in sync.
 *
 * SA-aware: falls back to Johannesburg (−26.2041, 28.0473) after a timeout so
 * the UI is never blocked on slow or denied geolocation.
 */

import { useState, useEffect } from 'react';

export interface UserLocation {
  lat: number;
  lng: number;
  /** true once we have a real fix (not the fallback) */
  isReal: boolean;
}

const JHB_FALLBACK: UserLocation = {
  lat: -26.2041,
  lng: 28.0473,
  isReal: false,
};

const GEO_OPTIONS: PositionOptions = {
  enableHighAccuracy: false,
  timeout: 8000,
  maximumAge: 60_000,
};

export function useUserLocation(): {
  location: UserLocation;
  loading: boolean;
  error: string | null;
} {
  const [location, setLocation] = useState<UserLocation>(JHB_FALLBACK);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!navigator.geolocation) {
      setError('Geolocation is not supported by this browser');
      setLoading(false);
      return;
    }

    // Use a timeout to fall back gracefully on slow devices/networks
    const fallbackTimer = setTimeout(() => {
      setLoading(false);
    }, 9000);

    navigator.geolocation.getCurrentPosition(
      (pos) => {
        clearTimeout(fallbackTimer);
        setLocation({
          lat: pos.coords.latitude,
          lng: pos.coords.longitude,
          isReal: true,
        });
        setLoading(false);
        setError(null);
      },
      (err) => {
        clearTimeout(fallbackTimer);
        // Permission denied or unavailable — silently use fallback
        setError(
          err.code === err.PERMISSION_DENIED
            ? 'Location access denied. Showing results near Johannesburg.'
            : 'Could not determine your location.'
        );
        setLoading(false);
      },
      GEO_OPTIONS
    );

    return () => clearTimeout(fallbackTimer);
  }, []);

  return { location, loading, error };
}
