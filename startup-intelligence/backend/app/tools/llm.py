import os

from dotenv import load_dotenv
from google import genai

load_dotenv()


class LLMTool:

    def __init__(self):

        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY not found"
            )

        self.client = genai.Client(
            api_key=api_key
        )

        self.model = os.getenv(
            "GEMINI_MODEL",
            "gemini-3.6-flash"
        )

    def generate(self, prompt):

        try:

            interaction = self.client.interactions.create(
                model=self.model,
                input=prompt
            )

            return {
                "status": "SUCCESS",
                "model": self.model,
                "output": interaction.output_text
            }

        except Exception as e:

            error_text = str(e)

            if "429" in error_text or "Rate limit" in error_text:

                return {
                    "status": "RATE_LIMITED",
                    "model": self.model,
                    "output": (
                        "Gemini free-tier request limit reached."
                    )
                }

            if "503" in error_text or "UNAVAILABLE" in error_text:

                return {
                    "status": "UNAVAILABLE",
                    "model": self.model,
                    "output": (
                        "Gemini is temporarily unavailable."
                    )
                }

            return {
                "status": "ERROR",
                "model": self.model,
                "output": error_text
            }