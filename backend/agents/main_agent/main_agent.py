# agents/main_agent.py

import json
from pathlib import Path
from dotenv import load_dotenv
from google import genai
from google.genai import types

# -------------------------------------------------
# PATH SETUP (CRITICAL FIX)
# -------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent

# -------------------------------------------------
# ENV
# -------------------------------------------------
load_dotenv()

client = genai.Client()
MODEL = "gemini-2.5-flash"


class MainAgent:
    def __init__(self):
        self.client = client
        self.model = MODEL

        # ---- Prompts ----
        with open(BASE_DIR / "prompts" / "technical_summary_prompt.txt", encoding="utf-8") as f:
            self.technical_prompt = f.read()

        with open(BASE_DIR / "prompts" / "pricing_summary_prompt.txt", encoding="utf-8") as f:
            self.pricing_prompt = f.read()

        # ---- Schemas ----
        with open(BASE_DIR / "prompts" / "technical_summary_schema.json", encoding="utf-8") as f:
            self.technical_schema = json.load(f)

        with open(BASE_DIR / "prompts" / "pricing_summary_schema.json", encoding="utf-8") as f:
            self.pricing_schema = json.load(f)

    # -------------------------------------------------
    # TECHNICAL SUMMARY (for Technical Agent)
    # -------------------------------------------------
    def generate_technical_summary(self, extracted_rfp_json: dict) -> dict:
        prompt = (
            self.technical_prompt
            .replace("{{TECHNICAL_SUMMARY_SCHEMA}}", json.dumps(self.technical_schema, indent=2))
            .replace("{{EXTRACTED_RFP_JSON}}", json.dumps(extracted_rfp_json, indent=2))
        )

        response = self.client.models.generate_content(
            model=self.model,
            contents=[prompt],
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            )
        )

        return json.loads(response.text)

    # -------------------------------------------------
    # PRICING SUMMARY (for Pricing Agent)
    # -------------------------------------------------
    def generate_pricing_summary(
        self,
        extracted_rfp_json: dict,
        technical_agent_output_json: dict
    ) -> dict:

        prompt = (
            self.pricing_prompt
            .replace("{{PRICING_SUMMARY_SCHEMA}}", json.dumps(self.pricing_schema, indent=2))
            .replace("{{EXTRACTED_RFP_JSON}}", json.dumps(extracted_rfp_json, indent=2))
            .replace("{{TECHNICAL_AGENT_OUTPUT_JSON}}", json.dumps(technical_agent_output_json, indent=2))
        )

        response = self.client.models.generate_content(
            model=self.model,
            contents=[prompt],
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            )
        )

        return json.loads(response.text)


# -------------------------------------------------
# LOCAL TEST
# -------------------------------------------------
if __name__ == "__main__":

   if __name__ == "__main__":
    BASE_DIR = Path(__file__).resolve().parent
    OUTPUT_DIR = BASE_DIR.parent.parent / "outputs"
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    extracted_rfp_path = OUTPUT_DIR / "extracted_rfp.json"
    technical_output_path = OUTPUT_DIR / "technical_agent_output.json"

    with open(extracted_rfp_path, "r", encoding="utf-8") as f:
        extracted_rfp = json.load(f)

    with open(technical_output_path, "r", encoding="utf-8") as f:
        technical_output = json.load(f)

    agent = MainAgent()

    technical_summary = agent.generate_technical_summary(extracted_rfp)
    pricing_summary = agent.generate_pricing_summary(
        extracted_rfp,
        technical_output
    )

    # ---- WRITE OUTPUTS TWO LEVELS UP ----
    with open(OUTPUT_DIR / "technical_summary.json", "w", encoding="utf-8") as f:
        json.dump(technical_summary, f, indent=2)

    with open(OUTPUT_DIR / "pricing_summary.json", "w", encoding="utf-8") as f:
        json.dump(pricing_summary, f, indent=2)

    print(f"Outputs written to: {OUTPUT_DIR}")
