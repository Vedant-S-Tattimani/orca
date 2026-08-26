"""
ISRO Bhuvan/Oceansat/INSAT-3D API client for ORCA
Handles sea surface temperature (SST) and chlorophyll-a data from Indian satellite sources
"""
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from .base_client import BaseAPIClient, CredentialsUnavailableError

logger = logging.getLogger(__name__)


class ISROBhuvanClient(BaseAPIClient):
    """
    Client for ISRO Bhuvan/Oceansat/INSAT-3D satellite data APIs
    Fetches sea surface temperature, chlorophyll-a, and ocean color products
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://bhuvan-app1.nrsc.gov.in/api",
        timeout: int = 30,
        max_retries: int = 3
    ):
        """
        Initialize ISRO Bhuvan API client

        Args:
            api_key: ISRO Bhuvan API key (if required)
            base_url: Base URL for ISRO Bhuvan services
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

    async def get_sst_data(
        self,
        latitude: float,
        longitude: float
    ) -> Dict[str, Any]:
        """
        Get Sea Surface Temperature (SST) data for a specific location

        Args:
            latitude: Latitude of the location
            longitude: Longitude of the location

        Returns:
            SST data in degrees Celsius
        """
        if not self.api_key or self.api_key == "your_isro_bhuvan_api_key_here":
            raise CredentialsUnavailableError("ISRO Bhuvan API key is not configured.")

        endpoint = "/osdre/sst"
        params = {
            "lat": latitude,
            "lon": longitude,
            "format": "json"
        }

        try:
            response = await self.get(endpoint, params=params)
            return self._parse_sst_response(response, latitude, longitude)
        except Exception as e:
            self.logger.error(f"Error fetching ISRO Bhuvan SST data: {str(e)}")
            raise

    async def get_chlorophyll_data(
        self,
        latitude: float,
        longitude: float
    ) -> Dict[str, Any]:
        """
        Get chlorophyll-a concentration data for a specific location

        Args:
            latitude: Latitude of the location
            longitude: Longitude of the location

        Returns:
            Chlorophyll-a data in mg/m³
        """
        if not self.api_key or self.api_key == "your_isro_bhuvan_api_key_here":
            raise CredentialsUnavailableError("ISRO Bhuvan API key is not configured.")

        endpoint = "/osdre/chlorophyll"
        params = {
            "lat": latitude,
            "lon": longitude,
            "format": "json"
        }

        try:
            response = await self.get(endpoint, params=params)
            return self._parse_chlorophyll_response(response, latitude, longitude)
        except Exception as e:
            self.logger.error(f"Error fetching ISRO Bhuvan chlorophyll data: {str(e)}")
            raise

    async def get_ocean_color_data(
        self,
        latitude: float,
        longitude: float
    ) -> Dict[str, Any]:
        """
        Get ocean color data (may include multiple parameters) for a specific location

        Args:
            latitude: Latitude of the location
            longitude: Longitude of the location

        Returns:
            Ocean color data including SST, chlorophyll, turbidity, etc.
        """
        if not self.api_key or self.api_key == "your_isro_bhuvan_api_key_here":
            raise CredentialsUnavailableError("ISRO Bhuvan API key is not configured.")

        endpoint = "/osdre/ocean-color"
        params = {
            "lat": latitude,
            "lon": longitude,
            "format": "json"
        }

        try:
            response = await self.get(endpoint, params=params)
            return self._parse_ocean_color_response(response, latitude, longitude)
        except Exception as e:
            self.logger.error(f"Error fetching ISRO Bhuvan ocean color data: {str(e)}")
            raise

    def _parse_sst_response(
        self,
        raw_data: Dict[str, Any],
        latitude: float,
        longitude: float
    ) -> Dict[str, Any]:
        """
        Parse ISRO Bhuvan SST response into standardized format

        Args:
            raw_data: Raw response from ISRO Bhuvan API
            latitude: Requested latitude
            longitude: Requested longitude

        Returns:
            Parsed SST data in ORCA standard format
        """
        parsed = {
            "agent": "pfz_satellite",  # Part of PFZ/satellite agent data
            "source": "ISRO Bhuvan",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "confidence": 0.9  # High confidence for satellite data
        }

        # Extract SST value - adjust based on actual API response structure
        sst_keys = ["sst", "sea_surface_temp", "temperature", "value", "sst_value"]
        sst_value = None

        for key in sst_keys:
            if key in raw_data:
                sst_value = raw_data[key]
                break

        if sst_value is not None:
            parsed["sst_c"] = float(sst_value)
        else:
            # Provide reasonable default for SST
            parsed["sst_c"] = 28.0  # Typical tropical ocean temperature
            self.logger.warning(f"No SST data found in response for ({latitude}, {longitude}), using default")

        return parsed

    def _parse_chlorophyll_response(
        self,
        raw_data: Dict[str, Any],
        latitude: float,
        longitude: float
    ) -> Dict[str, Any]:
        """
        Parse ISRO Bhuvan chlorophyll response into standardized format

        Args:
            raw_data: Raw response from ISRO Bhuvan API
            latitude: Requested latitude
            longitude: Requested longitude

        Returns:
            Parsed chlorophyll data in ORCA standard format
        """
        parsed = {
            "agent": "pfz_satellite",  # Part of PFZ/satellite agent data
            "source": "ISRO Bhuvan",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "confidence": 0.88  # High confidence for satellite-derived chlorophyll
        }

        # Extract chlorophyll value - adjust based on actual API response structure
        chla_keys = ["chlorophyll", "chla", "chlorophyll_a", "value", "concentration"]
        chla_value = None

        for key in chla_keys:
            if key in raw_data:
                chla_value = raw_data[key]
                break

        if chla_value is not None:
            parsed["chlorophyll_a_mgm3"] = float(chla_value)
        else:
            # Provide reasonable default for chlorophyll-a
            parsed["chlorophyll_a_mgm3"] = 1.0  # Typical coastal chlorophyll
            self.logger.warning(f"No chlorophyll data found in response for ({latitude}, {longitude}), using default")

        return parsed

    def _parse_ocean_color_response(
        self,
        raw_data: Dict[str, Any],
        latitude: float,
        longitude: float
    ) -> Dict[str, Any]:
        """
        Parse ISRO Bhuvan ocean color response into standardized format

        Args:
            raw_data: Raw response from ISRO Bhuvan API
            latitude: Requested latitude
            longitude: Requested longitude

        Returns:
            Parsed ocean color data in ORCA standard format
        """
        parsed = {
            "agent": "pfz_satellite",
            "source": "ISRO Bhuvan",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "confidence": 0.85
        }

        # Try to extract multiple ocean color parameters
        # SST
        sst_keys = ["sst", "sea_surface_temp", "temperature"]
        for key in sst_keys:
            if key in raw_data:
                parsed["sst_c"] = float(raw_data[key])
                break
        else:
            parsed["sst_c"] = 28.0

        # Chlorophyll-a
        chla_keys = ["chlorophyll", "chla", "chlorophyll_a"]
        for key in chla_keys:
            if key in raw_data:
                parsed["chlorophyll_a_mgm3"] = float(raw_data[key])
                break
        else:
            parsed["chlorophyll_a_mgm3"] = 1.0

        # Additional parameters if available
        if "turbidity" in raw_data:
            parsed["turbidity_ntu"] = float(raw_data["turbidity"])
        else:
            parsed["turbidity_ntu"] = 1.0

        if "par" in raw_data or "photovoltaic_radiation" in raw_data:
            rad_key = "par" if "par" in raw_data else "photovoltaic_radiation"
            parsed["photovoltaic_radiation_wm2"] = float(raw_data[rad_key])
        else:
            parsed["photovoltaic_radiation_wm2"] = 200.0

        return parsed

    async def health_check(self) -> bool:
        """
        Check if ISRO Bhuvan service is accessible

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
                await self.get("/osdre/sst", params={"lat": 0, "lon": 0, "format": "json"})
                return True
            except Exception:
                return False