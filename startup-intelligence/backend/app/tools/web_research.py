import os
from dotenv import load_dotenv
from tavily import TavilyClient

load_dotenv()


class WebResearchTool:

    def search(self, query):

        api_key = os.getenv("TAVILY_API_KEY")

        if not api_key:
            return {
                "query": query,
                "status_code": 0,
                "source": "Tavily",
                "content": [],
                "evidence_status": "UNKNOWN",
                "error": "TAVILY_API_KEY not found"
            }

        try:
            client = TavilyClient(api_key=api_key)

            response = client.search(
                query=query,
                search_depth="advanced",
                max_results=5
            )

            results = []

            for item in response.get("results", []):

                title = item.get("title")
                url = item.get("url")
                content = item.get("content")

                if title and url and content:

                    results.append({
                        "title": title,
                        "url": url,
                        "content": content
                    })

            return {
                "query": query,
                "status_code": 200,
                "source": "Tavily",
                "content": results,
                "evidence_status": "UNVERIFIED"
            }

        except Exception as e:

            return {
                "query": query,
                "status_code": 500,
                "source": "Tavily",
                "content": [],
                "evidence_status": "UNKNOWN",
                "error": str(e)
            }