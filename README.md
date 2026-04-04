# Call Center Compliance API

## Description
This project implements the Track 3: Call Center Compliance API for automated quality assurance in call centers. The API validates agent SOP adherence (Greeting, ID, Problem, Solution, Closing), classifies payment intent, extracts keywords, and performs sentiment analysis based on MP3 audio input (Base64). It natively supports Hinglish and Tanglish via multimodal transcription.

## Tech Stack
- **Language/Framework**: Python / FastAPI
- **Key libraries**: `google-generativeai`, `pydantic`, `uvicorn`
- **LLM/AI models used**: Google Gemini (`gemini-2.5-flash`) for audio-to-text multimodal processing and structured NLP extraction

## Setup Instructions
1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set environment variables based on `.env.example`
   - Ensure `GEMINI_API_KEY` is present.
4. Run the application: `uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload`

## Approach
The solution leverages the direct multimodal input capability of Gemini 2.5 Flash, which allows parsing MP3 audio files to perform seamless zero-shot transcription combined with structured JSON extraction strictly following the Hackathon's standard rubrics, directly bypassing standard localized dependencies.
