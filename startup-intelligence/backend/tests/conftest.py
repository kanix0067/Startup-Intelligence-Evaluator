"""
Tests never call Gemini or Tavily. If those SDKs are not installed in the
test environment, lightweight stubs are registered so imports succeed.
"""
import sys
import types

import pytest

sys.path.insert(0, ".")

try:
    import tavily  # noqa: F401
except ImportError:
    mod = types.ModuleType("tavily")
    mod.TavilyClient = type("TavilyClient", (), {"__init__": lambda s, api_key=None: None})
    sys.modules["tavily"] = mod

try:
    from google import genai  # noqa: F401
except ImportError:
    g = types.ModuleType("google.genai")
    g.Client = type("Client", (), {"__init__": lambda s, api_key=None: None})
    pkg = types.ModuleType("google")
    pkg.genai = g
    sys.modules["google"] = pkg
    sys.modules["google.genai"] = g


@pytest.fixture
def fake_agents(monkeypatch):
    """Replace every real agent with a fast fake (no network)."""
    from app.agents import orchestrator as o

    def make(name):
        class Fake:
            def analyze(self, *args):
                return {"agent": name, "research_data": ["x"], "evidence": []}
        return Fake

    monkeypatch.setattr(
        o, "RESEARCH_AGENTS", [(k, make(k)) for k, _ in o.RESEARCH_AGENTS]
    )
    monkeypatch.setattr(o, "ConflictDetectionAgent", make("conflicts"))
    monkeypatch.setattr(o, "SkepticAgent", make("skeptic"))
    monkeypatch.setattr(o, "FinalAdvisorAgent", make("final_advisor"))
    return o
