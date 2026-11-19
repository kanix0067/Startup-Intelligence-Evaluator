class EvidenceTool:

    def create_evidence(self, research):

        evidence = []

        for item in research.get("content", []):

            source_info = self.classify_source(
                item.get("url", "")
            )

            evidence.append({
                "claim": item.get("content"),
                "source_title": item.get("title"),
                "source_url": item.get("url"),
                "evidence_status": source_info["status"],
                "source_reliability": source_info["reliability"],
                "confidence": source_info["confidence"]
            })

        return evidence

    def classify_source(self, url):

        url = url.lower()

        trusted_domains = [
            ".gov",
            ".gov.in",
            ".edu",
            ".ac.in",
            "worldbank.org",
            "who.int",
            "oecd.org",
            "data.gov.in"
        ]

        for domain in trusted_domains:

            if domain in url:

                return {
                    "status": "VERIFIED_SOURCE",
                    "reliability": "HIGH",
                    "confidence": 0.90
                }

        return {
            "status": "UNVERIFIED_SOURCE",
            "reliability": "MEDIUM",
            "confidence": 0.50
        }