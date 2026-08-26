"""
Test for the Weather Agent
"""
import pytest
from datetime import datetime, timedelta
from app.agents.weather_agent import WeatherAgent

@pytest.mark.asyncio
async def test_weather_agent_process():
    """Test that the weather agent processes data correctly"""
    agent = WeatherAgent()

    # Test with sample coordinates
    latitude = 8.8932
    longitude = 76.6141
    start_time = datetime.utcnow()
    end_time = start_time + timedelta(hours=5)

    result = await agent.process(latitude, longitude, start_time, end_time)

    # Basic assertions
    assert "agent" in result
    assert result["agent"] == "weather"
    assert "timestamp" in result
    assert "confidence" in result
    assert 0.0 <= result["confidence"] <= 1.0

    # If no error, check for expected weather fields
    if "error" not in result:
        expected_fields = [
            "wind_speed_kmh", "wind_direction_deg", "rainfall_mm",
            "visibility_km", "temperature_c", "humidity_percent"
        ]
        for field in expected_fields:
            assert field in result, f"Missing field: {field}"

if __name__ == "__main__":
    pytest.main([__file__])