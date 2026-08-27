from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class HistoricalReadingModel(BaseModel):
    """Pydantic schema for historical_readings MongoDB collection"""
    location: str = Field(..., description="Name of the location")
    type: str = Field(..., description="Type of reading (e.g. SST, chlorophyll, wind)")
    value: float = Field(..., description="Numerical value of the reading")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Time of observation")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional context or metadata")
    created_at: datetime = Field(default_factory=datetime.utcnow)

class HazardAdvisoryModel(BaseModel):
    """Pydantic schema for hazard_advisories MongoDB collection"""
    id: str = Field(..., description="Unique alert ID")
    title: str = Field(..., description="Title of the advisory")
    severity: str = Field(..., description="Severity level (e.g., HIGH, WARNING, EXTREME)")
    location: str = Field(..., description="Affected location")
    time: str = Field(..., description="ISO formatted time string")
    hazard: str = Field(..., description="Type of hazard (e.g., Extreme Wind)")
    recommended_action: str = Field(..., description="Recommended safety action")
    provenance: str = Field(..., description="Source of the alert")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Time the alert was created")

class UserQueryModel(BaseModel):
    """Pydantic schema for user_queries MongoDB collection"""
    user_id: Optional[str] = Field(None, description="Optional user ID if authenticated")
    query_text: str = Field(..., description="Raw user query")
    parsed_intent: str = Field(..., description="Extracted intent")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    execution_time_ms: Optional[float] = Field(None, description="Time taken to serve request")

class AlertSubscriptionModel(BaseModel):
    """Pydantic schema for alert_subscriptions MongoDB collection"""
    phone_number: str = Field(..., description="Phone number with country code")
    location: str = Field(..., description="Location to monitor")
    created_at: datetime = Field(default_factory=datetime.utcnow)
