"""
Risk engine for ORCA - applies deterministic thresholds to agent outputs
Converts structured agent data into risk flags based on configurable thresholds
"""
import yaml
import logging
from typing import Dict, Any, List, Optional
from enum import Enum
from pathlib import Path

logger = logging.getLogger(__name__)

class RiskLevel(str, Enum):
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    EXTREME = "extreme"

class RiskFlag:
    """Represents a single risk flag from applying a threshold"""
    def __init__(
        self,
        field: str,
        value: Any,
        risk_level: RiskLevel,
        threshold_exceeded: str,
        description: str
    ):
        self.field = field
        self.value = value
        self.risk_level = risk_level
        self.threshold_exceeded = threshold_exceeded  # e.g., "high", "extreme"
        self.description = description

    def to_dict(self) -> Dict[str, Any]:
        return {
            "field": self.field,
            "value": self.value,
            "risk_level": self.risk_level.value,
            "threshold_exceeded": self.threshold_exceeded,
            "description": self.description
        }

class RiskEngine:
    """
    Applies risk thresholds to structured agent outputs
    Loads thresholds from YAML configuration file
    """

    def __init__(self, thresholds_file: str = "app/rules/thresholds.yaml"):
        self.thresholds_file = Path(thresholds_file)
        self.thresholds = self._load_thresholds()
        logger.info(f"Loaded risk thresholds from {self.thresholds_file}")

    def _load_thresholds(self) -> Dict[str, Any]:
        """Load thresholds from YAML file"""
        try:
            with open(self.thresholds_file, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            logger.warning(f"Thresholds file not found: {self.thresholds_file}. Using empty thresholds.")
            return {}
        except yaml.YAMLError as e:
            logger.error(f"Error parsing thresholds YAML: {e}")
            return {}

    def _get_risk_level(self, value: Any, thresholds: Dict[str, Any]) -> RiskLevel:
        """
        Determine risk level based on value and thresholds
        Assumes thresholds are ordered: low, moderate, high, extreme
        """
        if not thresholds or not isinstance(value, (int, float)):
            return RiskLevel.LOW

        # Check thresholds in order of increasing severity
        if value >= thresholds.get("extreme", float('inf')):
            return RiskLevel.EXTREME
        elif value >= thresholds.get("high", float('inf')):
            return RiskLevel.HIGH
        elif value >= thresholds.get("moderate", float('inf')):
            return RiskLevel.MODERATE
        else:
            return RiskLevel.LOW

    def assess_weather_risk(self, weather_data: Dict[str, Any]) -> List[RiskFlag]:
        """Assess risk from weather agent data"""
        flags = []
        weather_thresholds = self.thresholds.get("weather", {})

        # Wind speed
        if "wind_speed_kmh" in weather_data:
            risk_level = self._get_risk_level(
                weather_data["wind_speed_kmh"],
                weather_thresholds.get("wind_speed", {})
            )
            if risk_level != RiskLevel.LOW:
                flags.append(RiskFlag(
                    field="wind_speed_kmh",
                    value=weather_data["wind_speed_kmh"],
                    risk_level=risk_level,
                    threshold_exceeded=risk_level.value,
                    description=f"Wind speed of {weather_data['wind_speed_kmh']} km/h poses {risk_level.value} risk"
                ))

        # Rainfall
        if "rainfall_mm" in weather_data:
            risk_level = self._get_risk_level(
                weather_data["rainfall_mm"],
                weather_thresholds.get("rainfall", {})
            )
            if risk_level != RiskLevel.LOW:
                flags.append(RiskFlag(
                    field="rainfall_mm",
                    value=weather_data["rainfall_mm"],
                    risk_level=risk_level,
                    threshold_exceeded=risk_level.value,
                    description=f"Rainfall of {weather_data['rainfall_mm']} mm/h poses {risk_level.value} risk"
                ))

        # Visibility (inverted - lower visibility = higher risk)
        if "visibility_km" in weather_data:
            # For visibility, we need to check if it's BELOW the threshold
            visibility = weather_data["visibility_km"]
            vis_thresholds = weather_thresholds.get("visibility", {})

            # Reverse the logic for visibility - lower values are riskier
            if visibility <= vis_thresholds.get("extreme", float('-inf')):
                risk_level = RiskLevel.EXTREME
            elif visibility <= vis_thresholds.get("high", float('-inf')):
                risk_level = RiskLevel.HIGH
            elif visibility <= vis_thresholds.get("moderate", float('-inf')):
                risk_level = RiskLevel.MODERATE
            else:
                risk_level = RiskLevel.LOW

            if risk_level != RiskLevel.LOW:
                flags.append(RiskFlag(
                    field="visibility_km",
                    value=weather_data["visibility_km"],
                    risk_level=risk_level,
                    threshold_exceeded=risk_level.value,
                    description=f"Visibility of {weather_data['visibility_km']} km poses {risk_level.value} risk"
                ))

        return flags

    def assess_sea_state_risk(self, sea_state_data: Dict[str, Any]) -> List[RiskFlag]:
        """Assess risk from sea-state agent data"""
        flags = []
        sea_state_thresholds = self.thresholds.get("sea_state", {})

        # Wave height
        if "wave_height_m" in sea_state_data:
            risk_level = self._get_risk_level(
                sea_state_data["wave_height_m"],
                sea_state_thresholds.get("wave_height", {})
            )
            if risk_level != RiskLevel.LOW:
                flags.append(RiskFlag(
                    field="wave_height_m",
                    value=sea_state_data["wave_height_m"],
                    risk_level=risk_level,
                    threshold_exceeded=risk_level.value,
                    description=f"Wave height of {sea_state_data['wave_height_m']} m poses {risk_level.value} risk"
                ))

        # Swell height
        if "swell_height_m" in sea_state_data:
            risk_level = self._get_risk_level(
                sea_state_data["swell_height_m"],
                sea_state_thresholds.get("swell_height", {})
            )
            if risk_level != RiskLevel.LOW:
                flags.append(RiskFlag(
                    field="swell_height_m",
                    value=sea_state_data["swell_height_m"],
                    risk_level=risk_level,
                    threshold_exceeded=risk_level.value,
                    description=f"Swell height of {sea_state_data['swell_height_m']} m poses {risk_level.value} risk"
                ))

        # Current speed
        if "current_speed_knots" in sea_state_data:
            risk_level = self._get_risk_level(
                sea_state_data["current_speed_knots"],
                sea_state_thresholds.get("current_speed", {})
            )
            if risk_level != RiskLevel.LOW:
                flags.append(RiskFlag(
                    field="current_speed_knots",
                    value=sea_state_data["current_speed_knots"],
                    risk_level=risk_level,
                    threshold_exceeded=risk_level.value,
                    description=f"Current speed of {sea_state_data['current_speed_knots']} knots poses {risk_level.value} risk"
                ))

        return flags

    def assess_hazard_risk(self, hazard_data: Dict[str, Any]) -> List[RiskFlag]:
        """Assess risk from hazard agent data"""
        flags = []
        hazard_thresholds = self.thresholds.get("hazard", {})

        # Cyclone wind speed
        if "cyclone_wind_speed_kmh" in hazard_data:
            risk_level = self._get_risk_level(
                hazard_data["cyclone_wind_speed_kmh"],
                hazard_thresholds.get("cyclone_wind_speed", {})
            )
            if risk_level != RiskLevel.LOW:
                flags.append(RiskFlag(
                    field="cyclone_wind_speed_kmh",
                    value=hazard_data["cyclone_wind_speed_kmh"],
                    risk_level=risk_level,
                    threshold_exceeded=risk_level.value,
                    description=f"Cyclone wind speed of {hazard_data['cyclone_wind_speed_kmh']} km/h poses {risk_level.value} risk"
                ))

        # Lightning probability
        if "lightning_probability_percent" in hazard_data:
            risk_level = self._get_risk_level(
                hazard_data["lightning_probability_percent"],
                hazard_thresholds.get("lightning_probability", {})
            )
            if risk_level != RiskLevel.LOW:
                flags.append(RiskFlag(
                    field="lightning_probability_percent",
                    value=hazard_data["lightning_probability_percent"],
                    risk_level=risk_level,
                    threshold_exceeded=risk_level.value,
                    description=f"Lightning probability of {hazard_data['lightning_probability_percent']}% poses {risk_level.value} risk"
                ))

        # Tsunami wave height
        if "tsunami_wave_height_m" in hazard_data:
            risk_level = self._get_risk_level(
                hazard_data["tsunami_wave_height_m"],
                hazard_thresholds.get("tsunami_wave_height", {})
            )
            if risk_level != RiskLevel.LOW:
                flags.append(RiskFlag(
                    field="tsunami_wave_height_m",
                    value=hazard_data["tsunami_wave_height_m"],
                    risk_level=risk_level,
                    threshold_exceeded=risk_level.value,
                    description=f"Tsunami wave height of {hazard_data['tsunami_wave_height_m']} m poses {risk_level.value} risk"
                ))

        return flags

    def assess_pfz_satellite_risk(self, pfz_data: Dict[str, Any]) -> List[RiskFlag]:
        """Assess risk/opportunity from PFZ/satellite agent data"""
        flags = []
        pfz_thresholds = self.thresholds.get("pfz_satellite", {})

        # SST (optimal range is moderate, extremes are less ideal)
        if "sst_c" in pfz_data:
            sst = pfz_data["sst_c"]
            sst_thresholds = pfz_thresholds.get("sst", {})

            # For SST, we'll flag both too low and too high as moderate risk
            if sst <= sst_thresholds.get("low", float('-inf')) or sst >= sst_thresholds.get("extreme", float('inf')):
                risk_level = RiskLevel.MODERATE
            elif sst < sst_thresholds.get("moderate", float('-inf')) or sst > sst_thresholds.get("high", float('inf')):
                risk_level = RiskLevel.LOW  # Still acceptable but not optimal
            else:
                risk_level = RiskLevel.LOW  # Optimal range

            if risk_level != RiskLevel.LOW:
                flags.append(RiskFlag(
                    field="sst_c",
                    value=pfz_data["sst_c"],
                    risk_level=risk_level,
                    threshold_exceeded=risk_level.value,
                    description=f"Sea surface temperature of {pfz_data['sst_c']}°C poses {risk_level.value} risk for fishing comfort"
                ))

        # Chlorophyll-a (higher is generally better for fishing up to a point)
        if "chlorophyll_a_mgm3" in pfz_data:
            chla = pfz_data["chlorophyll_a_mgm3"]
            chla_thresholds = pfz_thresholds.get("chlorophyll_a", {})

            risk_level = self._get_risk_level(
                chla,
                chla_thresholds
            )
            # For chlorophyll-a, low values are risky (poor fishing), high values are good
            if risk_level == RiskLevel.LOW and chla < chla_thresholds.get("moderate", 0):
                risk_level = RiskLevel.MODERATE  # Too low chlorophyll is bad for fishing

            if risk_level != RiskLevel.LOW:
                flags.append(RiskFlag(
                    field="chlorophyll_a_mgm3",
                    value=pfz_data["chlorophyll_a_mgm3"],
                    risk_level=risk_level,
                    threshold_exceeded=risk_level.value,
                    description=f"Chlorophyll-a concentration of {pfz_data['chlorophyll_a_mgm3']} mg/m³ poses {risk_level.value} risk for fishing productivity"
                ))

        # PFZ confidence (lower confidence = higher risk)
        if "pfz_confidence_percent" in pfz_data:
            confidence = pfz_data["pfz_confidence_percent"]
            conf_thresholds = pfz_thresholds.get("pfz_confidence", {})

            # Reverse logic - lower confidence is riskier
            if confidence <= conf_thresholds.get("extreme", float('-inf')):
                risk_level = RiskLevel.EXTREME
            elif confidence <= conf_thresholds.get("high", float('-inf')):
                risk_level = RiskLevel.HIGH
            elif confidence <= conf_thresholds.get("moderate", float('-inf')):
                risk_level = RiskLevel.MODERATE
            else:
                risk_level = RiskLevel.LOW

            if risk_level != RiskLevel.LOW:
                flags.append(RiskFlag(
                    field="pfz_confidence_percent",
                    value=pfz_data["pfz_confidence_percent"],
                    risk_level=risk_level,
                    threshold_exceeded=risk_level.value,
                    description=f"PFZ confidence of {pfz_data['pfz_confidence_percent']}% poses {risk_level.value} risk due to low certainty"
                ))

        return flags

    def assess_all_risks(
        self,
        weather_data: Optional[Dict[str, Any]] = None,
        sea_state_data: Optional[Dict[str, Any]] = None,
        hazard_data: Optional[Dict[str, Any]] = None,
        pfz_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Assess risks from all available agent data

        Returns:
            Dictionary with keys for each agent type and values as lists of risk flags
        """
        results = {}

        if weather_data:
            results["weather"] = [flag.to_dict() for flag in self.assess_weather_risk(weather_data)]

        if sea_state_data:
            results["sea_state"] = [flag.to_dict() for flag in self.assess_sea_state_risk(sea_state_data)]

        if hazard_data:
            results["hazard"] = [flag.to_dict() for flag in self.assess_hazard_risk(hazard_data)]

        if pfz_data:
            results["pfz_satellite"] = [flag.to_dict() for flag in self.assess_pfz_satellite_risk(pfz_data)]

        return results

    def get_overall_risk_level(self, all_risks: Dict[str, List[Dict[str, Any]]]) -> RiskLevel:
        """
        Determine overall risk level from all risk flags
        Takes the highest risk level across all flags
        """
        max_risk = RiskLevel.LOW
        # Define risk level hierarchy for comparison
        risk_hierarchy = {
            RiskLevel.LOW: 0,
            RiskLevel.MODERATE: 1,
            RiskLevel.HIGH: 2,
            RiskLevel.EXTREME: 3
        }

        for agent_type, flags in all_risks.items():
            for flag in flags:
                flag_level = RiskLevel(flag["risk_level"])
                # Compare risk levels using hierarchy
                if risk_hierarchy[flag_level] > risk_hierarchy[max_risk]:
                    max_risk = flag_level

        return max_risk