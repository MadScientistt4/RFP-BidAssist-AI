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
        return json.loads(response)"""

# agents/main_agent.py

import json
from google import genai
from google.genai import types
import os
from dotenv import load_dotenv

# -------------------------------------------------
# ENV
# -------------------------------------------------
load_dotenv()
client = genai.Client()
MODEL = "gemini-2.5-flash"

def generate_technical_summary(schema: dict) -> dict:
    prompt = f"""
{open("agents/main_agent/prompts/technical_summary_prompt.txt").read()}

TECHNICAL SUMMARY SCHEMA:
{json.dumps(schema, indent=2)}

"""

    response = client.models.generate_content(
        model=MODEL,
        contents=[prompt],
        config=types.GenerateContentConfig(
            response_mime_type="application/json"
        )
    )

    return json.loads(response.text)


if __name__ == "__main__":
    with open("agents/main_agent/prompts/technical_summary_schema.json") as f:
        schema = json.load(f)

    summary = generate_technical_summary(schema)
    print(json.dumps(summary, indent=2))

