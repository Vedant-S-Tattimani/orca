#!/usr/bin/env python3
"""
Test script for the updated SeaStateAgent
"""
import asyncio
import sys
import os

# Add the orca-backend directory to the path so we can import the agent
sys.path.insert(0, '/c/Users/Lenovo/claudetest/orca-backend')

async def test_sea_state_agent():
    """Test the sea state agent with both real API (if available) and fallback"""
    try:
        from app.agents.sea_state_agent import SeaStateAgent
        from datetime import datetime, timedelta

        print("Testing SeaStateAgent...")

        agent = SeaStateAgent()

        # Test with Kollam coordinates as in the demo
        latitude = 8.8932
        longitude = 76.6141
        start_time = datetime.utcnow()
        end_time = start_time + timedelta(hours=5)

        print(f"Fetching sea-state data for ({latitude}, {longitude}) from {start_time} to {end_time}")

        # This will try to call the INCOIS API first, then fall back to mock data
        result = await agent.process(latitude, longitude, start_time, end_time)

        print("\nSea-State Agent Result:")
        print("=" * 50)
        for key, value in result.items():
            print(f"{key}: {value}")

        # Validate that we got the expected structure
        required_fields = ['agent', 'source', 'timestamp', 'confidence']
        for field in required_fields:
            if field not in result:
                print(f"ERROR: Missing required field '{field}'")
                return False

        # Check that we have sea-state-specific fields
        sea_state_fields = ['wave_height_m', 'wave_period_s', 'swell_height_m', 'swell_direction_deg',
                           'current_speed_knots', 'current_direction_deg', 'tide_height_m',
                           'sea_surface_temp_c', 'salinity_psu', 'forecast_hours']

        missing_sea_state_fields = [field for field in sea_state_fields if field not in result]
        if missing_sea_state_fields:
            print(f"WARNING: Missing sea-state fields: {missing_sea_state_fields}")
        else:
            print("\n[+] All required sea-state fields present")

        print(f"\n[+] Agent processed successfully!")
        print(f"  Source: {result.get('source', 'Unknown')}")
        print(f"  Confidence: {result.get('confidence', 0.0)}")

        return True

    except Exception as e:
        print(f"ERROR: Failed to test sea state agent: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_sea_state_agent())
    sys.exit(0 if success else 1)