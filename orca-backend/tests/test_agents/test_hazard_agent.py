"""
Test for the Hazard Agent
"""
import pytest
from datetime import datetime, timedelta
from app.agents.hazard_agent import HazardAgent

@pytest.mark.asyncio
async def test_hazard_agent_process():
    """Test that the hazard agent processes data correctly"""
    agent = HazardAgent()

    # Test with sample coordinates
    latitude = 8.8932
    longitude = 76.6141
    start_time = datetime.utcnow()
    end_time = start_time + timedelta(hours=5)

    result = await agent.process(latitude, longitude, start_time, end_time)

    # Basic assertions
    assert "agent" in result
    assert result["agent"] == "hazard"
    assert "timestamp" in result
    assert "confidence" in result
    assert 0.0 <= result["confidence"] <= 1.0

    # If no error, check for expected hazard fields
    if "error" not in result:
        expected_fields = [
            "cyclone_wind_speed_kmh", "lightning_probability_percent",
            "tsunami_wave_height_m"
        ]
        for field in expected_fields:
            assert field in result, f"Missing field: {field}"

if __name__ == "__main__":
    pytest.main([__file__])