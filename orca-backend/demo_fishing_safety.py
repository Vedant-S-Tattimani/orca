"""
End-to-end demo of ORCA backend for the fishing safety check example
From the architecture document: "Is it safe for me to go fishing tomorrow morning near Kollam?"
"""
import asyncio
from datetime import datetime, timedelta
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import ORCA components
from app.interface.schemas import StructuredQuery, TaskType, Location, TimeWindow
from app.orchestrator.location_resolver import LocationResolver
from app.orchestrator.planner import Planner
from app.orchestrator.merger import Merger
from app.agents.weather_agent import WeatherAgent
from app.agents.sea_state_agent import SeaStateAgent
from app.agents.hazard_agent import HazardAgent
from app.agents.pfz_agent import PFZAgent
from app.rules.risk_engine import RiskEngine
from app.synthesis.synthesis_agent import SynthesisAgent
from app.response.card_builder import CardBuilder

async def demo_fishing_safety_check():
    """
    Demo the complete flow for the fishing safety check query:
    "Is it safe for me to go fishing tomorrow morning near Kollam?"
    """
    logger.info("Starting ORCA Fishing Safety Check Demo")
    logger.info("=" * 50)

    # Step 1: Parse the user query (Interface Layer)
    logger.info("Step 1: Parsing user query...")
    query = StructuredQuery(
        task=TaskType.SAFETY_CHECK,
        location=Location(
            name="Kollam coast",
            latitude=8.8932,
            longitude=76.6141,
            radius_km=5.0
        ),
        time_window=TimeWindow(
            start=datetime.utcnow().replace(hour=5, minute=0, second=0, microsecond=0),
            end=datetime.utcnow().replace(hour=10, minute=0, second=0, microsecond=0) + timedelta(days=1)
        ),
        original_query="Is it safe for me to go fishing tomorrow morning near Kollam?",
        language="en"
    )
    logger.info(f"Parsed query: {query.original_query}")

    # Step 2: Orchestration Planning (Orchestrator Layer)
    logger.info("\nStep 2: Creating orchestration plan...")
    planner = Planner()
    plan = planner.create_plan(query)
    logger.info(f"Plan: {plan.to_dict()}")

    # Step 3: Location Resolution (Orchestrator Layer)
    logger.info("\nStep 3: Resolving location...")
    resolver = LocationResolver()
    location_info = resolver.resolve_with_radius("Kollam coast", radius_km=5.0)
    logger.info(f"Resolved location: {location_info}")

    # Step 4: Invoke Specialist Agents (Agents Layer)
    logger.info("\nStep 4: Invoking specialist agents...")

    # Initialize agents
    weather_agent = WeatherAgent()
    sea_state_agent = SeaStateAgent()
    hazard_agent = HazardAgent()
    pfz_agent = PFZAgent()

    # Execute agents in parallel (as mentioned in architecture)
    agent_tasks = [
        weather_agent.process(
            latitude=location_info["latitude"],
            longitude=location_info["longitude"],
            start_time=query.time_window.start,
            end_time=query.time_window.end,
            radius_km=location_info["radius_km"]
        ),
        sea_state_agent.process(
            latitude=location_info["latitude"],
            longitude=location_info["longitude"],
            start_time=query.time_window.start,
            end_time=query.time_window.end,
            radius_km=location_info["radius_km"]
        ),
        hazard_agent.process(
            latitude=location_info["latitude"],
            longitude=location_info["longitude"],
            start_time=query.time_window.start,
            end_time=query.time_window.end,
            radius_km=location_info["radius_km"]
        ),
        pfz_agent.process(
            latitude=location_info["latitude"],
            longitude=location_info["longitude"],
            start_time=query.time_window.start,
            end_time=query.time_window.end,
            radius_km=location_info["radius_km"]
        )
    ]

    # Wait for all agents to complete
    agent_results = await asyncio.gather(*agent_tasks, return_exceptions=True)

    # Process results
    agent_outputs = {}
    agent_names = ["weather", "sea_state", "hazard", "pfz_satellite"]

    for i, result in enumerate(agent_results):
        agent_name = agent_names[i]
        if isinstance(result, Exception):
            logger.error(f"Agent {agent_name} failed: {result}")
            agent_outputs[agent_name] = {
                "agent": agent_name,
                "error": str(result),
                "source": "error",
                "timestamp": datetime.utcnow().isoformat(),
                "confidence": 0.0
            }
        else:
            agent_outputs[agent_name] = result
            logger.info(f"{agent_name.capitalize()} agent completed")

    # Step 5: Merge Agent Outputs (Orchestrator Layer)
    logger.info("\nStep 5: Merging agent outputs...")
    merger = Merger()
    merged_data = merger.merge_agent_outputs(
        agent_outputs=agent_outputs,
        query_location={
            "name": query.location.name,
            "latitude": query.location.latitude,
            "longitude": query.location.longitude,
            "radius_km": query.location.radius_km
        },
        query_time_window={
            "start": query.time_window.start.isoformat(),
            "end": query.time_window.end.isoformat()
        }
    )
    logger.info(f"Merge complete: {merged_data['data_quality']['agents_responding']}/{merged_data['data_quality']['total_agents']} agents responding")

    # Step 6: Risk Assessment (Rules Layer)
    logger.info("\nStep 6: Assessing risks...")
    risk_engine = RiskEngine()

    # Extract data for risk assessment
    weather_data = agent_outputs.get("weather", {})
    if not weather_data or "error" in weather_data:
        weather_data = agent_outputs.get("openmeteo_weather", {})

    sea_state_data = agent_outputs.get("sea_state", {})
    if not sea_state_data or "error" in sea_state_data:
        sea_state_data = agent_outputs.get("openmeteo_marine", {})

    hazard_data = agent_outputs.get("hazard", {})
    pfz_data = agent_outputs.get("pfz_satellite", {})

    risk_flags = risk_engine.assess_all_risks(
        weather_data=weather_data if "error" not in weather_data else None,
        sea_state_data=sea_state_data if "error" not in sea_state_data else None,
        hazard_data=hazard_data if "error" not in hazard_data else None,
        pfz_data=pfz_data if "error" not in pfz_data else None
    )

    overall_risk = risk_engine.get_overall_risk_level(risk_flags)
    logger.info(f"Overall risk level: {overall_risk.value}")
    logger.info(f"Risk flags: {risk_flags}")

    # Step 7: Synthesis (Synthesis Layer)
    logger.info("\nStep 7: Synthesizing response...")
    synthesis_agent = SynthesisAgent()

    # For demo, we'll use empty RAG evidence (would come from vector store in production)
    rag_evidence = []

    synthesized_response = await synthesis_agent.synthesize_response(
        merged_agent_data=merged_data,
        risk_flags=risk_flags,
        rag_evidence=rag_evidence,
        original_query=query.original_query
    )

    logger.info("Synthesis complete")

    # Step 8: Response Formatting (Response Layer)
    logger.info("\nStep 8: Building response card...")
    card_builder = CardBuilder()

    # Generate different format outputs
    json_card = card_builder.build_risk_card(synthesized_response, "json")
    text_card = card_builder.build_risk_card(synthesized_response, "text")
    html_card = card_builder.build_risk_card(synthesized_response, "html")

    # Step 9: Display Results
    logger.info("\n" + "=" * 50)
    logger.info("ORCA FISHING SAFETY CHECK - RESULTS")
    logger.info("=" * 50)

    logger.info(f"\nQuery: {query.original_query}")
    logger.info(f"Location: {query.location.name} ({query.location.latitude}, {query.location.longitude})")
    logger.info(f"Time: {query.time_window.start.strftime('%Y-%m-%d %H:%M')} to {query.time_window.end.strftime('%Y-%m-%d %H:%M')}")

    logger.info(f"\nOverall Risk Level: {synthesized_response['risk_assessment']['overall_level'].upper()}")

    logger.info(f"\nAgent Status:")
    for agent_name, data in merged_data["agent_data"].items():
        status = "✓ OK" if "error" not in data else "✗ ERROR"
        logger.info(f"  {agent_name.capitalize()}: {status}")

    logger.info(f"\nEvidence Collected: {synthesized_response['evidence']['count']} data points")

    logger.info(f"\nSynthesized Response:")
    logger.info("-" * 30)
    logger.info(synthesized_response["response"])

    logger.info(f"\nKey Points:")
    for i, point in enumerate(json_card["orca_response"]["key_points"], 1):
        logger.info(f"  {i}. {point}")

    logger.info(f"\nRecommendation:")
    logger.info(f"  {json_card['orca_response']['recommendation']}")

    logger.info(f"\nEvidence Sources: {', '.join(json_card['orca_response']['evidence']['sources'])}")

    # Show text format (good for console/demo)
    logger.info(f"\nText Format Response:")
    logger.info("-" * 30)
    logger.info(text_card["content"])

    logger.info("\n" + "=" * 50)
    logger.info("Demo Complete!")
    logger.info("=" * 50)

    return {
        "query": query.dict(),
        "plan": plan.to_dict(),
        "location_resolved": location_info,
        "agent_outputs": agent_outputs,
        "merged_data": merged_data,
        "risk_assessment": {
            "overall_level": overall_risk.value,
            "flags": risk_flags
        },
        "synthesized_response": synthesized_response,
        "response_cards": {
            "json": json_card,
            "text": text_card,
            "html": html_card
        }
    }

if __name__ == "__main__":
    # Run the demo
    result = asyncio.run(demo_fishing_safety_check())
    logger.info("Demo script completed successfully")