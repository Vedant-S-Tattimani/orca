"""
Orchestrator planner for ORCA
Determines which specialist agents to invoke based on the structured query
"""
from typing import List, Dict, Any, Optional
from enum import Enum
import logging
from datetime import datetime

from ..interface.schemas import TaskType, StructuredQuery

logger = logging.getLogger(__name__)

class AgentType(str, Enum):
    """Types of specialist agents available in ORCA"""
    WEATHER = "weather"
    SEA_STATE = "sea_state"
    HAZARD = "hazard"
    PFZ_SATELLITE = "pfz_satellite"
    OPENMETEO_WEATHER = "openmeteo_weather"
    OPENMETEO_MARINE = "openmeteo_marine"
    GEOFENCE = "geofence"
    GIS = "gis_agent"
    AIS = "ais_agent"
    RISK = "risk_agent"
    ROUTING = "routing_agent"

class OrchestrationPlan:
    """
    Represents the plan for which agents to invoke and in what order
    """
    def __init__(
        self,
        agents_to_invoke: List[AgentType],
        location_resolution_needed: bool = True,
        rag_query_needed: bool = False,
        priority_order: List[AgentType] = None
    ):
        self.agents_to_invoke = agents_to_invoke
        self.location_resolution_needed = location_resolution_needed
        self.rag_query_needed = rag_query_needed
        self.priority_order = priority_order or agents_to_invoke

    def to_dict(self) -> Dict[str, Any]:
        return {
            "agents_to_invoke": [agent.value for agent in self.agents_to_invoke],
            "location_resolution_needed": self.location_resolution_needed,
            "rag_query_needed": self.rag_query_needed,
            "priority_order": [agent.value for agent in self.priority_order]
        }

