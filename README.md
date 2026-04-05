# DocuMind-AI & Call Center Compliance System

## 🚀 Project Overview
**DocuMind-AI** is a robust, production-grade Artificial Intelligence application that serves dual purposes: 
1. **AI Document Analysis System:** A high-performance asynchronous engine that extracts text from PDFs, DOCX files, and Images to perform comprehensive NLP analysis (Summarization, Named Entity Recognition, and Sentiment Analysis).
2. **Call Center Compliance API (Track 3):** An advanced multimodal processor analyzing Base64 audio recordings. It validates Standard Operating Procedure (SOP) adherence in customer calls, classifies intent/payment preferences, identifies rejection reasons, and performs targeted keyword extraction. It natively supports mixed languages like Hinglish and Tanglish.

## 🛠 Features

### 📄 1. Document Analyzer (`/api/document-analyze`)
- **Input:** Base64 Encoded Document (PDF, DOCX, Image / PNG / JPG).
- **Core Processing:** Extracts text reliably from documents using custom parsing and text sanitization pipelines.
- **NLP Execution:** Processes extracted text via `gemini-2.5-flash` to output:
  - Summarization
  - Named Entity Recognition (Dates, Names, Amounts, Organizations)
  - Broad Sentiment Analysis mapping
- **Architecture Validation:** Completely async design structure with extreme modularity mapped inside `src/services/`.

### 🎧 2. Call Center Compliance Analyzer (`/api/call-analytics`)
- **Input:** Base64 Encoded MP3 Audio snippet and target localized `language`.
- **Zero-Shot Multimodal Processing:** Leverages direct audio-streaming to text AI models. Bypasses traditional layered Speech-to-Text latency using Google Gemini's native audio decoding.
- **Strict Adherence Mapping:** Validates 5 core principles:
  - Greeting Recognition
  - Customer Identification
  - Problem Statement Delivery
  - Solution Offering Options
  - Proper End Call / Closing
- **Analytics Categorization:** Uses strictly enforced enumerated data structures to extract: `paymentPreference` (EMI / FULL / PARTIAL) and `rejectionReason` (HIGH_INTEREST / NOT_INTERESTED).

## ⚙️ Tech Stack & Deployment
- **Backend Framework:** Python 3.10+ / FastAPI / Uvicorn
- **AI / LLM Integration:** Google Gemini (`gemini-2.5-flash`) via `google-generativeai`
- **Data Validation:** Pydantic
- **Security:** Strict API Key enforcement (`x-api-key` header mapped securely).

**Deployment Strategy:**
The project is built entirely zero-configuration deployment ready. It natively supports hosting environments across:
- **Vercel** (`vercel.json` included natively).
- **Railway** (`railway.toml` included).
- **Render** (`render.yaml` included natively via Docker/Uvicorn).

## 📖 Setup Instructions (From Zero to End)

### Local Deployment
1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/DocuMind-AI.git
   cd DocuMind-AI
   ```
2. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Environment Setup:**
   Create a `.env` file based on `.env.example`:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   API_KEY=hcl_hack_api_key_2024_secure
   ```
4. **Run the API:**
   Start the FastAPI instance pointing specifically to the application's strict structure:
   ```bash
   uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
   ```

### Execution & Testing Integration
Included securely is `test_analytics.py`, which is dynamically designed to iterate test permutations over MP3s against your local endpoints!
```bash
python test_analytics.py
```
*(Tests include explicit missing-key 401 checks alongside fallback/active AI multimodal execution).*

## 📚 Project History
1. **Initial Phase: AI Document Analysis System**
   The project originally started as a standalone AI Document processing hub designed to execute fast, non-blocking asynchronous OCR tasks utilizing Transformer endpoints.
2. **Second Phase: Compliance & Audio Analytics (Hackathon Expansion)**
   The architecture was heavily refactored from a procedural `app/` setup into a deeply modular `src/` hierarchy featuring split `routes/`, `services/`, and `utils/`. Audio pipeline analysis was introduced using state-of-the-art multimodal extraction models allowing simultaneous Transcription and Entity categorization in a strict boolean formatting required by production evaluators.
