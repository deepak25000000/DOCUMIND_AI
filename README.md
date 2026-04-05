![Python](https://img.shields.io/badge/Python-3.11-blue) ![FastAPI](https://img.shields.io/badge/FastAPI-0.100.0-00a393) ![Google Gemini](https://img.shields.io/badge/Google%20Gemini-2.5%20Flash-orange) ![Docker](https://img.shields.io/badge/Docker-Ready-2496ed) ![License: MIT](https://img.shields.io/badge/License-MIT-yellow)

# DocuMind AI - Intelligent Document Analysis & Call Center Compliance System

**DocuMind AI** is an advanced AI-Powered extraction system that serves a dual purpose. It seamlessly processes PDF, DOCX, and Image files to extract structured insights using OCR, and acts as a **Call Center Compliance Engine** utilizing cutting-edge multimodal audio processing with Google Gemini AI.

## Features

- **Call Center Compliance Validation** -- Audio-streaming NLP mapping natively to standard operating procedures (SOP), evaluating agents on Greetings, IDs, Problems, Solutions, and Closings, alongside payment classifications.
- **Multimodal AI Pipeline (Call Analytics)** -- Zero-shot audio Base64 directly evaluated by `gemini-2.5-flash`, bypassing separated STT delays to extract sentiment and keywords.
- **Multi-Format Document Processing** -- Supports PDF, DOCX, and image files (PNG, JPG, JPEG) with format-specific parsing for maximum accuracy.
- **AI-Powered Summarization** -- Generates concise 2-3 sentence summaries and contextual awareness using Gemini AI.
- **Named Entity Recognition (NER)** -- Extracts people, organizations, dates, and monetary amounts from document text.
- **OCR Pipeline** -- Tesseract OCR with OpenCV preprocessing (grayscale, denoising, adaptive thresholding) for images.
- **RESTful API with Authentication** -- Secured endpoints utilizing API key authentication via `x-api-key` header with HTTP 401 robust validation.
- **Async Processing Pipeline** -- Built on FastAPI's async architecture for fast, non-blocking asynchronous workload processing.

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Backend** | Python 3.11, FastAPI, Uvicorn |
| **AI/NLP Engine** | Google Gemini (`gemini-2.5-flash`) Multimodal API |
| **OCR / Parsing** | Tesseract OCR, `pdfplumber`, `python-docx`, OpenCV |
| **Authentication** | Custom strict header-based validation (`x-api-key`) |
| **Deployment Options** | Docker, Render, Railway, Vercel |

---

## Architecture

**DocuMind Multi-Pipeline Flow**
```text
  ┌────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌────────────┐
  │            │    │  Doc Analyzer   │    │ Text Processing │    │            │
  │  Upload &  │───>│  Base64 -> Text │───>│ OCR/Norm/Clean  │───>│ Gemini 2.5 │
  │  Validate  │    └─────────────────┘    └─────────────────┘    │  Analysis  │
  │            │                                                    │            │
  │   Audio or │    ┌─────────────────┐                           │   Engine   │
  │   Document │───>│ Call Analytics  │──────────────────────────>│            │
  │   Base64   │    │ Base64 Audio    │                           │            │
  └────────────┘    └─────────────────┘                           └────────────┘
                                                                        │
                                                                        v
                                                             ┌────────────────────┐
                                                             │ Structured JSON    │
                                                             │ Out:               │
                                                             │ - SOP Validations  │
                                                             │ - Analytics Enums  │
                                                             │ - NER/Sentiment    │
                                                             └────────────────────┘
```
**Key Design Decisions:**
- Audio Base64 feeds directly to Gemini multimodal, ensuring native STT plus logic extrapolation in an atomic request.
- The OCR text extraction uses deep preprocessing (thresholding/grayscale) assuring robust text extraction before Gemini parsing.

---

## API Documentation

### Authentication
All requests require an API key passed via the `x-api-key` header. Invalid or absent keys will explicitly return HTTP `401 Unauthorized`.

| Header | Description | Required |
|---|---|---|
| `x-api-key` | Your API key defined in your environment configs | Yes |

### `POST /api/call-analytics`
Analyze an encoded audio call for agent compliance validation.

**Request Body (JSON)**:
```json
{
  "language": "Tamil | Hindi | English",
  "audioFormat": "mp3",
  "audioBase64": "<base64-encoded-audio>"
}
```

**Success Response (200)**:
```json
{
  "status": "success",
  "language": "Hindi",
  "transcript": "Agent: Welcome to company... Customer: Hello I want to pay.",
  "summary": "Customer discussed payment.",
  "sop_validation": {
    "greeting": true,
    "identification": true,
    "problemStatement": true,
    "solutionOffering": true,
    "closing": false,
    "complianceScore": 0.8,
    "adherenceStatus": "NOT_FOLLOWED",
    "explanation": "No closing recognized."
  },
  "analytics": {
    "paymentPreference": "FULL_PAYMENT",
    "rejectionReason": "NONE",
    "sentiment": "Positive"
  },
  "keywords": ["payment", "support"]
}
```

### `POST /api/document-analyze`
Analyze a base64-encoded document for NER, summary, and sentiment.

**Request Body (JSON)**:
```json
{
  "fileName": "report.pdf",
  "fileType": "pdf",
  "fileBase64": "<base64-encoded-file-content>"
}
```

---

## Setup Instructions

### Prerequisites
- Python 3.11+
- Tesseract OCR installed locally.
- Google Gemini API key.

### 1. Clone and Install
```bash
git clone https://github.com/YOUR_USERNAME/HCL_HACK.git
cd HCL_HACK
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
cp .env.example .env
```
Edit `.env` and set `GEMINI_API_KEY` and your custom `API_KEY`.

### 3. Run the Server
```bash
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

---

## Deployment (Zero-Config)

### Docker
```bash
docker build -t documind-ai .
docker run -p 8000:8000 --env-file .env documind-ai
```

### Deploy to Render / Railway
Render and Railway natively detect `render.yaml` and `railway.toml` out of the box. Ensure your custom `API_KEY` and `GEMINI_API_KEY` are mapped directly in the platform dashboard integrations.

---

## Project Structure
```text
HCL_HACK/
├── src/
│   ├── main.py                # FastAPI endpoints & core application
│   ├── routes/                # Modular routers
│   ├── services/              
│   │   ├── call_analytics.py  # Zero-shot Multimodal Audio engine
│   │   ├── text_extractor.py  # PDF, DOCX, and image OCR pipelines
│   │   ├── text_processor.py  # Context cleaner
│   │   └── ai_modules.py      # Core Gemini text-NLP logic
│   └── utils/
│       ├── auth.py            # Strict x-api-key authentication layer
│       └── file_detector.py   # Validation mechanisms
├── test_analytics.py          # Validation simulation testing script
├── Dockerfile                 # Container configurations
├── render.yaml                # Deploy configurations
├── railway.toml
├── Procfile             
├── .env.example               
└── README.md                  # This file
```

---

## Error Handling
- `400` - Bad request inputs.
- `401` - Strict lack of authentication mappings.
- `422` - Context processing errors or validation drops.
- `500` - Base Gemini / AI internal processing failures safely handled natively returning fallbacks.

## License
MIT License.
