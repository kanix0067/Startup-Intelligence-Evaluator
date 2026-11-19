import asyncio
import time

import pytest
from fastapi.testclient import TestClient

from app.models.startup import StartupInput

PAYLOAD = {
    "startup_idea": "Affordable food delivery",
    "problem": "Expensive for students",
    "target_customer": "Students",
    "industry": "Food Delivery",
    "location": "Coimbatore",
    "budget": 500000,
}


def run(coro):
    return asyncio.run(coro)


def test_all_stages_run_and_report_progress(fake_agents):
    events = []
    startup = StartupInput(**PAYLOAD)
    result = run(fake_agents.OrchestratorAgent().run(
        startup, lambda k, s, d, e: events.append((k, s))))

    assert set(result) == set(fake_agents.STAGE_KEYS)
    for key in fake_agents.STAGE_KEYS:
        assert (key, "running") in events
        assert (key, "completed") in events


def test_one_failing_agent_does_not_break_the_rest(fake_agents, monkeypatch):
    class Boom:
        def analyze(self, *a):
            raise RuntimeError("tavily exploded")

    agents = list(fake_agents.RESEARCH_AGENTS)
    agents[2] = ("competitor", Boom)
    monkeypatch.setattr(fake_agents, "RESEARCH_AGENTS", agents)

    result = run(fake_agents.OrchestratorAgent().run(StartupInput(**PAYLOAD)))

    assert result["competitor"]["status"] == "FAILED"
    assert "tavily exploded" in result["competitor"]["error"]
    assert result["market"]["research_data"] == ["x"]   # others unaffected
    assert "final_advisor" in result


def test_slow_agent_times_out(fake_agents, monkeypatch):
    class Slow:
        def analyze(self, *a):
            time.sleep(0.5)
            return {"research_data": ["late"]}

    agents = list(fake_agents.RESEARCH_AGENTS)
    agents[0] = ("market", Slow)
    monkeypatch.setattr(fake_agents, "RESEARCH_AGENTS", agents)

    result = run(fake_agents.OrchestratorAgent(timeout=0.05).run(
        StartupInput(**PAYLOAD)))

    assert result["market"]["status"] == "FAILED"
    assert "Timed out" in result["market"]["error"]


@pytest.fixture
def client(fake_agents, tmp_path, monkeypatch):
    from app import db
    monkeypatch.setattr(db, "DB_PATH", tmp_path / "test.db")
    db.init_db()
    from app.main import app
    with TestClient(app) as c:
        yield c


def wait_done(client, job_id, timeout=5):
    end = time.time() + timeout
    while time.time() < end:
        job = client.get(f"/analyses/{job_id}").json()
        if job["status"] in ("completed", "failed"):
            return job
        time.sleep(0.05)
    raise AssertionError("job did not finish")


def test_job_lifecycle_saves_report(client):
    r = client.post("/analyses", json=PAYLOAD)
    assert r.status_code == 202
    job = wait_done(client, r.json()["job_id"])

    assert job["status"] == "completed"
    assert all(a["status"] == "completed" for a in job["agents"].values())
    saved = client.get(f"/startups/{job['report_id']}").json()
    assert saved["startup"]["location"] == "Coimbatore"


def test_unknown_job_is_404(client):
    assert client.get("/analyses/does-not-exist").status_code == 404


def test_invalid_payload_is_422(client):
    assert client.post("/analyses", json={"startup_idea": "only this"}).status_code == 422
