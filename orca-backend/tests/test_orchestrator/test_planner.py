"""
Test for the Orchestrator Planner
"""
import pytest
from datetime import datetime
from app.interface.schemas import StructuredQuery, TaskType, Location, TimeWindow
from app.orchestrator.planner import Planner

def test_planner_initialization():
    """Test that the planner initializes correctly"""
    planner = Planner()
    assert planner is not None
    assert hasattr(planner, 'task_to_agents')

def test_create_plan_safety_check():
    """Test creating a plan for safety check task"""
    planner = Planner()

    query = StructuredQuery(
        task=TaskType.SAFETY_CHECK,
        location=Location(
            name="Kollam coast",
            latitude=8.8932,
            longitude=76.6141
        ),
        time_window=TimeWindow(
            start=datetime(2026, 8, 25, 5, 0, 0),
            end=datetime(2026, 8, 25, 10, 0, 0)
        ),
        original_query="Is it safe for me to go fishing tomorrow morning near Kollam?",
        language="en"
    )

    plan = planner.create_plan(query)

    # Should include weather, sea_state, and hazard agents for safety check
    assert "weather" in plan.agents_to_invoke
    assert "sea_state" in plan.agents_to_invoke
    assert "hazard" in plan.agents_to_invoke
    assert plan.location_resolution_needed == True
    assert plan.rag_query_needed == True  # Safety check uses RAG for advisories

def test_create_plan_fishing_zones():
    """Test creating a plan for fishing zones task"""
    planner = Planner()

    query = StructuredQuery(
        task=TaskType.FISHING_ZONES,
        location=Location(
            name="Kochi coast",
            latitude=9.9312,
            longitude=76.2673
        ),
        time_window=TimeWindow(
            start=datetime(2026, 8, 25, 6, 0, 0),
            end=datetime(2026, 8, 25, 12, 0, 0)
        ),
        original_query="Where are the best fishing zones near Kochi today?",
        language="en"
    )

    plan = planner.create_plan(query)

    # Should include pfz_satellite, weather, and sea_state for fishing zones
    assert "pfz_satellite" in plan.agents_to_invoke
    assert "weather" in plan.agents_to_invoke
    assert "sea_state" in plan.agents_to_invoke

def test_create_plan_weather_info():
    """Test creating a plan for weather info task"""
    planner = Planner()

    query = StructuredQuery(
        task=TaskType.WEATHER_INFO,
        location=Location(
            name="Goa coast",
            latitude=15.2993,
            longitude=74.1240
        ),
        time_window=TimeWindow(
            start=datetime(2026, 8, 25, 8, 0, 0),
            end=datetime(2026, 8, 25, 17, 0, 0)
        ),
        original_query="What's the weather like in Goa today?",
        language="en"
    )

    plan = planner.create_plan(query)

    # Should include weather agent for weather info
    assert "weather" in plan.agents_to_invoke
    assert plan.location_resolution_needed == True
    assert plan.rag_query_needed == False  # Weather info doesn't need RAG advisories

if __name__ == "__main__":
    pytest.main([__file__])