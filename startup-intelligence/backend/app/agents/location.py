from app.tools.web_research import WebResearchTool
from app.tools.evidence import EvidenceTool


class LocationRiskAgent:

    def analyze(self, startup):

        research_tool = WebResearchTool()
        evidence_tool = EvidenceTool()

        queries = [
            f"{startup.location} business environment",
            f"{startup.location} infrastructure",
            f"{startup.location} {startup.industry} market",
            f"{startup.location} startup risks",
            f"{startup.location} regulations business",
            f"{startup.location} {startup.target_customer}"
        ]

        all_research = []
        all_evidence = []

        for query in queries:

            research = research_tool.search(query)

            for item in research.get("content", []):

                item["research_category"] = self.get_category(
                    query,
                    startup.target_customer
                )

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

            category = item.get(
                "research_category",
                "OTHER"
            )

            category_counts[category] = (
                category_counts.get(category, 0) + 1
            )

        opportunities = self.generate_opportunities(
            unique_research
        )

        risks = self.generate_risks(
            unique_research
        )

        assumptions = [
            "Location assessment is based on available web research.",
            "Search results may not represent all local conditions.",
            "Infrastructure conditions may vary by neighborhood.",
            "Business regulations may depend on the specific business model.",
            "Local market conditions can change over time."
        ]

        unknowns = [
            "Exact operating cost at the chosen location.",
            "Exact customer density.",
            "Exact competitor density.",
            "Actual local customer demand.",
            "Exact regulatory requirements.",
            "Exact infrastructure quality at the final operating location."
        ]

        return {
            "agent": "Location Risk Agent",
            "location": startup.location,
            "research_queries": queries,
            "research_status": "COMPLETED",
            "research_source": "Tavily",
            "category_counts": category_counts,
            "total_results": len(unique_research),
            "research_data": unique_research,
            "evidence": all_evidence,
            "opportunities": opportunities,
            "risks": risks,
            "assumptions": assumptions,
            "unknowns": unknowns
        }

    def get_category(self, query, target_customer):

        query = query.lower()
        target_customer = target_customer.lower()

        if "business environment" in query:
            return "BUSINESS_ENVIRONMENT"

        if "infrastructure" in query:
            return "INFRASTRUCTURE"

        if "market" in query:
            return "MARKET"

        if "startup risks" in query:
            return "STARTUP_RISK"

        if "regulations" in query:
            return "REGULATION"

        if target_customer in query:
            return "CUSTOMER"

        return "OTHER"

    def generate_opportunities(self, research):

        opportunities = []

        categories = set(
            item.get("research_category")
            for item in research
        )

        if "BUSINESS_ENVIRONMENT" in categories:
            opportunities.append(
                "The location may provide a relevant business environment for the startup."
            )

        if "INFRASTRUCTURE" in categories:
            opportunities.append(
                "Available infrastructure may support business operations."
            )

        if "MARKET" in categories:
            opportunities.append(
                "Local market conditions may provide opportunities for customer acquisition."
            )

        if "CUSTOMER" in categories:
            opportunities.append(
                "The target customer group may have a presence in the selected location."
            )

        return opportunities

    def generate_risks(self, research):

        risks = []

        categories = set(
            item.get("research_category")
            for item in research
        )

        if "STARTUP_RISK" in categories:
            risks.append(
                "Local startup and business conditions may create operational risks."
            )

        if "REGULATION" in categories:
            risks.append(
                "Regulatory requirements may affect the startup's launch or operations."
            )

        if "INFRASTRUCTURE" not in categories:
            risks.append(
                "Insufficient infrastructure information may create planning uncertainty."
            )

        if "CUSTOMER" not in categories:
            risks.append(
                "Insufficient local customer information may make demand estimation difficult."
            )

        return risks