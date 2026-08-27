"""
Evidence tracker for ORCA synthesis layer
Maintains (source, field, timestamp) triples for each claim in the final response
"""
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import logging
import hashlib

logger = logging.getLogger(__name__)

@dataclass
class Evidence:
    """Represents a single piece of evidence backing a claim"""
    source: str  # e.g., "IMD", "INCOIS", "ISRO Bhuvan"
    field: str   # e.g., "wave_height_m", "wind_speed_kmh"
    timestamp: str  # ISO format timestamp of when the data was generated
    value: Any   # The actual value of the field
    data_status: str = "SIMULATED" # LIVE, SIMULATED, CACHED, etc.
    confidence: float = 1.0  # Confidence in this evidence (0.0 to 1.0)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source": self.source,
            "field": self.field,
            "timestamp": self.timestamp,
            "value": self.value,
            "data_status": self.data_status,
            "confidence": self.confidence,
            "metadata": self.metadata
        }

    def get_evidence_id(self) -> str:
        """Generate a unique ID for this evidence based on its content"""
        evidence_str = f"{self.source}:{self.field}:{self.timestamp}:{self.value}:{self.data_status}"
        return hashlib.md5(evidence_str.encode()).hexdigest()[:8]

@dataclass
class Claim:
    """Represents a claim in the final response backed by evidence"""
    statement: str  # The human-readable claim
    evidence: List[Evidence] = field(default_factory=list)
    risk_level: Optional[str] = None  # Associated risk level if applicable

    def to_dict(self) -> Dict[str, Any]:
        return {
            "statement": self.statement,
            "evidence": [ev.to_dict() for ev in self.evidence],
            "risk_level": self.risk_level
        }

class EvidenceTracker:
    """
    Tracks evidence for claims made in the synthesis layer
    Ensures every claim in the final response can be traced back to specific sources
    """

    def __init__(self):
        self.evidence_store: Dict[str, Evidence] = {}  # evidence_id -> Evidence
        self.claims: List[Claim] = []
        self.logger = logging.getLogger(f"{__name__}.EvidenceTracker")

    def add_evidence(
        self,
        source: str,
        field: str,
        timestamp: str,
        value: Any,
        data_status: str = "SIMULATED",
        confidence: float = 1.0,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Add a piece of evidence to the tracker

        Returns:
            evidence_id: Unique identifier for this evidence
        """
        evidence = Evidence(
            source=source,
            field=field,
            timestamp=timestamp,
            value=value,
            data_status=data_status,
            confidence=confidence,
            metadata=metadata or {}
        )

        evidence_id = evidence.get_evidence_id()
        self.evidence_store[evidence_id] = evidence
        self.logger.debug(f"Added evidence: {evidence_id} - {source}.{field} = {value}")
        return evidence_id

    def create_claim(
        self,
        statement: str,
        evidence_ids: List[str],
        risk_level: Optional[str] = None
    ) -> Claim:
        """
        Create a claim backed by specific evidence IDs

        Args:
            statement: The human-readable claim statement
            evidence_ids: List of evidence IDs that back this claim
            risk_level: Optional risk level associated with this claim

        Returns:
            Claim object
        """
        # Validate that all evidence IDs exist
        valid_evidence = []
        for ev_id in evidence_ids:
            if ev_id in self.evidence_store:
                valid_evidence.append(self.evidence_store[ev_id])
            else:
                self.logger.warning(f"Evidence ID {ev_id} not found in evidence store")

        claim = Claim(
            statement=statement,
            evidence=valid_evidence,
            risk_level=risk_level
        )

        self.claims.append(claim)
        self.logger.info(f"Created claim: '{statement}' backed by {len(valid_evidence)} pieces of evidence")
        return claim

    def extract_evidence_from_agent_data(
        self,
        agent_name: str,
        agent_data: Dict[str, Any],
        source_mapping: Optional[Dict[str, str]] = None
    ) -> List[str]:
        """
        Extract evidence from structured agent data and add to evidence store

        Args:
            agent_name: Name of the agent (weather, sea_state, etc.)
            agent_data: Structured data from the agent
            source_mapping: Optional mapping of agent names to source names

        Returns:
            List of evidence IDs that were added
        """
        if source_mapping is None:
            source_mapping = {
                "weather": "IMD",
                "sea_state": "INCOIS",
                "hazard": "IMD+INCOIS",
                "pfz_satellite": "INCOIS+ISRO",
                "geofence": "Survey of India"
            }

        agent_name_str = agent_name.value if hasattr(agent_name, "value") else str(agent_name)
        source = source_mapping.get(agent_name_str, agent_name_str.upper())
        timestamp = agent_data.get("timestamp", datetime.utcnow().isoformat())
        data_status = agent_data.get("data_status", "SIMULATED")

        evidence_ids = []

        # Extract all numeric and string fields as evidence (excluding metadata)
        exclude_fields = {"agent", "source", "timestamp", "confidence", "error", "status", "data_status"}

        for field, value in agent_data.items():
            if field not in exclude_fields and value is not None:
                # Only track meaningful data points
                if isinstance(value, (int, float, str, bool)) or \
                   (isinstance(value, list) and all(isinstance(x, (int, float, str)) for x in value)):

                    evidence_id = self.add_evidence(
                        source=source,
                        field=f"{agent_name_str}.{field}",
                        timestamp=timestamp,
                        value=value,
                        data_status=data_status,
                        confidence=agent_data.get("confidence", 1.0),
                        metadata={"agent": agent_name}
                    )
                    evidence_ids.append(evidence_id)

        self.logger.debug(f"Extracted {len(evidence_ids)} evidence pieces from {agent_name}")
        return evidence_ids

    def get_all_evidence(self) -> List[Dict[str, Any]]:
        """Get all evidence stored in the tracker"""
        return [ev.to_dict() for ev in self.evidence_store.values()]

    def get_evidence_objects(self) -> List[Evidence]:
        """Get all Evidence objects stored in the tracker"""
        return list(self.evidence_store.values())

    def get_claims_with_evidence(self) -> List[Dict[str, Any]]:
        """Get all claims with their backing evidence"""
        return [claim.to_dict() for claim in self.claims]

    def clear(self):
        """Clear all evidence and claims"""
        self.evidence_store.clear()
        self.claims.clear()
        self.logger.debug("Evidence tracker cleared")

# Example usage:
# tracker = EvidenceTracker()
#
# # Add evidence from weather agent
# weather_data = {
#     "wind_speed_kmh": 15.2,
#     "rainfall_mm": 0.0,
#     "source": "IMD",
#     "timestamp": "2026-08-24T05:00:00Z",
#     "confidence": 0.95
# }
#
# evidence_ids = tracker.extract_evidence_from_agent_data("weather", weather_data)
#
# # Create a claim
# claim = tracker.create_claim(
#     statement="Wind speed is 15.2 km/h, which is within safe limits for fishing",
#     evidence_ids=evidence_ids,
#     risk_level="low"
# )
#
# print(f"Stored {len(tracker.get_all_evidence())} evidence pieces")
# print(f"Made {len(tracker.get_claims_with_evidence())} claims")