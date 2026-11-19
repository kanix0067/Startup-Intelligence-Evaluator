from app.tools.web_research import WebResearchTool
from app.tools.evidence import EvidenceTool


class BusinessModelAgent:

    def analyze(self, startup):

        research_tool = WebResearchTool()
        evidence_tool = EvidenceTool()

        queries = [
            f"{startup.startup_idea} business model",
            f"{startup.startup_idea} revenue model",
            f"{startup.startup_idea} pricing",
            f"{startup.startup_idea} monetization"
        ]

        all_research = []
        all_evidence = []

        for query in queries:

            research = research_tool.search(query)

            for item in research["content"]:

                item["research_category"] = self.get_category(query)

                all_research.append(item)

            evidence = evidence_tool.create_evidence(research)

            all_evidence.extend(evidence)

        unique_research = []
        seen_urls = set()

        for item in all_research:

            url = item.get("url", "")

            if url and url not in seen_urls:

                seen_urls.add(url)
                unique_research.append(item)

        category_counts = {}

        for item in unique_research:

            category = item["research_category"]

            category_counts[category] = (
                category_counts.get(category, 0) + 1
            )

        business_model_evidence = []
        revenue_model_evidence = []
        pricing_evidence = []
        monetization_evidence = []

        for item in unique_research:

            category = item["research_category"]

            if category == "BUSINESS_MODEL":
                business_model_evidence.append(item)

            elif category == "REVENUE_MODEL":
                revenue_model_evidence.append(item)

            elif category == "PRICING":
                pricing_evidence.append(item)

            elif category == "MONETIZATION":
                monetization_evidence.append(item)

        insights = self.generate_insights(
            startup,
            unique_research,
            category_counts
        )

        assumptions = self.generate_assumptions(startup)

        unknowns = self.generate_unknowns(startup)

        confidence_summary = self.generate_confidence_summary(
            all_evidence
        )

        return {
            "agent": "Business Model Agent",
            "startup_idea": startup.startup_idea,
            "research_queries": queries,
            "research_status": "COMPLETED",
            "research_source": "Tavily",

            "category_counts": category_counts,

            "insights": insights,

            "assumptions": assumptions,
            "unknowns": unknowns,

            "confidence_summary": confidence_summary,

            "business_model_evidence": business_model_evidence,
            "revenue_model_evidence": revenue_model_evidence,
            "pricing_evidence": pricing_evidence,
            "monetization_evidence": monetization_evidence,

            "research_data": unique_research,
            "evidence": all_evidence
        }

    def get_category(self, query):

        query = query.lower()

        if "revenue model" in query:
            return "REVENUE_MODEL"

        if "pricing" in query:
            return "PRICING"

        if "monetization" in query:
            return "MONETIZATION"

        if "business model" in query:
            return "BUSINESS_MODEL"

        return "OTHER"

    def generate_insights(
        self,
        startup,
        research_data,
        category_counts
    ):

        insights = []

        if category_counts.get("BUSINESS_MODEL", 0) > 0:

            insights.append(
                "Business model research was found for the startup idea."
            )

        if category_counts.get("REVENUE_MODEL", 0) > 0:

            insights.append(
                "Revenue model information was found and should be evaluated against the target customer."
            )

        if category_counts.get("PRICING", 0) > 0:

            insights.append(
                "Pricing information was found and should be compared with customer affordability and competitors."
            )

        if category_counts.get("MONETIZATION", 0) > 0:

            insights.append(
                "Multiple monetization-related sources were found."
            )

        if not startup.budget:

            insights.append(
                "The startup budget was not provided, so financial feasibility requires additional assumptions."
            )

        return insights

    def generate_assumptions(self, startup):

        assumptions = [
            "Online pricing information may not represent the exact local market.",
            "Competitor pricing may change over time.",
            "Reported business models may not reflect the complete internal economics of each company.",
            "Customer willingness to pay cannot be established from web research alone."
        ]

        if startup.budget:

            assumptions.append(
                "The provided startup budget is assumed to be available for the planned business."
            )

        else:

            assumptions.append(
                "Startup budget is not provided."
            )

        return assumptions

    def generate_unknowns(self, startup):

        unknowns = [
            "Actual customer willingness to pay.",
            "Actual customer conversion rate.",
            "Actual customer acquisition cost.",
            "Actual competitor pricing in the target location.",
            "Actual profit margin achievable by the startup.",
            "Actual monthly revenue during the initial launch period."
        ]

        return unknowns

    def generate_confidence_summary(self, evidence):

        high = 0
        medium = 0
        low = 0

        for item in evidence:

            confidence = item.get("confidence", 0)

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