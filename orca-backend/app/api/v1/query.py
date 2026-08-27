"""
Query processing API endpoints for ORCA Backend
Handles POST requests for marine ecosystem queries and GET requests for results and agent status
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks, Request
from typing import Dict, Any, List, Optional
import uuid
from datetime import datetime
from pydantic import BaseModel
import logging
import asyncio
import time

from app.interface.schemas import (
    StructuredQuery, Location, TimeWindow, TaskType,
    AgentStatus, EvidenceItem, RiskCard
)
from app.interface.nlu import NLU
from app.orchestrator.planner import Planner
from app.orchestrator.merger import Merger
from app.orchestrator.location_resolver import LocationResolver
from app.synthesis.synthesis_agent import SynthesisAgent
from app.response.card_builder import CardBuilder
from app.config import settings

logger = logging.getLogger(__name__)

# Legacy router for backward compatibility
router = APIRouter(prefix="/api/v1/query", tags=["query"])

# New router for top-level /api endpoints matching contract
api_router = APIRouter(prefix="/api", tags=["orca_api"])

# In-memory store for query results
# Storing query results mapped by query_id
query_results: Dict[str, RiskCard] = {}


# In-memory store for conversation history mapped by session_id
conversation_history: Dict[str, List[Dict[str, str]]] = {}

class QueryPostInput(BaseModel):
    """Input payload for submitting a raw query"""
    text: str
    lat: Optional[float] = None
    lon: Optional[float] = None
    session_id: Optional[str] = None
    lang: Optional[str] = None


@api_router.post("/query")
async def submit_api_query(request: Request, input_data: QueryPostInput, background_tasks: BackgroundTasks):
    """
    POST /api/query
    Input: raw user text (+ optional lat/lon if browser geolocation is available)
    Output: { query_id: str, status: "processing" }
    """
    try:
        # Generate unique query ID
        query_id = str(uuid.uuid4())
        session_id = input_data.session_id or "default"
        demo_failure = request.headers.get("Failure-Demo") == "true"

        # Retrieve history
        if session_id not in conversation_history:
            conversation_history[session_id] = []
        
        history = conversation_history[session_id]

        # 1. Parse raw query text into StructuredQuery using NLU
        t0 = time.time()
        logger.info("Processing query via NLU...")
        nlu_processor = NLU()
        structured_query = await nlu_processor.parse_query(
            text=input_data.text,
            lat=input_data.lat,
            lon=input_data.lon,
            history=history
        )
        if input_data.lang:
            structured_query.language = input_data.lang
        t_nlu = time.time()
        logger.info(f"NLU processing complete in {t_nlu - t0:.2f}s.")

        # Append the new user query to history
        conversation_history[session_id].append({"role": "user", "content": input_data.text})

        # 2. Store initial query status (RiskCard loading skeleton)
        query_results[query_id] = RiskCard(
            risk_level="low",
            reasoning="ORCA is parsing coordinates and loading environmental sensors...",
            recommendation="Preparing advisory briefing, please wait...",
            evidence=[],
            agent_status=[],
            status="processing",
            dev_logs=["NLU: Starting natural language query parsing..."]
        )

        # 3. Process query in background
        background_tasks.add_task(
            process_query_background,
            query_id,
            structured_query,
            session_id,
            t_nlu,
            demo_failure
        )

        return {
            "query_id": query_id,
            "status": "processing"
        }

    except Exception as e:
        logger.error(f"Error submitting query: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to submit query: {str(e)}")


@api_router.get("/result/{query_id}", response_model=RiskCard)
async def get_api_result(query_id: str):
    """
    GET /api/result/{query_id}
    Output: RiskCard (poll until status = "done"; return partial/loading state otherwise)
    """
    if query_id not in query_results:
        raise HTTPException(status_code=404, detail="Query not found")
    
    return query_results[query_id]


@api_router.get("/agents/status", response_model=List[AgentStatus])
async def get_api_agents_status():
    """
    GET /api/agents/status
    Output: list[AgentStatus] - live health check of each specialist agent
    """
    from app.agents.weather_agent import WeatherAgent
    from app.agents.sea_state_agent import SeaStateAgent
    from app.agents.hazard_agent import HazardAgent
    from app.agents.pfz_agent import PFZAgent

    weather = WeatherAgent()
    sea_state = SeaStateAgent()
    hazard = HazardAgent()
    pfz = PFZAgent()

    results = await asyncio.gather(
        weather.check_health(),
        sea_state.check_health(),
        hazard.check_health(),
        pfz.check_health(),
        return_exceptions=True
    )

    statuses = []
    agent_names = ["weather", "sea_state", "hazard", "pfz_satellite"]

    for i, res in enumerate(results):
        if isinstance(res, Exception):
            statuses.append(AgentStatus(agent_name=agent_names[i], status="failed", note=f"Health check crashed: {str(res)}"))
        else:
            statuses.append(AgentStatus(agent_name=agent_names[i], status=res.get("status", "failed"), note=res.get("note", "Unknown state")))

    return statuses

@api_router.get("/ports")
async def get_ports():
    """GET /api/ports - Returns all registered ports"""
    from app.services.port_service import PortService
    return await PortService().get_all_ports()


@api_router.get("/vessels")
async def get_vessels():
    """GET /api/vessels - Returns simulated AIS vessel tracking feed"""
    from app.services.ais_service import AISService
    return await AISService().get_all_vessels()


@api_router.get("/alerts")
async def get_alerts():
    """GET /api/alerts - Returns active computed alerts across operating sectors"""
    from app.services.geospatial_service import GeospatialService
    geo_service = GeospatialService()
    
    # We can evaluate safety risks for a few key areas to populate active advisories
    # 1. Kandla area (cyclone warning)
    # 2. Lakshadweep area (restricted Navy zone warning)
    # 3. Sri Lanka border area (IMBL warning)
    
    lak_check = geo_service.check_geofences(11.2, 72.8) # Inside Lakshadweep restricted area
    sl_check = geo_service.check_geofences(9.4, 79.6) # Near Sri Lanka IMBL boundary
    
    active_alerts = []
    
    # Static cyclone alert placeholder (labeled as SIMULATED)
    active_alerts.append({
        "id": "alert-cyc-01",
        "title": "Cyclonic Depression Warning",
        "severity": "CRITICAL",
        "location": "Gulf of Kutch / Kandla",
        "time": datetime.utcnow().isoformat() + "Z",
        "hazard": "Gale winds up to 45 knots, wave swells > 4.0 meters",
        "recommended_action": "Vessels under 40ft should seek immediate harbor shelter. Secure moorings.",
        "provenance": "SIMULATED (IMD Satellite Alert Link)"
    })
    
    # Add restricted zone alert from geofence service
    for fence in lak_check:
        if fence["inside"] and fence["type"] == "RESTRICTED":
            active_alerts.append({
                "id": "alert-geo-02",
                "title": "Restricted Firing Zone Entry",
                "severity": "CRITICAL",
                "location": fence["geofence_name"],
                "time": datetime.utcnow().isoformat() + "Z",
                "hazard": "Naval live-fire exercises in progress",
                "recommended_action": fence["recommended_action"],
                "provenance": "SIMULATED (Coast Guard Geofencing Link)"
            })
            
    # Add IMBL alert
    for fence in sl_check:
        if fence["status"] == "CRITICAL" and fence["type"] == "IMBL":
            active_alerts.append({
                "id": "alert-geo-03",
                "title": "International Boundary Proximity Alert",
                "severity": "WARNING",
                "location": fence["geofence_name"],
                "time": datetime.utcnow().isoformat() + "Z",
                "hazard": f"Vessel is {fence['distance_km']} km from Sri Lanka boundary",
                "recommended_action": fence["recommended_action"],
                "provenance": "SIMULATED (Maritime Boundary Alert System)"
            })

    return active_alerts


class RouteRequest(BaseModel):
    origin_lat: float
    origin_lon: float
    dest_lat: float
    dest_lon: float
    vessel_speed_knots: float = 12.0
    vessel_draft_m: float = 4.0

@api_router.post("/route")
async def calculate_route(request: RouteRequest):
    """POST /api/route - Calculate a maritime route using A* graph (if available) or coastal fallback, and evaluate safety"""
    from app.services.routing_service import RoutingService
    from app.services.geospatial_service import GeospatialService
    
    rs = RoutingService()
    geo_service = GeospatialService()
    
    # In a full implementation, we would query the weather agent for these coordinates
    # For latency purposes, we will pass a placeholder environmental data block if not fetched
    env_data = {
        "wind_speed_kmh": 0,
        "wave_height_m": 0,
        "current_speed_knots": 0,
        "data_status": "UNAVAILABLE"
    }
    
    route_data = rs.calculate_route(
        origin_lat=request.origin_lat,
        origin_lon=request.origin_lon,
        dest_lat=request.dest_lat,
        dest_lon=request.dest_lon,
        vessel_speed_knots=request.vessel_speed_knots,
        vessel_draft_m=request.vessel_draft_m,
        env_data=env_data,
    )
    
    safety_eval = rs.evaluate_route_safety(
        route_data,
        {}, # Empty risk flags for now, but hazards logic works
        geo_service,
        env_data
    )
    
    return {
        "route_geometry": route_data,
        "route_safety": safety_eval
    }

class SectorRequest(BaseModel):
    name: str
    lat: float
    lon: float

class PFZRequest(BaseModel):
    sectors: Optional[List[SectorRequest]] = None

@api_router.post("/pfz")
async def get_pfz_data(request: PFZRequest):
    """POST /api/pfz - Fetch real PFZ + Weather data for multiple sectors"""
    from app.agents.pfz_agent import PFZAgent
    from app.agents.openmeteo_weather_agent import OpenMeteoWeatherAgent
    pfz_agent = PFZAgent()
    weather_agent = OpenMeteoWeatherAgent()
    
    start_time = datetime.utcnow()
    from datetime import timedelta
    end_time = start_time + timedelta(hours=24)
    
    # Wind thresholds from thresholds.yaml (km/h)
    WIND_THRESH_MODERATE = 20
    WIND_THRESH_HIGH = 40
    WIND_THRESH_EXTREME = 60
    
    req_sectors = request.sectors
    if not req_sectors:
        req_sectors = [
            SectorRequest(name="Mumbai-Offshore", lat=18.94, lon=72.85),
            SectorRequest(name="Ratnagiri-Coast", lat=16.98, lon=73.28),
            SectorRequest(name="Goa-Shelf", lat=15.40, lon=73.80),
            SectorRequest(name="Kochi-Zone", lat=9.96, lon=76.27),
            SectorRequest(name="Chennai-Coast", lat=13.09, lon=80.30),
            SectorRequest(name="Visakhapatnam-Bay", lat=17.69, lon=83.30),
            SectorRequest(name="Kollam-Shelf", lat=8.89, lon=76.61),
            SectorRequest(name="Mangalore-Coast", lat=12.87, lon=74.84)
        ]
        
    results = []
    for sector in req_sectors:
        try:
            # Fetch PFZ data and weather data in parallel for each sector
            import asyncio
            pfz_task = pfz_agent.fetch(sector.lat, sector.lon, start_time, end_time)
            weather_task = weather_agent.fetch(sector.lat, sector.lon, start_time, end_time)
            pfz_data, weather_data = await asyncio.gather(pfz_task, weather_task, return_exceptions=True)
            
            # Handle PFZ fetch errors
            if isinstance(pfz_data, Exception):
                logger.error(f"PFZ fetch error for {sector.name}: {pfz_data}")
                pfz_data = {}
            
            # Handle weather fetch errors
            if isinstance(weather_data, Exception):
                logger.warning(f"Weather fetch error for {sector.name}: {weather_data}")
                weather_data = {}
            
            # Map recommendation string to a suitability percentage for the UI
            rec = pfz_data.get("pfz_recommendation", "unknown").lower()
            if rec == "highly recommended":
                suitability = 90 + int(pfz_data.get("pfz_confidence_percent", 5))
            elif rec == "recommended":
                suitability = 75 + int(pfz_data.get("pfz_confidence_percent", 5) * 0.5)
            elif rec in ("excellent", "good"):
                suitability = 70 + int(pfz_data.get("pfz_confidence_percent", 5) * 0.3)
            elif rec == "marginal" or rec == "fair":
                suitability = 50
            else:
                suitability = 30
                
            # Clamp to 1-99%
            suitability = min(99, max(1, suitability))
            
            # Build structured wind object from weather data
            wind_speed_kmh = weather_data.get("wind_speed_kmh", 0.0)
            wind_gust_kmh = weather_data.get("wind_speed_max_kmh", 0.0)
            
            # --- Wind-based suitability penalty ---
            # Even if SST/chlorophyll are perfect, dangerous wind makes a zone unsuitable
            if wind_speed_kmh >= WIND_THRESH_EXTREME:
                suitability = min(suitability, 30)  # Cap at 30% for extreme wind
            elif wind_speed_kmh >= WIND_THRESH_HIGH:
                suitability = max(1, suitability - 25)  # Heavy penalty for high wind
            elif wind_speed_kmh >= WIND_THRESH_MODERATE:
                suitability = max(1, suitability - 10)  # Moderate penalty
            
            # Gust penalty (additional)
            if wind_gust_kmh >= WIND_THRESH_EXTREME:
                suitability = min(suitability, 25)
            elif wind_gust_kmh >= WIND_THRESH_HIGH:
                suitability = max(1, suitability - 10)
            
            # Re-clamp after penalties
            suitability = min(99, max(1, suitability))
            
            # Get color based on suitability (after wind penalties)
            if suitability >= 80:
                color = '#0057c0'
            elif suitability >= 65:
                color = '#10b981'
            elif suitability >= 40:
                color = '#f5a623'
            else:
                color = '#ee0000'
                
            wind_direction_deg = weather_data.get("wind_direction_deg", 0.0)
            weather_condition = weather_data.get("weather_condition", "Unknown")
            weather_status = weather_data.get("data_status", "SIMULATED")
            weather_source = weather_data.get("source", "Unknown")
            weather_timestamp = weather_data.get("timestamp", start_time.isoformat() + "Z")
            
            # Determine wind risk level from thresholds.yaml values
            if wind_speed_kmh >= WIND_THRESH_EXTREME:
                wind_risk = "EXTREME"
            elif wind_speed_kmh >= WIND_THRESH_HIGH:
                wind_risk = "HIGH"
            elif wind_speed_kmh >= WIND_THRESH_MODERATE:
                wind_risk = "MODERATE"
            else:
                wind_risk = "LOW"
            
            # Same for gusts
            if wind_gust_kmh >= WIND_THRESH_EXTREME:
                gust_risk = "EXTREME"
            elif wind_gust_kmh >= WIND_THRESH_HIGH:
                gust_risk = "HIGH"
            elif wind_gust_kmh >= WIND_THRESH_MODERATE:
                gust_risk = "MODERATE"
            else:
                gust_risk = "LOW"
            
            wind_obj = {
                "speed_kmh": round(wind_speed_kmh, 1),
                "direction_deg": round(wind_direction_deg, 1),
                "gust_kmh": round(wind_gust_kmh, 1),
                "risk": wind_risk,
                "gust_risk": gust_risk,
                "weather_condition": weather_condition,
                "source": weather_source,
                "data_status": weather_status,
                "timestamp": weather_timestamp
            }
            
            # Build rejection reasons and positive evidence
            rejection_reasons = []
            evidence = []
            
            sst_val = pfz_data.get("sst_c", 0)
            chla_val = pfz_data.get("chlorophyll_a_mgm3", 0)
            wind_ms_val = pfz_data.get("wind_speed_at_sea_ms", 0)
            
            if suitability < 80:
                if sst_val > 30 or sst_val < 24:
                    rejection_reasons.append("Sub-optimal sea surface temperature")
                if chla_val < 0.5:
                    rejection_reasons.append("Low biological productivity (Chlorophyll)")
                if wind_speed_kmh > 21.6:
                    rejection_reasons.append(f"High wind/wave risk ({wind_speed_kmh:.0f} km/h)")
            else:
                if 24 <= sst_val <= 30:
                    evidence.append(f"SST of {sst_val:.1f}°C is within optimal fishing range (24–30°C).")
                if 0.5 <= chla_val <= 3.0:
                    evidence.append(f"Chlorophyll-a of {chla_val:.2f} mg/m³ indicates good biological productivity.")
                if wind_speed_kmh <= 21.6 and gust_risk not in ("HIGH", "EXTREME"):
                    evidence.append(f"Wind speed of {wind_speed_kmh:.0f} km/h is within safe operating conditions.")
            
            # Add wind-specific warnings from weather data regardless of suitability
            if wind_risk == "EXTREME":
                rejection_reasons.append(f"UNSAFE: Extreme wind speed ({wind_speed_kmh:.0f} km/h)")
            elif wind_risk == "HIGH":
                rejection_reasons.append(f"HIGH WIND: {wind_speed_kmh:.0f} km/h — exercise caution")
            
            if gust_risk in ("HIGH", "EXTREME"):
                rejection_reasons.append(f"STRONG GUSTS: up to {wind_gust_kmh:.0f} km/h")
                
            results.append({
                "name": sector.name,
                "coords": [sector.lat, sector.lon],
                "suitability": suitability,
                "sst": sst_val,
                "chlorophyll": chla_val,
                "wind_speed": wind_ms_val,
                "wind": wind_obj,
                "wave_height": pfz_data.get("sea_surface_height_m", 0.0),
                "recommendation": pfz_data.get("pfz_recommendation", "unknown"),
                "color": color,
                "data_status": pfz_data.get("data_status", "SIMULATED"),
                "source": pfz_data.get("source", "Unknown"),
                "timestamp": pfz_data.get("timestamp", start_time.isoformat() + "Z"),
                "confidence": pfz_data.get("confidence", 0.0),
                "data_origin": pfz_data.get("data_origin", {}),
                "rejection_reasons": rejection_reasons,
                "evidence": evidence,
                "forecast_24h": weather_data.get("forecast_24h", [])
            })
        except Exception as e:
            logger.error(f"Error fetching PFZ for {sector.name}: {e}")
            results.append({
                "name": sector.name,
                "coords": [sector.lat, sector.lon],
                "suitability": 0,
                "sst": 0.0,
                "chlorophyll": 0.0,
                "wind_speed": 0.0,
                "wind": {
                    "speed_kmh": 0.0, "direction_deg": 0.0, "gust_kmh": 0.0,
                    "risk": "UNAVAILABLE", "gust_risk": "UNAVAILABLE",
                    "weather_condition": "Unknown", "source": "Error",
                    "data_status": "ERROR", "timestamp": start_time.isoformat() + "Z"
                },
                "wave_height": 0.0,
                "recommendation": "unavailable",
                "color": '#8f8f8f',
                "data_status": "ERROR",
                "source": "Error",
                "timestamp": start_time.isoformat() + "Z",
                "confidence": 0.0,
                "data_origin": {},
                "rejection_reasons": [str(e)]
            })
            
    return results


@api_router.get("/environmental-data")
@api_router.post("/environmental-data")
async def get_location_environmental_data(lat: float, lon: float):
    """
    GET/POST /api/environmental-data
    Fetch real live weather & marine environmental data for specified (lat, lon) coordinates
    using Open-Meteo Weather and Marine APIs.
    """
    from app.services.openmeteo_weather_client import OpenMeteoWeatherClient
    from app.services.openmeteo_marine_client import OpenMeteoMarineClient

    weather_client = OpenMeteoWeatherClient()
    marine_client = OpenMeteoMarineClient()

    weather_data = {}
    marine_data = {}

    try:
        weather_task = weather_client.get_weather_forecast(lat, lon, forecast_days=1)
        marine_task = marine_client.get_marine_forecast(lat, lon, forecast_days=1)

        weather_res, marine_res = await asyncio.gather(weather_task, marine_task, return_exceptions=True)

        if not isinstance(weather_res, Exception) and isinstance(weather_res, dict):
            weather_data = weather_res
        if not isinstance(marine_res, Exception) and isinstance(marine_res, dict):
            marine_data = marine_res
    except Exception as e:
        logger.error(f"Error fetching environmental data for ({lat}, {lon}): {e}")

    # Extract real indicator values or None if unavailable
    wind_speed_kmh = weather_data.get("wind_speed_kmh")
    wind_direction_deg = weather_data.get("wind_direction_deg")
    rainfall_mm = weather_data.get("rainfall_mm")
    weather_code = weather_data.get("weather_code")
    weather_condition = weather_data.get("weather_condition", "Unknown")

    wave_height_m = marine_data.get("wave_height_m")
    swell_wave_height_m = marine_data.get("swell_wave_height_m")
    ocean_current_speed_knots = marine_data.get("ocean_current_speed_knots")
    ocean_current_direction_deg = marine_data.get("ocean_current_direction_deg")
    sea_surface_temp_c = marine_data.get("sea_surface_temp_c")

    # Determine Lightning / Storm Risk based on real weather_code and precipitation
    storm_risk = "Low Risk"
    if weather_code in [95, 96, 99]:
        storm_risk = "High Risk (Thunderstorm)"
    elif weather_code in [80, 81, 82, 63, 65, 67]:
        storm_risk = "Moderate Risk (Heavy Rain)"
    elif weather_code in [51, 53, 55, 61]:
        storm_risk = "Low Risk (Light Rain)"
    elif weather_code is None:
        storm_risk = None

    # Calculate Fishing Safety Score deterministically
    fishing_safety = None
    if wind_speed_kmh is not None or wave_height_m is not None or weather_code is not None:
        score = 100
        if wind_speed_kmh is not None:
            if wind_speed_kmh > 55: score -= 50
            elif wind_speed_kmh > 37: score -= 30
            elif wind_speed_kmh > 22: score -= 15

        eff_wave = wave_height_m if wave_height_m is not None else swell_wave_height_m
        if eff_wave is not None:
            if eff_wave > 3.0: score -= 50
            elif eff_wave > 2.0: score -= 35
            elif eff_wave > 1.0: score -= 15

        if weather_code in [95, 96, 99]: score -= 45
        elif weather_code in [80, 81, 82, 63, 65]: score -= 25
        elif weather_code in [51, 53, 55, 61]: score -= 10

        if ocean_current_speed_knots is not None:
            if ocean_current_speed_knots > 2.5: score -= 25
            elif ocean_current_speed_knots > 1.0: score -= 10

        score = max(0, min(100, score))
        if score >= 80:
            status = "Safe for Fishing"
        elif score >= 50:
            status = "Caution Required"
        else:
            status = "Unsafe / High Risk"

        fishing_safety = {
            "score": score,
            "status": status
        }

    return {
        "latitude": lat,
        "longitude": lon,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "data": {
            "wind_speed_kmh": round(wind_speed_kmh, 1) if wind_speed_kmh is not None else None,
            "wind_speed_knots": round(wind_speed_kmh / 1.852, 1) if wind_speed_kmh is not None else None,
            "wind_direction_deg": round(wind_direction_deg, 1) if wind_direction_deg is not None else None,
            "wave_height_m": round(wave_height_m, 2) if wave_height_m is not None else None,
            "swell_wave_height_m": round(swell_wave_height_m, 2) if swell_wave_height_m is not None else None,
            "rainfall_mm": round(rainfall_mm, 2) if rainfall_mm is not None else None,
            "ocean_current_speed_knots": round(ocean_current_speed_knots, 2) if ocean_current_speed_knots is not None else None,
            "ocean_current_direction_deg": round(ocean_current_direction_deg, 1) if ocean_current_direction_deg is not None else None,
            "sea_surface_temp_c": round(sea_surface_temp_c, 1) if sea_surface_temp_c is not None else None,
            "weather_code": weather_code,
            "weather_condition": weather_condition,
            "storm_risk": storm_risk,
            "fishing_safety": fishing_safety
        },
        "source": "Open-Meteo Weather & Marine API"
    }



async def process_query_background(query_id: str, structured_query: StructuredQuery, session_id: str = "default", t_nlu: float = None, demo_failure: bool = False):
    if structured_query and (structured_query.location.lat is None or structured_query.location.lon is None):
        spatial_tasks = {TaskType.SAFETY_CHECK, TaskType.FISHING_ZONES, TaskType.ROUTE_PLANNING, TaskType.HAZARD_ALERT, TaskType.WEATHER_INFO}
        if structured_query.task in spatial_tasks:
            query_results[query_id].status = "done"
            query_results[query_id].risk_level = "low"
            query_results[query_id].reasoning = "I need a specific location to check weather and safety conditions. Please provide a coastal area, port, or city name."
            query_results[query_id].recommendation = "Try asking again with a location, e.g., 'What is the weather like in Kochi?'"
            return

    """
    Background pipeline task to process the query and synthesize the RiskCard
    """
    try:
        logger.info(f"Processing query {query_id} in background")

        # Initialize components
        location_resolver = LocationResolver()
        planner = Planner()
        merger = Merger()
        
        # Local progress log array
        logs = ["NLU: Extracted structured parameters, coordinates, and regional language tags."]
        query_results[query_id] = query_results[query_id].copy(update={"dev_logs": list(logs)})

        # Step 1: Resolve location (coordinates + radius)
        if structured_query.location.lat is not None and structured_query.location.lon is not None:
            location_info = {
                "latitude": structured_query.location.lat,
                "longitude": structured_query.location.lon,
                "radius_km": structured_query.location.radius_km or 10.0,
                "resolved_name": structured_query.location.name
            }
        else:
            location_info = location_resolver.resolve_with_radius(
                structured_query.location.name,
                structured_query.location.radius_km or 10.0
            )
        
        lat_str = f"{location_info['latitude']:.4f}" if location_info['latitude'] is not None else "None"
        lon_str = f"{location_info['longitude']:.4f}" if location_info['longitude'] is not None else "None"
        logs.append(f"Geocoding: Resolved location to '{location_info['resolved_name']}' ({lat_str}, {lon_str})")
        query_results[query_id] = query_results[query_id].copy(update={"dev_logs": list(logs)})

        # Step 2: Determine which agents to invoke
        agent_plan = planner.create_agent_plan(
            structured_query,
            location_info,
            {
                "start": structured_query.time_window.start,
                "end": structured_query.time_window.end
            }
        )
        logs.append(f"Planner: Created orchestration plan. Specialist agents to run: {agent_plan['agents']}")
        query_results[query_id] = query_results[query_id].copy(update={"dev_logs": list(logs)})
        if t_nlu:
            t_route = time.time()
            logger.info(f"Route generation complete in {t_route - t_nlu:.2f}s.")

        # Step 3: Invoke specialist agents in parallel
        logs.append("Planner: Dispatched parallel asynchronous agent queries...")
        query_results[query_id] = query_results[query_id].copy(update={"dev_logs": list(logs)})
        t_fetch_start = time.time()
        agent_results = await planner.invoke_agents(
            agent_plan["agents"],
            location_info["latitude"],
            location_info["longitude"],
            structured_query.time_window.start,
            structured_query.time_window.end,
            location_info.get("radius_km")
        )
        
        if demo_failure:
            if "weather" in agent_results:
                agent_results["weather"] = {"error": "Simulated Provider Failure: INCOIS Timeout"}
                logs.append("Agent Execution: weather invocation encountered simulated failure.")
        
        for agent_name in agent_plan["agents"]:
            ok = "error" not in agent_results.get(agent_name, {})
            status_lbl = "SUCCESS" if ok else "FAILED"
            logs.append(f"Agent Execution: {agent_name} invocation completed with status: {status_lbl}")
        query_results[query_id] = query_results[query_id].copy(update={"dev_logs": list(logs)})
        t_fetch = time.time()
        logger.info(f"Agent fetching complete in {t_fetch - t_fetch_start:.2f}s.")

        # Step 4: Merge agent results
        merged_data = merger.merge_agent_outputs(
            agent_results,
            {
                "latitude": location_info["latitude"],
                "longitude": location_info["longitude"],
                "name": structured_query.location.name
            },
            {
                "start": structured_query.time_window.start.isoformat(),
                "end": structured_query.time_window.end.isoformat()
            }
        )
        logs.append("Merger: Consolidated multiple telemetry feeds and geofencing structures.")
        query_results[query_id] = query_results[query_id].copy(update={"dev_logs": list(logs)})

        # Step 5: Get RAG evidence
        rag_evidence = planner.retrieve_evidence(
            structured_query,
            location_info,
            {
                "start": structured_query.time_window.start,
                "end": structured_query.time_window.end
            }
        )
        logs.append(f"KnowledgeRetrieval: Query matched {len(rag_evidence)} historical report(s) and safety guidelines.")
        query_results[query_id] = query_results[query_id].copy(update={"dev_logs": list(logs)})

        # Step 6: Assess deterministic rules thresholds
        from app.rules.risk_engine import RiskEngine
        risk_engine = RiskEngine()
        
        weather_data = agent_results.get("weather", {})
        if not weather_data or "error" in weather_data:
            weather_data = agent_results.get("openmeteo_weather", {})

        sea_state_data = agent_results.get("sea_state", {})
        if not sea_state_data or "error" in sea_state_data:
            sea_state_data = agent_results.get("openmeteo_marine", {})

        hazard_data = agent_results.get("hazard", {})
        pfz_data = agent_results.get("pfz_satellite", {})

        risk_flags = risk_engine.assess_all_risks(
            weather_data=weather_data if "error" not in weather_data else None,
            sea_state_data=sea_state_data if "error" not in sea_state_data else None,
            hazard_data=hazard_data if "error" not in hazard_data else None,
            pfz_data=pfz_data if "error" not in pfz_data else None
        )
        
        triggered_rules = []
        for category, flags in risk_flags.items():
            for f in flags:
                if f.get("risk_level") in ["moderate", "high", "extreme"]:
                    triggered_rules.append(f"{category.upper()}:{f.get('description', '')}")
        logs.append(f"RiskEngine: Checked safety parameters. Triggered flags: {triggered_rules if triggered_rules else 'None'}")
        query_results[query_id] = query_results[query_id].copy(update={"dev_logs": list(logs)})

        # Step 6.5: Route Safety Assessment
        if "routing_agent" in agent_results and "error" not in agent_results["routing_agent"]:
            from app.services.routing_service import RoutingService
            from app.services.geospatial_service import GeospatialService
            geo_service = GeospatialService()
            
            rs = RoutingService()
            safety_eval = rs.evaluate_route_safety(
                agent_results["routing_agent"],
                risk_flags,
                geo_service,
                sea_state_data
            )
            merged_data["route_safety_assessment"] = safety_eval
            logs.append(f"RoutingService: Assessed route safety - Status: {safety_eval['status']}")
            query_results[query_id] = query_results[query_id].copy(update={"dev_logs": list(logs)})

        t_merge = time.time()
        logger.info(f"Merging and Risk evaluation complete in {t_merge - t_fetch:.2f}s.")

        # Step 7: Synthesize response
        logs.append(f"SynthesisAgent: Collating claims and formatting LLM briefing card...")
        query_results[query_id] = query_results[query_id].copy(update={"dev_logs": list(logs)})
        
        logger.info("Starting synthesis...")
        t_synth_start = time.time()
        synthesis_agent = SynthesisAgent()
        card_builder = CardBuilder()
        
        synthesis_result = await synthesis_agent.synthesize_response(
            merged_agent_data=merged_data,
            risk_flags=risk_flags,
            rag_evidence=rag_evidence,
            original_query=structured_query.original_query,
            query_language=structured_query.language,
            history=conversation_history.get(session_id, [])
        )
        logs.append(f"SynthesisAgent: Response generated successfully in target language '{structured_query.language}'.")
        query_results[query_id] = query_results[query_id].copy(update={"dev_logs": list(logs)})

        # Step 8: Build the response card using response layer
        response_card = card_builder.build_risk_card(synthesis_result, "json")
        orca_response = response_card["orca_response"]

        # Step 9: Map references to EvidenceItems
        evidence_items = []
        for ref in synthesis_result.get("evidence", {}).get("references", []):
            # Resolve claim text matching the evidence reference ID
            claim_statement = ""
            for claim in synthesis_result.get("claims", []):
                if ref["id"] in claim.get("evidence_ids", []):
                    claim_statement = claim["statement"]
                    break
            
            if not claim_statement:
                claim_statement = f"Measured {ref['field']} of {ref['value']}"

            # Parse timestamp safely
            ts_str = ref.get("timestamp", datetime.utcnow().isoformat())
            try:
                ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
            except Exception:
                ts = datetime.utcnow()
                
            source_name = ref.get("source", "Environmental Sensor")
            d_status = ref.get("data_status", "SIMULATED")

            evidence_items.append(
                EvidenceItem(
                    claim=claim_statement,
                    source=source_name,
                    field=ref.get("field", "reading"),
                    value=ref.get("value"),
                    timestamp=ts,
                    confidence=ref.get("confidence", 0.9),
                    data_status=d_status
                )
            )

        # Step 10: Build AgentStatus list
        agent_statuses = []
        consulted_agents = orca_response["metadata"]["agents_consulted"]
        for agent_name in ['weather', 'sea_state', 'hazard', 'pfz_satellite']:
            if agent_name in consulted_agents:
                res = agent_results.get(agent_name, {})
                if isinstance(res, dict) and "error" in res:
                    status = "failed"
                    note = res["error"]
                else:
                    status = "ok"
                    note = "Agent reporting telemetry data"
            else:
                status = "degraded"
                note = "Agent not required for this query type"
            
            agent_statuses.append(
                AgentStatus(
                    agent_name=agent_name,
                    status=status,
                    note=note
                )
            )

        # Step 11: Map internal risk level to low | medium | high
        raw_risk = orca_response.get("risk_level", "low").lower()
        if raw_risk in ["low"]:
            risk_level = "low"
        elif raw_risk in ["moderate", "medium"]:
            risk_level = "medium"
        else:
            risk_level = "high"

        logs.append("Orchestrator: Assembling final RiskCard object and updating registry.")
        # Update in-memory store with completed RiskCard
        query_results[query_id] = RiskCard(
            risk_level=risk_level,
            reasoning=orca_response["summary"],
            recommendation=orca_response["recommendation"],
            evidence=evidence_items,
            agent_status=agent_statuses,
            status="done",
            dev_logs=list(logs)
        )
        t_synth = time.time()
        logger.info(f"Synthesis complete in {t_synth - t_synth_start:.2f}s.")

        # Save assistant response to history
        if session_id in conversation_history:
            conversation_history[session_id].append({
                "role": "assistant",
                "content": orca_response["summary"] + "\n" + orca_response["recommendation"]
            })

        logger.info(f"Query {query_id} background processing finished successfully")

    except Exception as e:
        logger.error(f"Error processing background query {query_id}: {str(e)}")
        query_results[query_id] = RiskCard(
            risk_level="medium",
            reasoning=f"Agent reasoning synthesis failed: {str(e)}",
            recommendation="Please try submitting your safety check query again.",
            evidence=[],
            agent_status=[AgentStatus(agent_name="synthesis", status="failed", note=str(e))],
            status="failed",
            dev_logs=["SYSTEM_ORCHESTRATOR ERROR: " + str(e)]
        )


# --- Legacy endpoints preserved for backward compatibility ---

# Import pydantic models to use in routes (if needed)
from pydantic import BaseModel

@router.post("/")
async def submit_query(query_data: Dict[str, Any], background_tasks: BackgroundTasks):
    """Legacy submission route"""
    query_id = str(uuid.uuid4())
    background_tasks.add_task(
        process_query_background_legacy,
        query_id,
        query_data
    )
    return {
        "query_id": query_id,
        "status": "accepted",
        "message": "Query submitted for processing"
    }

@router.get("/{query_id}")
async def get_query_result(query_id: str):
    """Legacy retrieval route"""
    if query_id not in query_results:
        raise HTTPException(status_code=404, detail="Query not found")
    
    card = query_results[query_id]
    if card.status == "processing":
        return {"query_id": query_id, "status": "processing"}
    elif card.status == "failed":
        return {"query_id": query_id, "status": "failed", "error": card.reasoning}
    else:
        # Construct legacy format
        return {
            "query_id": query_id,
            "status": "completed",
            "result": {
                "orca_response": {
                    "summary": card.reasoning,
                    "risk_level": "moderate" if card.risk_level == "medium" else card.risk_level,
                    "recommendation": card.recommendation,
                    "key_points": [e.claim for e in card.evidence],
                    "evidence": {
                        "available": len(card.evidence),
                        "sources": list(set([e.source for e in card.evidence]))
                    },
                    "metadata": {
                        "agents_consulted": [a.agent_name for a in card.agent_status if a.status == "ok"],
                        "data_quality_indicators": {
                            "agent_coverage": f"{len([a for a in card.agent_status if a.status == 'ok'])}/4",
                            "has_errors": any(a.status == "failed" for a in card.agent_status),
                            "evidence_available": len(card.evidence),
                            "response_complete": True
                        }
                    }
                }
            }
        }

async def process_query_background_legacy(query_id: str, query_data: Dict[str, Any]):
    nlu_processor = NLU()
    structured_query = await nlu_processor.parse_query(
        text=query_data.get("original_query", ""),
        lat=query_data.get("location", {}).get("latitude"),
        lon=query_data.get("location", {}).get("longitude")
    )
    # Put loading card
    query_results[query_id] = RiskCard(
        risk_level="low",
        reasoning="Processing...",
        recommendation="Please wait...",
        evidence=[],
        agent_status=[],
        status="processing"
    )

    if structured_query and (structured_query.location.lat is None or structured_query.location.lon is None):
        spatial_tasks = {TaskType.SAFETY_CHECK, TaskType.FISHING_ZONES, TaskType.ROUTE_PLANNING, TaskType.HAZARD_ALERT, TaskType.WEATHER_INFO}
        if structured_query.task in spatial_tasks:
            query_results[query_id] = RiskCard(
                risk_level="low",
                reasoning="I need a specific location to check weather and safety conditions. Please provide a coastal area, port, or city name.",
                recommendation="Try asking again with a location, e.g., 'What is the weather like in Kochi?'",
                evidence=[],
                agent_status=[],
                status="done"
            )
            return

    await process_query_background(query_id, structured_query)