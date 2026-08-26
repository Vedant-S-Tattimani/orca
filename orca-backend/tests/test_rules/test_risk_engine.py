"""
Test for the Risk Engine
"""
import pytest
from app.rules.risk_engine import RiskEngine, RiskLevel

def test_risk_engine_initialization():
    """Test that the risk engine initializes correctly"""
    engine = RiskEngine()
    assert engine is not None
    assert hasattr(engine, 'thresholds')

def test_assess_weather_risk():
    """Test weather risk assessment"""
    engine = RiskEngine()

    # Test data with high wind speed
    weather_data = {
        "wind_speed_kmh": 45,  # Should be high risk (>40)
        "rainfall_mm": 5,      # Should be moderate risk (>2.5)
        "visibility_km": 3     # Should be high risk (<5)
    }

    flags = engine.assess_weather_risk(weather_data)

    # Should have flags for wind, rain, and visibility
    assert len(flags) >= 3

    # Check that we have the expected risk levels
    risk_levels = [flag.risk_level.value for flag in flags]
    assert "high" in risk_levels  # Wind and visibility
    assert "moderate" in risk_levels  # Rainfall

def test_assess_sea_state_risk():
    """Test sea-state risk assessment"""
    engine = RiskEngine()

    # Test data with high wave height
    sea_state_data = {
        "wave_height_m": 3.0,   # Should be high risk (>2.5)
        "swell_height_m": 1.8,  # Should be high risk (>1.5)
        "current_speed_knots": 2.5  # Should be high risk (>2)
    }

    flags = engine.assess_sea_state_risk(sea_state_data)

    # Should have flags for wave, swell, and current
    assert len(flags) >= 3

    # Check that we have the expected risk levels
    risk_levels = [flag.risk_level.value for flag in flags]
    assert "high" in risk_levels  # All three should be high

def test_get_overall_risk_level():
    """Test overall risk level calculation"""
    engine = RiskEngine()

    # Mock risk flags with different levels
    risk_flags = {
        "weather": [
            {"field": "wind_speed_kmh", "risk_level": "moderate"},
            {"field": "visibility_km", "risk_level": "low"}
        ],
        "sea_state": [
            {"field": "wave_height_m", "risk_level": "high"},
            {"field": "swell_height_m", "risk_level": "moderate"}
        ]
    }

    overall_risk = engine.get_overall_risk_level(risk_flags)
    assert overall_risk == RiskLevel.HIGH  # Should be highest level present

def test_get_overall_risk_level_all_low():
    """Test overall risk level when all are low"""
    engine = RiskEngine()

    risk_flags = {
        "weather": [
            {"field": "wind_speed_kmh", "risk_level": "low"}
        ],
        "sea_state": [
            {"field": "wave_height_m", "risk_level": "low"}
        ]
    }

    overall_risk = engine.get_overall_risk_level(risk_flags)
    assert overall_risk == RiskLevel.LOW

if __name__ == "__main__":
    pytest.main([__file__])