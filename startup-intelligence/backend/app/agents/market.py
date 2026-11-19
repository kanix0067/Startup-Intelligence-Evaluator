from app.tools.web_research import WebResearchTool
from app.tools.evidence import EvidenceTool
from app.tools.llm import LLMTool


class MarketResearchAgent:

    def analyze(self, startup):

        research_tool = WebResearchTool()
        evidence_tool = EvidenceTool()
        llm_tool = LLMTool()

        query = f"{startup.industry} market {startup.location}"

        research = research_tool.search(query)

        evidence = evidence_tool.create_evidence(research)

        research_text = ""

        for item in research["content"]:
            research_text += (
                f"Title: {item.get('title')}\n"
                f"URL: {item.get('url')}\n"
                f"Content: {item.get('content')}\n\n"
            )

        prompt = f"""
You are a market research analyst.

Analyze the following research for a startup.

Startup idea:
{startup.startup_idea}

Industry:
{startup.industry}

Location:
{startup.location}

Research:
{research_text}

Return exactly these sections:

MARKET_OVERVIEW:
Write a short overview.

KEY_TRENDS:
Give 3 important trends.

MARKET_OPPORTUNITIES:
Give 3 possible opportunities.

MARKET_CHALLENGES:
Give 3 possible challenges.

IMPORTANT:
Do not invent statistics.
If the research does not provide enough evidence, say UNKNOWN.
Clearly distinguish research findings from assumptions.
"""

        llm_analysis = llm_tool.generate(prompt)

        return {
            "agent": "Market Research Agent",
            "industry": startup.industry,
            "location": startup.location,
            "research_query": query,
            "research_status": research["status_code"],
            "research_source": research["source"],
            "evidence_status": research["evidence_status"],
            "research_data": research["content"],
            "evidence": evidence,
            "llm_analysis": llm_analysis
        }