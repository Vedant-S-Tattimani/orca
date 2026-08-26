"""
Maritime Navigation Graph — Configuration
All configurable constants for graph construction, A* routing, and cost modelling.
"""
import os

# ============================================================
# REGIONAL BOUNDING BOX (Indian Coastal Waters for SIH demo)
# ============================================================
REGION_NORTH = 25.0   # °N — Gujarat / Kutch
REGION_SOUTH = 5.0    # °N — south of Kanyakumari / Lakshadweep
REGION_WEST = 65.0    # °E — western Arabian Sea
REGION_EAST = 90.0    # °E — eastern Bay of Bengal / Kolkata

# ============================================================
# GRID RESOLUTION
# ============================================================
GRID_RESOLUTION_ARCMIN = 2  # 2 arc-minutes ≈ 3.7 km per cell
# Derived values (do not modify directly)
GRID_STEP_DEG = GRID_RESOLUTION_ARCMIN / 60.0  # 0.0333...°

# ============================================================
# VESSEL DRAFT
# ============================================================
DEFAULT_VESSEL_DRAFT_M = 4.0      # metres — typical small fishing / coastal cargo
DEFAULT_SAFETY_CLEARANCE_M = 3.0  # metres — under-keel clearance
# Minimum navigable depth = -(draft + clearance), i.e. water must be at least this deep
DEFAULT_MIN_DEPTH_M = -(DEFAULT_VESSEL_DRAFT_M + DEFAULT_SAFETY_CLEARANCE_M)  # -7.0

# ============================================================
# PENALTY WEIGHTS (edge cost additions)
# ============================================================
PENALTY_RESTRICTED_INSIDE = float('inf')   # node removed — impassable
PENALTY_RESTRICTED_PROXIMITY = 500.0       # within 10 km of restricted zone
PENALTY_IMBL_CRITICAL = 1000.0             # within 5 km of IMBL
PENALTY_IMBL_WARNING = 200.0               # within 15 km of IMBL
PENALTY_ECOLOGICAL_INSIDE = 100.0          # inside ecological zone
PENALTY_ECOLOGICAL_PROXIMITY = 20.0        # within 5 km of ecological zone

# Environmental cost thresholds (from thresholds.yaml)
WIND_MODERATE_KMH = 20
WIND_HIGH_KMH = 40
WIND_EXTREME_KMH = 60
WAVE_MODERATE_M = 1.5
WAVE_HIGH_M = 2.5
WAVE_EXTREME_M = 4.0

# Environmental cost multipliers
WIND_PENALTY_LOW = 0.5     # per km/h above moderate
WIND_PENALTY_HIGH = 1.5    # per km/h above moderate when high
WAVE_PENALTY_LOW = 5.0     # per metre above moderate
WAVE_PENALTY_HIGH = 15.0   # per metre above moderate when high
CURRENT_FAVORABLE_BONUS = 2.0   # per knot (subtracted)
CURRENT_ADVERSE_PENALTY = 3.0   # per knot (added)
CURRENT_CROSS_PENALTY = 1.0     # per knot (added)

# ============================================================
# A* LIMITS
# ============================================================
ASTAR_MAX_NODES_EXPLORED = 500_000  # safety cutoff
ASTAR_TIMEOUT_SECONDS = 5.0        # max wall-clock time for a single route

# ============================================================
# DATA FILE PATHS
# ============================================================
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")

# GEBCO bathymetry (NetCDF format, regional subset)
GEBCO_NETCDF_PATH = os.path.join(DATA_DIR, "gebco_indian_ocean.nc")

# Natural Earth 1:10m land polygons (converted to GeoJSON)
LAND_GEOJSON_PATH = os.path.join(DATA_DIR, "land_polygons.geojson")

# Marine Regions EEZ (converted to GeoJSON, India subset)
EEZ_GEOJSON_PATH = os.path.join(DATA_DIR, "india_eez.geojson")

# Serialized graph cache
GRAPH_CACHE_PATH = os.path.join(DATA_DIR, "maritime_graph.pkl")

# ============================================================
# GRAPH CONNECTIVITY
# ============================================================
# 8-connected grid: N, NE, E, SE, S, SW, W, NW
NEIGHBORS_8 = [
    (-1, 0),   # North
    (-1, 1),   # NE
    (0, 1),    # East
    (1, 1),    # SE
    (1, 0),    # South
    (1, -1),   # SW
    (0, -1),   # West
    (-1, -1),  # NW
]
