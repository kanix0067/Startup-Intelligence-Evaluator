import asyncio
import logging
import time

from app.agents.market import MarketResearchAgent
from app.agents.customer import CustomerAgent
from app.agents.competitor import CompetitorAgent
from app.agents.location import LocationRiskAgent
from app.agents.business_model import BusinessModelAgent
from app.agents.financial import FinancialAgent
from app.agents.risk import RiskAgent
from app.agents.conflict import ConflictDetectionAgent
from app.agents.sceptic import SkepticAgent
from app.agents.advisor import FinalAdvisorAgent

logger = logging.getLogger("startup_intelligence")

# Seconds to wait for one agent before marking it failed (a stuck network
# call must not hang the whole analysis).
AGENT_TIMEOUT_SECONDS = 120

# Research agents run concurrently; their result keys.
RESEARCH_AGENTS = [
    ("market", MarketResearchAgent),
    ("customer", CustomerAgent),
    ("competitor", CompetitorAgent),
    ("location", LocationRiskAgent),
    ("business_model", BusinessModelAgent),
    ("financial", FinancialAgent),
    ("risk", RiskAgent),
]

# Ordered stages shown to the user (research agents, then review stages).
STAGE_KEYS = [k for k, _ in RESEARCH_AGENTS] + [
    "conflicts",
    "skeptic",
    "final_advisor",
]


def _failed_result(key, error):
    """Placeholder so one failed agent does not break the others."""
    return {
        "agent": key,
        "status": "FAILED",
        "error": error,
        "research_data": [],
        "evidence": [],
    }


class OrchestratorAgent:

    def __init__(self, timeout=AGENT_TIMEOUT_SECONDS):
        self.timeout = timeout

    @staticmethod
    def _emit(on_progress, key, status, duration=None, error=None):
        if on_progress:
            try:
                on_progress(key, status, duration, error)
            except Exception:
                logger.exception("progress callback failed")

    async def _run_stage(self, key, fn, args, on_progress):
        self._emit(on_progress, key, "running")
        started = time.perf_counter()
        try:
            result = await asyncio.wait_for(
                asyncio.to_thread(fn, *args),
                timeout=self.timeout,
            )
        except asyncio.TimeoutError:
            msg = f"Timed out after {self.timeout} seconds"
            logger.error("%s: %s", key, msg)
            self._emit(on_progress, key, "failed",
                       round(time.perf_counter() - started, 2), msg)
            return _failed_result(key, msg)
        except Exception as exc:
            logger.exception("%s failed", key)
            self._emit(on_progress, key, "failed",
                       round(time.perf_counter() - started, 2), str(exc))
            return _failed_result(key, str(exc))

        self._emit(on_progress, key, "completed",
                   round(time.perf_counter() - started, 2))
        return result

    async def run(self, startup, on_progress=None):

        results = await asyncio.gather(*[
            self._run_stage(key, cls().analyze, (startup,), on_progress)
            for key, cls in RESEARCH_AGENTS
        ])

        analysis = {
            key: result
            for (key, _), result in zip(RESEARCH_AGENTS, results)
        }

        analysis["conflicts"] = await self._run_stage(
            "conflicts", ConflictDetectionAgent().analyze,
            (dict(analysis),), on_progress,
        )

        analysis["skeptic"] = await self._run_stage(
            "skeptic", SkepticAgent().analyze,
            (startup, dict(analysis)), on_progress,
        )

        analysis["final_advisor"] = await self._run_stage(
            "final_advisor", FinalAdvisorAgent().analyze,
            (startup, dict(analysis)), on_progress,
        )

        return analysis
