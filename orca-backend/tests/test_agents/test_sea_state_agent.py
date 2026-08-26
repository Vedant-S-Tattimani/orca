"""
Test for the Sea-State Agent
"""
import pytest
from datetime import datetime, timedelta
from app.agents.sea_state_agent import SeaStateAgent

@pytest.mark.asyncio
async def test_sea_state_agent_process():
    """Test that the sea-state agent processes data correctly"""
    agent = SeaStateAgent()

    # Test with sample coordinates
    latitude = 8.8932
    longitude = 76.6141
    start_time = datetime.utcnow()
    end_time = start_time + timedelta(hours=5)

    result = await agent.process(latitude, longitude, start_time, end_time)

    # Basic assertions
    assert "agent" in result
    assert result["agent"] == "sea_state"
    assert "timestamp" in result
    assert "confidence" in result
    assert 0.0 <= result["confidence"] <= 1.0

    # If no error, check for expected sea-state fields
    if "error" not in result:
        expected_fields = [
            "wave_height_m", "wave_period_s", "swell_height_m",
            "swell_direction_deg", "current_speed_knots", "current_direction_deg",
            "tide_height_m"
        ]
        for field in expected_fields:
            assert field in result, f"Missing field: {field}"

if __name__ == "__main__":
    pytest.main([__file__])