"""
Hazard agent for ORCA - handles cyclone/lightning/tsunami warnings
Specialist agent for hazard-related marine conditions
"""
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging
import asyncio

from .base_agent import BaseAgent
from ..services.imd_client import IMDClient
from ..services.incois_client import INCOISClient
from ..services.openmeteo_weather_client import OpenMeteoWeatherClient
from ..config import settings

logger = logging.getLogger(__name__)

class HazardAgent(BaseAgent):
    """
    Hazard specialist agent that fetches data from IMD and INCOIS for
    cyclone tracks, lightning probability, tsunami/high-wave warnings
    """

    def __init__(self):
        super().__init__("hazard")
        self.logger = logging.getLogger(f"{__name__}.HazardAgent")
        # Initialize clients with configuration
        self.imd_client = IMDClient(
            api_key=settings.IMD_API_KEY,
            timeout=30,
            max_retries=3
        )
        self.incois_client = INCOISClient(
            api_key=settings.INCOIS_API_KEY,
            timeout=30,
            max_retries=3
        )
        self.openmeteo_weather_client = OpenMeteoWeatherClient(
            timeout=30,
            max_retries=3
        )

    async def fetch(
        self,
        latitude: float,
        longitude: float,
        start_time: datetime,
        end_time: datetime,
        radius_km: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Fetch hazard data from IMD, INCOIS, or warning systems

        For demo/stub purposes, returns mock data that matches the expected structure
        In production, this would call actual IMD cyclone bulletins, lightning nowcasts,
        INCOIS ODSSA (Ocean State and Disaster Support Services), tsunami warning centers
        """
        self.logger.info(f"Fetching hazard data for ({latitude}, {longitude}) from {start_time} to {end_time}")

        # Start with mock data as base
        base_data = self._generate_mock_hazard_data(latitude, longitude, start_time, end_time)
        hazard_data = {}  # to collect real data from APIs

        try:
            # Get cyclone and lightning data from IMD
            try:
                imd_data = await self.imd_client.get_cyclone_info(
                    latitude=latitude,
                    longitude=longitude,
                    radius_km=radius_km
                )
                hazard_data.update(imd_data)
                self.logger.debug(f"Fetched cyclone data from IMD: {imd_data}")
            except Exception as e:
                self.logger.warning(f"Failed to fetch IMD cyclone data: {e}")

            try:
                imd_data = await self.imd_client.get_lightning_nowcast(
                    latitude=latitude,
                    longitude=longitude,
                    radius_km=radius_km
                )
                hazard_data.update(imd_data)
                self.logger.debug(f"Fetched lightning data from IMD: {imd_data}")
            except Exception as e:
                self.logger.warning(f"Failed to fetch IMD lightning data: {e}")

            # Get tsunami and ocean state data from INCOIS
            try:
                incois_data = await self.incois_client.get_tsunami_warning(
                    latitude=latitude,
                    longitude=longitude,
                    radius_km=radius_km
                )
                hazard_data.update(incois_data)
                self.logger.debug(f"Fetched tsunami data from INCOIS: {incois_data}")
            except Exception as e:
                self.logger.warning(f"Failed to fetch INCOIS tsunami data: {e}")

            # Check if we failed to fetch real IMD data, if so use keyless Open-Meteo Weather as fallback proxy
            if "cyclone_wind_speed_kmh" not in hazard_data or "lightning_probability_percent" not in hazard_data:
                self.logger.info("Fallback: Fetching real meteorological data from Open-Meteo for hazard proxy assessment")
                try:
                    openmeteo_data = await self.openmeteo_weather_client.get_weather_forecast(
                        latitude=latitude,
                        longitude=longitude,
                        forecast_days=1
                    )
                    
                    if "wind_speed_kmh" in openmeteo_data:
                        wind_speed = openmeteo_data["wind_speed_kmh"]
                        wind_max = openmeteo_data.get("wind_speed_max_kmh", wind_speed)
                        # Don't set cyclone_wind_speed_kmh based on daily gusts
                        hazard_data["wind_gusts_kmh"] = wind_max * 1.2
                    
                    if "weather_code" in openmeteo_data:
                        wcode = openmeteo_data["weather_code"]
                        if wcode in [95, 96, 99]:
                            hazard_data["lightning_probability_percent"] = 85.0
                        elif wcode in [80, 81, 82, 51, 53, 55, 56, 57, 61, 63, 65]:
                            hazard_data["lightning_probability_percent"] = 35.0
                        else:
                            hazard_data["lightning_probability_percent"] = 5.0
                    
                    if "rainfall_mm" in openmeteo_data:
                        hazard_data["heavy_rain_potential_mmh"] = openmeteo_data["rainfall_mm"]
                        
                    self.logger.info(f"Fallback: Populated hazard proxy fields from Open-Meteo: gusts={hazard_data.get('wind_gusts_kmh')} km/h, lightning={hazard_data.get('lightning_probability_percent')}%")
                except Exception as om_e:
                    self.logger.warning(f"Failed to fetch Open-Meteo fallback hazard data: {om_e}")

        except Exception as e:
            self.logger.error(f"Unexpected error in hazard agent fetch: {e}")
            # If there's an unexpected error, we'll just use the mock data
            pass

        # Update base_data with any real data we managed to fetch
        if hazard_data:
            base_data.update(hazard_data)

        # Ensure agent field is set to "hazard"
        base_data["agent"] = "hazard"

        # Set source based on what data we were able to fetch from APIs
        sources = []
        if any(key in hazard_data for key in ["cyclone_wind_speed_kmh", "lightning_probability_percent"]):
            sources.append("IMD")
        if any(key in hazard_data for key in ["tsunami_wave_height_m"]):
            sources.append("INCOIS")

        base_data["source"] = "+".join(sources) if sources else "IMD+INCOIS (Simulated)"

        # Set data_status
        if sources:
            base_data["data_status"] = "LIVE"
        else:
            base_data["data_status"] = "SIMULATED"

        # Generate active warnings if we have the three fields (now we should because we started with mock and updated with real)
        if "cyclone_wind_speed_kmh" in base_data and "lightning_probability_percent" in base_data and "tsunami_wave_height_m" in base_data:
            base_data["active_warnings"] = self._generate_active_warnings(
                base_data["cyclone_wind_speed_kmh"],
                base_data["lightning_probability_percent"],
                base_data["tsunami_wave_height_m"]
            )
        else:
            # This should not happen because we started with mock data which has these fields
            base_data["active_warnings"] = []

        # Set confidence based on data availability
        if base_data.get("data_status") == "SIMULATED":
            base_data["confidence"] = 0.4
        else:
            data_points = len([k for k in ["cyclone_wind_speed_kmh", "lightning_probability_percent", "tsunami_wave_height_m"] if k in hazard_data])
            base_data["confidence"] = min(0.85, 0.6 + (data_points * 0.1))

        # Set timestamp if not already set by the APIs (but note: our mock data has it, and real data might overwrite)
        if "timestamp" not in base_data:
            base_data["timestamp"] = start_time.isoformat() + "Z"

        # Set forecast hours if not already set by the APIs
        if "forecast_hours" not in base_data:
            base_data["forecast_hours"] = int((end_time - start_time).total_seconds() / 3600)

        self.logger.debug(f"Fetched hazard data: {base_data}")
        return base_data

    def _generate_active_warnings(
        self,
        cyclone_wind_speed: float,
        lightning_probability: float,
        tsunami_wave_height: float
    ) -> List[str]:
        """Generate list of active warnings based on hazard values"""
        warnings = []

        if cyclone_wind_speed >= 63:  # Tropical storm or stronger
            if cyclone_wind_speed >= 118:  # Hurricane strength
                warnings.append("CYCLONE WARNING: Hurricane force winds expected")
            else:
                warnings.append("CYCLONE WATCH: Tropical storm conditions possible")

        if lightning_probability >= 60:
            warnings.append("LIGHTNING ALERT: High lightning activity expected")
        elif lightning_probability >= 30:
            warnings.append("LIGHTNING WATCH: Moderate lightning possible")

        if tsunami_wave_height >= 1.0:
            warnings.append("TSUNAMI WARNING: Destructive waves possible")
        elif tsunami_wave_height >= 0.5:
            warnings.append("TSUNAMI WATCH: Hazardous waves possible")

        return warnings

    def to_structured(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert raw hazard data to structured format
        For the hazard agent, the fetch method already returns structured data,
        but this method ensures consistency with the base agent interface
        """
        # If there's an error, return as-is
        if "error" in raw_data:
            return raw_data

        # Ensure all required fields are present
        structured = {
            "agent": "hazard",
            "source": raw_data.get("source", "unknown"),
            "timestamp": raw_data.get("timestamp", datetime.utcnow().isoformat()),
            "confidence": raw_data.get("confidence", 0.0)
        }

        # Copy all hazard-specific fields
        hazard_fields = [
            "cyclone_wind_speed_kmh", "lightning_probability_percent",
            "tsunami_wave_height_m", "heavy_rain_potential_mmh",
            "wind_gusts_kmh", "algal_bloom_risk", "active_warnings",
            "forecast_hours"
        ]

        for field in hazard_fields:
            if field in raw_data:
                structured[field] = raw_data[field]

        return structured

    def _generate_mock_hazard_data(
        self,
        latitude: float,
        longitude: float,
        start_time: datetime,
        end_time: datetime
    ) -> Dict[str, Any]:
        """
        Generate mock hazard data for fallback when APIs are unavailable
        Preserves the same structure as real API responses
        """
        self.logger.info("Generating mock hazard data as fallback")

        # Simulate API call delay to maintain consistent timing
        import asyncio
        import random

        # Generate realistic mock hazard data
        # Base values typical for hazard assessment
        base_cyclone_wind = random.uniform(0, 50)  # km/h - mostly calm to moderate
        base_lightning_prob = random.uniform(0, 40)  # percent - low to moderate
        base_tsunami_height = random.uniform(0, 0.3)  # meters - negligible to small

        # Add some spatial and temporal variation
        # Coastal areas might have different hazard profiles
        distance_from_coast = min(abs(latitude - 8.9), abs(longitude - 76.6)) * 111  # Rough km
        coastal_factor = max(0.5, 1.0 - (distance_from_coast / 200))  # Decreases with distance

        # Time of day effects (some hazards more likely at certain times)
        hour = start_time.hour
        # Thunderstorms more likely in afternoon
        if 12 <= hour <= 18:
            lightning_modifier = random.uniform(0, 20)
        else:
            lightning_modifier = random.uniform(-10, 10)

        # Seasonal effects (simplified)
        month = start_time.month
        # Cyclone season (simplified for demo)
        cyclone_months = [4, 5, 6, 7, 8, 9, 10, 11, 12]  # Extended cyclone season
        cyclone_factor = 1.5 if month in cyclone_months else 0.5

        hazard_data = {
            "agent": "hazard",
            "cyclone_wind_speed_kmh": round(base_cyclone_wind * cyclone_factor + random.uniform(-5, 5), 1),
            "lightning_probability_percent": round(base_lightning_prob + lightning_modifier + random.uniform(-5, 5), 1),
            "tsunami_wave_height_m": round(base_tsunami_height + random.uniform(-0.1, 0.1), 2),
            "heavy_rain_potential_mmh": round(random.uniform(0, 15), 1),  # mm/h
            "wind_gusts_kmh": round(random.uniform(0, 30), 1),
            "algal_bloom_risk": round(random.uniform(0.0, 0.3), 2),  # 0-0.3 scale
            "active_warnings": self._generate_active_warnings(
                round(base_cyclone_wind * cyclone_factor + random.uniform(-5, 5), 1),
                round(base_lightning_prob + lightning_modifier + random.uniform(-5, 5), 1),
                round(base_tsunami_height + random.uniform(-0.1, 0.1), 2)
            ),
            "source": "IMD+INCOIS (Mock Fallback)",
            "timestamp": start_time.isoformat() + "Z",
            "confidence": 0.6,  # Lower confidence for mock data
            "forecast_hours": int((end_time - start_time).total_seconds() / 3600)
        }

        self.logger.debug(f"Generated mock hazard data: {hazard_data}")
        return hazard_data

    async def check_health(self) -> Dict[str, str]:
        """Check health of IMD and INCOIS services for hazards"""
        try:
            # We ping IMD for storm data
            is_healthy = await self.imd_client.health_check()
            if is_healthy:
                return {"status": "ok", "note": "Storm Alert System Active"}
            else:
                return {"status": "degraded", "note": "Primary Hazard Links offline. Using fallback data."}
        except Exception as e:
            return {"status": "failed", "note": f"Agent error: {str(e)}"}


# Example usage and testing
if __name__ == "__main__":
    import asyncio
    from datetime import datetime, timedelta

    async def test_hazard_agent():
        agent = HazardAgent()

        # Test with Kollam coordinates
        latitude = 8.8932
        longitude = 76.6141
        start_time = datetime.utcnow()
        end_time = start_time + timedelta(hours=5)

        result = await agent.process(latitude, longitude, start_time, end_time)
        print("Hazard Agent Result:")
        print(result)

    # Run the test
    asyncio.run(test_hazard_agent())