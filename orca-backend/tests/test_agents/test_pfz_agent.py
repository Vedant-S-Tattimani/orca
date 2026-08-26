"""
Test for the PFZ/Satellite Agent
"""
import pytest
from datetime import datetime, timedelta
from app.agents.pfz_agent import PFZAgent

@pytest.mark.asyncio
async def test_pfz_agent_process():
    """Test that the PFZ/satellite agent processes data correctly"""
    agent = PFZAgent()

    # Test with sample coordinates
    latitude = 8.8932
    longitude = 76.6141
    start_time = datetime.utcnow()
    end_time = start_time + timedelta(hours=5)

    result = await agent.process(latitude, longitude, start_time, end_time)

    # Basic assertions
    assert "agent" in result
    assert result["agent"] == "pfz_satellite"
    assert "timestamp" in result
    assert "confidence" in result
    assert 0.0 <= result["confidence"] <= 1.0

    # If no error, check for expected PFZ/satellite fields
    if "error" not in result:
        expected_fields = [
            "sst_c", "chlorophyll_a_mgm3", "pfz_confidence_percent"
        ]
        for field in expected_fields:
            assert field in result, f"Missing field: {field}"

if __name__ == "__main__":
    pytest.main([__file__])