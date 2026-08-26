"""
Pydantic models for ORCA interface layer
Defines the structured query and risk card formats for user inputs and API responses
"""
from datetime import datetime
from typing import Optional, List, Any
from pydantic import BaseModel, Field, model_validator
from enum import Enum


class TaskType(str, Enum):
    """Types of tasks users can ask ORCA to perform"""
    SAFETY_CHECK = "safety_check"
    FISHING_ZONES = "fishing_zones"
    ROUTE_PLANNING = "route_planning"
    HAZARD_ALERT = "hazard_alert"
    WEATHER_INFO = "weather_info"
    GENERAL_INQUIRY = "general_inquiry"


class Location(BaseModel):
    """Geographic location representation"""
    name: Optional[str] = Field("Unknown", description="Human-readable location name")
    lat: float = Field(..., description="Latitude coordinate")
    lon: float = Field(..., description="Longitude coordinate")
    radius_km: Optional[float] = Field(
        default=10.0,
        ge=0.1,
        le=100,
        description="Search radius around the point in kilometers"
    )

    @model_validator(mode="before")
    @classmethod
    def populate_lat_lon(cls, data: any) -> any:
        """Enforce compatibility between latitude/longitude and lat/lon"""
        if isinstance(data, dict):
            if "latitude" in data and "lat" not in data:
                data["lat"] = data["latitude"]
            if "longitude" in data and "lon" not in data:
                data["lon"] = data["longitude"]
        return data

    @property
    def latitude(self) -> float:
        return self.lat

    @property
    def longitude(self) -> float:
        return self.lon


class TimeWindow(BaseModel):
    """Time window for the query"""
    start: datetime = Field(..., description="Start time of the query window")
    end: datetime = Field(..., description="End time of the query window")

    def duration_hours(self) -> float:
        """Calculate duration in hours"""
        return (self.end - self.start).total_seconds() / 3600


class StructuredQuery(BaseModel):
    """
    Structured representation of user query after NLU processing
    """
    task: TaskType = Field(..., description="Type of task/user intent")
    location: Location = Field(..., description="Geographic focus of the query")
    time_window: TimeWindow = Field(..., description="Time period of interest")
    confidence: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Confidence score of the NLU parsing (0.0 to 1.0)"
    )
    original_query: str = Field(..., description="Original user query text")
    language: str = Field(
        default="en",
        description="Language of the original query (ISO 639-1 code)"
    )


class AgentStatus(BaseModel):
    """Status representation for specialist agents"""
    agent_name: str = Field(..., description="Name of the specialist agent")
    status: str = Field(..., description="Status string: 'ok', 'degraded', or 'failed'")
    note: Optional[str] = Field(None, description="Optional notes on health status")


class EvidenceItem(BaseModel):
    """A claim traceable to a source telemetry data point"""
    claim: str = Field(..., description="Statement claim")
    source: str = Field(..., description="Sensor source name")
    field: str = Field(..., description="Data field key")
    value: Any = Field(None, description="Data value")
    timestamp: datetime = Field(..., description="Observation timestamp")
    confidence: float = Field(..., description="Sensor confidence level")
    data_status: str = Field(default="LIVE", description="Status of the data source: 'LIVE' or 'SIMULATED'")


class RiskCard(BaseModel):
    """The safety card produced by ORCA's synthesis engine"""
    risk_level: str = Field(..., description="Calculated threat rating: 'low', 'medium', or 'high'")
    reasoning: str = Field(..., description="Natural language explanation of risk")
    recommendation: str = Field(..., description="Safety actions and parameters recommendation")
    evidence: List[EvidenceItem] = Field(default_factory=list, description="Sensor data points backing the claim")
    agent_status: List[AgentStatus] = Field(default_factory=list, description="Responding agent states")
    status: str = Field("done", description="Parsing status: 'processing', 'done', or 'failed'")
    dev_logs: List[str] = Field(default_factory=list, description="Internal agent execution and developer logs")