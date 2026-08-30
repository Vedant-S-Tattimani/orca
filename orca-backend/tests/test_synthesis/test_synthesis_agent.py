import pytest
import asyncio
from app.synthesis.synthesis_agent import SynthesisAgent

@pytest.mark.asyncio
async def test_all_agents_timeout_scenario():
    """
    Test that when all agents timeout or fail (return 'error' or empty data),
    the Synthesis Agent handles it gracefully and returns a 'couldn't retrieve data' message
    without crashing.
    """
    synthesis_agent = SynthesisAgent()
    
    # Simulate all agents failing/timing out
    merged_agent_data = {
        "weather_agent": {"error": "API timeout"},
        "sea_state_agent": {"error": "API timeout"},
        "hazard_agent": {"error": "API timeout"},
        "pfz_satellite_agent": {"error": "API timeout"}
    }
    
    risk_flags = {}
    rag_evidence = []
    
    result = await synthesis_agent.synthesize_response(
        merged_agent_data=merged_agent_data,
        risk_flags=risk_flags,
        rag_evidence=rag_evidence,
        original_query="Is it safe to go out today?",
        query_language="en",
        history=[]
    )
    
    # Assert it didn't crash and returns a valid structure
    assert result is not None
    assert "response" in result
    
    # Assert that the response clearly states failure
    response_lower = result["response"].lower()
    
    # Checking for typical fallback phrases
    fallback_indicators = ["could not retrieve", "couldn't retrieve", "failed to retrieve", "unable to retrieve", "unavailable", "timeout", "offline", "error"]
    
    has_fallback_phrase = any(phrase in response_lower for phrase in fallback_indicators)
                          
    assert has_fallback_phrase, f"Expected a clear fallback message due to agent timeout, but got: {result['response']}"
