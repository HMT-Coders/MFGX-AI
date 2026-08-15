# MFGX AI — Production Investigation Copilot

![MFGX AI Brand Mark](frontend/src/assets/mfgx-icon.png)

**MFGX AI** is an intelligent, fact-grounded Production Investigation Copilot designed for manufacturing supervisors. It converts natural-language questions about production shortfalls, machine stoppages, quality rejections, and recurring maintenance into evidence-grounded investigation assessments and actionable SOP guidance.

---

## 🌟 Key Features

- **Telemetry Data Engine**: Fast querying across synthetic factory telemetry covering Production, Downtime, Maintenance, and Quality inspection data.
- **Hybrid Lightweight SOP RAG Engine**: Retrieves relevant sections from `SOP-301.pdf` through `SOP-305.pdf` using cloud embeddings when available and a local TF-IDF fallback when cloud retrieval is unavailable.
- **Fact-Grounded AI Copilot**: Synthesizes factory evidence and relevant SOP guidance while explicitly handling unavailable information instead of fabricating facts.
- **Intent-Aware Query Parser**: Detects investigation intent, machine/line entities, dates, historical scope, data-availability boundaries, and out-of-scope questions.
- **Investigation Report Generator**: One-click generation of print-friendly HTML/PDF investigation reports for management and shift handovers.
- **Modern Responsive Interface**: React 19 + TypeScript + Vite + Tailwind CSS dark-navy user interface.
- **Low-Memory Cloud Architecture**: Removes PyTorch, SentenceTransformers, and ChromaDB from the production retrieval runtime to support low-memory cloud deployment.

---

## 🎯 Problem

Manufacturing investigations often require supervisors to manually combine information from multiple sources:

- Production targets and actual output
- Machine downtime
- Maintenance history
- Quality inspections
- Standard Operating Procedures

This can make investigations slow and inconsistent.

MFGX AI provides a single natural-language interface that connects these sources and produces a focused investigation with supporting evidence and recommended action.

---

## 💡 Solution

MFGX AI works as a digital investigation assistant for factory operations.

```text
User Question
      ↓
Query & Intent Understanding
      ↓
Relevant Factory Data
      ↓
Relevant SOP Retrieval
      ↓
Evidence Grounding
      ↓
AI Investigation Synthesis
      ↓
Investigation + Evidence + Recommendation
```

The system is designed to keep the final operational decision with the authorized human supervisor.

For a detailed explanation of the problem, solution, architecture, and project outcome, see:

**[📖 Solution & Problem Statement](SOLUTION.md)**

---

## 🧠 Intent-Aware Investigation

MFGX AI does not treat every question as the same investigation.

| Intent | Example |
|---|---|
| `PRODUCTION_TARGET` | Why did Line L3 miss its production target? |
| `QUALITY_DEFECT` | Why did Line L3 have a high rejection rate? |
| `DOWNTIME_EVENT` | What happened to machine M301? |
| `MAINTENANCE_RECURRING` | Investigate recurring temperature problems on M301. |
| `SUPERVISOR_ACTION` | What should the supervisor do about the overheating problem? |
| `FINANCIAL_UNAVAILABLE` | What was the exact financial cost? |
| `OPERATOR_UNAVAILABLE` | Which operator was responsible? |
| `UNSUPPORTED_OUT_OF_SCOPE` | What is the weather today? |

This routing ensures that a quality question focuses on quality evidence, a maintenance question focuses on maintenance evidence, and a production question focuses on production performance.

---

## 🏗️ System Architecture

```text
MFGX AI (Production Investigation Copilot)
│
├── Frontend (React 19 + TypeScript + Vite + Tailwind CSS)
│   ├── Investigation Input & Scope Guidance
│   ├── Interactive Telemetry Cards
│   │   ├── Production
│   │   ├── Downtime
│   │   ├── Maintenance
│   │   └── Quality
│   ├── SOP Evidence & Supporting Evidence
│   └── One-Click Print / PDF Report Generator
│
├── Backend (Python FastAPI + Uvicorn)
│   ├── FactoryDataEngine
│   │   ├── Production
│   │   ├── Downtime
│   │   ├── Maintenance
│   │   └── Quality
│   ├── Lightweight Hybrid SOP RAG
│   │   ├── Cloud Embeddings
│   │   ├── NumPy Cosine Similarity
│   │   └── TF-IDF Local Fallback
│   └── InvestigationEngine
│       ├── Intent Parsing
│       ├── Evidence Routing
│       └── LLM Investigation Synthesis
│
└── Production Assets
    ├── Synthetic Factory CSVs
    └── Standard Operating Procedure PDFs
```

---

## 🔎 Hybrid Lightweight RAG

The production RAG architecture was redesigned to reduce memory usage in low-memory cloud environments.

### Previous Architecture

```text
SentenceTransformers
        +
PyTorch
        +
ChromaDB
```

### Current Architecture

```text
                 SOP Chunks
                    |
          +---------+---------+
          |                   |
          v                   v
   Cloud Embeddings      TF-IDF Fallback
          |                   |
          v                   v
       NumPy Cosine Similarity
                 |
                 v
          Relevant SOP Evidence
```

### Mode A — Cloud Embeddings

When a supported embedding API is available, the system retrieves dense embeddings for the query and compares them with precomputed SOP embeddings using NumPy cosine similarity.

### Mode B — TF-IDF Fallback

If cloud embedding access is unavailable, rate-limited, times out, or fails, the system falls back to local retrieval using:

