# backend/agents/technical_agent/technical_agent.py

import json
from typing import Dict, Any
from anyio import Path
from google import genai
from google.genai import types
import os
from dotenv import load_dotenv
load_dotenv()
MODEL_NAME = "gemini-2.5-flash-lite"

class TechnicalAgent:
    def __init__(self):
        self.client = genai.Client()

    def generate_scope_of_supply(
        self,
        extracted_rfp: Dict[str, Any],
        technical_summary: Dict[str, Any],
        scope_schema: Dict[str, Any]
    ) -> Dict[str, Any]:

        prompt = f"""
            You are a TECHNICAL EVALUATION AGENT.

            Your task is to generate a STRUCTURED SCOPE OF SUPPLY SUMMARY.

            RULES:
            - Follow the schema strictly
            - No hallucinations
            - No summarization beyond structure
            - Exact specs only

            SCHEMA:
            {json.dumps(scope_schema, indent=2)}

            EXTRACTED RFP:
            {json.dumps(extracted_rfp, indent=2)}

            TECHNICAL SUMMARY:
            {json.dumps(technical_summary, indent=2)}
            """

        response = self.client.models.generate_content(
            model=MODEL_NAME,
            contents=[prompt],
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            )
        )

        try:
            return json.loads(response.text)
        except json.JSONDecodeError:
            raise ValueError("Failed to parse Scope of Supply JSON")

if __name__ == "__main__":

    agent = TechnicalAgent()

    result = agent.generate_scope_of_supply(
        extracted_rfp="outputs/extracted_rfp.json",
        technical_summary="outputs/technical_summary_by_main_agent.json",
        scope_schema="schemas/scope_of_supply_schema.json"
    )

    output_path = Path("outputs/scope_of_supply_summary.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    print("✅ Scope of Supply Summary generated successfully")

