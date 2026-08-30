import asyncio
import logging
import time
from datetime import datetime
from app.db import db_manager
from app.services.port_service import PortService
from app.agents.weather_agent import WeatherAgent
from app.agents.sea_state_agent import SeaStateAgent

logger = logging.getLogger(__name__)

async def historical_logging_task():
    """Background task that runs periodically to fetch and log weather/sea state."""
    logger.info("Historical logging background task started.")
    
    port_service = PortService()
    weather_agent = WeatherAgent()
    sea_state_agent = SeaStateAgent()
    
    # Run every 6 hours (21600 seconds)
    INTERVAL_SECONDS = 6 * 60 * 60
    
    while True:
        try:
            logger.info("Executing historical logging routine...")
            ports = await port_service.get_all_ports()
            
            for port in ports:
                lat = port.get("lat")
                lon = port.get("lon")
                port_name = port.get("name", f"Port-{lat}-{lon}")
                
                if not lat or not lon:
                    continue
                    
                # 1. Fetch Weather
                try:
                    weather_data = await weather_agent.process({"lat": lat, "lon": lon})
                    if "error" not in weather_data:
                        # Construct a basic document to insert
                        doc = {
                            "location": port_name,
                            "type": "weather",
                            "data": weather_data,
                            "timestamp": datetime.utcnow(),
                            "created_at": datetime.utcnow()
                        }
                        if db_manager.db is not None:
                            await db_manager.db["historical_readings"].insert_one(doc)
                except Exception as we:
                    logger.error(f"Error fetching historical weather for {port_name}: {we}")
                    
                # 2. Fetch Sea State
                try:
                    sea_state_data = await sea_state_agent.process({"lat": lat, "lon": lon})
                    if "error" not in sea_state_data:
                        doc = {
                            "location": port_name,
                            "type": "sea_state",
                            "data": sea_state_data,
                            "timestamp": datetime.utcnow(),
                            "created_at": datetime.utcnow()
                        }
                        if db_manager.db is not None:
                            await db_manager.db["historical_readings"].insert_one(doc)
                except Exception as se:
                    logger.error(f"Error fetching historical sea state for {port_name}: {se}")
                    
                # Sleep briefly between ports to avoid rate limits
                await asyncio.sleep(2)
                
            logger.info(f"Historical logging routine completed. Sleeping for {INTERVAL_SECONDS}s.")
        except asyncio.CancelledError:
            logger.info("Historical logging task cancelled.")
            break
        except Exception as e:
            logger.error(f"Error in historical logging routine: {e}")
            
        await asyncio.sleep(INTERVAL_SECONDS)
