# backend/agents/technical_agent/technical_agent.py

import json
from typing import Dict, Any, List
from pathlib import Path
from google import genai
from google.genai import types
import os
from dotenv import load_dotenv

load_dotenv()

MODEL_NAME = "gemini-2.5-flash-lite"


class TechnicalAgent:
    def __init__(self):
        self.client = genai.Client()

    # -------------------------------------------------
    # LLM STEP: Scope of Supply generation
    # -------------------------------------------------
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

        return json.loads(response.text)

    # -------------------------------------------------
    # SPEC MATCH ENGINE (NO LLM)
    # -------------------------------------------------
"""
    def compare_specs(self, rfp_specs: Dict[str, Any], oem_specs: Dict[str, Any]) -> Dict[str, Any]:
        matched = 0
        total = len(rfp_specs)
        mismatches = []

        for key, rfp_value in rfp_specs.items():
            oem_value = oem_specs.get(key)

            if oem_value is None:
                mismatches.append(key)
                continue

            # String match
            if isinstance(rfp_value, str):
                if rfp_value.lower() in str(oem_value).lower():
                    matched += 1
                else:
                    mismatches.append(key)

            # Numeric match
            elif isinstance(rfp_value, (int, float)):
                try:
                    if float(oem_value) >= float(rfp_value):
                        matched += 1
                    else:
                        mismatches.append(key)
                except:
                    mismatches.append(key)

            # List match
            elif isinstance(rfp_value, list):
                if all(item in oem_value for item in rfp_value):
                    matched += 1
                else:
                    mismatches.append(key)

            else:
                mismatches.append(key)

        score = round((matched / total) * 100, 2) if total else 0

        return {
            "score_percent": score,
            "matched_specs": matched,
            "total_specs": total,
            "mismatched_specs": mismatches
        }

    # -------------------------------------------------
    # OEM RECOMMENDATION ENGINE
    # -------------------------------------------------
    def recommend_oems(
        self,
        scope_product: Dict[str, Any],
        oem_catalog: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:

        rfp_specs = scope_product["core_specifications"]

        results = []

        for oem in oem_catalog:
            match_result = self.compare_specs(rfp_specs, oem["technical_specifications"])

            results.append({
                "oem_name": oem["oem_name"],
                "product_name": oem["product_name"],
                "sku": oem["sku"],
                "spec_match": match_result
            })

        # Sort by best match
        results.sort(key=lambda x: x["spec_match"]["score_percent"], reverse=True)

        return results[:3]


# -------------------------------------------------
# MAIN (Local test runner)
# -------------------------------------------------
if __name__ == "__main__":
    base = Path("outputs")

    agent = TechnicalAgent()

    # Load inputs
    with open("outputs/scope_of_supply_summary.json") as f:
        scope_data = json.load(f)

    with open("oem_datasheets/oem_products.json") as f:
        oem_catalog = json.load(f)

    final_recommendations = []

    for product_line in scope_data["product_lines"]:
        line_name = product_line["product_line_name"]

        for product in product_line["products"]:
            product_name = product["product_name"]
            rfp_specs = product["technical_specifications"]

            # This is where spec match logic will go

            top_oems = agent.recommend_oems(product, oem_catalog)

            final_recommendations.append({
                "product_id": product["product_id"],
                "product_name": product["product_name"],
                "recommended_oems": top_oems
            })

    with open(base / "oem_datasheets/oem_recommendations.json", "w") as f:
        json.dump(final_recommendations, f, indent=2)

    print("✅ OEM recommendations generated successfully")
"""


