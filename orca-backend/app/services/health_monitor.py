import asyncio
import time
import logging
from datetime import datetime
from typing import Dict, Any, List

from app.services.openmeteo_weather_client import OpenMeteoWeatherClient
from app.services.openmeteo_marine_client import OpenMeteoMarineClient
from app.services.isro_bhuvan_client import ISROBhuvanClient
from app.services.incois_client import INCOISClient
from app.services.imd_client import IMDClient
from app.db import db_manager

logger = logging.getLogger(__name__)

class HealthMonitorService:
    def __init__(self):
        self.clients = {
            "OpenMeteo Weather": OpenMeteoWeatherClient(),
            "OpenMeteo Marine": OpenMeteoMarineClient(),
            "ISRO Bhuvan": ISROBhuvanClient(),
            "INCOIS": INCOISClient(),
            "IMD": IMDClient()
        }
        
    async def check_all_sources(self) -> Dict[str, Any]:
        results = []
        overall_status = "UP"
        
        for name, client in self.clients.items():
            start_time = time.time()
            try:
                # Check staleness if the client returns a timestamp in its data
                # But our basic client.health_check() currently just returns boolean True/False.
                # Let's add basic staleness check simulation or check if client has last_fetch_time
                is_healthy = await client.health_check()
                latency = round((time.time() - start_time) * 1000) # ms
                
                status = "UP" if is_healthy else "DOWN"
                
                # Check staleness (if data is older than 24 hours)
                # For this implementation, we rely on the client having a `last_successful_fetch` attribute
                last_fetch = getattr(client, "last_successful_fetch", None)
                staleness_warning = None
                
                if is_healthy and last_fetch:
                    age_hours = (datetime.utcnow() - last_fetch).total_seconds() / 3600
                    if age_hours > 2:
                        status = "DEGRADED"
                        staleness_warning = f"Data is stale by {round(age_hours, 1)} hours"
                        overall_status = "DEGRADED"
                
                result_entry = {
                    "name": name,
                    "status": status,
                    "latency_ms": latency,
                    "timestamp": datetime.utcnow().isoformat() + "Z"
                }
                if staleness_warning:
                    result_entry["staleness_warning"] = staleness_warning
                    
                results.append(result_entry)
                
                if not is_healthy:
                    overall_status = "DEGRADED"
                    
            except Exception as e:
                logger.error(f"Error checking health for {name}: {e}")
                results.append({
                    "name": name,
                    "status": "DOWN",
                    "latency_ms": -1,
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat() + "Z"
                })
                overall_status = "DEGRADED"
                
        # Optional: Save results to MongoDB
        if db_manager.db is not None:
            try:
                await db_manager.db["health_logs"].insert_many(results)
            except Exception as e:
                logger.error(f"Failed to log health checks to DB: {e}")
                
        return {
            "status": overall_status,
            "sources": results
        }

health_monitor = HealthMonitorService()
