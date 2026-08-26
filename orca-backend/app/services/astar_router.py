"""
A* Maritime Pathfinding for ORCA

Performs A* search over the MaritimeGraph with dynamic environmental cost injection.
Uses Python's heapq for performance (faster than networkx for this use case).
"""
import math
import time
import heapq
import logging
from typing import Dict, Any, List, Tuple, Optional

from app.services.graph_config import (
    ASTAR_MAX_NODES_EXPLORED, ASTAR_TIMEOUT_SECONDS,
    WIND_MODERATE_KMH, WIND_HIGH_KMH, WIND_EXTREME_KMH,
    WAVE_MODERATE_M, WAVE_HIGH_M, WAVE_EXTREME_M,
    WIND_PENALTY_LOW, WIND_PENALTY_HIGH,
    WAVE_PENALTY_LOW, WAVE_PENALTY_HIGH,
    CURRENT_FAVORABLE_BONUS, CURRENT_ADVERSE_PENALTY, CURRENT_CROSS_PENALTY,
)

logger = logging.getLogger(__name__)


def _haversine_nm(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Haversine distance in nautical miles (admissible heuristic)."""
    R_NM = 3440.065
    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)
    a = (math.sin(d_lat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(d_lon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R_NM * c


def _compute_environmental_penalty(env_data: Optional[Dict[str, Any]]) -> float:
    """
    Compute a per-edge environmental penalty based on current conditions.
    This is applied uniformly since we don't have spatial weather grids (yet).
    Returns a per-NM penalty multiplier.
    """
    if not env_data or env_data.get("error"):
        return 0.0

    penalty = 0.0

    # Wind penalty
    wind_speed = env_data.get("wind_speed_kmh", 0)
    if wind_speed >= WIND_EXTREME_KMH:
        return float('inf')  # Block routing in extreme wind
    elif wind_speed >= WIND_HIGH_KMH:
        penalty += (wind_speed - WIND_MODERATE_KMH) * WIND_PENALTY_HIGH
    elif wind_speed >= WIND_MODERATE_KMH:
        penalty += (wind_speed - WIND_MODERATE_KMH) * WIND_PENALTY_LOW

    # Wave penalty
    wave_height = env_data.get("wave_height_m", 0)
    if wave_height >= WAVE_EXTREME_M:
        return float('inf')  # Block routing in extreme seas
    elif wave_height >= WAVE_HIGH_M:
        penalty += (wave_height - WAVE_MODERATE_M) * WAVE_PENALTY_HIGH
    elif wave_height >= WAVE_MODERATE_M:
        penalty += (wave_height - WAVE_MODERATE_M) * WAVE_PENALTY_LOW

    # Current adjustment (simplified — no directionality without spatial data)
    current_speed = env_data.get("current_speed_knots", 0)
    current_favorable = env_data.get("current_favorable", None)
    if current_favorable is True:
        penalty -= current_speed * CURRENT_FAVORABLE_BONUS
    elif current_favorable is False:
        penalty += current_speed * CURRENT_ADVERSE_PENALTY
    elif current_speed > 0:
        penalty += current_speed * CURRENT_CROSS_PENALTY

    return max(0.0, penalty)


def astar_route(
    graph,  # MaritimeGraph instance
    origin_lat: float,
    origin_lon: float,
    dest_lat: float,
    dest_lon: float,
    env_data: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Run A* pathfinding on the maritime graph.

    Args:
        graph: A MaritimeGraph instance with .adjacency, .grid_to_latlon, .latlon_to_grid
        origin_lat, origin_lon: Start coordinates
        dest_lat, dest_lon: End coordinates
        env_data: Optional environmental data for dynamic cost adjustment

    Returns:
        Dict with path coordinates, distance, nodes explored, or error info
    """
    t0 = time.time()

    # Map coordinates to grid nodes
    start_node = graph.latlon_to_grid(origin_lat, origin_lon)
    end_node = graph.latlon_to_grid(dest_lat, dest_lon)

    # Check that both nodes are navigable
    if start_node not in graph.adjacency:
        # Try to find nearest navigable node
        start_node = _find_nearest_navigable(graph, start_node)
        if start_node is None:
            return {
                "success": False,
                "error": "Origin location is not in navigable waters",
                "nodes_explored": 0,
                "elapsed_s": time.time() - t0,
            }

    if end_node not in graph.adjacency:
        end_node = _find_nearest_navigable(graph, end_node)
        if end_node is None:
            return {
                "success": False,
                "error": "Destination location is not in navigable waters",
                "nodes_explored": 0,
                "elapsed_s": time.time() - t0,
            }

    # Trivial case: same node
    if start_node == end_node:
        return {
            "success": True,
            "coordinates": [[origin_lat, origin_lon], [dest_lat, dest_lon]],
            "distance_nm": _haversine_nm(origin_lat, origin_lon, dest_lat, dest_lon),
            "nodes_explored": 0,
            "elapsed_s": time.time() - t0,
        }

    # Compute environmental penalty (uniform for now)
    env_penalty_per_nm = _compute_environmental_penalty(env_data)
    if env_penalty_per_nm == float('inf'):
        return {
            "success": False,
            "error": "Extreme environmental conditions prevent routing",
            "nodes_explored": 0,
            "elapsed_s": time.time() - t0,
        }

    # Destination lat/lon for heuristic
    dest_lat_h, dest_lon_h = graph.grid_to_latlon(*end_node)

    # A* search
    # Priority queue: (f_score, counter, node)
    # counter breaks ties to avoid comparing tuples of nodes
    open_set = []
    counter = 0
    g_score = {start_node: 0.0}
    came_from = {}

    # Initial heuristic
    s_lat, s_lon = graph.grid_to_latlon(*start_node)
    h0 = _haversine_nm(s_lat, s_lon, dest_lat_h, dest_lon_h)
    heapq.heappush(open_set, (h0, counter, start_node))
    counter += 1

    nodes_explored = 0
    found = False

    while open_set:
        # Timeout check
        if time.time() - t0 > ASTAR_TIMEOUT_SECONDS:
            logger.warning(f"A* timeout after {nodes_explored} nodes explored")
            break

        if nodes_explored >= ASTAR_MAX_NODES_EXPLORED:
            logger.warning(f"A* node limit reached: {ASTAR_MAX_NODES_EXPLORED}")
            break

        f_current, _, current = heapq.heappop(open_set)
        nodes_explored += 1

        if current == end_node:
            found = True
            break

        # Skip if we already found a better path to this node
        if f_current > g_score.get(current, float('inf')) + _haversine_nm(
            *graph.grid_to_latlon(*current), dest_lat_h, dest_lon_h
        ) + 0.01:
            continue

        # Explore neighbors
        for neighbor, base_weight in graph.adjacency.get(current, []):
            # Dynamic environmental cost overlay
            edge_cost = base_weight + (env_penalty_per_nm * max(0.1, base_weight))

            tentative_g = g_score[current] + edge_cost

            if tentative_g < g_score.get(neighbor, float('inf')):
                g_score[neighbor] = tentative_g
                came_from[neighbor] = current

                n_lat, n_lon = graph.grid_to_latlon(*neighbor)
                h = _haversine_nm(n_lat, n_lon, dest_lat_h, dest_lon_h)
                f = tentative_g + h

                heapq.heappush(open_set, (f, counter, neighbor))
                counter += 1

    elapsed = time.time() - t0

    if not found:
        return {
            "success": False,
            "error": "No navigable path found between origin and destination",
            "nodes_explored": nodes_explored,
            "elapsed_s": round(elapsed, 3),
        }

    # Reconstruct path
    path_nodes = []
    node = end_node
    while node in came_from:
        path_nodes.append(node)
        node = came_from[node]
    path_nodes.append(start_node)
    path_nodes.reverse()

    # Convert to lat/lon coordinates
    coordinates = [[round(origin_lat, 4), round(origin_lon, 4)]]
    for n in path_nodes:
        lat, lon = graph.grid_to_latlon(*n)
        coordinates.append([round(lat, 4), round(lon, 4)])
    coordinates.append([round(dest_lat, 4), round(dest_lon, 4)])

    # Simplify path — remove collinear points to reduce coordinate count
    simplified = _simplify_path(coordinates, tolerance_nm=0.5)

    # Calculate total distance from the actual path geometry
    total_nm = 0.0
    for i in range(len(simplified) - 1):
        total_nm += _haversine_nm(
            simplified[i][0], simplified[i][1],
            simplified[i + 1][0], simplified[i + 1][1]
        )

    return {
        "success": True,
        "coordinates": simplified,
        "distance_nm": round(total_nm, 1),
        "nodes_explored": nodes_explored,
        "elapsed_s": round(elapsed, 3),
        "raw_node_count": len(path_nodes),
        "simplified_node_count": len(simplified),
    }


def _find_nearest_navigable(graph, node: Tuple[int, int], max_search: int = 20) -> Optional[Tuple[int, int]]:
    """Find the nearest navigable node by expanding in a spiral around the given node."""
    r0, c0 = node
    for radius in range(1, max_search + 1):
        for dr in range(-radius, radius + 1):
            for dc in range(-radius, radius + 1):
                if abs(dr) != radius and abs(dc) != radius:
                    continue  # Only check the outer ring
                candidate = (r0 + dr, c0 + dc)
                if candidate in graph.adjacency:
                    return candidate
    return None


def _simplify_path(coords: List[List[float]], tolerance_nm: float = 0.5) -> List[List[float]]:
    """
    Douglas-Peucker path simplification to reduce point count.
    Keeps the path shape accurate within tolerance_nm of nautical miles.
    """
    if len(coords) <= 2:
        return coords

    # Convert tolerance from NM to approximate degrees (very rough)
    # 1 NM ≈ 1/60 degree latitude
    tolerance_deg = tolerance_nm / 60.0

    return _douglas_peucker(coords, tolerance_deg)


def _douglas_peucker(points: List[List[float]], epsilon: float) -> List[List[float]]:
    """Recursive Douglas-Peucker simplification."""
    if len(points) <= 2:
        return points

    # Find the point farthest from the line between first and last
    max_dist = 0.0
    max_idx = 0

    p1 = points[0]
    p2 = points[-1]

    for i in range(1, len(points) - 1):
        d = _point_line_distance(points[i], p1, p2)
        if d > max_dist:
            max_dist = d
            max_idx = i

    if max_dist > epsilon:
        left = _douglas_peucker(points[:max_idx + 1], epsilon)
        right = _douglas_peucker(points[max_idx:], epsilon)
        return left[:-1] + right
    else:
        return [points[0], points[-1]]


def _point_line_distance(p: List[float], l1: List[float], l2: List[float]) -> float:
    """Perpendicular distance from point p to line segment l1-l2 (in degrees, approximate)."""
    dx = l2[1] - l1[1]
    dy = l2[0] - l1[0]
    if dx == 0 and dy == 0:
        return math.sqrt((p[0] - l1[0]) ** 2 + (p[1] - l1[1]) ** 2)

    t = ((p[0] - l1[0]) * dy + (p[1] - l1[1]) * dx) / (dy ** 2 + dx ** 2)
    t = max(0.0, min(1.0, t))

    proj_lat = l1[0] + t * dy
    proj_lon = l1[1] + t * dx

    return math.sqrt((p[0] - proj_lat) ** 2 + (p[1] - proj_lon) ** 2)
