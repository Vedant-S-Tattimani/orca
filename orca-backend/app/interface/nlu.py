"""
NLU (Natural Language Understanding) processing for ORCA
Parses raw user query text (+ optional geolocation coordinates) into StructuredQuery
"""
import re
import json
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List

from app.interface.schemas import StructuredQuery, Location, TimeWindow, TaskType
from app.synthesis.llm_client import LLMClient

logger = logging.getLogger(__name__)


# Preset Indian Port Coordinates database for robust geocoding fallback
INDIAN_OCEAN_PRESETS = {
    "kollam": {"name": "Kollam Coast", "lat": 8.8879, "lon": 76.5684},
    "quilon": {"name": "Kollam Coast", "lat": 8.8879, "lon": 76.5684},
    "kochi": {"name": "Kochi Port", "lat": 9.9637, "lon": 76.2711},
    "cochin": {"name": "Kochi Port", "lat": 9.9637, "lon": 76.2711},
    "vizhinjam": {"name": "Vizhinjam Harbour", "lat": 8.3812, "lon": 76.9905},
    "alappuzha": {"name": "Alappuzha Beach", "lat": 9.4981, "lon": 76.3315},
    "alleppey": {"name": "Alappuzha Beach", "lat": 9.4981, "lon": 76.3315},
    "karwar": {"name": "Karwar Coast", "lat": 14.8016, "lon": 74.1300},
    "mangalore": {"name": "New Mangalore Port", "lat": 12.9238, "lon": 74.8197},
    "mumbai": {"name": "Mumbai Port", "lat": 18.9438, "lon": 72.8588},
    "jnpt": {"name": "Nhava Sheva (JNPT)", "lat": 18.9502, "lon": 72.9519},
    "goa": {"name": "Mormugao (Goa)", "lat": 15.4124, "lon": 73.8078},
    "mormugao": {"name": "Mormugao (Goa)", "lat": 15.4124, "lon": 73.8078},
    "tuticorin": {"name": "Tuticorin (V.O.C.)", "lat": 8.7516, "lon": 78.1948},
    "chennai": {"name": "Chennai Port", "lat": 13.0906, "lon": 80.2989},
    "visakhapatnam": {"name": "Visakhapatnam Port", "lat": 17.6896, "lon": 83.2986},
    "vizag": {"name": "Visakhapatnam Port", "lat": 17.6896, "lon": 83.2986},
    "paradip": {"name": "Paradip Port", "lat": 20.2644, "lon": 86.6713},
    "kolkata": {"name": "Kolkata Port", "lat": 22.4821, "lon": 88.2913},
    "veraval": {"name": "Veraval Port", "lat": 20.9022, "lon": 70.3697},
    "kandla": {"name": "Kandla (Deendayal)", "lat": 23.0118, "lon": 70.2224},
    "porbandar": {"name": "Porbandar Port", "lat": 21.6422, "lon": 69.6093},
    "kakinada": {"name": "Kakinada Port", "lat": 16.9830, "lon": 82.2783}
}


