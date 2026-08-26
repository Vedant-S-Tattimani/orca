"""
Orchestrator merger for ORCA
Combines and structures outputs from multiple specialist agents before synthesis
"""
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class Merger:
    """
    Merges outputs from multiple specialist agents into a coherent structure
    for the synthesis layer to process
    """

    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.Merger")

    def merge_agent_outputs(
        self,
        agent_outputs: Dict[str, Dict[str, Any]],
        query_location: Dict[str, Any],
        query_time_window: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Merge outputs from multiple agents into a unified structure

        Args:
            agent_outputs: Dictionary mapping agent names to their structured outputs
            query_location: Location information from the original query
            query_time_window: Time window information from the original query

        Returns:
            Merged data structure ready for synthesis
        """
        self.logger.info(f"Merging outputs from {len(agent_outputs)} agents")

        # Initialize the merged structure
        merged = {
            "query_metadata": {
                "location": query_location,
                "time_window": query_time_window,
                "merged_at": datetime.utcnow().isoformat()
            },
            "agent_data": {},
            "combined_insights": {},
            "data_quality": {
                "agents_responding": len([k for k, v in agent_outputs.items() if "error" not in v]),
                "total_agents": len(agent_outputs),
                "has_errors": any("error" in v for v in agent_outputs.values())
            }
        }

        # Process each agent's output
        for agent_name, output in agent_outputs.items():
            self.logger.debug(f"Processing output from {agent_name}")

            # Store the raw agent output
            merged["agent_data"][agent_name] = output

            # Extract key insights for quick access
            if "error" not in output:
                insights = self._extract_key_insights(agent_name, output)
                merged["combined_insights"][agent_name] = insights
            else:
                merged["combined_insights"][agent_name] = {
                    "error": output["error"],
                    "status": "failed"
                }

        # Add any cross-agent correlations or patterns
        merged["combined_insights"]["correlations"] = self._find_correlations(agent_outputs)

        self.logger.info(f"Merge complete. {merged['data_quality']['agents_responding']}/{merged['data_quality']['total_agents']} agents responding")
        return merged

    def _extract_key_insights(self, agent_name: str, agent_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract key insights from agent data for easier consumption by synthesis
        """
        insights = {
            "agent": agent_name,
            "status": "success",
            "source": agent_data.get("source", "unknown"),
            "timestamp": agent_data.get("timestamp", datetime.utcnow().isoformat()),
            "confidence": agent_data.get("confidence", 0.0)
        }

        # Agent-specific insight extraction
        if agent_name in ["weather", "openmeteo_weather"]:
            insights.update({
                "wind_speed_kmh": agent_data.get("wind_speed_kmh"),
                "rainfall_mm": agent_data.get("rainfall_mm"),
                "visibility_km": agent_data.get("visibility_km"),
                "temperature_c": agent_data.get("temperature_c"),
                "primary_concern": self._get_weather_concern(agent_data)
            })
        elif agent_name in ["sea_state", "openmeteo_marine"]:
            insights.update({
                "wave_height_m": agent_data.get("wave_height_m"),
                "swell_height_m": agent_data.get("swell_height_m"),
                "current_speed_knots": agent_data.get("current_speed_knots"),
                "tide_height_m": agent_data.get("tide_height_m"),
                "primary_concern": self._get_sea_state_concern(agent_data)
            })
        elif agent_name == "hazard":
            insights.update({
                "cyclone_wind_speed_kmh": agent_data.get("cyclone_wind_speed_kmh"),
                "lightning_probability_percent": agent_data.get("lightning_probability_percent"),
                "tsunami_wave_height_m": agent_data.get("tsunami_wave_height_m"),
                "active_warnings": agent_data.get("active_warnings", []),
                "primary_concern": self._get_hazard_concern(agent_data)
            })
        elif agent_name == "pfz_satellite":
            insights.update({
                "sst_c": agent_data.get("sst_c"),
                "chlorophyll_a_mgm3": agent_data.get("chlorophyll_a_mgm3"),
                "pfz_confidence_percent": agent_data.get("pfz_confidence_percent"),
                "pfz_recommendation": agent_data.get("pfz_recommendation", "unknown"),
                "primary_concern": self._get_pfz_concern(agent_data)
            })
        elif agent_name == "gis_agent":
            insights.update({
                "active_violations_count": agent_data.get("active_violations_count", 0),
                "critical_warnings_count": agent_data.get("critical_warnings_count", 0),
                "primary_concern": "Restricted zone crossing" if agent_data.get("active_violations_count", 0) > 0 else "clear"
            })
        elif agent_name == "ais_agent":
            insights.update({
                "nearby_count": agent_data.get("nearby_count", 0),
                "primary_concern": "High vessel density" if agent_data.get("nearby_count", 0) > 3 else "normal"
            })
        elif agent_name == "risk_agent":
            insights.update({
                "overall_risk_level": agent_data.get("overall_risk_level", "low"),
                "risk_score": agent_data.get("risk_score", 10.0),
                "hazards": agent_data.get("hazards", []),
                "primary_concern": ", ".join(agent_data.get("hazards", [])) if agent_data.get("hazards") else "low threat"
            })
        elif agent_name == "routing_agent":
            insights.update({
                "route_type": agent_data.get("route_type"),
                "distance_nm": agent_data.get("distance_nm"),
                "duration_hours": agent_data.get("duration_hours"),
                "primary_concern": "route optimized"
            })

        return insights

    def _get_weather_concern(self, weather_data: Dict[str, Any]) -> str:
        """Determine primary weather concern"""
        concerns = []
        if weather_data.get("wind_speed_kmh", 0) > 40:
            concerns.append("high wind")
        if weather_data.get("rainfall_mm", 0) > 7.5:
            concerns.append("heavy rainfall")
        if weather_data.get("visibility_km", 20) < 5:
            concerns.append("poor visibility")
        return ", ".join(concerns) if concerns else "normal"

    def _get_sea_state_concern(self, sea_state_data: Dict[str, Any]) -> str:
        """Determine primary sea state concern"""
        concerns = []
        if sea_state_data.get("wave_height_m", 0) > 2.5:
            concerns.append("high waves")
        if sea_state_data.get("swell_height_m", 0) > 2:
            concerns.append("high swell")
        if sea_state_data.get("current_speed_knots", 0) > 2:
            concerns.append("strong currents")
        return ", ".join(concerns) if concerns else "normal"

    def _get_hazard_concern(self, hazard_data: Dict[str, Any]) -> str:
        """Determine primary hazard concern"""
        concerns = []
        if hazard_data.get("cyclone_wind_speed_kmh", 0) > 118:
            concerns.append("cyclone")
        if hazard_data.get("lightning_probability_percent", 0) > 60:
            concerns.append("lightning")
        if hazard_data.get("tsunami_wave_height_m", 0) > 1:
            concerns.append("tsunami")
        active_warnings = hazard_data.get("active_warnings", [])
        if active_warnings:
            concerns.append(f"active warnings: {', '.join(active_warnings)}")
        return ", ".join(concerns) if concerns else "normal"

    def _get_pfz_concern(self, pfz_data: Dict[str, Any]) -> str:
        """Determine primary PFZ/satellite concern"""
        concerns = []
        sst = pfz_data.get("sst_c", 27)
        if sst < 24 or sst > 32:
            concerns.append("extreme SST")
        chla = pfz_data.get("chlorophyll_a_mgm3", 1)
        if chla < 0.5:
            concerns.append("low chlorophyll")
        confidence = pfz_data.get("pfz_confidence_percent", 80)
        if confidence < 70:
            concerns.append("low PFZ confidence")
        return ", ".join(concerns) if concerns else "favorable"

    def _find_correlations(self, agent_outputs: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Find correlations or patterns across different agent outputs
        This could be expanded with more sophisticated analysis
        """
        correlations = {
            "weather_sea_state_link": None,
            "hazard_weather_link": None,
            "data_consistency": "unknown"
        }

        # Example: Check if high wind correlates with rough sea state
        weather_data = agent_outputs.get("weather", {})
        if not weather_data or "error" in weather_data:
            weather_data = agent_outputs.get("openmeteo_weather", {})

        sea_state_data = agent_outputs.get("sea_state", {})
        if not sea_state_data or "error" in sea_state_data:
            sea_state_data = agent_outputs.get("openmeteo_marine", {})

        if weather_data and "error" not in weather_data and sea_state_data and "error" not in sea_state_data:
            wind_speed = weather_data.get("wind_speed_kmh", 0)
            wave_height = sea_state_data.get("wave_height_m", 0)

            # Simple correlation: high wind (>30 km/h) often means rough seas (>2m waves)
            if wind_speed > 30 and wave_height > 2:
                correlations["weather_sea_state_link"] = "High wind likely contributing to rough sea state"
            elif wind_speed > 30 and wave_height <= 1:
                correlations["weather_sea_state_link"] = "High wind but calm seas - possible offshore wind"

        return correlations

# Example usage:
# merger = Merger()
# agent_outputs = {
#     "weather": {"wind_speed_kmh": 15, "rainfall_mm": 0, "source": "IMD", "confidence": 0.9},
#     "sea_state": {"wave_height_m": 1.8, "swell_height_m": 1.2, "source": "INCOIS", "confidence": 0.85}
# }
# query_location = {"latitude": 8.8932, "longitude": 76.6141, "name": "Kollam coast"}
# query_time_window = {"start": "2026-08-25T05:00:00Z", "end": "2026-08-25T10:00:00Z"}
# merged = merger.merge_agent_outputs(agent_outputs, query_location, query_time_window)