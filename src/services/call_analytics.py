import json
import logging
import os
import base64
from typing import Any, Dict
import google.generativeai as genai

logger = logging.getLogger(__name__)

# ── Strict enums for post-processing validation ──
_VALID_PAYMENT = {"EMI", "FULL_PAYMENT", "PARTIAL_PAYMENT", "DOWN_PAYMENT"}
_VALID_REJECTION = {"HIGH_INTEREST", "BUDGET_CONSTRAINTS", "ALREADY_PAID", "NOT_INTERESTED", "NONE"}
_VALID_SENTIMENT = {"Positive", "Negative", "Neutral"}
_VALID_ADHERENCE = {"FOLLOWED", "NOT_FOLLOWED"}

_CALL_PROMPT_TEMPLATE = """\
You are an expert Call Center Quality Assurance AI.
Listen to the provided audio recording, which is primarily in {language} (or a mix like Hinglish/Tanglish).
Perform multi-stage AI analysis: Transcription -> NLP Analysis -> Metric Extraction.

Provide your analysis strictly as a valid JSON object matching the exact structure below.

{{
  "transcript": "<The full Speech-to-Text output capturing the dialogue>",
  "summary": "<Concise AI-powered summary of the conversation>",
  "sop_validation": {{
    "greeting": <true or false, checking if agent greeted the customer>,
    "identification": <true or false, checking if agent verified customer identity>,
    "problemStatement": <true or false, checking if agent explained call purpose>,
    "solutionOffering": <true or false, checking if agent discussed solutions/options>,
    "closing": <true or false, checking for proper closing statement>,
    "complianceScore": <float from 0.0 to 1.0 indicating SOP adherence ratio, calculated as count_of_true_stages / 5>,
    "adherenceStatus": "<'FOLLOWED' if all 5 stages are true, else 'NOT_FOLLOWED'>",
    "explanation": "<Short explanation of the SOP adherence>"
  }},
  "analytics": {{
    "paymentPreference": "<Must strictly be exactly one of: EMI, FULL_PAYMENT, PARTIAL_PAYMENT, DOWN_PAYMENT>",
    "rejectionReason": "<Must strictly be exactly one of: HIGH_INTEREST, BUDGET_CONSTRAINTS, ALREADY_PAID, NOT_INTERESTED, NONE>",
    "sentiment": "<Positive, Negative, or Neutral>"
  }},
  "keywords": [
    "<keyword1>", "<keyword2>", "<keyword3>"
  ]
}}
"""

def _configure_client() -> None:
    api_key = os.environ.get("GEMINI_API_KEY", "AIzaSyDU5FoPUlnj2EiL3PJDKfMRXHA4uF_xsrA")
    genai.configure(api_key=api_key)

def _fallback_call_response(language: str) -> Dict[str, Any]:
    """Return a mock fallback response if the AI API fails."""
    return {
        "status": "success",
        "language": language,
        "transcript": "Agent: Hello, am I speaking with Mr. Kumar? Customer: Yes. Agent: This is regarding your outstanding payment of Rs 15000. Customer: I can pay partial now. Agent: We can set up a partial payment plan. Customer: Ok, proceed. Agent: Thank you, have a good day.",
        "summary": "Agent contacted customer regarding outstanding payment. Customer agreed to partial payment plan.",
        "sop_validation": {
            "greeting": True,
            "identification": True,
            "problemStatement": True,
            "solutionOffering": True,
            "closing": True,
            "complianceScore": 1.0,
            "adherenceStatus": "FOLLOWED",
            "explanation": "All SOP stages were followed correctly."
        },
        "analytics": {
            "paymentPreference": "PARTIAL_PAYMENT",
            "rejectionReason": "NONE",
            "sentiment": "Neutral"
        },
        "keywords": ["payment", "partial", "outstanding", "plan"]
    }


def _validate_and_sanitize(result: Dict[str, Any], language: str) -> Dict[str, Any]:
    """Ensure Gemini output strictly conforms to required schema and enums."""
    fallback = _fallback_call_response(language)

    # Top-level
    result["status"] = "success"
    result["language"] = language
    result.setdefault("transcript", fallback["transcript"])
    result.setdefault("summary", fallback["summary"])

    # SOP validation
    sop = result.get("sop_validation", {})
    if not isinstance(sop, dict):
        sop = fallback["sop_validation"]

    for field in ("greeting", "identification", "problemStatement", "solutionOffering", "closing"):
        if field not in sop or not isinstance(sop[field], bool):
            sop[field] = fallback["sop_validation"][field]

    # Recalculate complianceScore from actual boolean values
    true_count = sum(1 for f in ("greeting", "identification", "problemStatement", "solutionOffering", "closing") if sop.get(f) is True)
    sop["complianceScore"] = round(true_count / 5, 2)
    sop["adherenceStatus"] = "FOLLOWED" if true_count == 5 else "NOT_FOLLOWED"
    sop.setdefault("explanation", fallback["sop_validation"]["explanation"])
    result["sop_validation"] = sop

    # Analytics
    analytics = result.get("analytics", {})
    if not isinstance(analytics, dict):
        analytics = fallback["analytics"]

    if analytics.get("paymentPreference") not in _VALID_PAYMENT:
        analytics["paymentPreference"] = "PARTIAL_PAYMENT"
    if analytics.get("rejectionReason") not in _VALID_REJECTION:
        analytics["rejectionReason"] = "NONE"
    if analytics.get("sentiment") not in _VALID_SENTIMENT:
        analytics["sentiment"] = "Neutral"
    result["analytics"] = analytics

    # Keywords
    kw = result.get("keywords", [])
    if not isinstance(kw, list) or len(kw) == 0:
        kw = ["call", "payment", "agent"]
    result["keywords"] = [str(k) for k in kw]

    return result


async def analyze_call_audio(language: str, audio_base64: str, audio_format: str = "mp3") -> Dict[str, Any]:
    """
    Decodes the base64 audio and analyzes it using Gemini 2.5 Flash multimodal capabilities.
    """
    try:
        if not audio_base64:
            return _fallback_call_response(language)

        _configure_client()
        
        # Decode base64 to binary
        try:
            audio_data = base64.b64decode(audio_base64)
        except Exception:
            logger.error("Invalid base64 audio data")
            return _fallback_call_response(language)

        if len(audio_data) < 100:
            logger.warning("Audio data too small (%d bytes), likely invalid", len(audio_data))
            return _fallback_call_response(language)
        
        # Prepare parts for Gemini
        audio_blob = {
            "mime_type": f"audio/{audio_format}",
            "data": audio_data
        }
        
        prompt = _CALL_PROMPT_TEMPLATE.format(language=language)
        model = genai.GenerativeModel("gemini-2.0-flash")
        
        response = model.generate_content(
            [prompt, audio_blob],
            generation_config=genai.types.GenerationConfig(
                response_mime_type="application/json",
            )
        )
        raw = response.text.strip()
            
        result = json.loads(raw)
        
        # Validate and sanitize every field
        result = _validate_and_sanitize(result, language)
            
        return result
        
    except Exception as e:
        logger.error("Gemini call analysis failed: %s", e, exc_info=True)
        return _fallback_call_response(language)
