"""
Response layer for ORCA - builds structured risk cards and formats output
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class CardBuilder:
    """
    Builds structured risk cards for the ORCA response layer
    Creates machine-readable and human-readable formats of the final response
    """

    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.CardBuilder")

    def build_risk_card(
        self,
        synthesized_response: Dict[str, Any],
        format_type: str = "json"
    ) -> Dict[str, Any]:
        """
        Build a structured risk card from the synthesized response

        Args:
            synthesized_response: Output from the synthesis agent
            format_type: Output format ("json", "html", "text")

        Returns:
            Structured risk card in the requested format
        """
        self.logger.info(f"Building risk card in {format_type} format")

        if format_type == "json":
            return self._build_json_card(synthesized_response)
        elif format_type == "html":
            return self._build_html_card(synthesized_response)
        elif format_type == "text":
            return self._build_text_card(synthesized_response)
        else:
            self.logger.warning(f"Unknown format type: {format_type}. Defaulting to JSON.")
            return self._build_json_card(synthesized_response)

    def _build_json_card(self, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """Build a JSON-structured risk card"""
        # Extract key information
        response_text = response_data.get("response", "")
        risk_assessment = response_data.get("risk_assessment", {})
        evidence_data = response_data.get("evidence", {})
        claims_data = response_data.get("claims", [])
        metadata = response_data.get("metadata", {})

        # Build the card structure
        card = {
            "orca_response": {
                "version": "1.0",
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "summary": response_text,
                "risk_level": risk_assessment.get("overall_level", "unknown"),
                "risk_details": risk_assessment.get("agent_risks", {}),
                "evidence": {
                    "available": evidence_data.get("count", 0),
                    "sources": self._extract_evidence_sources(evidence_data.get("references", []))
                },
                "key_points": self._extract_key_points(claims_data),
                "recommendation": self._generate_recommendation(
                    risk_assessment.get("overall_level", "unknown"),
                    claims_data
                ),
                "metadata": {
                    "generated_at": metadata.get("generated_at"),
                    "agents_consulted": metadata.get("agents_consulted", []),
                    "data_quality_indicators": self._calculate_quality_indicators(response_data)
                }
            }
        }

        return card

    def _build_html_card(self, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """Build an HTML-formatted risk card (returns as dict with HTML string)"""
        json_card = self._build_json_card(response_data)
        orca_response = json_card["orca_response"]

        # HTML template for the risk card
        risk_level = orca_response["risk_level"]
        risk_colors = {
            "low": "#28a745",      # Green
            "moderate": "#ffc107", # Yellow
            "high": "#fd7e14",     # Orange
            "extreme": "#dc3545",  # Red
            "unknown": "#6c757d"   # Gray
        }
        risk_color = risk_colors.get(risk_level, "#6c757d")

        html_content = f"""
        <div class="orca-risk-card" style="border: 1px solid #ddd; border-radius: 8px; padding: 16px; max-width: 600px; font-family: Arial, sans-serif;">
            <div class="card-header" style="display: flex; align-items: center; margin-bottom: 16px;">
                <div class="risk-indicator" style="width: 12px; height: 12px; background-color: {risk_color}; border-radius: 50%; margin-right: 12px;"></div>
                <h2 class="card-title" style="margin: 0; color: #333;">ORCA Marine Safety Advisory</h2>
            </div>

            <div class="card-summary" style="margin-bottom: 16px; line-height: 1.5;">
                <p>{orca_response['summary']}</p>
            </div>

            <div class="risk-details" style="margin-bottom: 16px; padding: 12px; background-color: #f8f9fa; border-radius: 4px;">
                <h3 style="margin-top: 0; color: #495057;">Risk Assessment</h3>
                <p><strong>Overall Risk Level:</strong> <span style="text-transform: capitalize; color: {risk_color};">{orca_response['risk_level']}</span></p>
                <p><strong>Evidence Sources:</strong> {', '.join(orca_response['evidence']['sources']) if orca_response['evidence']['sources'] else 'None available'}</p>
                <p><strong>Data Points Analyzed:</strong> {orca_response['evidence']['available']}</p>
            </div>

            <div class="key-points" style="margin-bottom: 16px;">
                <h3 style="margin-top: 0; color: #495057;">Key Points</h3>
                <ul style="padding-left: 20px; margin: 0;">
        """

        for point in orca_response["key_points"]:
            html_content += f"<li>{point}</li>"

        html_content += f"""
                </ul>
            </div>

            <div class="recommendation" style="padding: 12px; background-color: #e9ecef; border-radius: 4px;">
                <h3 style="margin-top: 0; color: #495057;">Recommendation</h3>
                <p style="margin: 0; line-height: 1.4;">{orca_response['recommendation']}</p>
            </div>

            <div class="card-footer" style="margin-top: 16px; font-size: 0.9em; color: #6c757d; text-align: center;">
                Generated at {orca_response['metadata']['generated_at']} |
                Agents Consulted: {len(orca_response['metadata']['agents_consulted'])}
            </div>
        </div>
        """

        return {
            "format": "html",
            "content": html_content.strip(),
            "orca_response": orca_response  # Also include the structured data
        }

    def _build_text_card(self, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """Build a plain text-formatted risk card"""
        json_card = self._build_json_card(response_data)
        orca_response = json_card["orca_response"]

        risk_level = orca_response["risk_level"]
        risk_symbols = {
            "low": "✅",
            "moderate": "⚠️",
            "high": "🚨",
            "extreme": "☠️",
            "unknown": "❓"
        }
        risk_symbol = risk_symbols.get(risk_level, "❓")

        text_content = f"""
