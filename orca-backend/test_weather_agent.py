#!/usr/bin/env python3
"""
Test script for the updated WeatherAgent
"""
import asyncio
import sys
import os

# Add the orca-backend directory to the path so we can import the agent
sys.path.insert(0, '/c/Users/Lenovo/claudetest/orca-backend')

async def test_weather_agent():
    """Test the weather agent with both real API (if available) and fallback"""
    try:
        from app.agents.weather_agent import WeatherAgent
        from datetime import datetime, timedelta

        print("Testing WeatherAgent...")

        agent = WeatherAgent()

        # Test with Kollam coordinates as in the demo
        latitude = 8.8932
        longitude = 76.6141
        start_time = datetime.utcnow()
        end_time = start_time + timedelta(hours=5)

        print(f"Fetching weather data for ({latitude}, {longitude}) from {start_time} to {end_time}")

        # This will try to call the IMD API first, then fall back to mock data
        result = await agent.process(latitude, longitude, start_time, end_time)

        print("\nWeather Agent Result:")
        print("=" * 50)
        for key, value in result.items():
            print(f"{key}: {value}")

        # Validate that we got the expected structure
        required_fields = ['agent', 'source', 'timestamp', 'confidence']
        for field in required_fields:
            if field not in result:
                print(f"ERROR: Missing required field '{field}'")
                return False

        # Check that we have weather-specific fields
        weather_fields = ['wind_speed_kmh', 'wind_direction_deg', 'rainfall_mm',
                         'visibility_km', 'temperature_c', 'humidity_percent',
                         'pressure_hpa', 'forecast_hours']

        missing_weather_fields = [field for field in weather_fields if field not in result]
        if missing_weather_fields:
            print(f"WARNING: Missing weather fields: {missing_weather_fields}")
        else:
            print("\n[+] All required weather fields present")

        print(f"\n[+] Agent processed successfully!")
        print(f"  Source: {result.get('source', 'Unknown')}")
        print(f"  Confidence: {result.get('confidence', 0.0)}")

        return True

    except Exception as e:
        print(f"ERROR: Failed to test weather agent: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_weather_agent())
    sys.exit(0 if success else 1)