class NLU:
    """
    Parses natural language requests into structured queries using LLM with fallback
    """

    def __init__(self):
        self.llm_client = LLMClient()

    async def parse_query(self, text: str, lat: Optional[float] = None, lon: Optional[float] = None, history: Optional[List[Dict[str, str]]] = None) -> StructuredQuery:
        """
        Parse raw user query text and coordinates into a StructuredQuery using LLM.
        Falls back to local keyword parsing if LLM is unavailable or fails.
        """
        logger.info(f"NLU processing query: '{text}' with lat={lat}, lon={lon}")
        
        # Try local fallback first for faster parsing (structured NLU)
        local_parsed = self._parse_with_fallback(text, lat, lon)
        
        # If local parsing found a specific task and location, or if coordinates were provided
        has_specific_task = local_parsed.task != TaskType.GENERAL_INQUIRY
        has_specific_loc = (lat is not None and lon is not None) or local_parsed.location.name != "Kollam Coast"
        
        if has_specific_task and has_specific_loc:
            logger.info("Local NLU parsing successful, bypassing LLM for latency.")
            local_parsed.confidence = 0.9  # Boost confidence since it matched specific rules
            return local_parsed

        # Fallback to LLM if local parsing is too vague
        try:
            structured_data = await self._parse_with_llm(text, lat, lon)
            if structured_data:
                return structured_data
        except Exception as e:
            logger.warning(f"LLM NLU parsing failed: {e}")

        return local_parsed

    async def _parse_with_llm(self, text: str, lat: Optional[float] = None, lon: Optional[float] = None) -> Optional[StructuredQuery]:
        """
        Use LLM to perform named entity recognition, intent classification, and time parsing.
        """
        # If API key is not configured, skip to avoid slow failures
        if not await self.llm_client.is_available():
            return None

        prompt = f"""
Analyze the following marine/maritime query and extract key parameters. 
Your output MUST be a single, valid JSON object with EXACTLY the keys shown in the schema below. Do not include markdown code block markers or extra explanation text.

--- SCHEMA ---
{{
  "task": "safety_check" | "fishing_zones" | "route_planning" | "hazard_alert" | "weather_info" | "general_inquiry",
  "location_name": "extracted location name, or 'Unknown'",
  "latitude": float or null,
  "longitude": float or null,
  "time_window": {{
    "start_iso": "ISO-8601 string for start time",
    "end_iso": "ISO-8601 string for end time"
  }},
  "language": "en" | "hi" | "kn" | "mr" | "ta" | "te" | "ml" | "gu" | "bn" | "other"
}}

--- CURRENT TIMELINE (UTC) ---
Current Time: {datetime.utcnow().isoformat()}Z

--- RULES ---
1. Classify "task" based on user intent:
   - "safety_check": asking if it's safe to travel, navigate, fish, or sail.
   - "fishing_zones": asking where to fish, looking for potential fishing zones (PFZ), or chlorophyll/SST hotspots.
   - "route_planning": asking for optimized routes, paths, navigation checkpoints.
   - "hazard_alert": asking about cyclones, lightning, tsunamis, storms, warnings.
   - "weather_info": asking generally about rain, temperature, wind, cloud cover.
   - "general_inquiry": default fallback.
2. For location coordinates: If latitude/longitude are not provided in user metadata, try to geocode the location if it is a major Indian port/coast. (e.g. Mumbai [18.9438, 72.8588], Karwar [14.8016, 74.13], Chennai [13.0906, 80.2989], Kollam [8.8879, 76.5684], Kochi [9.9637, 76.2711], Vizhinjam [8.3812, 76.9905]).
3. Identify language: Detect if the input is written in Hindi (hi), Kannada (kn), Marathi (mr), Tamil (ta), Telugu (te), Malayalam (ml), English (en), etc.

Query: "{text}"
User Latitude Metadata: {lat if lat is not None else 'null'}
User Longitude Metadata: {lon if lon is not None else 'null'}

Output JSON:
"""
        response_text = await self.llm_client.generate_response(prompt)
        
        # Clean up JSON formatting helpers
        clean_json_str = response_text.strip()
        if clean_json_str.startswith("```json"):
            clean_json_str = clean_json_str[7:]
        if clean_json_str.endswith("```"):
            clean_json_str = clean_json_str[:-3]
        clean_json_str = clean_json_str.strip()

        try:
            parsed = json.loads(clean_json_str)
            
            # Map task string to enum
            task_str = parsed.get("task", "general_inquiry")
            try:
                task = TaskType(task_str)
            except ValueError:
                task = TaskType.GENERAL_INQUIRY

            # Extracted or metadata coordinates
            final_lat = lat if lat is not None else parsed.get("latitude")
            final_lon = lon if lon is not None else parsed.get("longitude")
            
            # If coordinates are still null, double check presets
            loc_name_lower = parsed.get("location_name", "").lower()
            if final_lat is None or final_lon is None:
                for k, preset in INDIAN_OCEAN_PRESETS.items():
                    if k in loc_name_lower:
                        final_lat = preset["lat"]
                        final_lon = preset["lon"]
                        break

            # Defaults if completely missing
            if final_lat is None or final_lon is None:
                final_lat = None
                final_lon = None

            location = Location(
                name=parsed.get("location_name", "Unknown"),
                lat=final_lat,
                lon=final_lon,
                radius_km=10.0
            )

            # Parse times safely
            try:
                start = datetime.fromisoformat(parsed["time_window"]["start_iso"].replace("Z", "+00:00"))
                end = datetime.fromisoformat(parsed["time_window"]["end_iso"].replace("Z", "+00:00"))
            except Exception:
                # Fallback to current / tomorrow
                start = datetime.utcnow()
                end = start + timedelta(days=1)

            time_window = TimeWindow(start=start.replace(tzinfo=None), end=end.replace(tzinfo=None))

            return StructuredQuery(
                task=task,
                location=location,
                time_window=time_window,
                confidence=0.95,
                original_query=text,
                language=parsed.get("language", "en")
            )
        except Exception as e:
            logger.error(f"Error parsing LLM response '{clean_json_str}': {e}")
            return None

    def _parse_with_fallback(self, text: str, lat: Optional[float] = None, lon: Optional[float] = None) -> StructuredQuery:
        """Keyword and regex-based NLU fallback"""
        text_lower = text.lower()

        # Regional script transliteration helpers for geocoding
        regional_mappings = {
            # Devanagari (Hindi/Marathi)
            "कांडला": "kandla",
            "मुंबई": "mumbai",
            "कोच्चि": "kochi",
            "कोचीन": "kochi",
            "कोल्लम": "kollam",
            "चेन्नई": "chennai",
            "करवार": "karwar",
            "मंगलोर": "mangalore",
            "विशाखापत्तनम": "visakhapatnam",
            "पोरबंदर": "porbandar",
            "वेरावल": "veraval",
            "काकीनाडा": "kakinada",
            "गोवा": "goa",
            "पारादीप": "paradip",
            "कोलकाता": "kolkata",
            # Kannada
            "ಮಂಗಳೂರು": "mangalore",
            "ಕಾರವಾರ": "karwar",
            "ಕೊಚ್ಚಿ": "kochi",
            "ಮುಂಬೈ": "mumbai",
            "ಚೆನ್ನೈ": "chennai",
            "ಕೊಲ್ಕತ್ತಾ": "kolkata",
            # Tamil
            "சென்னை": "chennai",
            "மும்பை": "mumbai",
            "கொச்சி": "kochi",
            "கொல்லம்": "kollam",
            # Telugu
            "విశాఖపట్నం": "visakhapatnam",
            "చెన్నై": "chennai",
            # Malayalam
            "കൊച്ചി": "kochi",
            "കൊല്ലം": "kollam"
        }
        for reg_key, eng_val in regional_mappings.items():
            if reg_key in text_lower:
                text_lower += f" {eng_val}"

        # 1. Intent Classification
        if any(w in text_lower for w in ["safe", "safety", "danger", "warning", "surakshit", "khatra", "सुरक्षित"]):
            task = TaskType.SAFETY_CHECK
        elif any(w in text_lower for w in ["fish", "pfz", "catch", "productivity", "machli", "meenu", "ಮೀನು"]):
            task = TaskType.FISHING_ZONES
        elif any(w in text_lower for w in ["route", "path", "navigation", "steer", "rasta", "ಮಾರ್ಗ"]):
            task = TaskType.ROUTE_PLANNING
        elif any(w in text_lower for w in ["hazard", "cyclone", "tsunami", "alert", "toofan", "tufan", "ಆಪತ್ತು"]):
            task = TaskType.HAZARD_ALERT
        elif any(w in text_lower for w in ["weather", "rain", "wind", "cloud", "mausam", "barish", "ಮಳೆ"]):
            task = TaskType.WEATHER_INFO
        else:
            task = TaskType.GENERAL_INQUIRY

        # 2. Location Geocoding
        location_name = "Unknown"
        resolved_lat = 0.0
        resolved_lon = 0.0

        if lat is not None and lon is not None:
            resolved_lat = lat
            resolved_lon = lon
            location_name = f"Custom Location ({lat:.4f}, {lon:.4f})"
            # Check proximity to presets
            for key, preset in INDIAN_OCEAN_PRESETS.items():
                if abs(lat - preset["lat"]) < 0.05 and abs(lon - preset["lon"]) < 0.05:
                    location_name = preset["name"]
                    break
        else:
            # Geocode based on text keywords
            for key, preset in INDIAN_OCEAN_PRESETS.items():
                if key in text_lower:
                    location_name = preset["name"]
                    resolved_lat = preset["lat"]
                    resolved_lon = preset["lon"]
                    break

        location = Location(
            name=location_name,
            lat=resolved_lat if resolved_lat != 0.0 else None,
            lon=resolved_lon if resolved_lon != 0.0 else None,
            radius_km=10.0
        )

        # 3. Time Window
        start = datetime.utcnow()
        end = start + timedelta(days=1)

        if "tomorrow" in text_lower or "naale" in text_lower or "kal" in text_lower or "ನಾಳೆ" in text_lower or "ನಾಳೆಯ" in text_lower:
            start = datetime.utcnow() + timedelta(days=1)
            if "morning" in text_lower or "subah" in text_lower or "belage" in text_lower or "ಬೆಳಿಗ್ಗೆ" in text_lower:
                start = start.replace(hour=5, minute=0, second=0, microsecond=0)
                end = start.replace(hour=12, minute=0, second=0, microsecond=0)
            else:
                end = start + timedelta(days=1)
        elif "tonight" in text_lower or "aaj raat" in text_lower:
            start = datetime.utcnow().replace(hour=18, minute=0, second=0, microsecond=0)
            end = start + timedelta(hours=12)

        time_window = TimeWindow(start=start, end=end)

        # 4. Multilingual Check
        # Detect regional languages by script / characters
        language = "en"
        # Malayalam
        if any(ord(c) >= 0x0D00 and ord(c) <= 0x0D7F for c in text):
            language = "ml"
        # Devanagari (Hindi/Marathi)
        elif any(ord(c) >= 0x0900 and ord(c) <= 0x097F for c in text):
            language = "hi"
        # Kannada
        elif any(ord(c) >= 0x0C80 and ord(c) <= 0x0CFF for c in text):
            language = "kn"
        # Tamil
        elif any(ord(c) >= 0x0B80 and ord(c) <= 0x0BFF for c in text):
            language = "ta"
        # Telugu
        elif any(ord(c) >= 0x0C00 and ord(c) <= 0x0C7F for c in text):
            language = "te"

        return StructuredQuery(
            task=task,
            location=location,
            time_window=time_window,
            confidence=0.7,
            original_query=text,
            language=language
        )
