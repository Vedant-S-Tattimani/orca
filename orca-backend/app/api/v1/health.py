from fastapi import APIRouter
from app.services.health_monitor import health_monitor

router = APIRouter()

@router.get("/sources")
async def get_sources_health():
    """
    Returns the real-time health and latency of all external API dependencies
    """
    return await health_monitor.check_all_sources()
