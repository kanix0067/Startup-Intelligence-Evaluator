import time

from app.agents import advisor as adv
from app.agents.advisor import FinalAdvisorAgent


def huge_report():
    big = {
        "research_data": [
            {"title": f"Source {i}", "url": f"https://x.com/{i}", "content": "word " * 1000}
            for i in range(60)
        ],
        "evidence": [{"claim": "c" * 500} for _ in range(200)],
        "llm_analysis": {"status": "SUCCESS", "output": "analysis " * 500},
    }
    return {
        "analysis_status": {"market": "RESEARCH_AVAILABLE"},
        "key_findings": {"market": big, "competitor": {**big, "category_counts": {"DIRECT_COMPETITOR": 3},
                         "direct_competitors": [{"name": f"C{i}"} for i in range(10)]}},
        "risk_summary": {"high": 2, "medium": 1, "low": 0, "total": 3},
        "conflict_summary": {"conflicts": [{"type": "T", "severity": "HIGH", "description": "d" * 900}] * 20},
        "skeptic_review": {"concerns": [{"category": "MARKET", "severity": "HIGH", "challenge": "q" * 900}] * 30},
        "assumptions": ["a" * 400] * 30,
        "unknowns": ["u" * 400] * 30,
    }


def test_digest_is_small_even_for_huge_reports():
    report = huge_report()
    assert len(str(report)) > 500_000          # what the old prompt contained
    digest = FinalAdvisorAgent().build_prompt_digest(report)
    assert len(digest) <= adv.MAX_DIGEST_CHARS


def test_digest_keeps_the_useful_parts():
    digest = FinalAdvisorAgent().build_prompt_digest(huge_report())
    assert "risk_summary" in digest and "DIRECT_COMPETITOR" in digest


def test_slow_llm_falls_back_instead_of_hanging(monkeypatch):
    monkeypatch.setattr(adv, "LLM_TIMEOUT_SECONDS", 0.05)

    class SlowLLM:
        model = "fake"
        def generate(self, prompt):
            time.sleep(0.5)
            return {"status": "SUCCESS", "model": "fake", "output": "late"}

    start = time.time()
    result = FinalAdvisorAgent().generate_with_timeout(SlowLLM(), "p")
    assert time.time() - start < 0.4
    assert result["status"] == "UNAVAILABLE"


def test_fast_llm_result_is_returned():
    class FastLLM:
        model = "fake"
        def generate(self, prompt):
            return {"status": "SUCCESS", "model": "fake", "output": "ok"}

    assert FinalAdvisorAgent().generate_with_timeout(FastLLM(), "p")["output"] == "ok"
