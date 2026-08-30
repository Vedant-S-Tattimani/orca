import asyncio
from datetime import datetime, timezone
from app.agents.boundary_agent import BoundaryAgent

async def test_boundary():
    agent = BoundaryAgent()
    
    # Near Sri Lanka boundary
    lat = 9.1
    lon = 79.5
    
    res = await agent.process(
        latitude=lat,
        longitude=lon,
        start_time=datetime.now(timezone.utc),
        end_time=datetime.now(timezone.utc),
        radius_km=None,
        user_id="test_user"
    )
    
    print(res)

if __name__ == "__main__":
    asyncio.run(test_boundary())
