"""
Maritime Navigation Graph Builder for ORCA

Reads bathymetry (GEBCO NetCDF), land polygons (GeoJSON), and restricted zones
(MongoDB geofences) to construct a navigable maritime graph suitable for A* pathfinding.

The graph is a sparse adjacency dictionary:
  graph[node_id] = [(neighbor_id, base_weight), ...]

Node IDs are (row, col) tuples into the grid.
"""
import os
import json
import math
import time
import pickle
import logging
import numpy as np
from typing import Dict, Any, List, Tuple, Optional

from app.services.graph_config import (
    REGION_NORTH, REGION_SOUTH, REGION_WEST, REGION_EAST,
    GRID_STEP_DEG, GRID_RESOLUTION_ARCMIN,
    DEFAULT_MIN_DEPTH_M,
    PENALTY_RESTRICTED_PROXIMITY, PENALTY_IMBL_CRITICAL,
    PENALTY_IMBL_WARNING, PENALTY_ECOLOGICAL_INSIDE,
    PENALTY_ECOLOGICAL_PROXIMITY,
    GEBCO_NETCDF_PATH, LAND_GEOJSON_PATH, GRAPH_CACHE_PATH,
    NEIGHBORS_8,
)

logger = logging.getLogger(__name__)


def _haversine_nm(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Haversine distance in nautical miles."""
    R_NM = 3440.065  # Earth radius in NM
    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)
    a = (math.sin(d_lat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(d_lon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R_NM * c


def _point_in_polygon_simple(px: float, py: float, polygon: List) -> bool:
    """Ray-casting point-in-polygon. polygon is [[lon, lat], ...] or [[lat, lon], ...] — caller specifies."""
    n = len(polygon)
    if n < 3:
        return False
    inside = False
    x, y = px, py
    p1x, p1y = polygon[0]
    for i in range(1, n + 1):
        p2x, p2y = polygon[i % n]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
        p1x, p1y = p2x, p2y
    return inside


class MaritimeGraph:
    """
    Builds and holds the navigable maritime graph for A* routing.
    """

    def __init__(self):
        self.loaded = False
        self.grid_rows = 0
        self.grid_cols = 0
        self.lat_min = REGION_SOUTH
        self.lat_max = REGION_NORTH
        self.lon_min = REGION_WEST
        self.lon_max = REGION_EAST
        self.step = GRID_STEP_DEG

        # Core data
        self.depth_grid: Optional[np.ndarray] = None     # float32, shape (rows, cols)
        self.navigable: Optional[np.ndarray] = None      # bool, shape (rows, cols)
        self.penalty_grid: Optional[np.ndarray] = None   # float32, shape (rows, cols) — static zone penalties

        # Sparse adjacency: dict[ (row,col) -> list[ ((row,col), base_weight_nm) ] ]
        self.adjacency: Dict[Tuple[int, int], List[Tuple[Tuple[int, int], float]]] = {}

        # Metadata
        self.build_time_s = 0.0
        self.node_count = 0
        self.edge_count = 0
        self.bathymetry_source = "GEBCO 2024"
        self.land_source = "Natural Earth 1:10m"

    # ------------------------------------------------------------------
    # Coordinate ↔ Grid conversion
    # ------------------------------------------------------------------

    def latlon_to_grid(self, lat: float, lon: float) -> Tuple[int, int]:
        """Convert lat/lon to (row, col) grid indices."""
        row = int((self.lat_max - lat) / self.step)
        col = int((lon - self.lon_min) / self.step)
        row = max(0, min(row, self.grid_rows - 1))
        col = max(0, min(col, self.grid_cols - 1))
        return (row, col)

    def grid_to_latlon(self, row: int, col: int) -> Tuple[float, float]:
        """Convert (row, col) grid indices to centre lat/lon."""
        lat = self.lat_max - (row + 0.5) * self.step
        lon = self.lon_min + (col + 0.5) * self.step
        return (lat, lon)

    # ------------------------------------------------------------------
    # Graph construction
    # ------------------------------------------------------------------

    async def build(self, geofence_cache=None, min_depth_m: float = DEFAULT_MIN_DEPTH_M) -> bool:
        """
        Build the maritime graph from data files.
        Returns True if the graph was successfully built, False otherwise.
        """
        t0 = time.time()

        # Calculate grid dimensions
        self.grid_rows = int((self.lat_max - self.lat_min) / self.step)
        self.grid_cols = int((self.lon_max - self.lon_min) / self.step)
        logger.info(f"Grid dimensions: {self.grid_rows} x {self.grid_cols} = {self.grid_rows * self.grid_cols:,} cells")

        # Try to load from cache first
        if os.path.exists(GRAPH_CACHE_PATH):
            try:
                if self._load_cache():
                    logger.info(f"Loaded maritime graph from cache in {time.time() - t0:.1f}s")
                    return True
            except Exception as e:
                logger.warning(f"Cache load failed: {e}. Rebuilding from data files.")

        # Step 1: Read bathymetry
        if not self._read_bathymetry():
            logger.warning("Bathymetry data not available. Maritime graph will not be built.")
            return False

        # Step 2: Build navigability mask
        self._build_navigability_mask(min_depth_m)

        # Step 3: Apply land mask from GeoJSON (if available)
        self._apply_land_mask()

        # Step 4: Apply restricted zone penalties (from geofence cache)
        self.penalty_grid = np.zeros((self.grid_rows, self.grid_cols), dtype=np.float32)
        if geofence_cache is not None:
            self._apply_restricted_zones(geofence_cache)

        # Step 5: Build adjacency graph
        self._build_adjacency()

        self.build_time_s = time.time() - t0
        self.loaded = True
        logger.info(
            f"Maritime graph built: {self.node_count:,} nodes, {self.edge_count:,} edges "
            f"in {self.build_time_s:.1f}s"
        )

        # Save cache
        self._save_cache()

        return True

    def _read_bathymetry(self) -> bool:
        """Read GEBCO NetCDF and resample to our grid resolution."""
        if not os.path.exists(GEBCO_NETCDF_PATH):
            logger.warning(f"GEBCO file not found: {GEBCO_NETCDF_PATH}")
            return False

        try:
            from scipy.io import netcdf_file
            logger.info(f"Reading GEBCO bathymetry from {GEBCO_NETCDF_PATH}")

            with netcdf_file(GEBCO_NETCDF_PATH, 'r', mmap=False) as nc:
                # GEBCO NetCDF typically has variables: lat, lon, elevation
                lat_var = None
                lon_var = None
                elev_var = None

                for name in ['lat', 'latitude', 'y']:
                    if name in nc.variables:
                        lat_var = nc.variables[name][:].copy()
                        break
                for name in ['lon', 'longitude', 'x']:
                    if name in nc.variables:
                        lon_var = nc.variables[name][:].copy()
                        break
                for name in ['elevation', 'z', 'Band1']:
                    if name in nc.variables:
                        elev_var = nc.variables[name][:].copy()
                        break

                if lat_var is None or lon_var is None or elev_var is None:
                    logger.error(f"Could not find lat/lon/elevation variables in NetCDF. Variables: {list(nc.variables.keys())}")
                    return False

            logger.info(f"GEBCO raw grid: {elev_var.shape}, lat range [{lat_var.min():.2f}, {lat_var.max():.2f}], lon range [{lon_var.min():.2f}, {lon_var.max():.2f}]")

            # Resample to our target grid using nearest-neighbor or area-average
            self.depth_grid = np.zeros((self.grid_rows, self.grid_cols), dtype=np.float32)

            for r in range(self.grid_rows):
                cell_lat = self.lat_max - (r + 0.5) * self.step
                # Find nearest GEBCO latitude index
                lat_idx = np.argmin(np.abs(lat_var - cell_lat))

                for c in range(self.grid_cols):
                    cell_lon = self.lon_min + (c + 0.5) * self.step
                    lon_idx = np.argmin(np.abs(lon_var - cell_lon))
                    self.depth_grid[r, c] = float(elev_var[lat_idx, lon_idx])

            logger.info(f"Resampled bathymetry to {self.grid_rows}x{self.grid_cols} grid. "
                        f"Depth range: [{self.depth_grid.min():.0f}, {self.depth_grid.max():.0f}]m")
            return True

        except ImportError:
            logger.error("scipy.io.netcdf not available. Cannot read GEBCO file.")
            return False
        except Exception as e:
            logger.error(f"Error reading GEBCO bathymetry: {e}")
            return False

    def _build_navigability_mask(self, min_depth_m: float):
        """Mark cells as navigable or not based on depth."""
        # Navigable: depth < min_depth_m (deeper is more negative in GEBCO)
        # GEBCO convention: negative = below sea level, positive = above
        self.navigable = np.zeros((self.grid_rows, self.grid_cols), dtype=bool)
        self.navigable[self.depth_grid < min_depth_m] = True

        nav_count = int(np.sum(self.navigable))
        total = self.grid_rows * self.grid_cols
        logger.info(f"Navigability mask: {nav_count:,} / {total:,} cells navigable "
                    f"({100.0 * nav_count / total:.1f}%) at min depth {min_depth_m}m")

    def _apply_land_mask(self):
        """Apply Natural Earth land polygons to mark land cells as non-navigable using shapely prep."""
        if not os.path.exists(LAND_GEOJSON_PATH):
            logger.warning(f"Land GeoJSON not found: {LAND_GEOJSON_PATH}. "
                          "Relying on bathymetry-only navigability.")
            return

        try:
            from shapely.geometry import Point, Polygon
            from shapely.ops import unary_union
            from shapely.prepared import prep
            
            logger.info(f"Reading land polygons from {LAND_GEOJSON_PATH}")
            with open(LAND_GEOJSON_PATH, 'r') as f:
                geojson = json.load(f)

            shapes = []
            features = geojson.get("features", [geojson]) if "features" in geojson else [geojson]
            for feature in features:
                geom = feature.get("geometry", feature)
                gtype = geom.get("type", "")
                if gtype == "Polygon":
                    shapes.append(Polygon(geom["coordinates"][0]))
                elif gtype == "MultiPolygon":
                    for poly in geom["coordinates"]:
                        shapes.append(Polygon(poly[0]))

            if not shapes:
                logger.warning("No land shapes found in GeoJSON.")
                return

            combined_land = unary_union(shapes)
            prepped_land = prep(combined_land)
            logger.info(f"Loaded {len(shapes)} land polygon rings and prepped spatial index.")

            # For efficiency, only check cells that are currently navigable
            land_masked = 0
            for r in range(self.grid_rows):
                lat = self.lat_max - (r + 0.5) * self.step
                for c in range(self.grid_cols):
                    if not self.navigable[r, c]:
                        continue
                    lon = self.lon_min + (c + 0.5) * self.step

                    pt = Point(lon, lat)
                    if prepped_land.contains(pt):
                        self.navigable[r, c] = False
                        land_masked += 1

            logger.info(f"Land mask applied: {land_masked:,} additional cells marked as land")

        except Exception as e:
            logger.warning(f"Error applying land mask: {e}. Continuing with bathymetry-only.")

    def _apply_restricted_zones(self, geofence_cache):
        """Apply restricted zone penalties to the penalty grid."""
        from app.services.geospatial_service import point_in_polygon, haversine_km

        zone_configs = [
            ("RESTRICTED_LAKSHADWEEP", geofence_cache.RESTRICTED_LAKSHADWEEP, "RESTRICTED", 10.0),
            ("ECO_GULF_OF_MANNAR", geofence_cache.ECO_GULF_OF_MANNAR, "ECOLOGICAL", 5.0),
            ("ECO_SUNDARBANS", geofence_cache.ECO_SUNDARBANS, "ECOLOGICAL", 5.0),
        ]

        for zone_name, polygon, zone_type, prox_km in zone_configs:
            if not polygon:
                continue

            inside_count = 0
            prox_count = 0

            for r in range(self.grid_rows):
                lat = self.lat_max - (r + 0.5) * self.step
                for c in range(self.grid_cols):
                    if not self.navigable[r, c]:
                        continue
                    lon = self.lon_min + (c + 0.5) * self.step

                    if point_in_polygon(lat, lon, polygon):
                        if zone_type == "RESTRICTED":
                            self.navigable[r, c] = False  # Remove node
                            inside_count += 1
                        else:
                            self.penalty_grid[r, c] += PENALTY_ECOLOGICAL_INSIDE
                            inside_count += 1
                    else:
                        # Proximity check — simplified: check distance to polygon centroid
                        # For a proper check we would test segments, but this is adequate at 3.7km resolution
                        min_dist = float('inf')
                        for i in range(len(polygon) - 1):
                            seg_lat = (polygon[i][0] + polygon[i+1][0]) / 2
                            seg_lon = (polygon[i][1] + polygon[i+1][1]) / 2
                            d = haversine_km(lat, lon, seg_lat, seg_lon)
                            min_dist = min(min_dist, d)

                        if min_dist < prox_km:
                            if zone_type == "RESTRICTED":
                                self.penalty_grid[r, c] += PENALTY_RESTRICTED_PROXIMITY
                            else:
                                self.penalty_grid[r, c] += PENALTY_ECOLOGICAL_PROXIMITY
                            prox_count += 1

            logger.info(f"Zone {zone_name}: {inside_count} cells inside, {prox_count} cells in proximity")

        # IMBL penalties (line-based, not polygon)
        imbl_configs = [
            ("IMBL_SRI_LANKA", geofence_cache.IMBL_SRI_LANKA),
            ("IMBL_PAKISTAN", geofence_cache.IMBL_PAKISTAN),
        ]

        for imbl_name, line_coords in imbl_configs:
            if not line_coords:
                continue
            prox_count = 0
            for r in range(self.grid_rows):
                lat = self.lat_max - (r + 0.5) * self.step
                for c in range(self.grid_cols):
                    if not self.navigable[r, c]:
                        continue
                    lon = self.lon_min + (c + 0.5) * self.step

                    min_dist = float('inf')
                    for i in range(len(line_coords) - 1):
                        mid_lat = (line_coords[i][0] + line_coords[i+1][0]) / 2
                        mid_lon = (line_coords[i][1] + line_coords[i+1][1]) / 2
                        d = haversine_km(lat, lon, mid_lat, mid_lon)
                        min_dist = min(min_dist, d)

                    if min_dist < 5.0:
                        self.penalty_grid[r, c] += PENALTY_IMBL_CRITICAL
                        prox_count += 1
                    elif min_dist < 15.0:
                        self.penalty_grid[r, c] += PENALTY_IMBL_WARNING
                        prox_count += 1

            logger.info(f"IMBL {imbl_name}: {prox_count} cells with proximity penalty")

    def _build_adjacency(self):
        """Build sparse adjacency from navigable cells."""
        self.adjacency = {}
        self.node_count = 0
        self.edge_count = 0

        for r in range(self.grid_rows):
            for c in range(self.grid_cols):
                if not self.navigable[r, c]:
                    continue

                node = (r, c)
                neighbors = []
                lat1, lon1 = self.grid_to_latlon(r, c)

                for dr, dc in NEIGHBORS_8:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < self.grid_rows and 0 <= nc < self.grid_cols:
                        if self.navigable[nr, nc]:
                            lat2, lon2 = self.grid_to_latlon(nr, nc)
                            dist_nm = _haversine_nm(lat1, lon1, lat2, lon2)
                            # Add static zone penalty (averaged between the two cells)
                            penalty = (self.penalty_grid[r, c] + self.penalty_grid[nr, nc]) / 2.0
                            weight = dist_nm + penalty
                            neighbors.append(((nr, nc), weight))
                            self.edge_count += 1

                if neighbors:
                    self.adjacency[node] = neighbors
                    self.node_count += 1

    # ------------------------------------------------------------------
    # Cache management
    # ------------------------------------------------------------------

    def _save_cache(self):
        """Serialize the built graph to disk."""
        try:
            os.makedirs(os.path.dirname(GRAPH_CACHE_PATH), exist_ok=True)
            cache_data = {
                "grid_rows": self.grid_rows,
                "grid_cols": self.grid_cols,
                "lat_min": self.lat_min,
                "lat_max": self.lat_max,
                "lon_min": self.lon_min,
                "lon_max": self.lon_max,
                "step": self.step,
                "navigable": self.navigable,
                "depth_grid": self.depth_grid,
                "penalty_grid": self.penalty_grid,
                "adjacency": self.adjacency,
                "node_count": self.node_count,
                "edge_count": self.edge_count,
                "build_time_s": self.build_time_s,
            }
            with open(GRAPH_CACHE_PATH, 'wb') as f:
                pickle.dump(cache_data, f, protocol=pickle.HIGHEST_PROTOCOL)
            cache_size_mb = os.path.getsize(GRAPH_CACHE_PATH) / (1024 * 1024)
            logger.info(f"Graph cache saved: {GRAPH_CACHE_PATH} ({cache_size_mb:.1f} MB)")
        except Exception as e:
            logger.warning(f"Failed to save graph cache: {e}")

    def _load_cache(self) -> bool:
        """Deserialize a previously built graph from disk."""
        with open(GRAPH_CACHE_PATH, 'rb') as f:
            cache_data = pickle.load(f)

        self.grid_rows = cache_data["grid_rows"]
        self.grid_cols = cache_data["grid_cols"]
        self.lat_min = cache_data["lat_min"]
        self.lat_max = cache_data["lat_max"]
        self.lon_min = cache_data["lon_min"]
        self.lon_max = cache_data["lon_max"]
        self.step = cache_data["step"]
        self.navigable = cache_data["navigable"]
        self.depth_grid = cache_data["depth_grid"]
        self.penalty_grid = cache_data["penalty_grid"]
        self.adjacency = cache_data["adjacency"]
        self.node_count = cache_data["node_count"]
        self.edge_count = cache_data["edge_count"]
        self.build_time_s = cache_data["build_time_s"]
        self.loaded = True

        logger.info(f"Graph cache loaded: {self.node_count:,} nodes, {self.edge_count:,} edges")
        return True

    def get_metadata(self) -> Dict[str, Any]:
        """Return metadata about the graph for API responses."""
        return {
            "graph_loaded": self.loaded,
            "graph_resolution_arcmin": GRID_RESOLUTION_ARCMIN,
            "node_count": self.node_count,
            "edge_count": self.edge_count,
            "build_time_s": round(self.build_time_s, 1),
            "bathymetry_source": self.bathymetry_source if self.loaded else "NOT_LOADED",
            "land_source": self.land_source if self.loaded else "NOT_LOADED",
            "data_files_loaded": self.loaded,
        }


# Global singleton
maritime_graph = MaritimeGraph()
