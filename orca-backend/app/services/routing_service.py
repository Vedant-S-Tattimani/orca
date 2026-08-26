"""
Maritime Route Optimization Service for ORCA
Calculates navigable sea routes around the Indian peninsula, preventing overland
paths. Computes distances in nautical miles and travel durations.
"""
from typing import Dict, Any, List, Tuple, Optional
import math
import logging

logger = logging.getLogger(__name__)

# Navigable coastal waypoint nodes in clockwise order around India
COASTAL_WAYPOINTS = [
    {"name": "Kandla", "lat": 23.0118, "lon": 70.2224},
    {"name": "Porbandar", "lat": 21.6422, "lon": 69.6093},
    {"name": "Veraval", "lat": 20.9022, "lon": 70.3697},
    {"name": "Mumbai", "lat": 18.9438, "lon": 72.8588},
    {"name": "Goa", "lat": 15.4124, "lon": 73.8078},
    {"name": "Mangalore", "lat": 12.9238, "lon": 74.8197},
    {"name": "Kochi", "lat": 9.9637, "lon": 76.2711},
    {"name": "Southern Tip (Kanyakumari)", "lat": 7.8000, "lon": 77.5000}, # Shifted slightly south into sea
    {"name": "Tuticorin", "lat": 8.7516, "lon": 78.1948},
    {"name": "Chennai", "lat": 13.0906, "lon": 80.2989},
    {"name": "Kakinada", "lat": 16.9830, "lon": 82.2783},
    {"name": "Visakhapatnam", "lat": 17.6896, "lon": 83.2986},
    {"name": "Paradip", "lat": 20.2644, "lon": 86.6713},
    {"name": "Kolkata", "lat": 22.4821, "lon": 88.2913}
]


def haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance in kilometers"""
    R = 6371.0
    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)
    a = (math.sin(d_lat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(d_lon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


class RoutingService:
    """
    Maritime routing engine that evaluates navigable ship routes around India.
    
    Supports two routing modes:
    1. GRAPH_ASTAR — genuine A* pathfinding over a bathymetric/geographic navigation graph
    2. COASTAL_FALLBACK — heuristic waypoint routing (used when graph data is unavailable)
    
    The engine automatically selects the best available mode.
    """

    def __init__(self):
        self._graph = None
        self._try_load_graph()

    def _try_load_graph(self):
        """Attempt to load the maritime graph singleton."""
        try:
            from app.services.maritime_graph import maritime_graph
            if maritime_graph.loaded:
                self._graph = maritime_graph
                logger.info("RoutingService: using GRAPH_ASTAR mode")
            else:
                logger.info("RoutingService: graph not loaded, using COASTAL_FALLBACK mode")
        except Exception as e:
            logger.warning(f"RoutingService: could not load maritime graph: {e}")

    def calculate_route(
        self,
        origin_lat: float,
        origin_lon: float,
        dest_lat: float,
        dest_lon: float,
        vessel_speed_knots: float = 12.0,
        vessel_draft_m: float = 4.0,
        env_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Calculate a safe maritime route.
        If the A* graph is loaded, uses graph-based pathfinding.
        Otherwise falls back to heuristic coastal waypoint routing.
        """
        # Try A* first if the graph is available
        if self._graph is not None and self._graph.loaded:
            result = self._calculate_route_astar(
                origin_lat, origin_lon, dest_lat, dest_lon,
                vessel_speed_knots, env_data
            )
            if result is not None:
                return result
            logger.warning("A* routing failed, falling back to COASTAL_FALLBACK")

        # Fallback: existing heuristic routing
        return self._calculate_route_fallback(
            origin_lat, origin_lon, dest_lat, dest_lon, vessel_speed_knots
        )

    def _calculate_route_astar(
        self,
        origin_lat: float,
        origin_lon: float,
        dest_lat: float,
        dest_lon: float,
        vessel_speed_knots: float,
        env_data: Optional[Dict[str, Any]] = None,
    ) -> Optional[Dict[str, Any]]:
        """A* graph-based route calculation."""
        try:
            from app.services.astar_router import astar_route

            result = astar_route(
                self._graph,
                origin_lat, origin_lon,
                dest_lat, dest_lon,
                env_data=env_data,
            )

            if not result.get("success"):
                logger.warning(f"A* failed: {result.get('error')}")
                return None

            total_nm = result["distance_nm"]
            total_km = total_nm / 0.539957
            duration_hours = total_nm / vessel_speed_knots if vessel_speed_knots > 0 else 0

            return {
                "route_type": "SAFE_ALTERNATIVE",
                "routing_mode": "GRAPH_ASTAR",
                "coordinates": result["coordinates"],
                "distance_nm": round(total_nm, 1),
                "distance_km": round(total_km, 1),
                "duration_hours": round(duration_hours, 1),
                "speed_knots": vessel_speed_knots,
                "crosses_land": False,
                "provenance": "ORCA Routing Engine v3 (A* Maritime Graph)",
                "graph_metadata": {
                    "nodes_explored": result.get("nodes_explored", 0),
                    "elapsed_s": result.get("elapsed_s", 0),
                    "raw_waypoints": result.get("raw_node_count", 0),
                    "simplified_waypoints": result.get("simplified_node_count", 0),
                    **self._graph.get_metadata(),
                },
            }
        except Exception as e:
            logger.error(f"A* routing error: {e}")
            return None

    def _calculate_route_fallback(
        self,
        origin_lat: float,
        origin_lon: float,
        dest_lat: float,
        dest_lon: float,
        vessel_speed_knots: float = 12.0
    ) -> Dict[str, Any]:
        """
        Calculate a safe maritime route.
        If the path crosses the Indian landmass (e.g. west coast to east coast),
        interleave coastal waypoints to route around the southern tip.
        """
        crosses_land = False
        if ((origin_lon < 77.5 and dest_lon > 77.5) or (origin_lon > 77.5 and dest_lon < 77.5)):
            if origin_lat > 8.5 and dest_lat > 8.5:
                crosses_land = True

        route_coords = []
        route_type = "DIRECT_FEASIBLE"
        routing_mode = "DYNAMIC_FEASIBLE"

        if crosses_land:
            origin_idx = self._find_closest_waypoint_index(origin_lat, origin_lon)
            dest_idx = self._find_closest_waypoint_index(dest_lat, dest_lon)
            
            route_coords.append([origin_lat, origin_lon])
            
            step = 1 if origin_idx < dest_idx else -1
            curr = origin_idx
            
            while curr != dest_idx:
                wp = COASTAL_WAYPOINTS[curr]
                if haversine_distance_km(route_coords[-1][0], route_coords[-1][1], wp["lat"], wp["lon"]) > 20:
                    route_coords.append([wp["lat"], wp["lon"]])
                curr += step
            
            wp_dest = COASTAL_WAYPOINTS[dest_idx]
            if haversine_distance_km(route_coords[-1][0], route_coords[-1][1], wp_dest["lat"], wp_dest["lon"]) > 20:
                route_coords.append([wp_dest["lat"], wp_dest["lon"]])
                
            route_coords.append([dest_lat, dest_lon])
            route_type = "SAFE_ALTERNATIVE"
            routing_mode = "COASTAL_FALLBACK"
        else:
            route_coords = [
                [origin_lat, origin_lon],
                [dest_lat, dest_lon]
            ]
            route_type = "DIRECT_FEASIBLE"
            routing_mode = "DYNAMIC_FEASIBLE"

        total_km = 0.0
        for i in range(len(route_coords) - 1):
            total_km += haversine_distance_km(
                route_coords[i][0], route_coords[i][1],
                route_coords[i+1][0], route_coords[i+1][1]
            )

        total_nm = total_km * 0.539957
        duration_hours = total_nm / vessel_speed_knots if vessel_speed_knots > 0 else 0

        return {
            "route_type": route_type,
            "routing_mode": routing_mode,
            "coordinates": route_coords,
            "distance_nm": round(total_nm, 1),
            "distance_km": round(total_km, 1),
            "duration_hours": round(duration_hours, 1),
            "speed_knots": vessel_speed_knots,
            "crosses_land": crosses_land,
            "provenance": "ORCA Routing Engine v2"
        }

    def _find_closest_waypoint_index(self, lat: float, lon: float) -> int:
        best_dist = float('inf')
        best_idx = 0
        for i, wp in enumerate(COASTAL_WAYPOINTS):
            d = haversine_distance_km(lat, lon, wp["lat"], wp["lon"])
            if d < best_dist:
                best_dist = d
                best_idx = i
        return best_idx

    def evaluate_route_safety(self, route_data: Dict[str, Any], risk_flags: Dict[str, List[Dict[str, Any]]], geo_service: Any, env_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Evaluate the safety of a computed route against active risk flags and precise geospatial polygons.
        Computes a dynamic route cost based on distance and penalties.
        """
        hazards = []
        status = "SAFE"
        geofence_conflicts = []
        
        hazard_penalty = 0.0
        restricted_zone_penalty = 0.0
        environmental_penalty = 0.0
        
        # 1. Geofence Evaluation using GeospatialService
        route_coords = route_data.get("coordinates", [])
        
        # Interpolate points along the route to ensure we catch segments crossing polygons
        test_points = []
        for i in range(len(route_coords) - 1):
            lat1, lon1 = route_coords[i][0], route_coords[i][1]
            lat2, lon2 = route_coords[i+1][0], route_coords[i+1][1]
            dist_km = haversine_distance_km(lat1, lon1, lat2, lon2)
            steps = max(1, int(dist_km / 10.0)) # sample every 10km
            for step in range(steps):
                fraction = step / float(steps)
                inter_lat = lat1 + (lat2 - lat1) * fraction
                inter_lon = lon1 + (lon2 - lon1) * fraction
                test_points.append((inter_lat, inter_lon))
        if route_coords:
            test_points.append((route_coords[-1][0], route_coords[-1][1]))
            
        for lat, lon in test_points:
            # Precise point-in-polygon checks via the service
            fence_results = geo_service.check_geofences(lat, lon)
            for res in fence_results:
                if res.get("status") in ["WARNING", "CRITICAL"]:
                    conflict = f"{res.get('type')} conflict: {res.get('geofence_name')}"
                    if conflict not in geofence_conflicts:
                        geofence_conflicts.append(conflict)
                        
                    if res.get("type") == "RESTRICTED" and res.get("inside"):
                        hazard_str = f"Route crosses RESTRICTED ZONE: {res.get('geofence_name')}"
                        if hazard_str not in hazards:
                            hazards.append(hazard_str)
                        status = "INVALID"
                        restricted_zone_penalty += 1000.0
                    elif res.get("type") == "IMBL" and status != "INVALID":
                        hazard_str = f"Route approaches IMBL: {res.get('geofence_name')}"
                        if hazard_str not in hazards:
                            hazards.append(hazard_str)
                        if status == "SAFE":
                            status = "WARNING"
                        restricted_zone_penalty += 100.0

        # 2. Hazard Evaluation (Risk Flags)
        for category, flags in risk_flags.items():
            for flag in flags:
                if flag.get("risk_level") in ["high", "extreme"]:
                    hazards.append(f"{category.upper()} Hazard: {flag.get('description')}")
                    if status != "INVALID":
                        status = "DANGEROUS"
                    hazard_penalty += 500.0
                elif flag.get("risk_level") == "moderate" and status not in ["INVALID", "DANGEROUS"]:
                    hazards.append(f"{category.upper()} Warning: {flag.get('description')}")
                    status = "WARNING"
                    hazard_penalty += 50.0

        # 3. Environmental Impact (Currents, Wind, Wave)
        env_factors = {
            "wind": "UNAVAILABLE",
            "waves": "UNAVAILABLE",
            "currents": "UNAVAILABLE"
        }
        
        if env_data and not env_data.get("error"):
            # If weather/marine data is provided, apply environmental costs
            wind_speed = env_data.get("wind_speed_kmh", 0)
            wave_height = env_data.get("wave_height_m", 0)
            current_speed = env_data.get("current_speed_knots", 0)
            
            # Determine LIVE vs SIMULATED from env_data status
            data_status = env_data.get("data_status", "SIMULATED")
            env_factors["wind"] = data_status if wind_speed else "UNAVAILABLE"
            env_factors["waves"] = data_status if wave_height else "UNAVAILABLE"
            env_factors["currents"] = data_status if current_speed else "UNAVAILABLE"
            
            if wind_speed > 40:
                environmental_penalty += (wind_speed - 40) * 2.0
            if wave_height > 2.5:
                environmental_penalty += (wave_height - 2.5) * 20.0
                
            # If favorable current (mocking it as negative penalty for demonstration)
            if current_speed > 0:
                environmental_penalty -= (current_speed * 10.0)

        # 4. Final Route Cost Calculation
        distance_cost = route_data.get("distance_nm", 0)
        route_cost = distance_cost + hazard_penalty + restricted_zone_penalty + environmental_penalty

        return {
            "status": status,
            "safety_level": status,
            "hazards": hazards,
            "warnings": hazards,
            "geofence_conflicts": geofence_conflicts,
            "environmental_factors": env_factors,
            "costs": {
                "distance_cost": round(distance_cost, 1),
                "hazard_penalty": round(hazard_penalty, 1),
                "restricted_zone_penalty": round(restricted_zone_penalty, 1),
                "environmental_penalty": round(environmental_penalty, 1),
                "total_route_cost": round(route_cost, 1)
            }
        }
