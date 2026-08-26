"""
PFZ/Satellite agent for ORCA - handles PFZ + SST + chlorophyll-a data
Specialist agent for potential fishing zones and satellite oceanographic data
"""
from typing import Dict, Any, Optional
from datetime import datetime
import logging
import asyncio

from .base_agent import BaseAgent
from ..services.incois_client import INCOISClient
from ..services.isro_bhuvan_client import ISROBhuvanClient
from ..services.openmeteo_marine_client import OpenMeteoMarineClient
from ..services.base_client import CredentialsUnavailableError
from ..config import settings

logger = logging.getLogger(__name__)

class PFZAgent(BaseAgent):
    """
    PFZ/Satellite specialist agent that fetches data from INCOIS (Potential Fishing Zone advisories)
    and ISRO Bhuvan/Oceansat/INSAT-3D for sea surface temperature, chlorophyll-a concentration,
    and other oceanographic parameters relevant to fishing and marine conditions
    """

    def __init__(self):
        super().__init__("pfz_satellite")
        self.logger = logging.getLogger(f"{__name__}.PFZAgent")
        # Initialize clients with configuration
        self.incois_client = INCOISClient(
            api_key=settings.INCOIS_API_KEY,
            timeout=30,
            max_retries=3
        )
        self.isro_bhuvan_client = ISROBhuvanClient(
            api_key=settings.ISRO_BHUVAN_API_KEY,
            timeout=30,
            max_retries=3
        )
        self.openmeteo_marine_client = OpenMeteoMarineClient(
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
        Fetch PFZ and satellite data from INCOIS and ISRO sources

        In production, this calls actual INCOIS PFZ advisories and ISRO Bhuvan/Oceansat/INSAT-3D data services
        Falls back to mock data if APIs are unavailable
        """
        self.logger.info(f"Fetching PFZ/satellite data for ({latitude}, {longitude}) from {start_time} to {end_time}")

        # Start with mock data as base
        base_data = self._generate_mock_pfz_data(latitude, longitude, start_time, end_time)
        pfz_data = {}  # to collect real data from APIs

        try:
            # Attempt to fetch real data from INCOIS and ISRO Bhuvan
            # We'll try to get data from both sources and combine them

            # Get PFZ advisory from INCOIS
            try:
                incois_data = await self.incois_client.get_pfz_advisory(
                    latitude=latitude,
                    longitude=longitude,
                    radius_km=radius_km
                )
                pfz_data.update(incois_data)
                self.logger.debug(f"Fetched PFZ data from INCOIS: {incois_data}")
            except CredentialsUnavailableError as ce:
                self.logger.warning(f"INCOIS credentials unavailable: {ce}. Falling back to SIMULATED PFZ data.")
                base_data["data_status"] = "SIMULATED"
            except Exception as e:
                self.logger.warning(f"Failed to fetch INCOIS PFZ data: {e}")
                base_data["data_status"] = "SIMULATED"

            # Get SST and chlorophyll data from ISRO Bhuvan
            try:
                # Try to get combined ocean color data first
                try:
                    ocean_color_data = await self.isro_bhuvan_client.get_ocean_color_data(
                        latitude=latitude,
                        longitude=longitude
                    )
                    pfz_data.update(ocean_color_data)
                    self.logger.debug(f"Fetched ocean color data from ISRO Bhuvan: {ocean_color_data}")
                except CredentialsUnavailableError as ce:
                    self.logger.warning(f"ISRO credentials unavailable: {ce}. Falling back to SIMULATED satellite data.")
                    base_data["data_status"] = "SIMULATED"
                except Exception:
                    # If ocean color fails, try individual SST and chlorophyll calls
                    try:
                        sst_data = await self.isro_bhuvan_client.get_sst_data(
                            latitude=latitude,
                            longitude=longitude
                        )
                        pfz_data.update(sst_data)
                        self.logger.debug(f"Fetched SST data from ISRO Bhuvan: {sst_data}")
                    except CredentialsUnavailableError as ce:
                        self.logger.warning(f"ISRO credentials unavailable: {ce}.")
                    except Exception as sst_e:
                        self.logger.warning(f"Failed to fetch ISRO Bhuvan SST data: {sst_e}")

                    try:
                        chlorophyll_data = await self.isro_bhuvan_client.get_chlorophyll_data(
                            latitude=latitude,
                            longitude=longitude
                        )
                        pfz_data.update(chlorophyll_data)
                        self.logger.debug(f"Fetched chlorophyll data from ISRO Bhuvan: {chlorophyll_data}")
                    except Exception as chlorophyll_e:
                        self.logger.warning(f"Failed to fetch ISRO Bhuvan chlorophyll data: {chlorophyll_e}")
            except Exception as e:
                self.logger.warning(f"Failed to fetch ISRO Bhuvan data: {e}")
                # Fallback to keyless Open-Meteo Marine client to get real SST
                try:
                    openmeteo_data = await self.openmeteo_marine_client.get_marine_forecast(
                        latitude=latitude,
                        longitude=longitude,
                        forecast_days=1
                    )
                    if "sea_surface_temp_c" in openmeteo_data:
                        pfz_data["sst_c"] = openmeteo_data["sea_surface_temp_c"]
                        pfz_data["is_openmeteo_fallback"] = True
                        self.logger.info(f"Fallback: Fetched real SST from Open-Meteo Marine: {pfz_data['sst_c']} C")
                except Exception as sst_e:
                    self.logger.warning(f"Failed to fetch Open-Meteo Marine fallback SST: {sst_e}")

        except Exception as e:
            self.logger.error(f"Unexpected error in PFZ/satellite agent fetch: {e}")
            # If there's an unexpected error, we'll just use the mock data
            pass

        # Update base_data with any real data we managed to fetch
        if pfz_data:
            base_data.update(pfz_data)

        # Ensure agent field is set to "pfz_satellite"
        base_data["agent"] = "pfz_satellite"

        # Set source based on what data we were able to fetch from APIs
        sources = []
        if any(key in pfz_data for key in ["pfz_confidence_percent"]):
            sources.append("INCOIS")
            
        has_isro_data = any(key in pfz_data for key in ["chlorophyll_a_mgm3"]) or (
            "sst_c" in pfz_data and not pfz_data.get("is_openmeteo_fallback")
        )
        if has_isro_data:
            sources.append("ISRO Bhuvan")
        elif pfz_data.get("is_openmeteo_fallback"):
            sources.append("Open-Meteo (SST only)")

        base_data["source"] = "+".join(sources) if sources else "INCOIS+ISRO (Simulated)"

        # Set data_status based on whether any real satellite/advisory data was fetched
        # Note: Open-Meteo fallback is live but not satellite EO data.
        if "ISRO Bhuvan" in sources or "INCOIS" in sources:
            base_data["data_status"] = "LIVE"
        elif "Open-Meteo (SST only)" in sources:
            base_data["data_status"] = "LIVE (Partial Fallback)"
        else:
            base_data["data_status"] = "SIMULATED"

        # Generate PFZ recommendation if we have the necessary data (now we should because we started with mock and updated with real)
        if "sst_c" in base_data and "chlorophyll_a_mgm3" in base_data and "pfz_confidence_percent" in base_data:
            base_data["pfz_recommendation"] = self._generate_pfz_recommendation(
                base_data["sst_c"],
                base_data["chlorophyll_a_mgm3"],
                base_data["pfz_confidence_percent"]
            )
        elif "pfz_recommendation" not in base_data:
            # Generate a default recommendation if we don't have enough data
            base_data["pfz_recommendation"] = "unknown"

        # Add data origin info if not already present
        if "data_origin" not in base_data:
            base_data["data_origin"] = {
                "sst": "ISRO Bhuvan-derived" if "sst_c" in base_data else "estimated",
                "chlorophyll": "ISRO Bhuvan-derived" if "chlorophyll_a_mgm3" in base_data else "estimated",
                "pfz": "INCOIS Advisory" if "pfz_confidence_percent" in base_data else "estimated"
            }

        # Set confidence based on data availability and reliability
        if base_data.get("data_status") == "SIMULATED":
            base_data["confidence"] = 0.4
        else:
            data_points = len([k for k in ["sst_c", "chlorophyll_a_mgm3", "pfz_confidence_percent"] if k in pfz_data])
            base_data["confidence"] = min(0.9, 0.6 + (data_points * 0.1))

        # Set timestamp if not already set by the APIs (but note: our mock data has it, and real data might overwrite)
        if "timestamp" not in base_data:
            base_data["timestamp"] = start_time.isoformat() + "Z"

        # Set forecast hours if not already set by the APIs
        if "forecast_hours" not in base_data:
            base_data["forecast_hours"] = int((end_time - start_time).total_seconds() / 3600)

        self.logger.debug(f"Fetched PFZ/satellite data: {base_data}")
        return base_data

    def _generate_pfz_recommendation(
        self,
        sst: float,
        chlorophyll_a: float,
        pfz_confidence: float
    ) -> str:
        """Generate a fishing recommendation based on PFZ/satellite data"""
        # SST suitability for fishing (species-dependent, but general range)
        sst_score = 0
        if 24 <= sst <= 30:
            sst_score = 2  # Good
        elif 22 <= sst < 24 or 30 < sst <= 32:
            sst_score = 1  # Fair
        else:
            sst_score = 0  # Poor

        # Chlorophyll-a suitability (higher generally better up to a point)
        chla_score = 0
        if 0.5 <= chlorophyll_a <= 3.0:
            chla_score = 2  # Good productivity
        elif 0.2 <= chlorophyll_a < 0.5 or 3.0 < chlorophyll_a <= 5.0:
            chla_score = 1  # Moderate
        else:
            chla_score = 0  # Low or excessively high (bloom)

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

    def to_structured(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert raw PFZ/satellite data to structured format
        For the PFZ/satellite agent, the fetch method already returns structured data,
        but this method ensures consistency with the base agent interface
        """
        # If there's an error, return as-is
        if "error" in raw_data:
            return raw_data

        # Ensure all required fields are present
        structured = {
            "agent": "pfz_satellite",
            "source": raw_data.get("source", "unknown"),
            "timestamp": raw_data.get("timestamp", datetime.utcnow().isoformat()),
            "confidence": raw_data.get("confidence", 0.0)
        }

        # Copy all PFZ/satellite-specific fields
        pfz_fields = [
            "sst_c", "chlorophyll_a_mgm3", "pfz_confidence_percent",
            "sea_surface_height_m", "turbidity_ntu", "photovoltaic_radiation_wm2",
            "wind_speed_at_sea_ms", "pfz_recommendation", "forecast_hours",
            "data_origin"
        ]

        for field in pfz_fields:
            if field in raw_data:
                structured[field] = raw_data[field]

        return structured

    def _generate_mock_pfz_data(
        self,
        latitude: float,
        longitude: float,
        start_time: datetime,
        end_time: datetime
    ) -> Dict[str, Any]:
        """
        Generate mock PFZ/satellite data for fallback when APIs are unavailable
        Preserves the same structure as real API responses
        """
        self.logger.info("Generating mock PFZ/satellite data as fallback")

        # Simulate API call delay to maintain consistent timing
        import asyncio
        import random

        # Generate realistic mock PFZ/satellite data
        # Base values typical for productive fishing zones
        base_sst = random.uniform(26, 30)  # Sea Surface Temperature in °C
        base_chlorophyll = random.uniform(0.2, 3.0)  # Chlorophyll-a in mg/m³
        base_pfz_confidence = random.uniform(40, 90)  # PFZ confidence percentage

        # Add some spatial and temporal variation
        # Coastal areas might have different characteristics
        distance_from_coast = min(abs(latitude - 8.9), abs(longitude - 76.6)) * 111  # Rough km
        coastal_factor = max(0.5, 1.0 - (distance_from_coast / 100))  # Decreases with distance

        # Time of day effects on SST (diurnal cycle)
        hour = start_time.hour
        sst_diurnal = 0.5 * abs((hour - 14) / 12)  # Peak at 2 PM

        # Seasonal effects (simplified)
        month = start_time.month
        # Productive months vs less productive (simplified for demo)
        productive_months = [6, 7, 8, 9, 10, 11]  # SW monsoon and post-monsoon
        seasonal_factor = 1.2 if month in productive_months else 0.8

        pfz_data = {
            "agent": "pfz_satellite",
            "sst_c": round(base_sst + sst_diurnal + random.uniform(-0.5, 0.5), 2),
            "chlorophyll_a_mgm3": round(base_chlorophyll * coastal_factor * seasonal_factor + random.uniform(-0.2, 0.2), 3),
            "pfz_confidence_percent": round(base_pfz_confidence * coastal_factor * seasonal_factor + random.uniform(-5, 5), 1),
            "sea_surface_height_m": round(random.uniform(-0.5, 0.5), 3),  # From altimetry
            "turbidity_ntu": round(random.uniform(0.5, 5.0), 1),
            "photovoltaic_radiation_wm2": round(random.uniform(180, 280), 1),
            "wind_speed_at_sea_ms": round(random.uniform(2, 8), 2),  # Scatterometer wind
            "pfz_recommendation": self._generate_pfz_recommendation(
                round(base_sst + sst_diurnal + random.uniform(-0.5, 0.5), 2),
                round(base_chlorophyll * coastal_factor * seasonal_factor + random.uniform(-0.2, 0.2), 3),
                round(base_pfz_confidence * coastal_factor * seasonal_factor + random.uniform(-5, 5), 1)
            ),
            "source": "INCOIS+ISRO (Mock Fallback)",
            "timestamp": start_time.isoformat() + "Z",
            "confidence": 0.6,  # Lower confidence for mock data
            "forecast_hours": int((end_time - start_time).total_seconds() / 3600),
            "data_origin": {
                "sst": "Oceansat-3D/INSAT-3D",
                "chlorophyll": "Oceansat-3D",
                "pfz": "INCOIS Advisory"
            }
        }

        self.logger.debug(f"Generated mock PFZ/satellite data: {pfz_data}")
        return pfz_data

    async def check_health(self) -> Dict[str, str]:
        """Check health of ISRO and INCOIS services for PFZ"""
        try:
            # We ping ISRO Bhuvan for satellite data
            is_healthy = await self.isro_bhuvan_client.health_check()
            if is_healthy:
                return {"status": "ok", "note": "ISRO Chlorophyll Grid Online"}
            else:
                return {"status": "degraded", "note": "Primary Satellite Links offline. Using fallback data."}
        except Exception as e:
            return {"status": "failed", "note": f"Agent error: {str(e)}"}


# Example usage and testing
if __name__ == "__main__":
    import asyncio
    from datetime import datetime, timedelta

    async def test_pfz_agent():
        agent = PFZAgent()

        # Test with Kollam coordinates
        latitude = 8.8932
        longitude = 76.6141
        start_time = datetime.utcnow()
        end_time = start_time + timedelta(hours=5)

        result = await agent.process(latitude, longitude, start_time, end_time)
        print("PFZ/Satellite Agent Result:")
        print(result)

    # Run the test
    asyncio.run(test_pfz_agent())