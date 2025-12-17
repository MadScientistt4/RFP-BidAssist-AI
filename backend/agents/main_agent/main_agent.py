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
PROJECT_ROOT = BASE_DIR.parent.parent

# -------------------------------------------------
# ENV
# -------------------------------------------------
load_dotenv()

client = genai.Client()
MODEL = "gemini-2.5-flash-lite"


class MainAgent:
    def __init__(self):
        self.client = client
        self.model = MODEL

        # ---- Prompts ----
        # ---- Prompts ----
    with open(PROJECT_ROOT / "prompts" / "technical_summary_prompt.txt", encoding="utf-8") as f:
        self.technical_prompt = f.read()

    with open(PROJECT_ROOT / "prompts" / "pricing_summary_prompt.txt", encoding="utf-8") as f:
        self.pricing_prompt = f.read()

# ---- Schemas ----
    with open(PROJECT_ROOT / "schemas" / "technical_summary_schema.json", encoding="utf-8") as f:
        self.technical_schema = json.load(f)

    with open(PROJECT_ROOT / "schemas" / "pricing_summary_schema.json", encoding="utf-8") as f:
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

    OUTPUT_DIR = PROJECT_ROOT / "outputs"
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    extracted_rfp_path = OUTPUT_DIR / "extracted_rfp.json"
    technical_input_path = OUTPUT_DIR / "technical_agent_output.json"

    with open(extracted_rfp_path, "r", encoding="utf-8") as f:
        extracted_rfp = json.load(f)

    with open(technical_input_path, "r", encoding="utf-8") as f:
        technical_output = json.load(f)

    agent = MainAgent()

    # ---- Generate outputs ----
    technical_summary = agent.generate_technical_summary(extracted_rfp)
    pricing_summary = agent.generate_pricing_summary(
        extracted_rfp,
        technical_output
    )

    # ---- Write outputs ----
    technical_out_path = OUTPUT_DIR / "technical_summary.json"
    pricing_out_path = OUTPUT_DIR / "pricing_summary.json"

    with open(technical_out_path, "w", encoding="utf-8") as f:
        json.dump(technical_summary, f, indent=2)

    with open(pricing_out_path, "w", encoding="utf-8") as f:
        json.dump(pricing_summary, f, indent=2)

    print("✅ Outputs generated:")
    print(f" - {technical_out_path}")
    print(f" - {pricing_out_path}")
