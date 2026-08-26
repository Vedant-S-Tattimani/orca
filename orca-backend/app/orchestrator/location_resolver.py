"""
Location resolver for ORCA orchestrator
Converts textual location descriptions to geographic coordinates
"""
from typing import Optional, Tuple
import logging
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError

logger = logging.getLogger(__name__)

class LocationResolver:
    """
    Resolves location names to latitude/longitude coordinates
    Uses Nominatim (OpenStreetMap) as the geocoding service
    For production, consider using a more robust service with API keys
    """

    def __init__(self, user_agent: str = "orca-backend/1.0"):
        self.geocoder = Nominatim(user_agent=user_agent)

    def resolve_location(self, location_name: str) -> Optional[Tuple[float, float]]:
        """
        Resolve a location name to latitude and longitude

        Args:
            location_name: Human-readable location name (e.g., "Kollam coast")

        Returns:
            Tuple of (latitude, longitude) or None if not found
        """
        try:
            logger.info(f"Resolving location: {location_name}")
            location = self.geocoder.geocode(location_name, timeout=10)
            if location:
                logger.info(f"Resolved {location_name} to ({location.latitude}, {location.longitude})")
                return (location.latitude, location.longitude)
            else:
                logger.warning(f"Could not resolve location: {location_name}")
                return None
        except (GeocoderTimedOut, GeocoderServiceError) as e:
            logger.error(f"Geocoding service error for {location_name}: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error resolving {location_name}: {str(e)}")
            return None

    def resolve_with_radius(self, location_name: str, radius_km: float = 10.0) -> dict:
        """
        Resolve location and return with search radius

        Args:
            location_name: Human-readable location name
            radius_km: Search radius in kilometers (default 10km)

        Returns:
            Dictionary with latitude, longitude, and radius_km
            Returns None values if resolution fails
        """
        coords = self.resolve_location(location_name)
        if coords:
            lat, lon = coords
            return {
                "latitude": lat,
                "longitude": lon,
                "radius_km": radius_km,
                "resolved_name": location_name
            }
        else:
            return {
                "latitude": None,
                "longitude": None,
                "radius_km": radius_km,
                "resolved_name": None
            }


# Example usage:
# resolver = LocationResolver()
# result = resolver.resolve_with_radius("Kollam coast", radius_km=5.0)
# print(result)  # {'latitude': 8.8932, 'longitude': 76.6141, 'radius_km': 5.0, 'resolved_name': 'Kollam coast'}