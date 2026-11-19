class ConflictDetectionAgent:

    def analyze(self, analysis):

        conflicts = []

        market = analysis.get("market", {})
        customer = analysis.get("customer", {})
        competitor = analysis.get("competitor", {})
        financial = analysis.get("financial", {})
        business_model = analysis.get("business_model", {})
        risk = analysis.get("risk", {})

        self.check_market_conflict(
            market,
            risk,
            conflicts
        )

        self.check_customer_conflict(
            customer,
            risk,
            conflicts
        )

        self.check_competition_conflict(
            competitor,
            risk,
            conflicts
        )

        self.check_financial_conflict(
            financial,
            risk,
            conflicts
        )

        self.check_business_model_conflict(
            business_model,
            financial,
            risk,
            conflicts
        )

        self.check_data_gaps(
            market,
            customer,
            competitor,
            financial,
            conflicts
        )

        for conflict in conflicts:

            conflict["confidence"] = (
                self.calculate_conflict_confidence(
                    conflict
                )
            )

        return {
            "agent": "Conflict Detection Agent",
            "total_conflicts": len(conflicts),
            "conflicts": conflicts
        }

    def check_market_conflict(
        self,
        market,
        risk,
        conflicts
    ):

        risks = risk.get(
            "risks",
            []
        )

        market_insights = market.get(
            "insights",
            []
        )

        market_text = " ".join(
            str(item)
            for item in market_insights
        ).lower()

        for risk_item in risks:

            if risk_item.get("category") != "MARKET":
                continue

            if any(
                word in market_text
                for word in [
                    "strong",
                    "growth",
                    "opportunity",
                    "positive"
                ]
            ):

                conflicts.append({
                    "type": "MARKET_CONFLICT",
                    "severity": "HIGH",
                    "description": (
                        "Market research contains positive market "
                        "signals while the Risk Agent identifies "
                        "potential market demand risk."
                    ),
                    "source_agents": [
                        "Market Research Agent",
                        "Risk Agent"
                    ]
                })

    def check_customer_conflict(
        self,
        customer,
        risk,
        conflicts
    ):

        risks = risk.get(
            "risks",
            []
        )

        customer_insights = customer.get(
            "insights",
            []
        )

        customer_text = " ".join(
            str(item)
            for item in customer_insights
        ).lower()

        for risk_item in risks:

            if risk_item.get("category") != "CUSTOMER":
                continue

            if any(
                word in customer_text
                for word in [
                    "strong",
                    "high demand",
                    "positive",
                    "willing"
                ]
            ):

                conflicts.append({
                    "type": "CUSTOMER_CONFLICT",
                    "severity": "HIGH",
                    "description": (
                        "Customer research contains positive demand "
                        "signals while the Risk Agent identifies "
                        "customer willingness-to-pay risk."
                    ),
                    "source_agents": [
                        "Customer Agent",
                        "Risk Agent"
                    ]
                })

    def check_competition_conflict(
        self,
        competitor,
        risk,
        conflicts
    ):

        risks = risk.get(
            "risks",
            []
        )

        competitors = competitor.get(
            "competitors",
            []
        )

        direct_competitors = competitor.get(
            "direct_competitors",
            []
        )

        for risk_item in risks:

            if risk_item.get("category") != "COMPETITION":
                continue

            if len(competitors) == 0:

                conflicts.append({
                    "type": "COMPETITION_DATA_GAP",
                    "severity": "MEDIUM",
                    "description": (
                        "The Risk Agent identifies competition risk, "
                        "but competitor research returned no results."
                    ),
                    "source_agents": [
                        "Competitor Agent",
                        "Risk Agent"
                    ]
                })

            elif len(direct_competitors) == 0:

                conflicts.append({
                    "type": "DIRECT_COMPETITOR_GAP",
                    "severity": "MEDIUM",
                    "description": (
                        "Competitor research returned results, "
                        "but no direct competitor was identified."
                    ),
                    "source_agents": [
                        "Competitor Agent",
                        "Risk Agent"
                    ]
                })

    def check_financial_conflict(
        self,
        financial,
        risk,
        conflicts
    ):

        risks = risk.get(
            "risks",
            []
        )

        budget_status = financial.get(
            "budget_status"
        )

        for risk_item in risks:

            if risk_item.get("category") != "FINANCIAL":
                continue

            if budget_status == "NOT_PROVIDED":

                conflicts.append({
                    "type": "FINANCIAL_DATA_GAP",
                    "severity": "MEDIUM",
                    "description": (
                        "The Risk Agent identifies financial risk, "
                        "but no startup budget was provided."
                    ),
                    "source_agents": [
                        "Financial Agent",
                        "Risk Agent"
                    ]
                })

    def check_business_model_conflict(
        self,
        business_model,
        financial,
        risk,
        conflicts
    ):

        pricing = business_model.get(
            "pricing_evidence",
            []
        )

        revenue_models = business_model.get(
            "revenue_model_evidence",
            []
        )

        financial_unknowns = financial.get(
            "unknowns",
            []
        )

        if (
            len(pricing) == 0
            and len(revenue_models) == 0
            and len(financial_unknowns) > 0
        ):

            conflicts.append({
                "type": "BUSINESS_MODEL_FINANCIAL_GAP",
                "severity": "MEDIUM",
                "description": (
                    "Business model research does not contain "
                    "clear pricing or revenue-model evidence while "
                    "financial analysis contains important unknowns."
                ),
                "source_agents": [
                    "Business Model Agent",
                    "Financial Agent"
                ]
            })

    def check_data_gaps(
        self,
        market,
        customer,
        competitor,
        financial,
        conflicts
    ):

        if not market.get("research_data"):

            conflicts.append({
                "type": "MARKET_DATA_GAP",
                "severity": "HIGH",
                "description": (
                    "Market Agent returned no research data."
                ),
                "source_agents": [
                    "Market Research Agent"
                ]
            })

        if not customer.get("research_data"):

            conflicts.append({
                "type": "CUSTOMER_DATA_GAP",
                "severity": "HIGH",
                "description": (
                    "Customer Agent returned no research data."
                ),
                "source_agents": [
                    "Customer Agent"
                ]
            })

        # Competitor Agent stores results under "competitors"/"evidence",
        # not "research_data", so check all of them to avoid a false gap.
        if not (
            competitor.get("research_data")
            or competitor.get("competitors")
            or competitor.get("evidence")
        ):

            conflicts.append({
                "type": "COMPETITOR_DATA_GAP",
                "severity": "HIGH",
                "description": (
                    "Competitor Agent returned no research data."
                ),
                "source_agents": [
                    "Competitor Agent"
                ]
            })

        if not financial.get("research_data"):

            conflicts.append({
                "type": "FINANCIAL_DATA_GAP",
                "severity": "HIGH",
                "description": (
                    "Financial Agent returned no research data."
                ),
                "source_agents": [
                    "Financial Agent"
                ]
            })

    def calculate_conflict_confidence(
        self,
        conflict
    ):

        severity = conflict.get(
            "severity"
        )

        if severity == "HIGH":

            return 0.90

        elif severity == "MEDIUM":

            return 0.70

        return 0.50