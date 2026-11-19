from app.tools.web_research import WebResearchTool
from app.tools.evidence import EvidenceTool


class FinancialAgent:

    def analyze(self, startup):

        research_tool = WebResearchTool()
        evidence_tool = EvidenceTool()

        query = (
            f"{startup.industry} startup costs "
            f"operating costs revenue {startup.location}"
        )

        research = research_tool.search(query)

        evidence = evidence_tool.create_evidence(research)

        budget = startup.budget

        if budget:

            annual_budget = budget
            monthly_budget = round(budget / 12, 2)
            budget_status = "PROVIDED"

            budget_allocation = {
                "operations": round(budget * 0.40, 2),
                "technology": round(budget * 0.25, 2),
                "marketing": round(budget * 0.20, 2),
                "emergency_reserve": round(budget * 0.15, 2)
            }

            monthly_operating_cost = round(
                budget_allocation["operations"] / 12,
                2
            )

            runway_months = round(
                budget / monthly_operating_cost,
                2
            )

        else:

            annual_budget = 0
            monthly_budget = 0
            budget_status = "NOT_PROVIDED"

            budget_allocation = {
                "operations": 0,
                "technology": 0,
                "marketing": 0,
                "emergency_reserve": 0
            }

            monthly_operating_cost = 0
            runway_months = 0

        revenue_assumptions = [
            "Revenue cannot be reliably estimated without customer demand data.",
            "Customer acquisition volume is currently unknown.",
            "Customer willingness to pay requires validation.",
            "Actual revenue will depend on pricing, demand, retention and operating capacity."
        ]

        financial_risks = [
            {
                "risk": "Actual operating costs may exceed the planning estimate.",
                "severity": "HIGH"
            },
            {
                "risk": "Customer revenue may be lower than expected during the initial launch.",
                "severity": "HIGH"
            },
            {
                "risk": "Marketing costs may increase customer acquisition expenses.",
                "severity": "MEDIUM"
            },
            {
                "risk": "Unexpected expenses may reduce available runway.",
                "severity": "MEDIUM"
            }
        ]

        assumptions = [
            "Budget allocation percentages are planning assumptions.",
            "Operations allocation is assumed to be 40% of the total budget.",
            "Technology allocation is assumed to be 25% of the total budget.",
            "Marketing allocation is assumed to be 20% of the total budget.",
            "Emergency reserve is assumed to be 15% of the total budget.",
            "Runway is an estimate based on the assumed operating allocation."
        ]

        unknowns = [
            "Actual monthly operating cost.",
            "Actual customer acquisition cost.",
            "Actual monthly revenue.",
            "Actual gross margin.",
            "Actual break-even point.",
            "Actual customer retention rate."
        ]

        confidence_summary = self.generate_confidence_summary(
            evidence
        )

        return {
            "agent": "Financial Agent",

            "budget": budget,
            "annual_budget": annual_budget,
            "monthly_budget": monthly_budget,
            "budget_status": budget_status,

            "budget_allocation": budget_allocation,

            "monthly_operating_cost": monthly_operating_cost,
            "runway_months": runway_months,

            "revenue_assumptions": revenue_assumptions,
            "financial_risks": financial_risks,

            "assumptions": assumptions,
            "unknowns": unknowns,

            "confidence_summary": confidence_summary,

            "research_query": query,
            "research_status": research["status_code"],
            "research_source": research["source"],
            "evidence_status": research["evidence_status"],
            "research_data": research["content"],
            "evidence": evidence
        }

    def generate_confidence_summary(self, evidence):

        high = 0
        medium = 0
        low = 0

        for item in evidence:

            confidence = item.get(
                "confidence",
                0
            )

            if confidence >= 0.80:
                high += 1

            elif confidence >= 0.50:
                medium += 1

            else:
                low += 1

        return {
            "high": high,
            "medium": medium,
            "low": low,
            "total": len(evidence)
        }