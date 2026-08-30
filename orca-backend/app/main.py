"""
ORCA Backend - Main Application Entry Point
Marine EcoSystem Reasoning with Collaborative Agents
"""

import os
import time
from fastapi import FastAPI, Request
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

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    
    # Log structured information about the request
    logger.info(
        f"Method={request.method} Path={request.url.path} "
        f"Status={response.status_code} Latency={process_time:.4f}s"
    )
    return response

@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    # Basic CSP for API and Swagger docs
    response.headers["Content-Security-Policy"] = "default-src 'self'; img-src 'self' data: https:; script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net; style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; connect-src 'self'"
    return response

# Setup CORS origins
allowed_origins_env = os.getenv("ALLOWED_ORIGINS")
if allowed_origins_env:
    origins = [origin.strip() for origin in allowed_origins_env.split(",") if origin.strip()]
else:
    logger.warning("No ALLOWED_ORIGINS set — using localhost defaults, do not use this config in production.")
    origins = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ]

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Include API routers
from app.api.v1.query import router as query_router
from app.api.v1.query import api_router as orca_api_router
from app.api.v1.auth import router as auth_router
from app.api.v1.health import router as health_router
from app.api.v1.historical import router as historical_router
from app.api.v1.reports import router as reports_router
from app.api.v1.alerts import router as alerts_router

from app.db import connect_to_mongo, close_mongo_connection
from app.services.geospatial_service import GeofenceCache

app.include_router(query_router)
app.include_router(orca_api_router)
app.include_router(auth_router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(health_router, prefix="/api/v1/health", tags=["health"])
app.include_router(historical_router, prefix="/api/v1/historical", tags=["historical"])
app.include_router(reports_router, prefix="/api/v1/reports", tags=["reports"])
app.include_router(alerts_router, prefix="/api/v1/alerts", tags=["alerts"])

@app.on_event("startup")
async def startup_event():
    logger.info("Initializing database connection...")
    await connect_to_mongo()
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
                      
    from app.tasks.historical_logger import historical_logging_task
    import asyncio
    asyncio.create_task(historical_logging_task())

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Closing database connection...")
    await close_mongo_connection()

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