ORCA MARINE SAFETY ADVISORY
{'=' * 40}

{risk_symbol} RISK LEVEL: {risk_level.upper()}

SUMMARY:
{orca_response['summary']}

EVIDENCE:
• Sources: {', '.join(orca_response['evidence']['sources']) if orca_response['evidence']['sources'] else 'None available'}
• Data Points: {orca_response['evidence']['available']}

KEY POINTS:
"""
        for i, point in enumerate(orca_response["key_points"], 1):
            text_content += f"{i}. {point}\n"

        text_content += f"""
RECOMMENDATION:
{orca_response['recommendation']}

{'=' * 40}
Generated at: {orca_response['metadata']['generated_at']}
Agents Consulted: {', '.join(orca_response['metadata']['agents_consulted'])}
Data Quality Indicators: {self._calculate_quality_indicators(response_data)}
        """.strip()

        return {
            "format": "text",
            "content": text_content,
            "orca_response": orca_response
        }

    def _extract_evidence_sources(self, evidence_references: List[Dict[str, Any]]) -> List[str]:
        """Extract unique sources from evidence references"""
        sources = set()
        for ref in evidence_references:
            source = ref.get("source", "")
            if source:
                sources.add(source)
        return sorted(list(sources))

    def _extract_key_points(self, claims_data: List[Dict[str, Any]]) -> List[str]:
        """Extract key points from claims for display in the card"""
        key_points = []

        # Prioritize claims by risk level (high to low)
        sorted_claims = sorted(
            claims_data,
            key=lambda x: {"extreme": 3, "high": 2, "moderate": 1, "low": 0}.get(x.get("risk_level", "low"), 0),
            reverse=True
        )

        # Take top claims (limit to avoid clutter)
        for claim in sorted_claims[:5]:
            statement = claim.get("statement", "")
            if statement:
                # Add risk level indicator if present
                risk_level = claim.get("risk_level")
                if risk_level and risk_level != "low":
                    key_points.append(f"[{risk_level.upper()}] {statement}")
                else:
                    key_points.append(statement)

        return key_points

    def _generate_recommendation(self, overall_risk: str, claims_data: List[Dict[str, Any]]) -> str:
        """Generate a recommendation based on risk level and claims"""
        risk_actions = {
            "low": "Conditions appear favorable for marine activities. Standard precautions advised.",
            "moderate": "Exercise caution. Consider postponing non-essential activities or implementing additional safety measures.",
            "high": "High risk conditions detected. Strongly consider postponing marine activities. If proceeding, take extreme precautions and monitor conditions continuously.",
            "extreme": "Extremely dangerous conditions. Marine activities are not recommended. Seek shelter and follow official emergency guidance.",
            "unknown": "Unable to assess risk due to insufficient data. Exercise extreme caution and consult local authorities."
        }

        base_recommendation = risk_actions.get(overall_risk, "Please consult local marine authorities for guidance.")

        # Add specific advice based on claims
        specific_advice = []
        for claim in claims_data:
            statement = claim.get("statement", "").lower()
            risk_level = claim.get("risk_level", "").lower()

            if "wind" in statement and risk_level in ["high", "extreme"]:
                specific_advice.append("Secure vessels and avoid open waters due to high winds.")
            elif "wave" in statement and risk_level in ["high", "extreme"]:
                specific_advice.append("Avoid coastal areas and open waters due to hazardous wave conditions.")
            elif "visibility" in statement and risk_level in ["high", "extreme"]:
                specific_advice.append("Exercise extreme caution in navigation due to poor visibility.")
            elif "rainfall" in statement and risk_level in ["high", "extreme"]:
                specific_advice.append("Be aware of potential flooding and reduced sea conditions due to heavy rainfall.")
            elif "lightning" in statement and risk_level in ["high", "extreme"]:
                specific_advice.append("Seek shelter immediately due to lightning risk.")
            elif "cyclone" in statement:
                specific_advice.append("Follow official cyclone warnings and evacuation procedures.")
            elif "tsunami" in statement:
                specific_advice.append("Move to higher ground immediately and follow tsunami evacuation procedures.")

        if specific_advice:
            # Add up to 2 specific pieces of advice to avoid overwhelming the user
            return base_recommendation + " " + " ".join(specific_advice[:2])

        return base_recommendation

    def _calculate_quality_indicators(self, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate quality indicators for the response"""
        metadata = response_data.get("metadata", {})
        data_quality = metadata.get("data_quality", {})

        agents_consulted = metadata.get("agents_consulted", [])
        agents_responding = data_quality.get("agents_responding", 0)
        total_agents = data_quality.get("total_agents", len(agents_consulted))

        return {
            "agent_coverage": f"{agents_responding}/{total_agents}" if total_agents > 0 else "0/0",
            "has_errors": data_quality.get("has_errors", False),
            "evidence_available": response_data.get("evidence", {}).get("count", 0),
            "response_complete": agents_responding > 0 and not data_quality.get("has_errors", False)
        }

# Example usage:
# card_builder = CardBuilder()
# synthesized_response = {...}  # From synthesis agent
# json_card = card_builder.build_risk_card(synthesized_response, "json")
# html_card = card_builder.build_risk_card(synthesized_response, "html")
# text_card = card_builder.build_risk_card(synthesized_response, "text")