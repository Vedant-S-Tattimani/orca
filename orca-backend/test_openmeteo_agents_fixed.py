#!/usr/bin/env python3
"""
Test script for the Open-Meteo agents (fixed encoding)
"""
import asyncio
import sys
from datetime import datetime, timedelta

# Add the current directory to the path so we can import app modules
sys.path.insert(0, '.')

async def test_agents():
    """Test the Open-Meteo agents"""
    try:
        from app.agents.openmeteo_weather_agent import OpenMeteoWeatherAgent
        from app.agents.openmeteo_marine_agent import OpenMeteoMarineAgent

        print("Testing Open-Meteo Weather Agent...")
        weather_agent = OpenMeteoWeatherAgent()

        # Test with Kollam coordinates
        latitude = 8.8932
        longitude = 76.6141
        start_time = datetime.utcnow()
        end_time = start_time + timedelta(hours=5)

        weather_result = await weather_agent.process(latitude, longitude, start_time, end_time)
        print("Weather Agent Result:", weather_result)

        print("\nTesting Open-Meteo Marine Agent...")
        marine_agent = OpenMeteoMarineAgent()

        marine_result = await marine_agent.process(latitude, longitude, start_time, end_time)
        print("Marine Agent Result:", marine_result)

        # Check if we got reasonable data
        if "error" not in weather_result and "error" not in marine_result:
            print("\nSUCCESS: Both agents returned data successfully!")
            # Check for some key fields
            if "temperature_c" in weather_result:
                print(f"   Temperature: {weather_result['temperature_c']}°C")
            if "wave_height_m" in marine_result:
                print(f"   Wave Height: {marine_result['wave_height_m']}m")
        else:
            print("\nERROR: One or both agents returned errors:")
            if "error" in weather_result:
                print(f"   Weather Agent Error: {weather_result['error']}")
            if "error" in marine_result:
                print(f"   Marine Agent Error: {marine_result['error']}")

        return True

    except Exception as e:
        print(f"ERROR: Failed to test agents: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_agents())
    sys.exit(0 if success else 1)