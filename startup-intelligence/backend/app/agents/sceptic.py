class SkepticAgent:

    def analyze(self, startup, analysis):

        concerns = []

        market = analysis.get(
            "market",
            {}
        )

        customer = analysis.get(
            "customer",
            {}
        )

        competitor = analysis.get(
            "competitor",
            {}
        )

        location = analysis.get(
            "location",
            {}
        )

        business_model = analysis.get(
            "business_model",
            {}
        )

        financial = analysis.get(
            "financial",
            {}
        )

        risk = analysis.get(
            "risk",
            {}
        )

        conflicts = analysis.get(
            "conflicts",
            {}
        )

        self.check_input_quality(
            startup,
            concerns
        )

        self.check_market(
            market,
            concerns
        )

        self.check_customer(
            customer,
            concerns
        )

        self.check_competition(
            competitor,
            concerns
        )

        self.check_location(
            location,
            concerns
        )

        self.check_business_model(
            business_model,
            concerns
        )

        self.check_financial(
            financial,
            concerns
        )

        self.check_conflicts(
            conflicts,
            concerns
        )

        self.check_risks(
            risk,
            concerns
        )

        self.add_validation_concerns(
            concerns
        )

        for concern in concerns:

            concern["confidence"] = (
                self.calculate_confidence(
                    concern
                )
            )

        summary = self.generate_summary(
            concerns
        )

        return {
            "agent": "Skeptic / Red-Team Agent",
            "total_concerns": len(concerns),
            "summary": summary,
            "concerns": concerns,
            "analysis": (
                "The startup analysis should be challenged "
                "before major business decisions are made."
            )
        }

    def check_input_quality(
        self,
        startup,
        concerns
    ):

        if not startup.target_market:

            concerns.append({
                "category": "CUSTOMER",
                "severity": "HIGH",
                "challenge": (
                    "Target market is not clearly defined."
                )
            })

        if not startup.budget:

            concerns.append({
                "category": "FINANCIAL",
                "severity": "HIGH",
                "challenge": (
                    "Startup budget is not provided."
                )
            })

        if not startup.additional_information:

            concerns.append({
                "category": "INFORMATION",
                "severity": "MEDIUM",
                "challenge": (
                    "Additional startup information is limited."
                )
            })

    def check_market(
        self,
        market,
        concerns
    ):

        research_data = market.get(
            "research_data",
            []
        )

        if not research_data:

            concerns.append({
                "category": "MARKET",
                "severity": "HIGH",
                "challenge": (
                    "Market analysis does not contain "
                    "research data."
                )
            })

        unknowns = market.get(
            "unknowns",
            []
        )

        if unknowns:

            concerns.append({
                "category": "MARKET",
                "severity": "MEDIUM",
                "challenge": (
                    "Market analysis contains unknowns "
                    "that require further validation."
                )
            })

    def check_customer(
        self,
        customer,
        concerns
    ):

        research_data = customer.get(
            "research_data",
            []
        )

        if not research_data:

            concerns.append({
                "category": "CUSTOMER",
                "severity": "HIGH",
                "challenge": (
                    "Customer analysis does not contain "
                    "research data."
                )
            })

        unknowns = customer.get(
            "unknowns",
            []
        )

        if unknowns:

            concerns.append({
                "category": "CUSTOMER",
                "severity": "HIGH",
                "challenge": (
                    "Important customer assumptions remain "
                    "unvalidated."
                )
            })

    def check_competition(
        self,
        competitor,
        concerns
    ):

        competitors = competitor.get(
            "competitors",
            []
        )

        direct_competitors = competitor.get(
            "direct_competitors",
            []
        )

        if not competitors:

            concerns.append({
                "category": "COMPETITION",
                "severity": "HIGH",
                "challenge": (
                    "Competitor analysis did not identify "
                    "competitors."
                )
            })

        if not direct_competitors:

            concerns.append({
                "category": "COMPETITION",
                "severity": "HIGH",
                "challenge": (
                    "No direct competitors were identified. "
                    "This may indicate incomplete competitor research."
                )
            })

    def check_location(
        self,
        location,
        concerns
    ):

        research_data = location.get(
            "research_data",
            []
        )

        if not research_data:

            concerns.append({
                "category": "LOCATION",
                "severity": "MEDIUM",
                "challenge": (
                    "Location analysis does not contain "
                    "research data."
                )
            })

        unknowns = location.get(
            "unknowns",
            []
        )

        if unknowns:

            concerns.append({
                "category": "LOCATION",
                "severity": "MEDIUM",
                "challenge": (
                    "Important local market or infrastructure "
                    "information remains unknown."
                )
            })

    def check_business_model(
        self,
        business_model,
        concerns
    ):

        pricing = business_model.get(
            "pricing_evidence",
            []
        )

        revenue_models = business_model.get(
            "revenue_model_evidence",
            []
        )

        if not pricing:

            concerns.append({
                "category": "BUSINESS_MODEL",
                "severity": "HIGH",
                "challenge": (
                    "Clear pricing evidence was not found."
                )
            })

        if not revenue_models:

            concerns.append({
                "category": "BUSINESS_MODEL",
                "severity": "HIGH",
                "challenge": (
                    "Clear revenue-model evidence was not found."
                )
            })

    def check_financial(
        self,
        financial,
        concerns
    ):

        budget_status = financial.get(
            "budget_status"
        )

        if budget_status == "NOT_PROVIDED":

            concerns.append({
                "category": "FINANCIAL",
                "severity": "HIGH",
                "challenge": (
                    "Financial feasibility cannot be properly "
                    "assessed without a startup budget."
                )
            })

        unknowns = financial.get(
            "unknowns",
            []
        )

        if unknowns:

            concerns.append({
                "category": "FINANCIAL",
                "severity": "HIGH",
                "challenge": (
                    "Important financial values such as revenue, "
                    "costs or break-even remain unknown."
                )
            })

    def check_conflicts(
        self,
        conflicts,
        concerns
    ):

        conflict_list = conflicts.get(
            "conflicts",
            []
        )

        for conflict in conflict_list:

            conflict_type = conflict.get(
                "type",
                "UNKNOWN_CONFLICT"
            )

            severity = conflict.get(
                "severity",
                "UNKNOWN"
            )

            confidence = conflict.get(
                "confidence",
                0
            )

            source_agents = conflict.get(
                "source_agents",
                []
            )

            concerns.append({
                "category": "CONFLICT",
                "severity": severity,
                "challenge": (
                    f"Conflict detected: {conflict_type}. "
                    f"Confidence: {confidence}. "
                    f"Source agents: "
                    f"{', '.join(source_agents)}. "
                    "The conflicting findings should be reviewed."
                )
            })

    def check_risks(
        self,
        risk,
        concerns
    ):

        risks = risk.get(
            "risks",
            []
        )

        for risk_item in risks:

            if risk_item.get(
                "severity"
            ) == "HIGH":

                concerns.append({
                    "category": risk_item.get(
                        "category",
                        "RISK"
                    ),
                    "severity": "HIGH",
                    "challenge": (
                        f"High-severity risk identified: "
                        f"{risk_item.get('risk', 'Unknown risk')}. "
                        f"Suggested mitigation: "
                        f"{risk_item.get('mitigation', 'No mitigation provided')}"
                    )
                })

    def add_validation_concerns(
        self,
        concerns
    ):

        concerns.append({
            "category": "VALIDATION",
            "severity": "HIGH",
            "challenge": (
                "Market assumptions should be validated "
                "using reliable evidence."
            )
        })

        concerns.append({
            "category": "VALIDATION",
            "severity": "HIGH",
            "challenge": (
                "Customer demand should be tested with "
                "real target customers."
            )
        })

        concerns.append({
            "category": "VALIDATION",
            "severity": "MEDIUM",
            "challenge": (
                "Revenue and pricing assumptions should "
                "be validated with real customers."
            )
        })

    def calculate_confidence(
        self,
        concern
    ):

        severity = concern.get(
            "severity"
        )

        if severity == "HIGH":

            return 0.90

        elif severity == "MEDIUM":

            return 0.70

        return 0.50

    def generate_summary(
        self,
        concerns
    ):

        high = 0
        medium = 0
        low = 0

        categories = {}

        for concern in concerns:

            severity = concern.get(
                "severity"
            )

            category = concern.get(
                "category",
                "OTHER"
            )

            categories[category] = (
                categories.get(category, 0) + 1
            )

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
            "total": len(concerns),
            "categories": categories
        }