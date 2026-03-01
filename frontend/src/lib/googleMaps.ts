/**
 * Google Maps JavaScript API loader
 *
 * Dynamically injects the Maps script once and resolves when ready.
 * Uses VITE_GOOGLE_MAPS_API_KEY from the environment.
 *
 * Required GCP APIs to enable:
 *   - Maps JavaScript API
 *   - Places API
 *   - Geocoding API
 */

const MAPS_API_KEY = import.meta.env.VITE_GOOGLE_MAPS_API_KEY as string | undefined;

let loadPromise: Promise<typeof google.maps> | null = null;

/** Load the Google Maps JS SDK exactly once. Returns the `google.maps` namespace. */
export function loadGoogleMaps(): Promise<typeof google.maps> {
  if (!MAPS_API_KEY) {
    return Promise.reject(
      new Error('VITE_GOOGLE_MAPS_API_KEY is not set. Add it to your .env file.')
    );
  }

  if (loadPromise) return loadPromise;

  loadPromise = new Promise((resolve, reject) => {
    // Already loaded (e.g. hot-reload scenario)
    if (window.google?.maps) {
      resolve(window.google.maps);
      return;
    }

    const callbackName = '__googleMapsLoaded__';
    (window as any)[callbackName] = () => {
      resolve(window.google.maps);
      delete (window as any)[callbackName];
    };

    const script = document.createElement('script');
    script.src = `https://maps.googleapis.com/maps/api/js?key=${MAPS_API_KEY}&libraries=places&callback=${callbackName}`;
    script.async = true;
    script.defer = true;
    script.onerror = () => {
      loadPromise = null;
      reject(new Error('Failed to load Google Maps script'));
    };
    document.head.appendChild(script);
  });

  return loadPromise;
}

/** Geocode an address string to lat/lng coordinates. */
export async function geocodeAddress(
  address: string
): Promise<{ lat: number; lng: number; formattedAddress: string } | null> {
  const maps = await loadGoogleMaps();
  const geocoder = new maps.Geocoder();

  return new Promise((resolve) => {
    geocoder.geocode({ address, region: 'ZA' }, (results, status) => {
      if (status === 'OK' && results && results[0]) {
        const loc = results[0].geometry.location;
        resolve({
          lat: loc.lat(),
          lng: loc.lng(),
          formattedAddress: results[0].formatted_address,
        });
      } else {
        resolve(null);
      }
    });
  });
}

/**
 * Attach a Google Places Autocomplete widget to an <input> element.
 * Calls `onPlace` when the user selects a suggestion.
 *
 * @returns cleanup function to remove the listener
 */
export async function attachPlacesAutocomplete(
  input: HTMLInputElement,
  onPlace: (result: { lat: number; lng: number; address: string }) => void
): Promise<() => void> {
  const maps = await loadGoogleMaps();

  const autocomplete = new maps.places.Autocomplete(input, {
    componentRestrictions: { country: 'za' },
    fields: ['geometry', 'formatted_address'],
    types: ['address'],
  });

  const listener = autocomplete.addListener('place_changed', () => {
    const place = autocomplete.getPlace();
    if (place.geometry?.location) {
      onPlace({
        lat: place.geometry.location.lat(),
        lng: place.geometry.location.lng(),
        address: place.formatted_address ?? input.value,
      });
    }
  });

  return () => {
    maps.event.removeListener(listener);
  };
}
