"""
Synthesis agent for ORCA - fuses structured agent outputs + risk flags + retrieved evidence
into a reasoned answer with evidence citations
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging
import json

from .evidence_tracker import EvidenceTracker, Claim
from .llm_client import LLMClient

logger = logging.getLogger(__name__)

class SynthesisAgent:
    """
    Synthesis agent that combines:
    1. Structured outputs from specialist agents
    2. Risk flags from the risk engine
    3. Retrieved evidence from RAG/vector store
    4. Generates a reasoned, evidence-backed natural language response
    """

    def __init__(
        self,
        llm_client: Optional[LLMClient] = None,
        evidence_tracker: Optional[EvidenceTracker] = None
    ):
        self.llm_client = llm_client or LLMClient()
        self.evidence_tracker = evidence_tracker or EvidenceTracker()
        self.logger = logging.getLogger(f"{__name__}.SynthesisAgent")

    async def synthesize_response(
        self,
        merged_agent_data: Dict[str, Any],
        risk_flags: Dict[str, List[Dict[str, Any]]],
        rag_evidence: List[Dict[str, Any]] = None,
        original_query: str = "",
        query_language: str = "en",
        history: List[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Main synthesis method that creates an evidence-backed response

        Args:
            merged_agent_data: Output from the orchestrator merger
            risk_flags: Risk assessment results from the risk engine
            rag_evidence: Evidence retrieved from RAG/vector store (advisories, warnings, etc.)
            original_query: The original user query for context

        Returns:
            Dictionary containing the synthesized response with evidence citations
        """
        self.logger.info("Starting synthesis process")

        # Step 1: Extract and track evidence from agent data
        self._extract_and_track_agent_evidence(merged_agent_data)

        # Step 2: Extract and track evidence from RAG results
        if rag_evidence:
            self._extract_and_track_rag_evidence(rag_evidence)

        # Step 3: Create claims based on agent data and risk flags
        claims = self._create_claims_from_data(
            merged_agent_data, risk_flags, original_query
        )

        # Step 4: Generate natural language response using LLM
        natural_language_response = await self._generate_narrative_response(
            claims, merged_agent_data, risk_flags, original_query, query_language, history
        )

        # Step 5: Structure the final response
        final_response = self._structure_final_response(
            natural_language_response,
            claims,
            risk_flags,
            merged_agent_data
        )

        self.logger.info("Synthesis complete")
        return final_response

    def _extract_and_track_agent_evidence(
        self,
        merged_agent_data: Dict[str, Any]
    ):
        """Extract evidence from all agent data in the merged structure"""
        agent_data = merged_agent_data.get("agent_data", {})

        for agent_name, data in agent_data.items():
            if "error" not in data:
                self.evidence_tracker.extract_evidence_from_agent_data(
                    agent_name, data
                )
                self.logger.debug(f"Tracked evidence from {agent_name}")

    def _extract_and_track_rag_evidence(
        self,
        rag_evidence: List[Dict[str, Any]]
    ):
        """Extract evidence from RAG/vector store results"""
        for i, evidence_item in enumerate(rag_evidence):
            # Assuming RAG evidence has source, content, timestamp, etc.
            source = evidence_item.get("source", "RAG Store")
            content = evidence_item.get("content", "")
            timestamp = evidence_item.get("timestamp", datetime.utcnow().isoformat())
            confidence = evidence_item.get("confidence", 0.8)

            # Create evidence from RAG content
            evidence_id = self.evidence_tracker.add_evidence(
                source=source,
                field=f"rag_content_{i}",
                timestamp=timestamp,
                value=content,
                confidence=confidence,
                metadata={"type": "rag_advisory", "original_data": evidence_item}
            )
            self.logger.debug(f"Tracked RAG evidence: {evidence_id}")

    def _create_claims_from_data(
        self,
        merged_agent_data: Dict[str, Any],
        risk_flags: Dict[str, List[Dict[str, Any]]],
        original_query: str
    ) -> List[Claim]:
        """Create claims based on processed data and risk assessments"""
        claims = []
        agent_data = merged_agent_data.get("agent_data", {})
        query_metadata = merged_agent_data.get("query_metadata", {})

        # Create claims for each agent's key findings
        for agent_name, data in agent_data.items():
            if "error" in data:
                # Create a claim about data unavailability
                claim = self.evidence_tracker.create_claim(
                    statement=f"Data from {agent_name} agent is currently unavailable: {data.get('error', 'Unknown error')}",
                    evidence_ids=[],  # No evidence for missing data
                    risk_level="unknown"
                )
                claims.append(claim)
                continue

            # Create specific claims based on agent type
            if agent_name in ["weather", "openmeteo_weather"]:
                claims.extend(self._create_weather_claims(data))
            elif agent_name in ["sea_state", "openmeteo_marine"]:
                claims.extend(self._create_sea_state_claims(data))
            elif agent_name == "hazard":
                claims.extend(self._create_hazard_claims(data))
            elif agent_name == "pfz_satellite":
                claims.extend(self._create_pfz_claims(data))
            elif agent_name == "routing_agent":
                claims.extend(self._create_routing_claims(data, merged_agent_data.get("route_safety_assessment")))

        # Create claims based on risk flags
        for agent_type, flags in risk_flags.items():
            for flag in flags:
                if flag["risk_level"] in ["moderate", "high", "extreme"]:
                    # Find evidence IDs related to this field
                    evidence_ids = self._find_evidence_for_field(
                        f"{agent_type}.{flag['field']}"
                    )

                    claim = self.evidence_tracker.create_claim(
                        statement=flag["description"],
                        evidence_ids=evidence_ids,
                        risk_level=flag["risk_level"]
                    )
                    claims.append(claim)

        # Create an overall safety assessment claim
        overall_claim = self._create_overall_safety_claim(
            risk_flags, query_metadata, original_query
        )
        if overall_claim:
            claims.append(overall_claim)

        self.logger.info(f"Created {len(claims)} claims for synthesis")
        return claims

    def _create_weather_claims(self, weather_data: Dict[str, Any]) -> List[Claim]:
        """Create specific claims from weather agent data"""
        claims = []

        # Wind claim
        if "wind_speed_kmh" in weather_data:
            ws = weather_data["wind_speed_kmh"]
            evidence_ids = self.evidence_tracker.extract_evidence_from_agent_data(
                "weather", {"wind_speed_kmh": ws}
            )[-1:]  # Get the last evidence ID added

            if ws > 40:
                risk_level = "high"
            elif ws > 20:
                risk_level = "moderate"
            else:
                risk_level = "low"

            claim = self.evidence_tracker.create_claim(
                statement=f"Wind speed is {ws} km/h",
                evidence_ids=evidence_ids,
                risk_level=risk_level
            )
            claims.append(claim)

        # Rainfall claim
        if "rainfall_mm" in weather_data:
            rf = weather_data["rainfall_mm"]
            evidence_ids = self.evidence_tracker.extract_evidence_from_agent_data(
                "weather", {"rainfall_mm": rf}
            )[-1:]

            if rf > 7.5:
                risk_level = "high"
            elif rf > 2.5:
                risk_level = "moderate"
            else:
                risk_level = "low"

            claim = self.evidence_tracker.create_claim(
                statement=f"Rainfall is {rf} mm/h",
                evidence_ids=evidence_ids,
                risk_level=risk_level
            )
            claims.append(claim)

        # Visibility claim (inverted logic)
        if "visibility_km" in weather_data:
            vis = weather_data["visibility_km"]
            evidence_ids = self.evidence_tracker.extract_evidence_from_agent_data(
                "weather", {"visibility_km": vis}
            )[-1:]

            if vis < 5:
                risk_level = "high"
            elif vis < 10:
                risk_level = "moderate"
            else:
                risk_level = "low"

            claim = self.evidence_tracker.create_claim(
                statement=f"Visibility is {vis} km",
                evidence_ids=evidence_ids,
                risk_level=risk_level
            )
            claims.append(claim)

        return claims

    def _create_sea_state_claims(self, sea_state_data: Dict[str, Any]) -> List[Claim]:
        """Create specific claims from sea-state agent data"""
        claims = []

        # Wave height claim
        if "wave_height_m" in sea_state_data:
            wh = sea_state_data["wave_height_m"]
            evidence_ids = self.evidence_tracker.extract_evidence_from_agent_data(
                "sea_state", {"wave_height_m": wh}
            )[-1:]

            if wh > 2.5:
                risk_level = "high"
            elif wh > 1.5:
                risk_level = "moderate"
            else:
                risk_level = "low"

            claim = self.evidence_tracker.create_claim(
                statement=f"Wave height is {wh} meters",
                evidence_ids=evidence_ids,
                risk_level=risk_level
            )
            claims.append(claim)

        # Swell height claim
        if "swell_height_m" in sea_state_data:
            sh = sea_state_data["swell_height_m"]
            evidence_ids = self.evidence_tracker.extract_evidence_from_agent_data(
                "sea_state", {"swell_height_m": sh}
            )[-1:]

            if sh > 2:
                risk_level = "high"
            elif sh > 1:
                risk_level = "moderate"
            else:
                risk_level = "low"

            claim = self.evidence_tracker.create_claim(
                statement=f"Swell height is {sh} meters",
                evidence_ids=evidence_ids,
                risk_level=risk_level
            )
            claims.append(claim)

        return claims

    def _create_hazard_claims(self, hazard_data: Dict[str, Any]) -> List[Claim]:
        """Create specific claims from hazard agent data"""
        claims = []

        # Cyclone claim
        if "cyclone_wind_speed_kmh" in hazard_data:
            cws = hazard_data["cyclone_wind_speed_kmh"]
            evidence_ids = self.evidence_tracker.extract_evidence_from_agent_data(
                "hazard", {"cyclone_wind_speed_kmh": cws}
            )[-1:]

            if cws > 118:
                risk_level = "high"
            elif cws > 63:
                risk_level = "moderate"
            else:
                risk_level = "low"

            claim = self.evidence_tracker.create_claim(
                statement=f"Cyclone wind speed is {cws} km/h",
                evidence_ids=evidence_ids,
                risk_level=risk_level
            )
            claims.append(claim)

        # Lightning claim
        if "lightning_probability_percent" in hazard_data:
            lp = hazard_data["lightning_probability_percent"]
            evidence_ids = self.evidence_tracker.extract_evidence_from_agent_data(
                "hazard", {"lightning_probability_percent": lp}
            )[-1:]

            if lp > 60:
                risk_level = "high"
            elif lp > 30:
                risk_level = "moderate"
            else:
                risk_level = "low"

            claim = self.evidence_tracker.create_claim(
                statement=f"Lightning probability is {lp}%",
                evidence_ids=evidence_ids,
                risk_level=risk_level
            )
            claims.append(claim)

        return claims

    def _create_pfz_claims(self, pfz_data: Dict[str, Any]) -> List[Claim]:
        """Create specific claims from PFZ/satellite agent data"""
        claims = []

        # SST claim
        if "sst_c" in pfz_data:
            sst = pfz_data["sst_c"]
            evidence_ids = self.evidence_tracker.extract_evidence_from_agent_data(
                "pfz_satellite", {"sst_c": sst}
            )[-1:]

            if sst < 24 or sst > 32:
                risk_level = "moderate"  # Outside optimal range
            elif sst < 27 or sst > 30:
                risk_level = "low"  # Acceptable but not optimal
            else:
                risk_level = "low"  # Optimal range

            claim = self.evidence_tracker.create_claim(
                statement=f"Sea surface temperature is {sst}°C",
                evidence_ids=evidence_ids,
                risk_level=risk_level
            )
            claims.append(claim)

        # Chlorophyll-a claim
        if "chlorophyll_a_mgm3" in pfz_data:
            chla = pfz_data["chlorophyll_a_mgm3"]
            evidence_ids = self.evidence_tracker.extract_evidence_from_agent_data(
                "pfz_satellite", {"chlorophyll_a_mgm3": chla}
            )[-1:]

            if chla < 0.5:
                risk_level = "moderate"  # Low productivity
            elif chla > 5:
                risk_level = "low"  # Very high (might indicate bloom)
            else:
                risk_level = "low"  # Good range

            claim = self.evidence_tracker.create_claim(
                statement=f"Chlorophyll-a concentration is {chla} mg/m³",
                evidence_ids=evidence_ids,
                risk_level=risk_level
            )
            claims.append(claim)

        return claims

    def _create_routing_claims(self, routing_data: Dict[str, Any], safety_eval: Optional[Dict[str, Any]]) -> List[Claim]:
        """Create specific claims from routing agent data and safety evaluation"""
        claims = []

        route_type = routing_data.get("route_type", "Unknown Route")
        distance = routing_data.get("distance_nm", 0)
        
        evidence_ids = self.evidence_tracker.extract_evidence_from_agent_data(
            "routing_agent", {"distance_nm": distance, "route_type": route_type}
        )[-1:]

        # Create geometry claim
        claim_geo = self.evidence_tracker.create_claim(
            statement=f"Route Geometry: {route_type}, Distance: {distance} NM",
            evidence_ids=evidence_ids,
            risk_level="low"
        )
        claims.append(claim_geo)

        # Create safety assessment claim
        if safety_eval:
            status = safety_eval.get("status", "UNKNOWN")
            hazards = safety_eval.get("hazards", [])
            
            risk_level = "low"
            if status == "DANGEROUS":
                risk_level = "high"
            elif status == "WARNING":
                risk_level = "moderate"
                
            hazard_str = ", ".join(hazards) if hazards else "No significant hazards detected along route."
            claim_safety = self.evidence_tracker.create_claim(
                statement=f"Route Safety Assessment: {status}. {hazard_str}",
                evidence_ids=evidence_ids,
                risk_level=risk_level
            )
            claims.append(claim_safety)

        return claims

    def _find_evidence_for_field(self, field_pattern: str) -> List[str]:
        """Find evidence IDs that match a field pattern"""
        matching_ids = []
        alternate_pattern = None
        if field_pattern.startswith("weather."):
            alternate_pattern = field_pattern.replace("weather.", "openmeteo_weather.", 1)
        elif field_pattern.startswith("sea_state."):
            alternate_pattern = field_pattern.replace("sea_state.", "openmeteo_marine.", 1)

        for evidence_id, evidence in self.evidence_tracker.evidence_store.items():
            if field_pattern in evidence.field or (alternate_pattern and alternate_pattern in evidence.field):
                matching_ids.append(evidence_id)
        return matching_ids

    def _create_overall_safety_claim(
        self,
        risk_flags: Dict[str, List[Dict[str, Any]]],
        query_metadata: Dict[str, Any],
        original_query: str
    ) -> Optional[Claim]:
        """Create an overall safety assessment claim"""
        # Determine overall risk level from flags
        max_risk_level = "low"
        risk_level_values = {"low": 0, "moderate": 1, "high": 2, "extreme": 3}

        for agent_type, flags in risk_flags.items():
            for flag in flags:
                flag_level = flag["risk_level"]
                if risk_level_values[flag_level] > risk_level_values[max_risk_level]:
                    max_risk_level = flag_level

        # Create evidence IDs from all risk flags
        evidence_ids = []
        for agent_type, flags in risk_flags.items():
            for flag in flags:
                evidence_ids.extend(self._find_evidence_for_field(
                    f"{agent_type}.{flag['field']}"
                ))

        # Remove duplicates
        evidence_ids = list(set(evidence_ids))

        location = query_metadata.get("location", {})
        location_name = location.get("name", "the queried area") if isinstance(location, dict) else str(location)

        statement = f"Overall safety assessment for {location_name}: {max_risk_level} risk level"

        if original_query:
            statement += f" based on query: '{original_query}'"

        return self.evidence_tracker.create_claim(
            statement=statement,
            evidence_ids=evidence_ids,
            risk_level=max_risk_level
        )

    async def _generate_narrative_response(
        self,
        claims: List[Claim],
        merged_agent_data: Dict[str, Any],
        risk_flags: Dict[str, List[Dict[str, Any]]],
        original_query: str = "",
        query_language: str = "en",
        history: List[Dict[str, str]] = None
    ) -> str:
        """
        Generate a natural language response using the LLM
        This is where the LLM's narrowly scoped job happens: turn computed risks + evidence into readable language
        """
        # Prepare context for the LLM
        context = {
            "original_query": original_query,
            "claims": [claim.to_dict() for claim in claims],
            "risk_summary": self._summarize_risks(risk_flags),
            "agent_status": self._summarize_agent_status(merged_agent_data),
            "evidence_count": len(self.evidence_tracker.get_all_evidence()),
            "query_language": query_language
        }

        # Create prompt for the LLM
        prompt = self._create_synthesis_prompt(context, query_language, history)

        # Get response from LLM
        try:
            response = await self.llm_client.generate_response(prompt)
            self.logger.debug(f"LLM response generated: {response[:100]}...")
            return response
        except Exception as e:
            self.logger.error(f"Error generating LLM response: {e}")
            # Fallback to template-based response
            return self._generate_fallback_response(claims, risk_flags, query_language)

    def _create_synthesis_prompt(self, context: Dict[str, Any], query_language: str = "en", history: List[Dict[str, str]] = None) -> str:
        """Create the prompt for the LLM synthesis task"""
        
        history_str = ""
        if history and len(history) > 1:
            history_str = "\nCONVERSATION HISTORY:\n"
            for msg in history[-5:-1]: # Last few turns, excluding the current query
                history_str += f"{msg['role'].upper()}: {msg['content']}\n"
        
        prompt = f"""
You are ORCA's synthesis agent. Your job is to turn already-computed risk assessments and evidence into a clear, natural language response.

DO NOT compute risks or make new assessments - only explain what has already been determined.
{history_str}
Original user query: "{context['original_query']}"

Here are the facts and risk assessments that have already been computed:

CLAIMS WITH EVIDENCE:
"""
        for i, claim in enumerate(context['claims'], 1):
            prompt += f"\n{i}. {claim['statement']}"
            if claim['risk_level']:
                prompt += f" (Risk level: {claim['risk_level']})"
            prompt += f" - Backed by {len(claim['evidence'])} piece(s) of evidence"

        prompt += f"\n\nRISK SUMMARY:\n{context['risk_summary']}"
        prompt += f"\n\nAGENT STATUS:\n{context['agent_status']}"
        prompt += f"\n\nEVIDENCE AVAILABLE: {context['evidence_count']} verified pieces"

        prompt += """

Based ONLY on the information above, produce a clear, helpful response that:
1. Directly answers the user's question
2. Explains the reasoning in simple terms
3. Mentions key evidence sources without getting too technical
4. Provides a clear recommendation if appropriate
5. Notes any data limitations or uncertainties

Response MUST be extremely concise (under 100 words) and suitable for general public consumption.
"""
        if query_language and query_language != "en":
            lang_names = {
                "hi": "Hindi (हिंदी)",
                "kn": "Kannada (ಕನ್ನಡ)",
                "mr": "Marathi (मराठी)",
                "ta": "Tamil (தமிழ்)",
                "te": "Telugu (తెలుగు)",
                "ml": "Malayalam (മലയാളം)",
                "gu": "Gujarati (ગુજરાતી)",
                "bn": "Bengali (বাংলা)"
            }
            lang_name = lang_names.get(query_language, "the same language as the user's query")
            prompt += f"\nCRITICAL: The user's query is in {lang_name}. You MUST translate all your output summaries, explanations, and advice and output them completely in {lang_name}. Do NOT output in English."
            
        return prompt

    def _summarize_risks(self, risk_flags: Dict[str, List[Dict[str, Any]]]) -> str:
        """Create a human-readable summary of risk flags"""
        if not risk_flags or all(not flags for flags in risk_flags.values()):
            return "No significant risks detected."

        summary_parts = []
        for agent_type, flags in risk_flags.items():
            if not flags:
                continue

            high_risk_flags = [f for f in flags if f["risk_level"] in ["high", "extreme"]]
            mod_risk_flags = [f for f in flags if f["risk_level"] == "moderate"]

            if high_risk_flags:
                summary_parts.append(f"{agent_type.upper()}: {len(high_risk_flags)} high-risk issue(s)")
            elif mod_risk_flags:
                summary_parts.append(f"{agent_type.upper()}: {len(mod_risk_flags)} moderate-risk issue(s)")
            else:
                summary_parts.append(f"{agent_type.upper()}: Low risk")

        return "; ".join(summary_parts)

    def _summarize_agent_status(self, merged_agent_data: Dict[str, Any]) -> str:
        """Create a summary of which agents provided data"""
        agent_data = merged_agent_data.get("agent_data", {})
        total_agents = len(agent_data)
        responding_agents = [name for name, data in agent_data.items() if "error" not in data]

        return f"{len(responding_agents)}/{total_agents} agents providing data: {', '.join(responding_agents)}"

    def _generate_fallback_response(
        self,
        claims: List[Claim],
        risk_flags: Dict[str, List[Dict[str, Any]]],
        query_language: str = "en"
    ) -> str:
        """Generate a fallback response when LLM is unavailable"""
        if not claims:
            return "Unable to generate a response due to insufficient data."

        # Simplified translation mappings
        translations = {
            "hi": {
                "high": "🚨 अत्यधिक जोखिम वाली स्थितियाँ पाई गईं:",
                "mod": "⚠️ मध्यम जोखिम वाली स्थितियाँ:",
                "low": "✅ परिस्थितियाँ अनुकूल प्रतीत होती हैं:",
                "evidence": "\n📊 आधिकारिक स्रोतों से {count} सत्यापित डेटा बिंदुओं पर आधारित।"
            },
            "kn": {
                "high": "🚨 ಹೆಚ್ಚಿನ ಅಪಾಯದ ಪರಿಸ್ಥಿತಿಗಳು ಪತ್ತೆಯಾಗಿವೆ:",
                "mod": "⚠️ ಮಧ್ಯಮ ಅಪಾಯದ ಪರಿಸ್ಥಿತಿಗಳು:",
                "low": "✅ ಪರಿಸ್ಥಿತಿಗಳು ಅನುಕೂಲಕರವಾಗಿವೆ:",
                "evidence": "\n📊 ಅಧಿಕೃತ ಮೂಲಗಳಿಂದ {count} ಪರಿಶೀಲಿಸಿದ ದತ್ತಾಂಶಗಳ ಆಧಾರದ ಮೇಲೆ."
            },
            "ml": {
                "high": "🚨 ഉയർന്ന അപകടസാധ്യതയുള്ള സാഹചര്യങ്ങൾ കണ്ടെത്തി:",
                "mod": "⚠️ മിതമായ അപകടസാധ്യതയുള്ള സാഹചര്യങ്ങൾ:",
                "low": "✅ അനുകൂലമായ സാഹചര്യങ്ങൾ കാണപ്പെടുന്നു:",
                "evidence": "\n📊 ഔദ്യോഗിക സ്രോതസ്സുകളിൽ നിന്നുള്ള {count} ഡാറ്റ അടിസ്ഥാനമാക്കി."
            },
            "ta": {
                "high": "🚨 அதிக ஆபத்துள்ள சூழ்நிலைகள் கண்டறியப்பட்டுள்ளன:",
                "mod": "⚠️ மிதமான ஆபத்துள்ள சூழ்நிலைகள்:",
                "low": "✅ சாதகமான சூழ்நிலைகள் காணப்படுகின்றன:",
                "evidence": "\n📊 அதிகாரப்பூர்வ ஆதாரங்களில் இருந்து {count} சரிபார்க்கப்பட்ட தரவுகளின் அடிப்படையில்."
            },
            "te": {
                "high": "🚨 తీవ్రమైన ప్రమాదకర పరిస్థితులు కనుగొనబడ్డాయి:",
                "mod": "⚠️ మధ్యస్థ ప్రమాదకర పరిస్థితులు:",
                "low": "✅ పరిస్థితులు అనుకూలంగా ఉన్నాయి:",
                "evidence": "\n📊 అధికారిక మూలాల నుండి {count} ధృవీకరించబడిన డేటా పాయింట్ల ఆధారంగా."
            },
            "mr": {
                "high": "🚨 अत्यंत धोकादायक परिस्थिती आढळली:",
                "mod": "⚠️ मध्यम धोकादायक परिस्थिती:",
                "low": "✅ परिस्थिती अनुकूल वाटत आहे:",
                "evidence": "\n📊 अधिकृत स्रोतांकडून मिळालेल्या {count} डेटा पॉइंट्सच्या आधारे."
            },
            "en": {
                "high": "⚠️ HIGH RISK CONDITIONS DETECTED:",
                "mod": "⚠️ MODERATE RISK CONDITIONS:",
                "low": "✅ CONDITIONS APPEAR FAVORABLE:",
                "evidence": "\n📊 Based on {count} verified data points from official sources."
            }
        }

        lang_trans = translations.get(query_language, translations["en"])

        # Simple template-based response
        high_risk_claims = [c for c in claims if c.risk_level in ["high", "extreme"]]
        mod_risk_claims = [c for c in claims if c.risk_level == "moderate"]
        low_risk_claims = [c for c in claims if c.risk_level == "low"]

        response_parts = []

        if high_risk_claims:
            response_parts.append(lang_trans["high"])
            for claim in high_risk_claims:
                response_parts.append(f"  • {claim.statement}")

        if mod_risk_claims:
            response_parts.append(lang_trans["mod"])
            for claim in mod_risk_claims:
                response_parts.append(f"  • {claim.statement}")

        if low_risk_claims and not high_risk_claims and not mod_risk_claims:
            response_parts.append(lang_trans["low"])
            for claim in low_risk_claims[:3]:  # Limit to avoid too much text
                response_parts.append(f"  • {claim.statement}")

        # Add evidence note
        evidence_count = len(self.evidence_tracker.get_all_evidence())
        response_parts.append(lang_trans["evidence"].format(count=evidence_count))

        return "\n".join(response_parts)

    def _structure_final_response(
        self,
        natural_language_response: str,
        claims: List[Claim],
        risk_flags: Dict[str, List[Dict[str, Any]]],
        merged_agent_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Structure the final response with all necessary components"""
        # Determine overall risk level from claims and risk flags
        overall_risk = "low"
        risk_level_values = {"low": 0, "moderate": 1, "high": 2, "extreme": 3, "unknown": 0}

        # Check risk levels from claims
        for claim in claims:
            if risk_level_values[claim.risk_level] > risk_level_values[overall_risk]:
                overall_risk = claim.risk_level

        # Check risk levels from risk flags (additional risk assessments)
        for agent_type, flags in risk_flags.items():
            for flag in flags:
                if risk_level_values[flag["risk_level"]] > risk_level_values[overall_risk]:
                    overall_risk = flag["risk_level"]

        # Prepare evidence references
        evidence_references = []
        for evidence in self.evidence_tracker.get_evidence_objects():
            evidence_references.append({
                "id": evidence.get_evidence_id(),
                "source": evidence.source,
                "field": evidence.field,
                "value": evidence.value,
                "timestamp": evidence.timestamp,
                "data_status": evidence.data_status
            })

        # Build final response structure
        final_response = {
            "response": natural_language_response,
            "risk_assessment": {
                "overall_level": overall_risk,
                "agent_risks": risk_flags
            },
            "evidence": {
                "references": evidence_references,
                "count": len(evidence_references)
            },
            "claims": [claim.to_dict() for claim in claims],
            "metadata": {
                "generated_at": datetime.utcnow().isoformat(),
                "agents_consulted": list(merged_agent_data.get("agent_data", {}).keys()),
                "data_quality": merged_agent_data.get("data_quality", {})
            }
        }

        return final_response

# Example usage:
# synthesis_agent = SynthesisAgent()
# merged_data = {...}  # From orchestrator merger
# risks = {...}        # From risk engine
# response = await synthesis_agent.synthesize_response(merged_data, risks)