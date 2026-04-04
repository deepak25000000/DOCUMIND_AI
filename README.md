![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Google Gemini](https://img.shields.io/badge/Google%20Gemini-8E75B2?style=for-the-badge&logo=googlegemini&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)

# DocuMind AI - Intelligent Document Analysis System

> **AI-Powered Document Analysis & Extraction System** that processes PDF, DOCX, and image files to extract structured insights using Google Gemini AI. Upload any document and receive an instant summary, named entities, and sentiment analysis -- all through a single API call.

---

## Features

- **Multi-Format Document Processing** -- Supports PDF, DOCX, and image files (PNG, JPG, JPEG) with format-specific parsing for maximum accuracy
- **AI-Powered Summarization** -- Generates concise 2-3 sentence summaries using Google Gemini 2.0 Flash
- **Named Entity Recognition** -- Extracts people, organizations, dates, and monetary amounts from document text
- **Sentiment Analysis** -- Classifies overall document tone as Positive, Negative, or Neutral
- **OCR Pipeline** -- Tesseract OCR with OpenCV preprocessing (grayscale, denoising, adaptive thresholding) for accurate image text extraction
- **Beautiful Dark-Themed Web Interface** -- Glassmorphism-styled UI with drag-and-drop file upload
- **RESTful API with Authentication** -- Secured endpoints with API key authentication via `x-api-key` header
- **Base64 Document Encoding** -- Secure document transmission without multipart form complexity
- **Async Processing Pipeline** -- Built on FastAPI's async architecture for non-blocking document analysis

---

## Tech Stack

| Layer             | Technology                                                   |
|-------------------|--------------------------------------------------------------|
| **Backend**       | Python 3.11, FastAPI, Uvicorn                                |
| **AI/ML**         | Google Gemini 2.0 Flash API                                  |
| **OCR**           | Tesseract OCR with OpenCV preprocessing                      |
| **PDF Parsing**   | pdfplumber                                                   |
| **DOCX Parsing**  | python-docx                                                  |
| **Image Handling**| Pillow, OpenCV (headless)                                    |
| **Frontend**      | Vanilla HTML/CSS/JS with glassmorphism dark theme            |
| **Deployment**    | Docker, Render, Railway                                      |

---

## Architecture

```
                         DocuMind AI Processing Pipeline

  ┌────────────┐    ┌────────────┐    ┌────────────┐    ┌────────────┐    ┌────────────┐
  │            │    │            │    │            │    │            │    │            │
  │  Upload &  │───>│  Base64    │───>│   Text     │───>│   Text     │───>│  Gemini AI │
  │  Validate  │    │  Decode    │    │ Extraction │    │  Cleaning  │    │  Analysis  │
  │            │    │            │    │            │    │            │    │            │
  │ fileName   │    │ Decode to  │    │ PDF:       │    │ Normalize  │    │ Summary    │
  │ fileType   │    │ raw bytes  │    │  pdfplumber│    │ Deduplicate│    │ NER        │
  │ fileBase64 │    │ Size check │    │ DOCX:      │    │ Strip noise│    │ Sentiment  │
  │            │    │ (max 20MB) │    │  python-doc│    │            │    │            │
  │            │    │            │    │ Image:     │    │            │    │            │
  │            │    │            │    │  OCR pipe  │    │            │    │            │
  └────────────┘    └────────────┘    └────────────┘    └────────────┘    └────────────┘
                                                                               │
                                                                               v
                                                                    ┌────────────────┐
                                                                    │  Structured    │
                                                                    │  JSON Response │
                                                                    │                │
                                                                    │  summary       │
                                                                    │  entities      │
                                                                    │  sentiment     │
                                                                    └────────────────┘
```

**Key design decisions:**

- A **single Gemini API call** performs summarization, NER, and sentiment analysis together, reducing latency and API costs
- Format-specific parsers (pdfplumber, python-docx, Tesseract) ensure the best possible text extraction for each file type
- The OCR pipeline applies **grayscale conversion, noise reduction, and adaptive thresholding** before passing images to Tesseract for maximum accuracy
- A **fallback response** is returned if the Gemini API is unavailable, ensuring the system degrades gracefully

---

## API Documentation

### Authentication

All requests require an API key passed via the `x-api-key` header.

| Header      | Description                    | Required |
|-------------|--------------------------------|----------|
| `x-api-key` | Your API key from `.env`      | Yes      |

### `POST /api/document-analyze`

Analyze a base64-encoded document and receive structured AI insights.

**Request Body (JSON):**

```json
{
  "fileName": "quarterly_report.pdf",
  "fileType": "pdf",
  "fileBase64": "<base64-encoded-file-content>"
}
```

| Field        | Type   | Description                                      |
|--------------|--------|--------------------------------------------------|
| `fileName`   | string | Original file name                               |
| `fileType`   | string | One of: `pdf`, `docx`, `image`                   |
| `fileBase64` | string | Base64-encoded file content                      |

**Success Response (200):**

```json
{
  "status": "success",
  "fileName": "quarterly_report.pdf",
  "summary": "The document outlines Q3 2024 financial results, highlighting a 15% year-over-year revenue increase driven by expansion into Asian markets. Operating margins improved to 22%, and the company announced plans for two new product lines in Q1 2025.",
  "entities": {
    "names": ["John Smith", "Sarah Chen"],
    "dates": ["Q3 2024", "January 2025"],
    "organizations": ["Acme Corp", "Global Industries"],
    "amounts": ["$4.2 million", "$850,000"]
  },
  "sentiment": "Positive"
}
```

**Error Responses:**

| Status | Reason                                      |
|--------|---------------------------------------------|
| 400    | Missing or invalid fields, bad base64       |
| 401    | Missing or invalid API key                  |
| 422    | No text could be extracted from the file    |
| 500    | Internal server error                       |

### `GET /health`

Returns `{"status": "healthy"}` -- useful for uptime monitoring and container health checks.

### cURL Example

```bash
# Encode a PDF to base64 and send it for analysis
BASE64=$(base64 -w 0 document.pdf)

curl -X POST http://localhost:8000/api/document-analyze \
  -H "Content-Type: application/json" \
  -H "x-api-key: your_api_key_here" \
  -d "{
    \"fileName\": \"document.pdf\",
    \"fileType\": \"pdf\",
    \"fileBase64\": \"$BASE64\"
  }"
```

### Python Example

```python
import base64
import requests

with open("report.pdf", "rb") as f:
    encoded = base64.b64encode(f.read()).decode("utf-8")

response = requests.post(
    "http://localhost:8000/api/document-analyze",
    headers={"x-api-key": "your_api_key_here"},
    json={
        "fileName": "report.pdf",
        "fileType": "pdf",
        "fileBase64": encoded,
    },
)

data = response.json()
print(f"Summary: {data['summary']}")
print(f"Entities: {data['entities']}")
print(f"Sentiment: {data['sentiment']}")
```

---

## Setup Instructions

### Prerequisites

- Python 3.11+
- Tesseract OCR
- A Google Gemini API key ([get one free from Google AI Studio](https://aistudio.google.com/apikey))

### 1. Clone and Install

```bash
git clone https://github.com/YOUR_USERNAME/HCL_HACK.git
cd HCL_HACK

python -m venv venv
source venv/bin/activate   # Linux/macOS
# venv\Scripts\activate    # Windows

pip install -r requirements.txt
```

### 2. Install Tesseract OCR

**Ubuntu/Debian:**
```bash
sudo apt-get install tesseract-ocr tesseract-ocr-eng
```

**macOS:**
```bash
brew install tesseract
```

**Windows:**
Download the installer from [UB-Mannheim/tesseract](https://github.com/UB-Mannheim/tesseract/wiki) and add it to your PATH.

### 3. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` and set your keys (see [Environment Variables](#environment-variables) below).

### 4. Run the Server

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at `http://localhost:8000`. Interactive Swagger docs are at `http://localhost:8000/docs`.

---

## Docker

```bash
# Build the image
docker build -t documind-ai .

# Run the container
docker run -p 8000:8000 \
  -e GEMINI_API_KEY=your_gemini_key \
  -e API_KEY=your_api_key \
  documind-ai
```

Or using an env file:

```bash
docker run -p 8000:8000 --env-file .env documind-ai
```

### Deploy to Render

1. Push your code to GitHub
2. Connect the repository on [render.com](https://render.com)
3. Render will auto-detect the `render.yaml` configuration
4. Set the `GEMINI_API_KEY` and `API_KEY` environment variables
5. Deploy

### Deploy to Railway

1. Push your code to GitHub
2. Connect the repository on [railway.app](https://railway.app)
3. Railway will auto-detect the `railway.toml` configuration
4. Set the `GEMINI_API_KEY` and `API_KEY` environment variables
5. Deploy

---

## Project Structure

```
HCL_HACK/
├── app/
│   ├── __init__.py            # Package initializer
│   ├── main.py                # FastAPI application & /api/document-analyze endpoint
│   ├── auth.py                # API key authentication middleware
│   ├── file_detector.py       # File type detection and validation
│   ├── text_extractor.py      # PDF, DOCX, and image (OCR) text extraction
│   ├── text_processor.py      # Text cleaning, normalization, deduplication
│   └── ai_modules.py          # Gemini AI integration (summary, NER, sentiment)
├── static/                    # Frontend assets (HTML/CSS/JS)
├── requirements.txt           # Python dependencies
├── Dockerfile                 # Docker container configuration
├── render.yaml                # Render.com deployment config
├── railway.toml               # Railway deployment config
├── Procfile                   # Process file for PaaS platforms
├── test_api.py                # API test script
├── .env.example               # Environment variable template
├── LICENSE                    # MIT License
└── README.md                  # This file
```

---

## Approach

### Text Extraction
Each supported format has a dedicated parser optimized for that file type:
- **PDF**: `pdfplumber` extracts text page-by-page, preserving layout and structure
- **DOCX**: `python-docx` reads paragraphs and tables from Word documents
- **Images**: A multi-step OCR pipeline processes images before Tesseract extraction

### OCR Pipeline
```
Input Image --> Grayscale Conversion --> Noise Reduction --> Adaptive Thresholding --> Tesseract OCR --> Raw Text
```

### AI Analysis
A single, carefully engineered prompt is sent to Google Gemini 2.0 Flash requesting all three analyses (summarization, NER, sentiment) in one API call. This approach:
- Minimizes latency (one round trip instead of three)
- Reduces API costs
- Ensures consistent analysis across tasks

### Error Handling
- Invalid files return descriptive error messages with appropriate HTTP status codes
- If the Gemini API is unreachable, a fallback response with a truncated summary and empty entities is returned
- Input text is truncated to 30,000 characters to stay within model token limits
- File size is capped at 20 MB

---

## Environment Variables

| Variable         | Description                              | Required | Default     |
|------------------|------------------------------------------|----------|-------------|
| `GEMINI_API_KEY` | Google Gemini API key                    | Yes      | --          |
| `API_KEY`        | API key for authenticating requests      | Yes      | --          |
| `HOST`           | Server bind address                      | No       | `0.0.0.0`  |
| `PORT`           | Server port                              | No       | `8000`     |

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