class Planner:
    """
    Determines which specialist agents to invoke based on the user's query intent
    Implements the logic from the architecture document: "Decompose by data domain, not by query type"
    """

    def __init__(self):
        # Mapping of task types to required agents
        # Based on the architecture document's design principle: "Decompose by data domain, not by query type"
        # We include both official agents (IMD/INCOIS) and Open-Meteo agents as alternatives/fallbacks
        self.task_to_agents = {
            TaskType.SAFETY_CHECK: [
                AgentType.WEATHER,
                AgentType.SEA_STATE,
                AgentType.HAZARD,
                AgentType.GIS,
                AgentType.RISK
            ],
            TaskType.FISHING_ZONES: [
                AgentType.PFZ_SATELLITE,
                AgentType.WEATHER,
                AgentType.SEA_STATE,
                AgentType.GIS,
                AgentType.RISK
            ],
            TaskType.ROUTE_PLANNING: [
                AgentType.WEATHER,
                AgentType.SEA_STATE,
                AgentType.HAZARD,
                AgentType.GIS,
                AgentType.RISK,
                AgentType.ROUTING
            ],
            TaskType.HAZARD_ALERT: [
                AgentType.HAZARD,
                AgentType.WEATHER,
                AgentType.SEA_STATE,
                AgentType.GIS,
                AgentType.RISK
            ],
            TaskType.WEATHER_INFO: [
                AgentType.WEATHER
            ],
            TaskType.GENERAL_INQUIRY: [
                AgentType.WEATHER,
                AgentType.SEA_STATE,
                AgentType.HAZARD,
                AgentType.PFZ_SATELLITE,
                AgentType.GIS,
                AgentType.AIS,
                AgentType.RISK,
                AgentType.ROUTING
            ]
        }

        # Tasks that benefit from RAG queries (advisories, warnings, etc.)
        self.rag_tasks = {
            TaskType.SAFETY_CHECK,
            TaskType.FISHING_ZONES,
            TaskType.ROUTE_PLANNING,
            TaskType.HAZARD_ALERT
        }

    def structure_query(self, query_data: Dict[str, Any]) -> 'StructuredQuery':
        """
        Convert raw query data into a StructuredQuery object

        Args:
            query_data: Raw query data from the API

        Returns:
            StructuredQuery object
        """
        from ..interface.schemas import StructuredQuery, Location, TimeWindow
        from datetime import datetime

        # Extract location information
        location_data = query_data.get("location", {})
        location = Location(
            name=location_data.get("name", "Unknown"),
            latitude=location_data.get("latitude", 0.0),
            longitude=location_data.get("longitude", 0.0)
        )

        # Extract time window
        time_window_data = query_data.get("time_window", {})
        start_time = datetime.fromisoformat(time_window_data.get("start", datetime.utcnow().isoformat()).replace('Z', '+00:00'))
        end_time = datetime.fromisoformat(time_window_data.get("end", datetime.utcnow().isoformat()).replace('Z', '+00:00'))
        time_window = TimeWindow(start=start_time, end=end_time)

        # Create structured query
        structured_query = StructuredQuery(
            task=TaskType(query_data.get("task", "general_inquiry")),
            location=location,
            time_window=time_window,
            confidence=query_data.get("confidence", 0.0),
            original_query=query_data.get("original_query", ""),
            language=query_data.get("language", "en")
        )

        return structured_query

    def create_agent_plan(self, structured_query: 'StructuredQuery', location_info: Dict[str, Any], time_window_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a detailed agent plan based on the structured query and resolved location

        Args:
            structured_query: The structured query
            location_info: Resolved location information
            time_window_dict: Time window information

        Returns:
            Dictionary containing agent plan and risk flags
        """
        # Get the base orchestration plan
        plan = self.create_plan(structured_query)

        # Initialize risk flags dictionary (will be populated by individual agents)
        risk_flags = {}

        # Add task-specific risk assessment logic
        if structured_query.task == TaskType.SAFETY_CHECK:
            # For safety checks, we'll assess risks based on agent outputs later
            pass
        elif structured_query.task == TaskType.FISHING_ZONES:
            # For fishing zones, we might want to prioritize PFZ data
            pass

        return {
            "agents": plan.agents_to_invoke,
            "risk_flags": risk_flags,
            "plan_dict": plan.to_dict()
        }

    async def invoke_agents(self, agent_types: List[str], latitude: float, longitude: float,
                          start_time: datetime, end_time: datetime, radius_km: Optional[float] = None) -> Dict[str, Any]:
        """
        Invoke specialist agents in parallel to fetch data

        Args:
            agent_types: List of agent type strings to invoke
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            start_time: Start of time window
            end_time: End of time window
            radius_km: Optional search radius

        Returns:
            Dictionary mapping agent names to their results
        """
        from app.agents.weather_agent import WeatherAgent
        from app.agents.sea_state_agent import SeaStateAgent
        from app.agents.hazard_agent import HazardAgent
        from app.agents.pfz_agent import PFZAgent
        from app.agents.openmeteo_weather_agent import OpenMeteoWeatherAgent
        from app.agents.openmeteo_marine_agent import OpenMeteoMarineAgent
        from app.agents.gis_agent import GISAgent
        from app.agents.ais_agent import AISAgent
        from app.agents.risk_agent import RiskAgent
        from app.agents.routing_agent import RoutingAgent

        # Map agent type strings to agent classes
        agent_classes = {
            "weather": WeatherAgent,
            "sea_state": SeaStateAgent,
            "hazard": HazardAgent,
            "pfz_satellite": PFZAgent,
            "openmeteo_weather": OpenMeteoWeatherAgent,
            "openmeteo_marine": OpenMeteoMarineAgent,
            "gis_agent": GISAgent,
            "ais_agent": AISAgent,
            "risk_agent": RiskAgent,
            "routing_agent": RoutingAgent
        }

        # Create agent instances
        agents = {}
        for agent_type in agent_types:
            if agent_type in agent_classes:
                agents[agent_type] = agent_classes[agent_type]()

        # Invoke all agents in parallel properly using asyncio.gather
        agent_tasks = []
        agent_names = []
        import asyncio
        for agent_name, agent_instance in agents.items():
            process_coro = agent_instance.process(
                latitude=latitude,
                longitude=longitude,
                start_time=start_time,
                end_time=end_time,
                radius_km=radius_km
            )
            # Wrap with a 10 second timeout
            task = asyncio.create_task(asyncio.wait_for(process_coro, timeout=10.0))
            agent_tasks.append(task)
            agent_names.append(agent_name)

        # Wait for all agents to complete concurrently
        results = {}
        gathered_results = await asyncio.gather(*agent_tasks, return_exceptions=True)
        
        for agent_name, result in zip(agent_names, gathered_results):
            if isinstance(result, Exception):
                logger.error(f"Error invoking agent {agent_name}: {str(result)}")
                results[agent_name] = {
                    "agent": agent_name,
                    "error": str(result),
                    "source": "error",
                    "timestamp": datetime.utcnow().isoformat(),
                    "confidence": 0.0
                }
            else:
                results[agent_name] = result

        return results

    def retrieve_evidence(self, structured_query: 'StructuredQuery', location_info: Dict[str, Any],
                              time_window_dict: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Retrieve relevant evidence from the RAG store

        Args:
            structured_query: The structured query
            location_info: Resolved location information
            time_window_dict: Time window information

        Returns:
            List of evidence dictionaries
        """
        # For now, return empty list as RAG store implementation is future work
        # In production, this would query the vector store for relevant advisories, warnings, etc.
        logger.info("Retrieving evidence from RAG store (placeholder implementation)")
        return []

    def create_plan(self, query: StructuredQuery) -> OrchestrationPlan:
        """
        Create an orchestration plan based on the structured query
        (Backward compatibility method)

        Args:
            query: The structured query from the interface layer

        Returns:
            OrchestrationPlan specifying which agents to invoke
        """
        logger.info(f"Creating plan for task: {query.task}")

        # Get the base agents required for this task type
        agents_to_invoke = self.task_to_agents.get(query.task, [])

        # Determine if we need RAG query (for advisories, warnings, etc.)
        rag_query_needed = query.task in self.rag_tasks

        # Location resolution is almost always needed for geographic queries
        location_resolution_needed = query.task != TaskType.GENERAL_INQUIRY or \
                                       (hasattr(query.location, 'name') and query.location.name.strip() != "")

        # For safety checks and hazard alerts, prioritize hazard agent first
        priority_order = list(agents_to_invoke)  # Default order
        if query.task in [TaskType.SAFETY_CHECK, TaskType.HAZARD_ALERT]:
            if AgentType.HAZARD in agents_to_invoke:
                priority_order.remove(AgentType.HAZARD)
                priority_order.insert(0, AgentType.HAZARD)

        plan = OrchestrationPlan(
            agents_to_invoke=agents_to_invoke,
            location_resolution_needed=location_resolution_needed,
            rag_query_needed=rag_query_needed,
            priority_order=priority_order
        )

        logger.info(f"Created plan: {plan.to_dict()}")
        return plan

# Example usage:
# planner = Planner()
# query = StructuredQuery(
#     task=TaskType.SAFETY_CHECK,
#     location=Location(name="Kollam coast", latitude=8.8932, longitude=76.6141),
#     time_window=TimeWindow(start=datetime(...), end=datetime(...)),
#     original_query="Is it safe for me to go fishing tomorrow morning near Kollam?",
#     language="en"
# )
# plan = planner.create_plan(query)
# print(plan.to_dict())