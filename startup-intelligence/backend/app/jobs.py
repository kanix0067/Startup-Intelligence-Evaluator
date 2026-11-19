"""
Background analysis jobs with per-agent status.

Jobs are kept in memory (single process) so the frontend can poll live
progress. The finished report is persisted to the database, so reports
survive a restart; in-flight job status does not.
"""

import asyncio
import logging
import uuid
from datetime import datetime, timezone

from app import db
from app.agents.orchestrator import OrchestratorAgent, STAGE_KEYS

logger = logging.getLogger("startup_intelligence")

MAX_JOBS = 100
JOBS = {}
_tasks = set()  # keep references so tasks are not garbage collected


def _now():
    return datetime.now(timezone.utc).isoformat()


def _prune():
    if len(JOBS) <= MAX_JOBS:
        return
    done = [j for j in JOBS.values() if j["status"] in ("completed", "failed")]
    done.sort(key=lambda j: j["created_at"])
    for job in done[: len(JOBS) - MAX_JOBS]:
        JOBS.pop(job["id"], None)


def create_job():
    job = {
        "id": str(uuid.uuid4()),
        "status": "queued",
        "created_at": _now(),
        "agents": {
            key: {"status": "pending", "duration_s": None, "error": None}
            for key in STAGE_KEYS
        },
        "report_id": None,
        "error": None,
    }
    JOBS[job["id"]] = job
    _prune()
    return job


def get_job(job_id):
    return JOBS.get(job_id)


async def _run(job, startup):
    job["status"] = "running"

    def on_progress(key, status, duration, error):
        job["agents"][key] = {
            "status": status,
            "duration_s": duration,
            "error": error,
        }

    try:
        analysis = await OrchestratorAgent().run(startup, on_progress)
        job["report_id"] = db.save_report(startup.model_dump(), analysis)
        job["status"] = "completed"
    except Exception as exc:
        logger.exception("Analysis job failed")
        job["status"] = "failed"
        job["error"] = str(exc)


def start_job(startup):
    job = create_job()
    task = asyncio.create_task(_run(job, startup))
    _tasks.add(task)
    task.add_done_callback(_tasks.discard)
    return job
