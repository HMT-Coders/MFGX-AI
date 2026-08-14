# MFGX AI — Production Investigation Copilot

![MFGX AI Brand Mark](frontend/src/assets/mfgx-icon.png)

**MFGX AI** is an intelligent, fact-grounded Production Investigation Copilot designed for manufacturing supervisors. It converts natural language queries regarding line shortfalls, machine stoppages, quality rejections, and recurring maintenance into evidence-grounded investigation assessments and actionable SOP guidance.

---

## 🌟 Key Features

- **Telemetry Data Engine**: Fast querying across synthetic factory telemetry (Production, Downtime, Maintenance, and Quality inspection data).
- **SOP Vector RAG Engine**: Semantic search over Standard Operating Procedures (`SOP-301.pdf` through `SOP-305.pdf`) powered by ChromaDB and `all-MiniLM-L6-v2` embeddings.
- **Fact-Grounded AI Copilot**: Grounded LLM reasoning (Gemini 3.6 Flash / OpenAI GPT-4o) that synthesizes hard telemetry facts and SOP protocols without hallucination.
- **Intent-Aware Query Parser**: Automatic machine-to-line inference (e.g. `M301` $\rightarrow$ `Line L3`), historical scope resolution, data availability boundaries, and out-of-scope guidance.
- **Investigation Report Generator**: One-click generation of print-friendly HTML/PDF investigation reports for management and shift handovers.
- **Modern Responsive Interface**: React 19 + TypeScript + Vite + Tailwind CSS dark-navy user interface.

---

## 🏗️ System Architecture

```
MFGX AI (Production Investigation Copilot)
├── Frontend (React 19 + TypeScript + Vite + Tailwind CSS)
│   ├── Investigation Input & Scope Guidance
│   ├── Interactive Telemetry Cards (Production, Downtime, Maintenance, Quality)
│   ├── SOP Citation Badges & Evidence Grounding
│   └── One-Click Print / PDF Report Generator
│
├── Backend (Python FastAPI + Uvicorn)
│   ├── FactoryDataEngine (Queries production.csv, downtime.csv, quality.csv, maintenance.csv)
│   ├── SOPRAG (ChromaDB vector database containing embedded SOP chunks)
│   └── InvestigationEngine (Intent parsing + LLM reasoning via Gemini 3.6 Flash)
│
└── Production Assets
    ├── Synthetic Factory CSVs (data/*.csv)
    └── Standard Operating Procedure PDFs (sops/*.pdf)
```

---

## 📁 Directory Structure

```
MFGX-AI/
├── frontend/                  # React + TypeScript + Vite Frontend
│   ├── src/
│   │   ├── assets/            # Official MFGX AI logo & icon assets
│   │   ├── components/        # React UI components (ProductionCard, SopEvidence, etc.)
│   │   ├── services/          # API client (submitInvestigation)
│   │   ├── types/             # TypeScript type definitions
│   │   └── utils/             # Print-friendly Report Generator
│   ├── public/                # Favicon and static assets
│   ├── netlify.toml           # Netlify SPA deployment manifest
│   ├── package.json
│   └── vite.config.ts
│
├── backend/                   # Python FastAPI Backend
│   ├── data_engine.py         # Factory telemetry CSV data loader & analyzer
│   ├── sop_rag.py             # ChromaDB vector RAG search interface
│   ├── ingest_sops.py         # PDF parsing & vector embedding script
│   ├── investigation_engine.py# Query parser & LLM investigation engine
│   ├── main.py                # FastAPI REST API server
│   ├── test_queries.py        # Automated test suite (Queries A through K)
│   └── requirements.txt
│
├── data/                      # Synthetic Factory Telemetry Datasets
│   ├── production.csv
│   ├── downtime.csv
│   ├── quality.csv
│   └── maintenance.csv
│
├── sops/                      # Factory Standard Operating Procedure PDFs
│   ├── SOP-301.pdf            # General Line Maintenance & Equipment Audits
│   ├── SOP-302.pdf            # Machine Overheating & Thermal Stoppage Response
│   ├── SOP-303.pdf            # High Quality Rejection & Defect Triaging
│   ├── SOP-304.pdf            # Emergency Stop Protocols
│   └── SOP-305.pdf            # Shift Handover & Production Target Recovery
│
├── render.yaml                # Render backend deployment manifest
├── .env.example               # Root environment variable template
└── .gitignore                 # Git ignore rules for secrets and build artifacts
```

---

## 🚀 Getting Started

### Prerequisites
- **Node.js**: `v20.0.0+`
- **Python**: `3.10+` or `3.11+`
- **Git**

---

### 1. Backend Setup

1. **Navigate to the backend directory**:
   ```bash
   cd backend
   ```

2. **Create a virtual environment (recommended)**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables**:
   Copy `.env.example` to `.env` in the root project directory:
   ```bash
   cp ../.env.example ../.env
   ```
   Add your Gemini or OpenAI API Key to `../.env`:
   ```env
   LLM_API_KEY=your_gemini_api_key_here
   LLM_MODEL=gemini-3.6-flash
   ```

5. **Start the FastAPI backend server**:
   ```bash
   python main.py
   ```
   The backend API will start on **`http://127.0.0.1:8000`**.  
   Swagger API documentation is available at **`http://127.0.0.1:8000/docs`**.

---

### 2. Frontend Setup

1. **Navigate to the frontend directory**:
   ```bash
   cd frontend
   ```

2. **Install Node.js dependencies**:
   ```bash
   npm install
   ```

3. **Configure Environment Variables (Optional for local dev)**:
   Copy `.env.example` to `.env`:
   ```env
   VITE_API_BASE_URL=http://127.0.0.1:8000
   ```

4. **Start the Vite development server**:
   ```bash
   npm run dev
   ```
   Open your browser at **`http://127.0.0.1:5173`**.

---

## 📡 API Reference

### `POST /investigate`
Submits a natural language query for automated production investigation.

**Request Body**:
```json
{
  "question": "Why did Line L3 miss its production target on August 4, and what action should be taken?"
}
```

**Response Payload**:
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
    "production_performance": { "target": 3300, "actual": 2895, "shortfall": 405, "shortfall_percentage": 12.27 },
    "major_downtime_events": [...],
    "maintenance_evidence": [...],
    "quality_evidence": {...},
    "relevant_sops": [...],
    "supporting_evidence": [...],
    "limitations": [...]
  }
}
```

---

## 🌐 Production Deployment

### Backend Deployment (Render / Railway)
The project includes a ready-to-use [`render.yaml`](render.yaml) manifest:
- **Build Command**: `pip install -r backend/requirements.txt`
- **Start Command**: `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`
- **Environment Variables**: Set `LLM_API_KEY`, `LLM_MODEL`, and `ALLOWED_ORIGINS` in your cloud provider's secret manager.

### Frontend Deployment (Netlify / Vercel)
The project includes a ready-to-use [`frontend/netlify.toml`](frontend/netlify.toml) manifest:
- **Build Directory**: `frontend`
- **Build Command**: `npm run build`
- **Publish Directory**: `frontend/dist`
- **Environment Variable**: Set `VITE_API_BASE_URL` to your deployed backend URL.

---

## 🧪 Testing & Verification

Run the automated 11-query test suite against the backend:
```bash
cd backend
python test_queries.py
```

Run frontend production build verification:
```bash
cd frontend
npm run build
```

---

## 📜 License

Internal Proprietary Software — **MFGX AI Production Investigation Copilot**.
