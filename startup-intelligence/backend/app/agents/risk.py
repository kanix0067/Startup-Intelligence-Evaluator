from app.tools.web_research import WebResearchTool
from app.tools.evidence import EvidenceTool


class RiskAgent:

    def analyze(self, startup):

        research_tool = WebResearchTool()
        evidence_tool = EvidenceTool()

        query = (
            f"{startup.industry} startup risks "
            f"{startup.location}"
        )

        research = research_tool.search(query)

        evidence = evidence_tool.create_evidence(
            research
        )

        risks = self.generate_risk_register(
            startup
        )

        risk_summary = self.generate_risk_summary(
            risks
        )

        category_summary = self.generate_category_summary(
            risks
        )

        likelihood_summary = self.generate_likelihood_summary(
            risks
        )

        assumptions = self.generate_assumptions(
            startup
        )

        unknowns = self.generate_unknowns(
            startup
        )

        risk_evidence = self.map_risk_evidence(
            risks,
            evidence
        )

        confidence_summary = self.generate_confidence_summary(
            evidence
        )

        return {
            "agent": "Risk Agent",
            "industry": startup.industry,
            "location": startup.location,

            "research_query": query,
            "research_status": research["status_code"],
            "research_source": research["source"],
            "evidence_status": research["evidence_status"],

            "research_data": research["content"],
            "evidence": evidence,

            "risk_summary": risk_summary,
            "category_summary": category_summary,
            "likelihood_summary": likelihood_summary,

            "risk_evidence": risk_evidence,

            "assumptions": assumptions,
            "unknowns": unknowns,

            "confidence_summary": confidence_summary,

            "risks": risks
        }

    def generate_risk_register(self, startup):

        risks = [

            {
                "risk": "Market demand may be lower than expected.",
                "category": "MARKET",
                "severity": "HIGH",
                "likelihood": "MEDIUM",
                "impact": "Low demand can reduce revenue and slow growth.",
                "mitigation": "Validate demand with customer interviews and a small MVP."
            },

            {
                "risk": "Customers may not be willing to pay the expected price.",
                "category": "CUSTOMER",
                "severity": "HIGH",
                "likelihood": "MEDIUM",
                "impact": "Low willingness to pay can reduce conversion and revenue.",
                "mitigation": "Test pricing with real target customers before scaling."
            },

            {
                "risk": "Existing competitors may have stronger market presence.",
                "category": "COMPETITION",
                "severity": "HIGH",
                "likelihood": "HIGH",
                "impact": "Customer acquisition may be difficult.",
                "mitigation": "Identify clear differentiation and test it with target customers."
            },

            {
                "risk": "Startup costs may be higher than estimated.",
                "category": "FINANCIAL",
                "severity": "HIGH",
                "likelihood": "MEDIUM",
                "impact": "Higher costs can reduce runway.",
                "mitigation": "Track actual operating costs and maintain an emergency reserve."
            },

            {
                "risk": "Operational problems may affect service quality.",
                "category": "OPERATIONAL",
                "severity": "MEDIUM",
                "likelihood": "MEDIUM",
                "impact": "Service problems can reduce customer satisfaction.",
                "mitigation": "Define operational processes and monitor service performance."
            },

            {
                "risk": "Regulatory requirements may affect the business.",
                "category": "REGULATORY",
                "severity": "MEDIUM",
                "likelihood": "MEDIUM",
                "impact": "Non-compliance can create additional costs or delays.",
                "mitigation": "Identify applicable regulations before launching."
            }
        ]

        return risks

    def generate_risk_summary(self, risks):

        high = 0
        medium = 0
        low = 0

        for risk in risks:

            severity = risk["severity"]

            if severity == "HIGH":
                high += 1

            elif severity == "MEDIUM":
                medium += 1

            elif severity == "LOW":
                low += 1

        return {
            "high": high,
            "medium": medium,
            "low": low,
            "total": len(risks)
        }

    def generate_category_summary(self, risks):

        categories = {}

        for risk in risks:

            category = risk.get(
                "category",
                "OTHER"
            )

            categories[category] = (
                categories.get(category, 0) + 1
            )

        return categories

    def generate_likelihood_summary(self, risks):

        likelihoods = {}

        for risk in risks:

            likelihood = risk.get(
                "likelihood",
                "UNKNOWN"
            )

            likelihoods[likelihood] = (
                likelihoods.get(likelihood, 0) + 1
            )

        return likelihoods

    def generate_assumptions(self, startup):

        assumptions = [

            "The selected risk categories are relevant to the startup.",

            "Risk severity is based on a rule-based initial assessment.",

            "Risk likelihood is an initial estimate and has not been statistically validated.",

            "Mitigation actions are general recommendations and may require startup-specific adjustment."
        ]

        if startup.budget:

            assumptions.append(
                "The provided startup budget is assumed to be available for the business."
            )

        else:

            assumptions.append(
                "Startup budget is not provided."
            )

        return assumptions

    def generate_unknowns(self, startup):

        return [

            "Actual probability of each risk occurring.",

            "Actual financial impact of each risk.",

            "Actual customer response to the product.",

            "Actual competitive pressure in the target market.",

            "Actual regulatory requirements applicable to the business.",

            "Actual operational failure rate after launch."
        ]

    def map_risk_evidence(
        self,
        risks,
        evidence
    ):

        risk_evidence = []

        for risk in risks:

            category = risk["category"]

            matching_evidence = []

            if category == "MARKET":

                keywords = [
                    "market",
                    "demand",
                    "industry"
                ]

            elif category == "CUSTOMER":

                keywords = [
                    "customer",
                    "consumer",
                    "demand"
                ]

            elif category == "COMPETITION":

                keywords = [
                    "competitor",
                    "competition",
                    "market"
                ]

            elif category == "FINANCIAL":

                keywords = [
                    "cost",
                    "revenue",
                    "financial",
                    "funding"
                ]

            elif category == "OPERATIONAL":

                keywords = [
                    "operation",
                    "service",
                    "delivery",
                    "business"
                ]

            elif category == "REGULATORY":

                keywords = [
                    "regulation",
                    "legal",
                    "law",
                    "compliance"
                ]

            else:

                keywords = []

            for item in evidence:

                claim = item.get(
                    "claim",
                    ""
                ).lower()

                for keyword in keywords:

                    if keyword in claim:

                        matching_evidence.append(
                            item
                        )

                        break

            risk_evidence.append({

                "risk": risk["risk"],

                "category": category,

                "supporting_evidence":
                    matching_evidence

            })

        return risk_evidence

    def generate_confidence_summary(
        self,
        evidence
    ):

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