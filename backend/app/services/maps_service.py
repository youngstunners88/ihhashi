"""Google Maps service for geocoding and routing."""
import logging
from typing import List, Dict, Any, Optional
import httpx

from app.config import settings

logger = logging.getLogger(__name__)

GOOGLE_MAPS_API_BASE = "https://maps.googleapis.com/maps/api"


class MapsService:
    """Google Maps API service."""
    
    def __init__(self):
        self.api_key = settings.GOOGLE_MAPS_API_KEY if hasattr(settings, 'GOOGLE_MAPS_API_KEY') else None
        self.client = httpx.AsyncClient(base_url=GOOGLE_MAPS_API_BASE, timeout=30.0)
    
    async def geocode_address(self, address: str) -> Optional[Dict[str, Any]]:
        """
        Geocode an address to coordinates.
        
        Args:
            address: Address string
            
        Returns:
            Location data with lat/lng
        """
        if not self.api_key:
            logger.warning("Google Maps API key not configured")
            return None
        
        try:
            response = await self.client.get(
                "/geocode/json",
                params={
                    "address": address,
                    "key": self.api_key
                }
            )
            response.raise_for_status()
            data = response.json()
            
            if data["status"] != "OK" or not data["results"]:
                logger.warning(f"Geocoding failed: {data['status']}")
                return None
            
            result = data["results"][0]
            location = result["geometry"]["location"]
            
            return {
                "latitude": location["lat"],
                "longitude": location["lng"],
                "formatted_address": result["formatted_address"],
                "place_id": result["place_id"]
            }
            
        except Exception as e:
            logger.error(f"Geocoding error: {e}")
            return None
    
    async def reverse_geocode(self, latitude: float, longitude: float) -> Optional[Dict[str, Any]]:
        """
        Reverse geocode coordinates to address.
        
        Args:
            latitude: Latitude
            longitude: Longitude
            
        Returns:
            Address data
        """
        if not self.api_key:
            logger.warning("Google Maps API key not configured")
            return None
        
        try:
            response = await self.client.get(
                "/geocode/json",
                params={
                    "latlng": f"{latitude},{longitude}",
                    "key": self.api_key
                }
            )
            response.raise_for_status()
            data = response.json()
            
            if data["status"] != "OK" or not data["results"]:
                return None
            
            result = data["results"][0]
            
            return {
                "formatted_address": result["formatted_address"],
                "place_id": result["place_id"]
            }
            
        except Exception as e:
            logger.error(f"Reverse geocoding error: {e}")
            return None
    
    async def calculate_distance(
        self,
        origin: Dict[str, float],
        destination: Dict[str, float],
        mode: str = "driving"
    ) -> Optional[Dict[str, Any]]:
        """
        Calculate distance and duration between two points.
        
        Args:
            origin: Origin coordinates {lat, lng}
            destination: Destination coordinates {lat, lng}
            mode: Travel mode (driving, walking, bicycling)
            
        Returns:
            Distance and duration data
        """
        if not self.api_key:
            logger.warning("Google Maps API key not configured")
            return None
        
        try:
            response = await self.client.get(
                "/distancematrix/json",
                params={
                    "origins": f"{origin['lat']},{origin['lng']}",
                    "destinations": f"{destination['lat']},{destination['lng']}",
                    "mode": mode,
                    "key": self.api_key
                }
            )
            response.raise_for_status()
            data = response.json()
            
            if data["status"] != "OK":
                logger.warning(f"Distance calculation failed: {data['status']}")
                return None
            
            element = data["rows"][0]["elements"][0]
            
            if element["status"] != "OK":
                return None
            
            return {
                "distance_meters": element["distance"]["value"],
                "duration_seconds": element["duration"]["value"],
                "distance_text": element["distance"]["text"],
                "duration_text": element["duration"]["text"]
            }
            
        except Exception as e:
            logger.error(f"Distance calculation error: {e}")
            return None
    
    async def get_directions(
        self,
        origin: Dict[str, float],
        destination: Dict[str, float],
        mode: str = "driving"
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Get turn-by-turn directions.
        
        Args:
            origin: Origin coordinates
            destination: Destination coordinates
            mode: Travel mode
            
        Returns:
            List of route steps
        """
        if not self.api_key:
            logger.warning("Google Maps API key not configured")
            return None
        
        try:
            response = await self.client.get(
                "/directions/json",
                params={
                    "origin": f"{origin['lat']},{origin['lng']}",
                    "destination": f"{destination['lat']},{destination['lng']}",
                    "mode": mode,
                    "key": self.api_key
                }
            )
            response.raise_for_status()
            data = response.json()
            
            if data["status"] != "OK" or not data["routes"]:
                return None
            
            route = data["routes"][0]
            legs = route["legs"][0]
            
            steps = []
            for step in legs["steps"]:
                steps.append({
                    "instruction": step["html_instructions"],
                    "distance": step["distance"]["text"],
                    "duration": step["duration"]["text"],
                    "start_location": step["start_location"],
                    "end_location": step["end_location"]
                })
            
            return steps
            
        except Exception as e:
            logger.error(f"Directions error: {e}")
            return None
    
    async def calculate_delivery_fee(
        self,
        origin: Dict[str, float],
        destination: Dict[str, float],
        base_fee: float = 2.0,
        per_km_rate: float = 1.5
    ) -> float:
        """
        Calculate delivery fee based on distance.
        
        Args:
            origin: Restaurant location
            destination: Customer location
            base_fee: Base delivery fee
            per_km_rate: Rate per kilometer
            
        Returns:
            Calculated delivery fee
        """
        distance_data = await self.calculate_distance(origin, destination)
        
        if not distance_data:
            return base_fee  # Return base fee if calculation fails
        
        distance_km = distance_data["distance_meters"] / 1000
        fee = base_fee + (distance_km * per_km_rate)
        
        return round(fee, 2)


# Alternative: Use OpenStreetMap (free, no API key required)
class OpenStreetMapService:
    """OpenStreetMap Nominatim service (free alternative)."""
    
    def __init__(self):
        self.client = httpx.AsyncClient(
            base_url="https://nominatim.openstreetmap.org",
            timeout=30.0,
            headers={"User-Agent": "DeliveryApp/1.0"}
        )
    
    async def geocode_address(self, address: str) -> Optional[Dict[str, Any]]:
        """Geocode using OpenStreetMap."""
        try:
            response = await self.client.get(
                "/search",
                params={
                    "q": address,
                    "format": "json",
                    "limit": 1
                }
            )
            response.raise_for_status()
            data = response.json()
            
            if not data:
                return None
            
            result = data[0]
            
            return {
                "latitude": float(result["lat"]),
                "longitude": float(result["lon"]),
                "formatted_address": result["display_name"],
                "place_id": result.get("osm_id")
            }
            
        except Exception as e:
            logger.error(f"OpenStreetMap geocoding error: {e}")
            return None
    
    async def reverse_geocode(self, latitude: float, longitude: float) -> Optional[Dict[str, Any]]:
        """Reverse geocode using OpenStreetMap."""
        try:
            response = await self.client.get(
                "/reverse",
                params={
                    "lat": latitude,
                    "lon": longitude,
                    "format": "json"
                }
            )
            response.raise_for_status()
            data = response.json()
            
            return {
                "formatted_address": data.get("display_name", ""),
                "place_id": data.get("osm_id")
            }
            
        except Exception as e:
            logger.error(f"OpenStreetMap reverse geocoding error: {e}")
            return None
