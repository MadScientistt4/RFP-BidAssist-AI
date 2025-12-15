"""class MainAgent:
    def __init__(self, llm_client, technical_prompt, pricing_prompt):
        self.llm = llm_client
        self.technical_prompt = technical_prompt
        self.pricing_prompt = pricing_prompt

    def generate_technical_summary(self, extracted_rfp_json: dict) -> dict:
        prompt = self.technical_prompt.replace(
            "{{EXTRACTED_RFP_JSON}}",
            json.dumps(extracted_rfp_json, indent=2)
        )

        response = self.llm.generate(prompt)
        return json.loads(response)

    def generate_pricing_summary(self, extracted_rfp_json: dict) -> dict:
        prompt = self.pricing_prompt.replace(
            "{{EXTRACTED_RFP_JSON}}",
            json.dumps(extracted_rfp_json, indent=2)
        )

        response = self.llm.generate(prompt)
        return json.loads(response)
"""

# agents/main_agent.py

import json
import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

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

        with open("prompts/technical_summary_prompt.txt") as f:
            self.technical_prompt = f.read()

        with open("prompts/pricing_summary_prompt.txt") as f:
            self.pricing_prompt = f.read()

        with open("prompts/technical_summary_schema.json") as f:
            self.technical_schema = json.load(f)

        with open("prompts/pricing_summary_schema.json") as f:
            self.pricing_schema = json.load(f)

    # -------------------------------------------------
    # TECHNICAL SUMMARY (for Technical Agent)
    # -------------------------------------------------
    def generate_technical_summary(self, extracted_rfp_json: dict) -> dict:
        prompt = self.technical_prompt \
            .replace("{{TECHNICAL_SUMMARY_SCHEMA}}", json.dumps(self.technical_schema, indent=2)) \
            .replace("{{EXTRACTED_RFP_JSON}}", json.dumps(extracted_rfp_json, indent=2))

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

        prompt = self.pricing_prompt \
            .replace("{{PRICING_SUMMARY_SCHEMA}}", json.dumps(self.pricing_schema, indent=2)) \
            .replace("{{EXTRACTED_RFP_JSON}}", json.dumps(extracted_rfp_json, indent=2)) \
            .replace("{{TECHNICAL_AGENT_OUTPUT_JSON}}", json.dumps(technical_agent_output_json, indent=2))

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

    with open("../outputs/extracted_rfp.json") as f:
        extracted_rfp = json.load(f)

    with open("../outputs/technical_agent_output.json") as f:
        technical_output = json.load(f)

    agent = MainAgent()

    print("\n=== TECHNICAL SUMMARY ===")
    technical_summary = agent.generate_technical_summary(extracted_rfp)
    print(json.dumps(technical_summary, indent=2))

    print("\n=== PRICING SUMMARY ===")
    pricing_summary = agent.generate_pricing_summary(
        extracted_rfp,
        technical_output
    )
    print(json.dumps(pricing_summary, indent=2))
