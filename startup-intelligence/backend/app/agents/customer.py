from app.tools.web_research import WebResearchTool
from app.tools.evidence import EvidenceTool
from app.tools.llm import LLMTool


class CustomerAgent:

    def analyze(self, startup):

        research_tool = WebResearchTool()
        evidence_tool = EvidenceTool()
        llm_tool = LLMTool()

        query = (
            f"{startup.target_customer} "
            f"{startup.industry} "
            f"{startup.location} customer market"
        )

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
You are a customer research analyst.

Analyze the following research for a startup.

Startup idea:
{startup.startup_idea}

Problem:
{startup.problem}

Target customer:
{startup.target_customer}

Target market:
{startup.target_market}

Industry:
{startup.industry}

Location:
{startup.location}

Research:
{research_text}

Return exactly these sections:

CUSTOMER_OVERVIEW:
Describe the target customer and relevant market characteristics.

CUSTOMER_SEGMENTS:
Identify 3 relevant customer segments.

CUSTOMER_NEEDS:
Identify 3 important customer needs or pain points.

BUYING_BEHAVIOR:
Describe likely buying or usage behavior based only on the research.

CUSTOMER_OPPORTUNITIES:
Give 3 possible opportunities.

CUSTOMER_CHALLENGES:
Give 3 possible challenges.

IMPORTANT:
Do not invent statistics.
If the research does not provide enough evidence, say UNKNOWN.
Clearly distinguish research findings from assumptions.
"""

        llm_analysis = llm_tool.generate(prompt)

        return {
            "agent": "Customer Agent",
            "target_customer": startup.target_customer,
            "target_market": startup.target_market,
            "research_query": query,
            "research_status": research["status_code"],
            "research_source": research["source"],
            "evidence_status": research["evidence_status"],
            "research_data": research["content"],
            "evidence": evidence,
            "llm_analysis": llm_analysis
        }