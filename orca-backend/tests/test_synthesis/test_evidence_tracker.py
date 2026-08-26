"""
Test for the Evidence Tracker
"""
import pytest
from app.synthesis.evidence_tracker import EvidenceTracker, Evidence, Claim

def test_evidence_tracker_initialization():
    """Test that the evidence tracker initializes correctly"""
    tracker = EvidenceTracker()
    assert tracker is not None
    assert len(tracker.evidence_store) == 0
    assert len(tracker.claims) == 0

def test_add_evidence():
    """Test adding evidence to the tracker"""
    tracker = EvidenceTracker()

    evidence_id = tracker.add_evidence(
        source="IMD",
        field="wind_speed_kmh",
        timestamp="2026-08-24T05:00:00Z",
        value=15.2,
        confidence=0.95
    )

    assert evidence_id is not None
    assert len(tracker.evidence_store) == 1
    assert evidence_id in tracker.evidence_store

    evidence = tracker.evidence_store[evidence_id]
    assert evidence.source == "IMD"
    assert evidence.field == "wind_speed_kmh"
    assert evidence.value == 15.2
    assert evidence.confidence == 0.95

def test_create_claim():
    """Test creating a claim with evidence"""
    tracker = EvidenceTracker()

    # Add some evidence first
    evidence_id1 = tracker.add_evidence(
        source="IMD",
        field="wind_speed_kmh",
        timestamp="2026-08-24T05:00:00Z",
        value=15.2,
        confidence=0.95
    )

    evidence_id2 = tracker.add_evidence(
        source="INCOIS",
        field="wave_height_m",
        timestamp="2026-08-24T05:00:00Z",
        value=1.8,
        confidence=0.90
    )

    # Create a claim
    claim = tracker.create_claim(
        statement="Wind speed is 15.2 km/h and wave height is 1.8 m",
        evidence_ids=[evidence_id1, evidence_id2],
        risk_level="low"
    )

    assert claim is not None
    assert len(tracker.claims) == 1
    assert claim.statement == "Wind speed is 15.2 km/h and wave height is 1.8 m"
    assert claim.risk_level == "low"
    assert len(claim.evidence) == 2

def test_extract_evidence_from_agent_data():
    """Test extracting evidence from agent data"""
    tracker = EvidenceTracker()

    agent_data = {
        "agent": "weather",
        "wind_speed_kmh": 15.2,
        "rainfall_mm": 0.0,
        "source": "IMD",
        "timestamp": "2026-08-24T05:00:00Z",
        "confidence": 0.95
    }

    evidence_ids = tracker.extract_evidence_from_agent_data("weather", agent_data)

    # Should extract wind_speed_kmh and rainfall_mm (excluding metadata fields)
    assert len(evidence_ids) == 2
    assert len(tracker.evidence_store) == 2

    # Check that the evidence was stored correctly
    for evidence_id in evidence_ids:
        evidence = tracker.evidence_store[evidence_id]
        assert evidence.source == "IMD"
        assert evidence.metadata.get("agent") == "weather"  # From metadata
        assert evidence.field in ["weather.wind_speed_kmh", "weather.rainfall_mm"]

def test_get_all_evidence():
    """Test getting all evidence"""
    tracker = EvidenceTracker()

    # Add multiple evidence pieces
    tracker.add_evidence("IMD", "wind_speed_kmh", "2026-08-24T05:00:00Z", 15.2)
    tracker.add_evidence("INCOIS", "wave_height_m", "2026-08-24T05:00:00Z", 1.8)
    tracker.add_evidence("IMD", "temperature_c", "2026-08-24T05:00:00Z", 28.5)

    all_evidence = tracker.get_all_evidence()
    assert len(all_evidence) == 3

    # Check structure
    for evidence in all_evidence:
        assert "source" in evidence
        assert "field" in evidence
        assert "value" in evidence
        assert "timestamp" in evidence

if __name__ == "__main__":
    pytest.main([__file__])