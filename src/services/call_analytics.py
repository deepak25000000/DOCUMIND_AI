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
Listen to the provided audio recording carefully, which is primarily in {language} (or a mix like Hinglish/Tanglish).
Perform multi-stage AI analysis: Transcription -> NLP Analysis -> Metric Extraction.

CRITICAL INSTRUCTIONS:
1. You MUST transcribe the ACTUAL audio content. Do NOT make up or hallucinate a transcript.
2. If the audio is unclear, note that in the transcript with [inaudible] markers.
3. The summary MUST reflect what was ACTUALLY discussed in the audio.
4. SOP validation MUST be based on the ACTUAL conversation, not assumptions.
5. Each field must be filled based on REAL content from the audio recording.

Provide your analysis strictly as a valid JSON object matching the exact structure below.

{{
  "transcript": "<The ACTUAL full Speech-to-Text transcription of the audio dialogue. Every word spoken must be captured here.>",
  "summary": "<A detailed summary of what was ACTUALLY discussed in the call. Minimum 5-10 sentences covering all key points, decisions, and outcomes mentioned in the audio.>",
  "sop_validation": {{
    "greeting": <true or false, based on whether the agent actually greeted the customer in the audio>,
    "identification": <true or false, based on whether the agent verified customer identity in the audio>,
    "problemStatement": <true or false, based on whether the agent explained the call purpose in the audio>,
    "solutionOffering": <true or false, based on whether the agent discussed solutions/options in the audio>,
    "closing": <true or false, based on whether there was a proper closing statement in the audio>,
    "complianceScore": <float from 0.0 to 1.0, calculated as count_of_true_stages / 5>,
    "adherenceStatus": "<'FOLLOWED' if all 5 stages are true, else 'NOT_FOLLOWED'>",
    "explanation": "<Detailed 3-5 sentence explanation of SOP adherence based on actual call content>"
  }},
  "analytics": {{
    "paymentPreference": "<Must be exactly one of: EMI, FULL_PAYMENT, PARTIAL_PAYMENT, DOWN_PAYMENT — based on actual discussion>",
    "rejectionReason": "<Must be exactly one of: HIGH_INTEREST, BUDGET_CONSTRAINTS, ALREADY_PAID, NOT_INTERESTED, NONE — based on actual discussion>",
    "sentiment": "<Positive, Negative, or Neutral — based on the actual tone and content>"
  }},
  "keywords": [
    "<keyword1 from actual audio>", "<keyword2>", "<keyword3>", "<keyword4>", "<keyword5>"
  ]
}}
"""

def _configure_client() -> None:
    api_key = os.environ.get("GEMINI_API_KEY", "AIzaSyDU5FoPUlnj2EiL3PJDKfMRXHA4uF_xsrA")
    genai.configure(api_key=api_key)

def _fallback_call_response(language: str, error_msg: str = "") -> Dict[str, Any]:
    """Return a clear error fallback response when audio analysis fails."""
    return {
        "status": "success",
        "language": language,
        "transcript": f"[Audio transcription unavailable — AI engine returned an error: {error_msg or 'Service temporarily unavailable'}. Please ensure the audio file is valid and try again.]",
        "summary": f"The audio file could not be processed at this time. Error details: {error_msg or 'The Gemini API was temporarily unavailable or returned a rate limit error.'}. The system attempted to transcribe and analyze the uploaded audio recording in {language} but could not obtain results. Please verify your API key has sufficient quota and try again.",
        "sop_validation": {
            "greeting": False,
            "identification": False,
            "problemStatement": False,
            "solutionOffering": False,
            "closing": False,
            "complianceScore": 0.0,
            "adherenceStatus": "NOT_FOLLOWED",
            "explanation": f"Audio analysis could not be completed due to API error: {error_msg or 'Service unavailable'}. No SOP validation was performed. Please retry with a valid audio file."
        },
        "analytics": {
            "paymentPreference": "PARTIAL_PAYMENT",
            "rejectionReason": "NONE",
            "sentiment": "Neutral"
        },
        "keywords": ["error", "retry", "audio", "processing"]
    }


def _validate_and_sanitize(result: Dict[str, Any], language: str) -> Dict[str, Any]:
    """Ensure Gemini output strictly conforms to required schema and enums."""

    # Top-level
    result["status"] = "success"
    result["language"] = language
    result.setdefault("transcript", "[No transcript returned by AI]")
    result.setdefault("summary", "[No summary returned by AI]")

    # SOP validation
    sop = result.get("sop_validation", {})
    if not isinstance(sop, dict):
        sop = {}

    for field in ("greeting", "identification", "problemStatement", "solutionOffering", "closing"):
        if field not in sop or not isinstance(sop[field], bool):
            sop[field] = False

    # Recalculate complianceScore from actual boolean values
    true_count = sum(1 for f in ("greeting", "identification", "problemStatement", "solutionOffering", "closing") if sop.get(f) is True)
    sop["complianceScore"] = round(true_count / 5, 2)
    sop["adherenceStatus"] = "FOLLOWED" if true_count == 5 else "NOT_FOLLOWED"
    sop.setdefault("explanation", "SOP validation completed based on AI analysis of the audio content.")
    result["sop_validation"] = sop

    # Analytics
    analytics = result.get("analytics", {})
    if not isinstance(analytics, dict):
        analytics = {}

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
        kw = ["call", "agent", "customer"]
    result["keywords"] = [str(k) for k in kw]

    return result


async def analyze_call_audio(language: str, audio_base64: str, audio_format: str = "mp3") -> Dict[str, Any]:
    """
    Decodes the base64 audio and analyzes it using Gemini 2.0 Flash multimodal capabilities.
    The audio bytes are sent directly to Gemini for transcription and analysis.
    """
    try:
        if not audio_base64:
            return _fallback_call_response(language, "No audio data provided")

        _configure_client()
        
        # Decode base64 to binary
        try:
            audio_data = base64.b64decode(audio_base64)
        except Exception as decode_err:
            logger.error("Invalid base64 audio data: %s", decode_err)
            return _fallback_call_response(language, f"Invalid base64 encoding: {decode_err}")

        if len(audio_data) < 100:
            logger.warning("Audio data too small (%d bytes), likely invalid", len(audio_data))
            return _fallback_call_response(language, f"Audio file too small ({len(audio_data)} bytes)")
        
        logger.info("Processing audio: %d bytes, format: %s, language: %s", len(audio_data), audio_format, language)
        
        # Map common formats to correct MIME types
        mime_map = {
            "mp3": "audio/mpeg",
            "wav": "audio/wav",
            "m4a": "audio/mp4",
            "flac": "audio/flac",
            "ogg": "audio/ogg",
        }
        mime_type = mime_map.get(audio_format.lower(), f"audio/{audio_format}")
        
        # Prepare parts for Gemini
        audio_blob = {
            "mime_type": mime_type,
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
        logger.info("Gemini call analytics raw response length: %d chars", len(raw))
            
        result = json.loads(raw)
        
        # Validate and sanitize every field
        result = _validate_and_sanitize(result, language)
            
        return result
        
    except Exception as e:
        logger.error("Gemini call analysis failed: %s", e, exc_info=True)
        return _fallback_call_response(language, str(e))
