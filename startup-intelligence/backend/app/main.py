import logging

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.models.startup import StartupInput
from app.agents.orchestrator import OrchestratorAgent
from app import db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("startup_intelligence")

app = FastAPI(title="Startup Intelligence API")

# CORS is required so a browser-based frontend (served from a different
# origin, e.g. a static file, localhost:5500, or a hosted page) is allowed
# to call this API. Restrict allow_origins in production instead of "*".
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    db.init_db()


# Also run at import time: some ASGI test clients and process managers
# don't fire the "startup" lifespan event, and we want the table to exist
# no matter how the app is launched.
db.init_db()


@app.get("/")
def home():
    return {"message": "Startup Intelligence API is running"}


@app.post("/startup")
async def create_startup(data: StartupInput):
    orchestrator = OrchestratorAgent()

    try:
        result = await orchestrator.run(data)
    except Exception as exc:
        logger.exception("Orchestrator failed")
        raise HTTPException(
            status_code=500,
            detail=f"Analysis pipeline failed: {exc}",
        )

    startup_dict = data.model_dump()

    try:
        report_id = db.save_report(startup_dict, result)
    except Exception:
        logger.exception("Could not persist report (continuing without it)")
        report_id = None

    return {
        "id": report_id,
        "startup": startup_dict,
        "analysis": result,
    }


@app.get("/startups")
def list_startups(limit: int = 50):
    return {"reports": db.list_reports(limit=limit)}


@app.get("/startups/{report_id}")
def get_startup(report_id: str):
    report = db.get_report(report_id)

    if report is None:
        raise HTTPException(status_code=404, detail="Report not found")

    return report


@app.delete("/startups/{report_id}")
def delete_startup(report_id: str):
    deleted = db.delete_report(report_id)

    if not deleted:
        raise HTTPException(status_code=404, detail="Report not found")

    return {"deleted": True}

from app.tools.finance import FinanceInput, simulate as simulate_finance


@app.post("/finance/simulate")
def finance_simulate(data: FinanceInput):
    """Deterministic break-even / runway simulation (no LLM involved)."""
    return simulate_finance(data)

from app import jobs


@app.post("/analyses", status_code=202)
async def start_analysis(data: StartupInput):
    """Start an analysis in the background; poll GET /analyses/{job_id}."""
    job = jobs.start_job(data)
    return {"job_id": job["id"], "status": job["status"]}


@app.get("/analyses/{job_id}")
def analysis_status(job_id: str):
    job = jobs.get_job(job_id)

    if job is None:
        raise HTTPException(status_code=404, detail="Analysis job not found")

    return job
