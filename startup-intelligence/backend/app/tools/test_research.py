from app.tools.web_research import WebResearchTool


tool = WebResearchTool()

result = tool.search("food delivery market India")

print(result["status_code"])
print(result["source"])
print(result["evidence_status"])
print(result["content"][:1000])