from app.tools.web_research import WebResearchTool
from app.tools.evidence import EvidenceTool


class CompetitorAgent:

    def analyze(self, startup):

        research_tool = WebResearchTool()
        evidence_tool = EvidenceTool()

        queries = [
            f"{startup.industry} competitors {startup.location}",
            f"{startup.industry} companies {startup.location}",
            f"{startup.industry} pricing {startup.location}",
            f"{startup.industry} startups {startup.location}"
        ]

        all_research = []
        all_evidence = []

        for query in queries:

            research = research_tool.search(query)

            all_research.extend(
                research.get("content", [])
            )

            evidence = evidence_tool.create_evidence(
                research
            )

            all_evidence.extend(evidence)

        unique_research = []
        seen_urls = set()

        for item in all_research:

            url = item.get("url", "")

            if url and url not in seen_urls:

                seen_urls.add(url)
                unique_research.append(item)

        competitors = []

        for item in unique_research:

            title = item.get("title", "")
            url = item.get("url", "")
            content = item.get("content", "")

            category = self.classify_result(
                title,
                url,
                content
            )

            competitors.append({
                "name": title,
                "url": url,
                "category": category,
                "description": content
            })

        category_counts = {}

        for competitor in competitors:

            category = competitor["category"]

            category_counts[category] = (
                category_counts.get(category, 0) + 1
            )

        direct_competitors = [
            item for item in competitors
            if item["category"] == "DIRECT_COMPETITOR"
        ]

        potential_competitors = [
            item for item in competitors
            if item["category"] == "POTENTIAL_COMPETITOR"
        ]

        market_reports = [
            item for item in competitors
            if item["category"] == "MARKET_REPORT"
        ]

        assumptions = [
            "Search results may contain duplicate or incomplete competitor information.",
            "Potential competitors are not confirmed competitors.",
            "Competitor classification is rule-based.",
            "Online pricing may differ from actual local pricing.",
            "Search results do not establish competitor market share."
        ]

        unknowns = [
            "Actual competitor market share.",
            "Actual competitor revenue.",
            "Actual customer acquisition cost.",
            "Actual competitor profitability.",
            "Actual customer loyalty.",
            "Complete list of competitors."
        ]

        return {
            "agent": "Competitor Agent",
            "industry": startup.industry,
            "location": startup.location,
            "research_queries": queries,
            "research_status": "COMPLETED",
            "research_source": "Tavily",
            "category_counts": category_counts,
            "total_results": len(competitors),
            "direct_competitors": direct_competitors,
            "potential_competitors": potential_competitors,
            "market_reports": market_reports,
            "competitors": competitors,
            "evidence": all_evidence,
            "assumptions": assumptions,
            "unknowns": unknowns
        }

    def classify_result(self, title, url, content):

        text = (
            title + " " +
            url + " " +
            content
        ).lower()

        url = url.lower()

        if "justdial.com" in url or "sulekha.com" in url:
            return "DIRECTORY"

        if "tracxn.com" in url:
            return "MARKET_REPORT"

        if "quora.com" in url or "reddit.com" in url:
            return "DISCUSSION"

        direct_competitor_domains = [
            "swiggy.com",
            "zomato.com"
        ]

        for domain in direct_competitor_domains:

            if domain in url:
                return "DIRECT_COMPETITOR"

        business_keywords = [
            "order food",
            "food delivery service",
            "meal delivery",
            "food ordering",
            "cloud kitchen",
            "home-cooked food"
        ]

        for keyword in business_keywords:

            if keyword in text:
                return "POTENTIAL_COMPETITOR"

        return "OTHER"