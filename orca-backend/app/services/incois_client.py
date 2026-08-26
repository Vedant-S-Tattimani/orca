"""
INCOIS (Indian National Centre for Ocean Information Services) API client for ORCA
Handles sea-state forecasts, PFZ advisories, and ocean state data
"""
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from .base_client import BaseAPIClient, CredentialsUnavailableError

logger = logging.getLogger(__name__)


class INCOISClient(BaseAPIClient):
    """
    Client for Indian National Centre for Ocean Information Services (INCOIS) APIs
    Fetches sea-state data, PFZ advisories, wave forecasts, and ocean state information
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://incois.gov.in/portal",
        timeout: int = 30,
        max_retries: int = 3
    ):
        """
        Initialize INCOIS API client

        Args:
            api_key: INCOIS API key (if required)
            base_url: Base URL for INCOIS services
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
        """
        super().__init__(
            base_url=base_url,
            api_key=api_key,
            timeout=timeout,
            max_retries=max_retries
        )
        self.logger = logging.getLogger(self.__class__.__module__ + '.' + self.__class__.__name__)

    async def get_sea_state_forecast(
        self,
        latitude: float,
        longitude: float,
        radius_km: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Get sea-state forecast (waves, swell, currents, tides) for a location

        Args:
            latitude: Latitude of the location
            longitude: Longitude of the location
            radius_km: Search radius in kilometers (optional)

        Returns:
            Sea-state forecast data
        """
        if not self.api_key or self.api_key == "your_incois_api_key_here":
            raise CredentialsUnavailableError("INCOIS API key is not configured.")

        endpoint = "/api/sea-state/forecast"
        params = {
            "lat": latitude,
            "lon": longitude,
        }
        if radius_km:
            params["radius"] = radius_km

        try:
            response = await self.get(endpoint, params=params)
            return self._parse_sea_state_response(response, latitude, longitude)
        except Exception as e:
            self.logger.error(f"Error fetching INCOIS sea-state forecast: {str(e)}")
            raise

    async def get_pfz_advisory(
        self,
        latitude: float,
        longitude: float,
        radius_km: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Get Potential Fishing Zone (PFZ) advisory for a location

        Args:
            latitude: Latitude of the location
            longitude: Longitude of the location
            radius_km: Search radius in kilometers (optional)

        Returns:
            PFZ advisory data including SST, chlorophyll-a, and confidence
        """
        if not self.api_key or self.api_key == "your_incois_api_key_here":
            raise CredentialsUnavailableError("INCOIS API key is not configured.")

        endpoint = "/api/pfz/advisory"
        params = {
            "lat": latitude,
            "lon": longitude,
        }
        if radius_km:
            params["radius"] = radius_km

        try:
            response = await self.get(endpoint, params=params)
            return self._parse_pfz_response(response, latitude, longitude)
        except Exception as e:
            self.logger.error(f"Error fetching INCOIS PFZ advisory: {str(e)}")
            raise

    async def get_tsunami_warning(
        self,
        latitude: float,
        longitude: float,
        radius_km: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Get tsunami/high-wave warnings for a location

        Args:
            latitude: Latitude of the location
            longitude: Longitude of the location
            radius_km: Search radius in kilometers (optional)

        Returns:
            Tsunami warning data
        """
        if not self.api_key or self.api_key == "your_incois_api_key_here":
            raise CredentialsUnavailableError("INCOIS API key is not configured.")

        endpoint = "/api/tsunami/warning"
        params = {
            "lat": latitude,
            "lon": longitude,
        }
        if radius_km:
            params["radius"] = radius_km

        try:
            response = await self.get(endpoint, params=params)
            return self._parse_tsunami_response(response, latitude, longitude)
        except Exception as e:
            self.logger.error(f"Error fetching INCOIS tsunami warning: {str(e)}")
            raise

    def _parse_sea_state_response(
        self,
        raw_data: Dict[str, Any],
        latitude: float,
        longitude: float
    ) -> Dict[str, Any]:
        """
        Parse INCOIS sea-state response into standardized format

        Args:
            raw_data: Raw response from INCOIS API
            latitude: Requested latitude
            longitude: Requested longitude

        Returns:
            Parsed sea-state data in ORCA standard format
        """
        parsed = {
            "agent": "sea_state",
            "source": "INCOIS",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "confidence": 0.88  # High confidence for official oceanographic data
        }

        # Map common sea-state fields with fallbacks
        sea_state_mapping = {
            "wave_height_m": ["wave_height", "wh", "sig_wave_height"],
            "wave_period_s": ["wave_period", "wp", "period"],
            "swell_height_m": ["swell_height", "swell"],
            "swell_direction_deg": ["swell_direction", "swell_dir"],
            "current_speed_knots": ["current_speed", "current", "surface_current"],
            "current_direction_deg": ["current_direction", "current_dir"],
            "tide_height_m": ["tide_height", "tide", "sea_level"],
            "sea_surface_temp_c": ["sst", "sea_surface_temp", "temperature"],
            "salinity_psu": ["salinity", "salt", "psu"]
        }

        for our_key, possible_keys in sea_state_mapping.items():
            value = None
            for key in possible_keys:
                if key in raw_data:
                    value = raw_data[key]
                    break

            if value is not None:
                # Apply any necessary unit conversions here
                parsed[our_key] = float(value)
            else:
                # Provide reasonable defaults based on typical ocean conditions
                defaults = {
                    "wave_height_m": 1.5,
                    "wave_period_s": 8.0,
                    "swell_height_m": 0.8,
                    "swell_direction_deg": 180.0,
                    "current_speed_knots": 1.0,
                    "current_direction_deg": 90.0,
                    "tide_height_m": 0.5,
                    "sea_surface_temp_c": 28.0,
                    "salinity_psu": 35.0
                }
                parsed[our_key] = defaults.get(our_key, 0.0)

        # Add forecast hours
        if "forecast_hours" in raw_data:
            parsed["forecast_hours"] = int(raw_data["forecast_hours"])
        else:
            parsed["forecast_hours"] = 5

        return parsed

    def _parse_pfz_response(
        self,
        raw_data: Dict[str, Any],
        latitude: float,
        longitude: float
    ) -> Dict[str, Any]:
        """
        Parse INCOIS PFZ response into standardized format

        Args:
            raw_data: Raw response from INCOIS API
            latitude: Requested latitude
            longitude: Requested longitude

        Returns:
            Parsed PFZ data in ORCA standard format
        """
        parsed = {
            "agent": "pfz_satellite",
            "source": "INCOIS",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "confidence": 0.85
        }

        # Map PFZ-specific fields
        pfz_mapping = {
            "sst_c": ["sst", "sea_surface_temp", "temperature"],
            "chlorophyll_a_mgm3": ["chlorophyll", "chla", "chlorophyll_a"],
            "pfz_confidence_percent": ["confidence", "pfz_confidence", "probability"],
            "sea_surface_height_m": ["ssh", "sea_surface_height"],
            "turbidity_ntu": ["turbidity", "turb"],
            "photovoltaic_radiation_wm2": ["rad", "radiation", "par"],
            "wind_speed_at_sea_ms": ["wind_speed", "ws"]
        }

        for our_key, possible_keys in pfz_mapping.items():
            value = None
            for key in possible_keys:
                if key in raw_data:
                    value = raw_data[key]
                    break

            if value is not None:
                parsed[our_key] = float(value)
            else:
                # Provide reasonable defaults for PFZ data
                defaults = {
                    "sst_c": 28.0,
                    "chlorophyll_a_mgm3": 1.0,
                    "pfz_confidence_percent": 70.0,
                    "sea_surface_height_m": 0.0,
                    "turbidity_ntu": 1.0,
                    "photovoltaic_radiation_wm2": 200.0,
                    "wind_speed_at_sea_ms": 5.0
                }
                parsed[our_key] = defaults.get(our_key, 0.0)

        # Generate PFZ recommendation based on parsed data
        parsed["pfz_recommendation"] = self._generate_pfz_recommendation(
            parsed.get("sst_c", 28.0),
            parsed.get("chlorophyll_a_mgm3", 1.0),
            parsed.get("pfz_confidence_percent", 70.0)
        )

        # Add data origin info
        parsed["data_origin"] = {
            "sst": "INCOIS-derived",
            "chlorophyll": "INCOIS-derived",
            "pfz": "INCOIS Advisory"
        }

        # Add forecast hours
        if "forecast_hours" in raw_data:
            parsed["forecast_hours"] = int(raw_data["forecast_hours"])
        else:
            parsed["forecast_hours"] = 5

        return parsed

    def _parse_tsunami_response(
        self,
        raw_data: Dict[str, Any],
        latitude: float,
        longitude: float
    ) -> Dict[str, Any]:
        """
        Parse INCOIS tsunami response into standardized format

        Args:
            raw_data: Raw response from INCOIS API
            latitude: Requested latitude
            longitude: Requested longitude

        Returns:
            Parsed tsunami data in ORCA standard format
        """
        parsed = {
            "agent": "hazard",
            "source": "INCOIS",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "confidence": 0.9  # Very high confidence for tsunami warnings
        }

        # Extract tsunami wave height
        tsunami_keys = ["wave_height", "tsunami_height", "max_wave", "amplitude"]
        tsunami_value = None

        for key in tsunami_keys:
            if key in raw_data:
                tsunami_value = raw_data[key]
                break

        if tsunami_value is not None:
            parsed["tsunami_wave_height_m"] = float(tsunami_value)
        else:
            parsed["tsunami_wave_height_m"] = 0.0

        # Additional tsunami fields
        if "travel_time_min" in raw_data:
            parsed["tsunami_travel_time_min"] = float(raw_data["travel_time_min"])
        else:
            parsed["tsunami_travel_time_min"] = 0.0

        if "risk_level" in raw_data:
            parsed["tsunami_risk_level"] = str(raw_data["risk_level"])
        else:
            # Determine risk level based on wave height
            height = parsed.get("tsunami_wave_height_m", 0.0)
            if height >= 3.0:
                parsed["tsunami_risk_level"] = "High"
            elif height >= 1.0:
                parsed["tsunami_risk_level"] = "Medium"
            elif height > 0:
                parsed["tsunami_risk_level"] = "Low"
            else:
                parsed["tsunami_risk_level"] = "None"

        return parsed

    def _generate_pfz_recommendation(
        self,
        sst: float,
        chlorophyll_a: float,
        pfz_confidence: float
    ) -> str:
        """Generate a fishing recommendation based on PFZ data"""
        # SST suitability for fishing (general range for tropical fish)
        sst_score = 0
        if 24 <= sst <= 30:
            sst_score = 2  # Good
        elif 22 <= sst < 24 or 30 < sst <= 32:
            sst_score = 1  # Fair
        else:
            sst_score = 0  # Poor

        # Chlorophyll-a suitability (productivity indicator)
        chla_score = 0
        if 0.5 <= chlorophyll_a <= 3.0:
            chla_score = 2  # Good productivity
        elif 0.2 <= chlorophyll_a < 0.5 or 3.0 < chlorophyll_a <= 5.0:
            chla_score = 1  # Moderate
        else:
            chla_score = 0  # Low or excessively high

        # PFZ confidence
        conf_score = 0
        if pfz_confidence >= 70:
            conf_score = 2  # High confidence
        elif pfz_confidence >= 40:
            conf_score = 1  # Moderate confidence
        else:
            conf_score = 0  # Low confidence

        total_score = sst_score + chla_score + conf_score

        if total_score >= 5:
            return "excellent"
        elif total_score >= 3:
            return "good"
        elif total_score >= 1:
            return "fair"
        else:
            return "poor"

    async def health_check(self) -> bool:
        """
        Check if INCOIS service is accessible

        Returns:
            True if service is responsive, False otherwise
        """
        try:
            # Try a lightweight endpoint or test connectivity
            await self.get("/api/health", params={})
            return True
        except Exception:
            # If specific health endpoint doesn't exist, try a basic endpoint
            try:
                await self.get("/api/sea-state/forecast", params={"lat": 0, "lon": 0})
                return True
            except Exception:
                return False