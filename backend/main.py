import os
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional

try:
    from data_engine import FactoryDataEngine
    from sop_rag import search_sops
    from investigation_engine import InvestigationEngine
except ImportError:
    from backend.data_engine import FactoryDataEngine
    from backend.sop_rag import search_sops
    from backend.investigation_engine import InvestigationEngine

app = FastAPI(
    title="MFGX AI",
    description="Production Investigation Copilot",
    version="0.1.0"
)

# Parse CORS allowed origins from environment
allowed_origins_env = os.environ.get("ALLOWED_ORIGINS")
default_local_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000"
]

if allowed_origins_env and allowed_origins_env.strip() != "*":
    origins = [o.strip() for o in allowed_origins_env.split(",") if o.strip()]
    for loc in default_local_origins:
        if loc not in origins:
            origins.append(loc)
    allow_all = False
else:
    origins = ["*"]
    allow_all = True

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=not allow_all,
    allow_methods=["*"],
    allow_headers=["*"],
)

try:
    engine = FactoryDataEngine()
except Exception as e:
    engine = None
    print(f"Warning: Failed to initialize FactoryDataEngine: {e}")

try:
    investigation_engine = InvestigationEngine(data_engine=engine)
except Exception as e:
    investigation_engine = None
    print(f"Warning: Failed to initialize InvestigationEngine: {e}")


class InvestigationRequest(BaseModel):
    question: str = Field(..., example="Why did Line L3 miss its production target on August 4, and what action should be taken?")


@app.get("/")
def read_root():
    return {
        "app": "MFGX AI — Production Investigation Copilot",
        "version": "0.1.0",
        "status": "online"
    }


@app.post("/investigate")
def investigate(req: InvestigationRequest):
    """
    Primary Production Investigation Endpoint.
    Executes full data engine facts collection, RAG SOP retrieval, and AI investigation synthesis.
    """
    if not req.question or not req.question.strip():
        raise HTTPException(status_code=400, detail="Question string cannot be empty.")

    if investigation_engine is None:
        raise HTTPException(status_code=500, detail="Investigation Engine is uninitialized.")

    result = investigation_engine.run_investigation(req.question)

    status = result.get("status")
    if status == "clarification_required":
        raise HTTPException(status_code=400, detail=result.get("message"))
    elif status == "not_found":
        raise HTTPException(status_code=404, detail=result.get("message"))
    elif status == "success":
        return {
            "status": "success",
            "investigation": result.get("investigation"),
            "note": result.get("note")
        }
    else:
        raise HTTPException(status_code=500, detail="An unknown error occurred during investigation execution.")


@app.post("/debug/investigate")
def debug_investigate(req: InvestigationRequest):
    """
    Debug endpoint returning raw extracted facts and retrieved SOPs.
    """
    if investigation_engine is None:
        raise HTTPException(status_code=500, detail="Investigation engine is uninitialized.")

    scope = investigation_engine.parse_query_scope(req.question)
    line = scope.get("line")
    date = scope.get("date")

    if not line or not date:
        return {
            "debug": True,
            "status": "clarification_required",
            "parsed_scope": scope,
            "message": "Specify target line (e.g. L3) and date (e.g. 2026-08-04) in question."
        }

    prod = engine.investigate_production(line=line, date_str=date) if engine else None
    downtime = engine.get_downtime(line=line, date_str=date) if engine else None
    quality = engine.get_quality(line=line, date_str=date) if engine else None

    downtime_records = downtime.get("records", []) if downtime else []
    machines = list(set([d.get("machine_id") for d in downtime_records if d.get("machine_id")]))
    maint_records = []
    for m_id in machines:
        try:
            m_hist = engine.get_maintenance_history(machine_id=m_id)
            if m_hist and m_hist.get("records"):
                maint_records.extend(m_hist.get("records"))
        except Exception:
            pass

    sop_results = search_sops(query=f"Line {line} {downtime_records[0].get('reason', '') if downtime_records else ''}", top_k=3)

    return {
        "debug": True,
        "question": req.question,
        "parsed_scope": scope,
        "production_facts": prod,
        "downtime_facts": downtime,
        "maintenance_facts": maint_records,
        "quality_facts": quality,
        "sop_retrieval_results": sop_results
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "0.0.0.0")
    uvicorn.run("main:app", host=host, port=port, reload=False)
