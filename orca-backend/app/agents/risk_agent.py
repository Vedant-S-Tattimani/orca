"""
Risk Assessment Agent for ORCA
Correlates meteorological, oceanographic, and geospatial outputs into
a unified risk rating, identifying active hazards and providing action recommendations.
"""
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging

from .base_agent import BaseAgent
from ..rules.risk_engine import RiskEngine
from ..services.openmeteo_weather_client import OpenMeteoWeatherClient
from ..services.openmeteo_marine_client import OpenMeteoMarineClient
from ..services.geospatial_service import GeospatialService

logger = logging.getLogger(__name__)


class RiskAgent(BaseAgent):
    """
    Risk specialist agent that fuses multiple data feeds to score maritime threat levels.
    """

    def __init__(self):
        super().__init__("risk_agent")
        self.logger = logging.getLogger(f"{__name__}.RiskAgent")
        self.risk_engine = RiskEngine()
        self.weather_client = OpenMeteoWeatherClient()
        self.marine_client = OpenMeteoMarineClient()
        self.geospatial_service = GeospatialService()

    async def fetch(
        self,
        latitude: float,
        longitude: float,
        start_time: datetime,
        end_time: datetime,
        radius_km: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Fetch weather, marine, and geofencing to evaluate overall threat score (0-100).
        """
        self.logger.info(f"Risk Agent assessing maritime threats for ({latitude}, {longitude})")
        
        hazards = []
        risk_score = 10.0  # Base safe score
        
        import asyncio
        weather_data, marine_data = {}, {}
        
        async def fetch_weather():
            try:
                return await self.weather_client.get_weather_forecast(latitude, longitude, forecast_days=1)
            except Exception as e:
                self.logger.warning(f"Risk Agent failed fetching weather data: {e}")
                return {}
                
        async def fetch_marine():
            try:
                return await self.marine_client.get_marine_forecast(latitude, longitude, forecast_days=1)
            except Exception as e:
                self.logger.warning(f"Risk Agent failed fetching marine data: {e}")
                return {}
                
        weather_data, marine_data = await asyncio.gather(fetch_weather(), fetch_marine())
        
        # Evaluate wind
        wind = weather_data.get("wind_speed_kmh", 0)
        if wind > 40:
            hazards.append("High Gale Winds")
            risk_score += 30.0
        elif wind > 20:
            hazards.append("Moderate winds")
            risk_score += 15.0
            
        # Evaluate rain
        rain = weather_data.get("rainfall_mm", 0)
        if rain > 7.5:
            hazards.append("Heavy Rainfall")
            risk_score += 20.0
            
        # Evaluate wave height
        wave = marine_data.get("wave_height_m", 0)
        if wave > 2.5:
            hazards.append("High Wave Swells")
            risk_score += 30.0
        elif wave > 1.5:
            hazards.append("Choppy Sea State")
            risk_score += 15.0

        # 3. Check Geofences
        geofences = []
        try:
            geofences = self.geospatial_service.check_geofences(latitude, longitude)
            for fence in geofences:
                if fence["inside"] and fence["type"] == "RESTRICTED":
                    hazards.append("Restricted Firing Zone Entry")
                    risk_score += 45.0
                elif fence["inside"] and fence["type"] == "ECOLOGICAL":
                    hazards.append("MPA Regulatory Zone")
                    risk_score += 5.0
                elif fence["status"] == "CRITICAL" and fence["type"] == "IMBL":
                    hazards.append("International Maritime Border Proximity")
                    risk_score += 25.0
        except Exception as e:
            self.logger.warning(f"Risk Agent failed checking geofences: {e}")

        # Clamp risk score
        risk_score = min(100.0, risk_score)
        
        # Classify overall risk level
        if risk_score >= 70.0:
            overall_level = "high"
        elif risk_score >= 35.0:
            overall_level = "medium"
        else:
            overall_level = "low"

        return {
            "agent": "risk_agent",
            "overall_risk_level": overall_level,
            "risk_score": round(risk_score, 1),
            "hazards": hazards,
            "weather_snapshot": {
                "wind_speed_kmh": weather_data.get("wind_speed_kmh"),
                "rainfall_mm": weather_data.get("rainfall_mm")
            },
            "marine_snapshot": {
                "wave_height_m": marine_data.get("wave_height_m"),
                "wave_period_s": marine_data.get("wave_period_s")
            },
            "geofence_violations": [g for g in geofences if g["inside"] or g["status"] in ["CRITICAL", "WARNING"]],
            "source": "ORCA Multi-feeder Risk Core",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "confidence": 0.92,
            "status": "LIVE"
        }

    def to_structured(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Standardize the Risk structured output format
        """
        if "error" in raw_data:
            return raw_data

        return {
            "agent": "risk_agent",
            "source": raw_data.get("source", "ORCA Risk Core"),
            "timestamp": raw_data.get("timestamp", datetime.utcnow().isoformat() + "Z"),
            "confidence": raw_data.get("confidence", 0.92),
            "status": raw_data.get("status", "LIVE"),
            "overall_risk_level": raw_data.get("overall_risk_level", "low"),
            "risk_score": raw_data.get("risk_score", 10.0),
            "hazards": raw_data.get("hazards", []),
            "geofence_violations": raw_data.get("geofence_violations", [])
        }