```python
TfidfVectorizer(
    ngram_range=(1, 3),
    sublinear_tf=True
)
```

This fallback does not require PyTorch, SentenceTransformers, or ChromaDB.

### SOP Cache

```text
backend/sop_chunks_cache.json
backend/sop_embeddings_cache.json
```

These caches avoid unnecessarily rebuilding SOP data for every investigation.

---

## 📁 Directory Structure

```text
MFGX-AI/
│
├── frontend/
│   ├── src/
│   │   ├── assets/
│   │   ├── components/
│   │   ├── services/
│   │   ├── types/
│   │   └── utils/
│   ├── public/
│   ├── netlify.toml
│   ├── package.json
│   └── vite.config.ts
│
├── backend/
│   ├── data_engine.py
│   ├── sop_rag.py
│   ├── sop_chunks_cache.json
│   ├── sop_embeddings_cache.json
│   ├── investigation_engine.py
│   ├── main.py
│   ├── test_queries.py
│   └── requirements.txt
│
├── data/
│   ├── production.csv
│   ├── downtime.csv
│   ├── quality.csv
│   └── maintenance.csv
│
├── sops/
│   ├── SOP-301.pdf
│   ├── SOP-302.pdf
│   ├── SOP-303.pdf
│   ├── SOP-304.pdf
│   └── SOP-305.pdf
│
├── render.yaml
├── .env.example
├── .gitignore
├── LICENSE
├── README.md
└── SOLUTION.md
```

---

## 🚀 Getting Started

### Prerequisites

- **Node.js**: `v20.0.0+`
- **Python**: `3.10+` or `3.11+`
- **Git**

### Backend Setup

```bash
cd backend
python -m venv venv
```

Windows:

```bash
venv\Scripts\activate
```

macOS/Linux:

```bash
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Copy `.env.example` to `.env` in the root project directory:

```bash
cp ../.env.example ../.env
```

Configure:

```env
LLM_API_KEY=your_api_key_here
LLM_MODEL=your_supported_model
ALLOWED_ORIGINS=http://localhost:5173
```

**Never commit `.env` or expose API keys in frontend code.**

Start the backend:

```bash
python main.py
```

Backend:

```text
http://127.0.0.1:8000
```

Swagger:

```text
http://127.0.0.1:8000/docs
```

### Frontend Setup

```bash
cd frontend
npm install
```

For local development:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000
```

Start:

```bash
npm run dev
```

Open:

```text
http://127.0.0.1:5173
```

---

## 📡 API Reference

### `POST /investigate`

Submits a natural-language question for automated production investigation.

#### Request

```json
{
  "question": "Why did Line L3 miss its production target on August 4, and what action should be taken?"
}
```

#### Response Structure

```json
{
  "status": "success",
  "investigation": {
    "investigation_question": "...",
    "investigation_scope": {
      "line": "L3",
      "date": "2026-08-04"
    },
    "likely_contributing_factor": "...",
    "recommended_action": "...",
    "confidence": "high",
    "production_performance": {
      "target": 3300,
      "actual": 2895,
      "shortfall": 405,
      "shortfall_percentage": 12.27
    },
    "major_downtime_events": [],
    "maintenance_evidence": [],
    "quality_evidence": {},
    "relevant_sops": [],
    "supporting_evidence": [],
    "limitations": []
  }
}
```

---

## 🌐 Production Deployment

### Backend — Render

The project includes:

```text
render.yaml
```

Build:

```text
pip install -r backend/requirements.txt
```

Start:

```text
cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT
```

Configure:

```text
LLM_API_KEY
LLM_MODEL
ALLOWED_ORIGINS
```

Never place the API key in GitHub or frontend environment variables.

### Frontend — Netlify

The project includes:

```text
frontend/netlify.toml
```

Build:

```text
npm run build
```

Publish directory:

```text
frontend/dist
```

Set:

```text
VITE_API_BASE_URL=<your deployed backend URL>
```

---

## 🧪 Testing & Verification

Run the backend test suite:

```bash
cd backend
python test_queries.py
```

Run the frontend production build:

```bash
cd frontend
npm run build
```

### Main Verified Investigation

| Metric | Result |
|---|---:|
| Production target | 3,300 |
| Actual production | 2,895 |
| Shortfall | 405 |
| Shortfall rate | 12.27% |
| M301 overheating downtime | 47 minutes |
| Quality rejections | 139 |
| Rejection rate | 4.80% |
| M301 historical maintenance records | 4 |

### Memory Validation

The lightweight backend was stress-tested with **55 investigation requests**.

Reported measurements included:

- Approximately **128.90 MB** after application initialization
- Approximately **129.85 MB** after the first investigation
- Approximately **129.93 MB** after 30+ investigations
- Approximately **130.23 MB** during concurrent-request measurement
- Approximately **157.41 MB** reported peak during the stress-test measurement

Reported memory drift across 55 requests was approximately **0.35 MB**.

---

## 🔐 Security

Sensitive configuration is stored in environment variables:

```text
LLM_API_KEY
LLM_MODEL
ALLOWED_ORIGINS
```

The frontend must never contain the backend LLM API key.

The repository `.gitignore` protects `.env` and other local secrets/build artifacts from Git tracking.

---

## 📖 Project Documentation

- [Solution & Problem Statement](SOLUTION.md)

---

## 📜 License

Internal Proprietary Software — **MFGX AI Production Investigation Copilot**.

[![License: Custom](https://img.shields.io/badge/License-MFGX%20AI-blue.svg)](LICENSE)

See the [LICENSE](LICENSE) file for the complete terms.
