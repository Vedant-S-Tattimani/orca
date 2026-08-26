#!/usr/bin/env python3
"""
Test script for the updated PFZAgent
"""
import asyncio
import sys
import os

# Add the orca-backend directory to the path so we can import the agent
sys.path.insert(0, '/c/Users/Lenovo/claudetest/orca-backend')

async def test_pfz_agent():
    """Test the PFZ/satellite agent with both real API (if available) and fallback"""
    try:
        from app.agents.pfz_agent import PFZAgent
        from datetime import datetime, timedelta

        print("Testing PFZAgent...")

        agent = PFZAgent()

        # Test with Kollam coordinates as in the demo
        latitude = 8.8932
        longitude = 76.6141
        start_time = datetime.utcnow()
        end_time = start_time + timedelta(hours=5)

        print(f"Fetching PFZ/satellite data for ({latitude}, {longitude}) from {start_time} to {end_time}")

        # This will try to call the INCOIS and ISRO Bhuvan APIs first, then fall back to mock data
        result = await agent.process(latitude, longitude, start_time, end_time)

        print("\nPFZ/Satellite Agent Result:")
        print("=" * 50)
        for key, value in result.items():
            print(f"{key}: {value}")

        # Validate that we got the expected structure
        required_fields = ['agent', 'source', 'timestamp', 'confidence']
        for field in required_fields:
            if field not in result:
                print(f"ERROR: Missing required field '{field}'")
                return False

        # Check that we have PFZ/satellite-specific fields
        pfz_fields = ['sst_c', 'chlorophyll_a_mgm3', 'pfz_confidence_percent',
                     'sea_surface_height_m', 'turbidity_ntu', 'photovoltaic_radiation_wm2',
                     'wind_speed_at_sea_ms', 'pfz_recommendation', 'forecast_hours',
                     'data_origin']

        missing_pfz_fields = [field for field in pfz_fields if field not in result]
        if missing_pfz_fields:
            print(f"WARNING: Missing PFZ fields: {missing_pfz_fields}")
        else:
            print("\n[+] All required PFZ/satellite fields present")

        print(f"\n[+] Agent processed successfully!")
        print(f"  Source: {result.get('source', 'Unknown')}")
        print(f"  Confidence: {result.get('confidence', 0.0)}")
        print(f"  Recommendation: {result.get('pfz_recommendation', 'Unknown')}")

        return True

    except Exception as e:
        print(f"ERROR: Failed to test PFZ agent: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_pfz_agent())
    sys.exit(0 if success else 1)