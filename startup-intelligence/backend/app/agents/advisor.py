import json
import logging
import os
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeout

from app.tools.llm import LLMTool

logger = logging.getLogger("startup_intelligence")

# Max seconds to wait for Gemini in the final synthesis. If it is slower,
# the rule-based advisor report is returned instead of making the user wait.
LLM_TIMEOUT_SECONDS = float(os.getenv("LLM_TIMEOUT_SECONDS", "45"))
# Upper bound on the analysis digest sent to the model (characters).
MAX_DIGEST_CHARS = 7000


class FinalAdvisorAgent:

    def analyze(self, startup, analysis):

        market = analysis.get(
            "market",
            {}
        )

        customer = analysis.get(
            "customer",
            {}
        )

        competitor = analysis.get(
            "competitor",
            {}
        )

        location = analysis.get(
            "location",
            {}
        )

        business_model = analysis.get(
            "business_model",
            {}
        )

        financial = analysis.get(
            "financial",
            {}
        )

        risk = analysis.get(
            "risk",
            {}
        )

        conflicts = analysis.get(
            "conflicts",
            {}
        )

        skeptic = analysis.get(
            "skeptic",
            {}
        )

        risk_summary = risk.get(
            "risk_summary",
            {}
        )

        conflict_list = conflicts.get(
            "conflicts",
            []
        )

        skeptic_concerns = skeptic.get(
            "concerns",
            []
        )

        assumptions = self.collect_assumptions(
            analysis
        )

        unknowns = self.collect_unknowns(
            analysis
        )

        validation_experiments = (
            self.generate_validation_experiments(
                startup,
                market,
                customer,
                competitor,
                financial,
                risk
            )
        )

        executive_summary = (
            self.generate_executive_summary(
                startup,
                market,
                customer,
                competitor,
                risk,
                conflicts,
                skeptic
            )
        )

        rule_based_report = {
            "executive_summary": executive_summary,

            "startup_idea": startup.startup_idea,

            "analysis_status": {
                "market": self.get_status(market),
                "customer": self.get_status(customer),
                "competitor": self.get_status(competitor),
                "location": self.get_status(location),
                "business_model": self.get_status(business_model),
                "financial": self.get_status(financial),
                "risk": self.get_status(risk)
            },

            "key_findings": {
                "market": market,
                "customer": customer,
                "competitor": competitor,
                "location": location,
                "business_model": business_model,
                "financial": financial
            },

            "risk_summary": risk_summary,

            "conflict_summary": {
                "total_conflicts": len(
                    conflict_list
                ),
                "conflicts": conflict_list
            },

            "skeptic_review": {
                "total_concerns": len(
                    skeptic_concerns
                ),
                "summary": skeptic.get(
                    "summary",
                    {}
                ),
                "concerns": skeptic_concerns
            },

            "assumptions": assumptions,

            "unknowns": unknowns,

            "validation_experiments": validation_experiments,

            "mvp_recommendation": (
                self.generate_mvp_recommendation(
                    startup
                )
            ),

            "action_plan": (
                self.generate_action_plan(
                    startup
                )
            ),

            "next_steps": [
                "Validate the most important customer assumption.",
                "Validate the main market assumption.",
                "Research direct competitors.",
                "Test pricing with target customers.",
                "Build a small MVP.",
                "Measure real customer response before scaling."
            ]
        }

        llm_result = self.generate_llm_synthesis(
            startup,
            rule_based_report
        )

        return {
            "agent": "Final Advisor Agent",

            "executive_summary": executive_summary,

            "startup_idea": startup.startup_idea,

            "analysis_status": rule_based_report[
                "analysis_status"
            ],

            "key_findings": rule_based_report[
                "key_findings"
            ],

            "risk_summary": risk_summary,

            "conflict_summary": rule_based_report[
                "conflict_summary"
            ],

            "skeptic_review": rule_based_report[
                "skeptic_review"
            ],

            "assumptions": assumptions,

            "unknowns": unknowns,

            "validation_experiments": (
                validation_experiments
            ),

            "mvp_recommendation": (
                rule_based_report[
                    "mvp_recommendation"
                ]
            ),

            "action_plan": (
                rule_based_report[
                    "action_plan"
                ]
            ),

            "next_steps": rule_based_report[
                "next_steps"
            ],

            "llm_synthesis": llm_result
        }

    def generate_llm_synthesis(
        self,
        startup,
        report
    ):

        try:

            llm_tool = LLMTool()

            digest = self.build_prompt_digest(report)

            prompt = f"""
You are the final synthesis layer of a startup
due-diligence analysis system.

Startup idea:
{startup.startup_idea}

Problem:
{startup.problem}

Target customer:
{startup.target_customer}

Industry:
{startup.industry}

Location:
{startup.location}

Target market:
{startup.target_market}

Budget:
{startup.budget}

Structured analysis (compact digest):
{digest}

Create a concise decision-support synthesis.

Return exactly these sections:

EXECUTIVE_SYNTHESIS:
Summarize the most important findings.

KEY_EVIDENCE:
List the strongest evidence available.

KEY_ASSUMPTIONS:
List the most important assumptions.

KEY_UNKNOWNS:
List important unknowns that still require validation.

MAJOR_RISKS:
List the most important risks.

CONFLICTS:
Explain important conflicts between agents.
If there are no conflicts, say NONE.

VALIDATION_PRIORITY:
List the most important experiments that should be performed next.

IMPORTANT:
Do not invent statistics.
Do not invent facts.
Do not claim that the startup will succeed or fail.
Clearly distinguish evidence, assumptions and unknowns.
Use only the supplied analysis.
"""

            started = time.perf_counter()
            result = self.generate_with_timeout(
                llm_tool,
                prompt
            )
            logger.info(
                "Final advisor LLM: %s chars in prompt, %.1fs, status=%s",
                len(prompt),
                time.perf_counter() - started,
                result.get("status")
            )

            return {
                "status": result.get(
                    "status",
                    "UNKNOWN"
                ),

                "model": result.get(
                    "model",
                    "UNKNOWN"
                ),

                "output": result.get(
                    "output",
                    ""
                )
            }

        except Exception as e:

            return {
                "status": "ERROR",
                "model": "UNKNOWN",
                "output": str(e)
            }

    def build_prompt_digest(self, report):
        """
        Compact, bounded summary of the analysis for the LLM prompt.

        The full report holds every raw search result and evidence item,
        which made the prompt huge and the model slow. The model only needs
        findings, counts, top risks/conflicts and unknowns.
        """

        def clip(text, n):
            text = "" if text is None else str(text)
            return text if len(text) <= n else text[:n] + "..."

        findings = report.get("key_findings", {}) or {}
        agents = {}

        for name, data in findings.items():
            data = data or {}
            entry = {
                "status": (report.get("analysis_status") or {}).get(name),
                "sources": [
                    {"title": clip(r.get("title"), 80)}
                    for r in (data.get("research_data") or [])[:4]
                    if isinstance(r, dict)
                ],
            }
            llm = data.get("llm_analysis") or {}
            if llm.get("status") == "SUCCESS":
                entry["ai_summary"] = clip(llm.get("output"), 600)
            if name == "competitor":
                entry["category_counts"] = data.get("category_counts")
                entry["top_competitors"] = [
                    c.get("name")
                    for c in (data.get("direct_competitors") or [])[:5]
                ]
            if name == "financial":
                for k in ("budget", "monthly_operating_cost",
                          "runway_months", "budget_allocation"):
                    entry[k] = data.get(k)
            agents[name] = entry

        conflicts = (report.get("conflict_summary") or {}).get("conflicts") or []
        concerns = (report.get("skeptic_review") or {}).get("concerns") or []
        high = [c for c in concerns if c.get("severity") == "HIGH"] or concerns

        digest = {
            "agents": agents,
            "risk_summary": report.get("risk_summary"),
            "conflicts": [
                {"type": c.get("type"), "severity": c.get("severity"),
                 "description": clip(c.get("description"), 160)}
                for c in conflicts[:6]
            ],
            "top_red_team_concerns": [
                {"category": c.get("category"),
                 "challenge": clip(c.get("challenge"), 160)}
                for c in high[:6]
            ],
            "assumptions": [clip(a, 140) for a in (report.get("assumptions") or [])[:8]],
            "unknowns": [clip(u, 140) for u in (report.get("unknowns") or [])[:8]],
        }

        text = json.dumps(digest, default=str)
        return text if len(text) <= MAX_DIGEST_CHARS else text[:MAX_DIGEST_CHARS]

    def generate_with_timeout(self, llm_tool, prompt):
        """Call Gemini but never wait longer than LLM_TIMEOUT_SECONDS."""

        pool = ThreadPoolExecutor(max_workers=1)
        future = pool.submit(llm_tool.generate, prompt)

        try:
            return future.result(timeout=LLM_TIMEOUT_SECONDS)
        except FutureTimeout:
            return {
                "status": "UNAVAILABLE",
                "model": getattr(llm_tool, "model", "UNKNOWN"),
                "output": (
                    "Gemini did not respond within "
                    f"{LLM_TIMEOUT_SECONDS:g} seconds. "
                    "The rule-based advisor report is shown instead."
                )
            }
        finally:
            pool.shutdown(wait=False)

    def get_status(
        self,
        agent_result
    ):

        if not agent_result:

            return "NO_DATA"

        if (
            agent_result.get("research_data")
            or agent_result.get("competitors")
            or agent_result.get("evidence")
        ):

            return "RESEARCH_AVAILABLE"

        return "LIMITED_DATA"

    def generate_executive_summary(
        self,
        startup,
        market,
        customer,
        competitor,
        risk,
        conflicts,
        skeptic
    ):

        competitor_count = len(
            competitor.get(
                "competitors",
                []
            )
        )

        risk_count = risk.get(
            "risk_summary",
            {}
        ).get(
            "total",
            0
        )

        conflict_count = len(
            conflicts.get(
                "conflicts",
                []
            )
        )

        skeptic_count = len(
            skeptic.get(
                "concerns",
                []
            )
        )

        return (
            f"The startup idea '{startup.startup_idea}' "
            "was analyzed across market, customer, "
            "competition, location, business model, "
            "financial and risk dimensions. "
            f"The analysis contains {competitor_count} "
            "competitor-related research results, "
            f"{risk_count} structured risks, "
            f"{conflict_count} detected conflicts and "
            f"{skeptic_count} red-team concerns. "
            "The findings should be treated as decision-support "
            "rather than proof of business viability. "
            "Key assumptions should be validated with real "
            "customers and reliable market evidence before "
            "major investment or scaling decisions."
        )

    def collect_assumptions(
        self,
        analysis
    ):

        assumptions = []

        keys = [
            "market",
            "customer",
            "location",
            "business_model",
            "financial",
            "risk"
        ]

        for key in keys:

            agent_result = analysis.get(
                key,
                {}
            )

            items = agent_result.get(
                "assumptions",
                []
            )

            assumptions.extend(
                items
            )

        return self.remove_duplicates(
            assumptions
        )

    def collect_unknowns(
        self,
        analysis
    ):

        unknowns = []

        keys = [
            "market",
            "customer",
            "location",
            "business_model",
            "financial",
            "risk"
        ]

        for key in keys:

            agent_result = analysis.get(
                key,
                {}
            )

            items = agent_result.get(
                "unknowns",
                []
            )

            unknowns.extend(
                items
            )

        return self.remove_duplicates(
            unknowns
        )

    def remove_duplicates(
        self,
        items
    ):

        unique_items = []

        seen = set()

        for item in items:

            item_text = str(
                item
            )

            if item_text not in seen:

                seen.add(
                    item_text
                )

                unique_items.append(
                    item
                )

        return unique_items

    def generate_validation_experiments(
        self,
        startup,
        market,
        customer,
        competitor,
        financial,
        risk
    ):

        experiments = [

            {
                "experiment": "Customer interviews",
                "objective": (
                    "Determine whether the target customer "
                    "actually experiences the stated problem."
                ),
                "method": (
                    "Interview 15-20 target customers "
                    "using the same problem-focused questions."
                ),
                "success_signal": (
                    "A meaningful portion of interviewed "
                    "customers independently describe the problem."
                )
            },

            {
                "experiment": "Problem demand test",
                "objective": (
                    "Measure actual interest in the proposed solution."
                ),
                "method": (
                    "Create a simple landing page or prototype "
                    "and measure sign-ups or demo requests."
                ),
                "success_signal": (
                    "Target customers take a measurable action "
                    "rather than only expressing verbal interest."
                )
            },

            {
                "experiment": "Pricing test",
                "objective": (
                    "Test whether customers are willing to pay "
                    "the proposed price."
                ),
                "method": (
                    "Present different price points to target "
                    "customers and record conversion or purchase intent."
                ),
                "success_signal": (
                    "Customers accept a price that can support "
                    "the proposed business model."
                )
            },

            {
                "experiment": "Competitor comparison",
                "objective": (
                    "Understand whether the startup has a "
                    "clear differentiation."
                ),
                "method": (
                    "Compare the MVP against direct competitors "
                    "on price, features and customer experience."
                ),
                "success_signal": (
                    "Customers identify a meaningful reason "
                    "to choose the startup."
                )
            },

            {
                "experiment": "MVP pilot",
                "objective": (
                    "Test real customer behavior with a "
                    "small-scale product."
                ),
                "method": (
                    "Launch the smallest usable version "
                    "to a limited customer group."
                ),
                "success_signal": (
                    "Users actively use the product and "
                    "provide measurable feedback."
                )
            }
        ]

        return experiments

    def generate_mvp_recommendation(
        self,
        startup
    ):

        return {
            "objective": (
                "Test the core startup hypothesis "
                "with minimum resources."
            ),

            "scope": [
                "Implement only the core customer problem solution.",
                "Avoid unnecessary features during the first version.",
                "Use a small target customer group.",
                "Collect measurable usage and feedback data."
            ],

            "metrics": [
                "Number of interested users.",
                "Number of active users.",
                "Conversion rate.",
                "Customer retention.",
                "Customer willingness to pay.",
                "Customer feedback."
            ],

            "decision_rule": (
                "Use measured customer evidence to decide "
                "whether to improve, change or expand the MVP."
            )
        }

    def generate_action_plan(
        self,
        startup
    ):

        return {
            "30_days": [
                "Interview target customers.",
                "Validate the main customer problem.",
                "Research direct competitors.",
                "Define the MVP scope.",
                "Create initial pricing hypotheses."
            ],

            "60_days": [
                "Build the MVP.",
                "Launch a small pilot.",
                "Measure customer engagement.",
                "Test pricing.",
                "Collect structured feedback."
            ],

            "90_days": [
                "Analyze pilot results.",
                "Improve the MVP.",
                "Validate unit economics.",
                "Review major risks.",
                "Decide whether to expand the pilot."
            ]
        }