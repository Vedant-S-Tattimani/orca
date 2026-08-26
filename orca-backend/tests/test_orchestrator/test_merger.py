"""
Test for the Orchestrator Merger
"""
import pytest
from datetime import datetime
from app.orchestrator.merger import Merger

def test_merger_initialization():
    """Test that the merger initializes correctly"""
    merger = Merger()
    assert merger is not None

def test_merge_agent_outputs():
    """Test merging agent outputs"""
    merger = Merger()

    # Mock agent outputs
    agent_outputs = {
        "weather": {
            "agent": "weather",
            "wind_speed_kmh": 15.2,
            "rainfall_mm": 0.0,
            "source": "IMD",
            "timestamp": datetime.utcnow().isoformat(),
            "confidence": 0.9
        },
        "sea_state": {
            "agent": "sea_state",
            "wave_height_m": 1.8,
            "swell_height_m": 1.2,
            "source": "INCOIS",
            "timestamp": datetime.utcnow().isoformat(),
            "confidence": 0.85
        }
    }

    query_location = {
        "name": "Kollam coast",
        "latitude": 8.8932,
        "longitude": 76.6141,
        "radius_km": 5.0
    }

    query_time_window = {
        "start": datetime(2026, 8, 25, 5, 0, 0).isoformat(),
        "end": datetime(2026, 8, 25, 10, 0, 0).isoformat()
    }

    merged = merger.merge_agent_outputs(
        agent_outputs=agent_outputs,
        query_location=query_location,
        query_time_window=query_time_window
    )

    # Check structure
    assert "query_metadata" in merged
    assert "agent_data" in merged
    assert "combined_insights" in merged
    assert "data_quality" in merged

    # Check data quality
    assert merged["data_quality"]["agents_responding"] == 2
    assert merged["data_quality"]["total_agents"] == 2
    assert merged["data_quality"]["has_errors"] == False

    # Check that agent data is preserved
    assert merged["agent_data"]["weather"]["wind_speed_kmh"] == 15.2
    assert merged["agent_data"]["sea_state"]["wave_height_m"] == 1.8

    # Check combined insights
    assert "weather" in merged["combined_insights"]
    assert "sea_state" in merged["combined_insights"]
    assert merged["combined_insights"]["weather"]["agent"] == "weather"
    assert merged["combined_insights"]["sea_state"]["agent"] == "sea_state"

def test_merge_with_errors():
    """Test merging when some agents have errors"""
    merger = Merger()

    agent_outputs = {
        "weather": {
            "agent": "weather",
            "wind_speed_kmh": 15.2,
            "source": "IMD",
            "timestamp": datetime.utcnow().isoformat(),
            "confidence": 0.9
        },
        "sea_state": {
            "agent": "sea_state",
            "error": "API timeout",
            "source": "error",
            "timestamp": datetime.utcnow().isoformat(),
            "confidence": 0.0
        }
    }

    query_location = {
        "name": "Kollam coast",
        "latitude": 8.8932,
        "longitude": 76.6141
    }

    query_time_window = {
        "start": datetime(2026, 8, 25, 5, 0, 0).isoformat(),
        "end": datetime(2026, 8, 25, 10, 0, 0).isoformat()
    }

    merged = merger.merge_agent_outputs(
        agent_outputs=agent_outputs,
        query_location=query_location,
        query_time_window=query_time_window
    )

    # Check data quality reflects error
    assert merged["data_quality"]["agents_responding"] == 1
    assert merged["data_quality"]["total_agents"] == 2
    assert merged["data_quality"]["has_errors"] == True

    # Check that error is captured in insights
    assert "error" in merged["combined_insights"]["sea_state"]
    assert merged["combined_insights"]["sea_state"]["status"] == "failed"

if __name__ == "__main__":
    pytest.main([__file__])