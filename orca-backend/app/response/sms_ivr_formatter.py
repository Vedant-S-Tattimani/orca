"""
SMS/IVR formatter for ORCA - creates low-bandwidth summaries for limited connectivity
"""
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class SMSIVRFormatter:
    """
    Formats ORCA responses for SMS/IVR delivery
    Creates concise, plain-text summaries suitable for low-bandwidth environments
    """

    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.SMSIVRFormatter")

    def format_for_sms(
        self,
        synthesized_response: Dict[str, Any],
        max_length: int = 160
    ) -> str:
        """
        Format response for SMS delivery (typically 160 characters)

        Args:
            synthesized_response: Output from the synthesis agent
            max_length: Maximum length of the SMS message

        Returns:
            SMS-formatted message string
        """
        self.logger.info("Formatting response for SMS")

        # Extract key information
        response_text = synthesized_response.get("response", "")
        risk_level = synthesized_response.get("risk_assessment", {}).get("overall_level", "unknown")

        # Create a very concise summary
        # Start with the risk level
        risk_symbols = {
            "low": "✅",
            "moderate": "⚠️",
            "high": "🚨",
            "extreme": "☠️",
            "unknown": "❓"
        }
        symbol = risk_symbols.get(risk_level, "❓")

        # Try to extract the most important sentence from the response
        sentences = [s.strip() for s in response_text.split('.') if s.strip()]
        key_sentence = sentences[0] if sentences else "Marine conditions assessed."

        # Build SMS message
        sms_parts = [
            f"ORCA: {symbol} {risk_level.upper()}",
            key_sentence[:100]  # Limit first part
        ]

        sms_message = " - ".join(sms_parts)

        # Truncate to max length if needed
        if len(sms_message) > max_length:
            sms_message = sms_message[:max_length-3] + "..."

        self.logger.debug(f"SMS formatted ({len(sms_message)} chars): {sms_message}")
        return sms_message

    def format_for_ivr(
        self,
        synthesized_response: Dict[str, Any]
    ) -> str:
        """
        Format response for IVR (Interactive Voice Response) delivery
        Creates a script suitable for text-to-speech

        Args:
            synthesized_response: Output from the synthesis agent

        Returns:
            IVR-formatted script string
        """
        self.logger.info("Formatting response for IVR")

        response_text = synthesized_response.get("response", "")
        risk_level = synthesized_response.get("risk_assessment", {}).get("overall_level", "unknown")
        evidence_count = synthesized_response.get("evidence", {}).get("count", 0)

        # Risk level descriptions for voice
        risk_descriptions = {
            "low": "low risk",
            "moderate": "moderate risk",
            "high": "high risk",
            "extreme": "extreme risk",
            "unknown": "unknown risk level"
        }
        risk_desc = risk_descriptions.get(risk_level, "unknown risk")

        # Build IVR script
        ivr_script = f"""
        ORCA Marine Safety Advisory.
        Overall risk assessment: {risk_desc}.
        Based on {evidence_count} verified data points from official sources.
        {response_text}
        For more details, please visit our website or contact local marine authorities.
        This message is provided by ORCA, the Marine EcoSystem Reasoning with Collaborative Agents system.
        """.strip()

        # Clean up extra whitespace
        ivr_script = " ".join(ivr_script.split())

        self.logger.debug(f"IVR formatted: {ivr_script[:100]}...")
        return ivr_script

    def format_emergency_alert(
        self,
        synthesized_response: Dict[str, Any]
    ) -> str:
        """
        Format an emergency alert for critical conditions
        Used when risk level is high or extreme

        Args:
            synthesized_response: Output from the synthesis agent

        Returns:
            Emergency alert formatted string
        """
        risk_level = synthesized_response.get("risk_assessment", {}).get("overall_level", "unknown")

        if risk_level not in ["high", "extreme"]:
            return ""  # Not an emergency

        response_text = synthesized_response.get("response", "")
        warnings = []

        # Extract warnings from claims
        claims = synthesized_response.get("claims", [])
        for claim in claims:
            if claim.get("risk_level") in ["high", "extreme"]:
                warnings.append(claim.get("statement", ""))

        alert_parts = [
            "🚨 MARINE SAFETY ALERT 🚨",
            f"Risk Level: {risk_level.upper()}",
            "",
            "KEY WARNINGS:"
        ]

        for i, warning in enumerate(warnings[:3], 1):  # Limit to top 3 warnings
            alert_parts.append(f"{i}. {warning}")

        alert_parts.extend([
            "",
            "ACTION REQUIRED:",
            "Exercise extreme caution or postpone marine activities.",
            "Follow official guidance from local authorities.",
            "",
            f"Details: {response_text[:200]}...",
            "",
            "Issued by ORCA Marine Safety System"
        ])

        return "\n".join(alert_parts)

# Example usage:
# formatter = SMSIVRFormatter()
# sms_msg = formatter.format_for_sms(synthesized_response)
# ivr_script = formatter.format_for_ivr(synthesized_response)
# emergency_alert = formatter.format_emergency_alert(synthesized_response)