"""
ORCA Backend - Main Application Entry Point
Marine EcoSystem Reasoning with Collaborative Agents
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="ORCA Backend",
    description="Marine EcoSystem Reasoning with Collaborative Agents",
    version="0.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
from app.api.v1.query import router as query_router
from app.api.v1.query import api_router as orca_api_router

from app.database import db_manager
from app.services.geospatial_service import GeofenceCache

app.include_router(query_router)
app.include_router(orca_api_router)

@app.on_event("startup")
async def startup_event():
    logger.info("Initializing database connection...")
    await db_manager.connect_db()
    logger.info("Loading geofences into cache...")
    await GeofenceCache.load_from_db()
    
    # Initialize maritime navigation graph (graceful — does not block if data files are missing)
    try:
        from app.services.maritime_graph import maritime_graph
        logger.info("Attempting to build maritime navigation graph...")
        graph_built = await maritime_graph.build(geofence_cache=GeofenceCache)
        if graph_built:
            logger.info(f"Maritime graph ready: {maritime_graph.node_count:,} nodes, {maritime_graph.edge_count:,} edges")
        else:
            logger.warning("Maritime graph not built (data files may be missing). "
                          "Routing will use COASTAL_FALLBACK mode.")
    except Exception as e:
        logger.warning(f"Maritime graph initialization failed: {e}. "
                      "Routing will use COASTAL_FALLBACK mode.")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Closing database connection...")
    await db_manager.close_db()

@app.get("/")
async def root():
    """Root endpoint - health check"""
    return {"message": "ORCA Backend is running", "status": "healthy"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "orca-backend"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)