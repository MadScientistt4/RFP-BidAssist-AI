# backend/agents/technical_agent/technical_agent.py

import json
from typing import Dict, Any, List
from pathlib import Path

# ---- INTERNAL MODULES ----
from normalize_scope_of_summary import normalize_scope
from normalize_rfp_specs import normalize_rfp_specs
from enforce_normalize_specs import enforce_all
from spec_scorer import (
    rank_oem_skus,
    build_final_recommendation_table,
)

# ---- LLM ----
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()
MODEL_NAME = "gemini-2.5-flash"


class TechnicalAgent:
    """
    End-to-end technical evaluation pipeline.
    """

    def __init__(self):
        self.client = genai.Client()

    # =================================================
    # STEP 1️⃣ SCOPE OF SUPPLY (LLM)
    # =================================================
    def generate_scope_of_supply(
        self,
        extracted_rfp: Dict[str, Any],
        technical_summary: Dict[str, Any],
        scope_schema: Dict[str, Any],
    ) -> Dict[str, Any]:

        prompt = f"""
You are a TECHNICAL EVALUATION AGENT.

Your task is to generate a STRUCTURED SCOPE OF SUPPLY SUMMARY.

RULES:
- Follow the schema strictly
- No hallucinations
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
            ),
        )

        return json.loads(response.text)

    # =================================================
    # STEP 2️⃣ FULL TECHNICAL PIPELINE
    # =================================================
    def run(
        self,
        extracted_rfp: Dict[str, Any],
        technical_summary: Dict[str, Any],
        scope_schema: Dict[str, Any],
        oem_repo: List[Dict[str, Any]],
    ) -> Dict[str, Any]:

        # -----------------------------
        # 1️⃣ Scope of Supply
        # -----------------------------
        raw_scope = self.generate_scope_of_supply(
            extracted_rfp=extracted_rfp,
            technical_summary=technical_summary,
            scope_schema=scope_schema,
        )

        if "product_lines" in raw_scope:
            scope_summary = raw_scope
        elif "scope_of_supply_input" in raw_scope:
            scope_summary = raw_scope["scope_of_supply_input"]
        elif "data" in raw_scope:
            scope_summary = raw_scope["data"]
        else:
            raise ValueError("Invalid scope_of_supply structure from LLM")


        # -----------------------------
        # 2️⃣ Normalize Scope
        # -----------------------------
        normalized_scope = normalize_scope(scope_summary)

        # -----------------------------
        # 3️⃣ Normalize RFP Specs (LLM)
        # -----------------------------
        normalized_specs_llm = normalize_rfp_specs(
            extracted_rfp_technical_specs=extracted_rfp
        )

        # -----------------------------
        # 4️⃣ Enforce Normalized Specs
        # -----------------------------
        enforced_specs = enforce_all(normalized_specs_llm)

        # -----------------------------
        # 5️⃣ Rank OEMs
        # -----------------------------
        top_3_oems = rank_oem_skus(
            rfp_specs=enforced_specs,
            oem_repo=oem_repo,
            top_k=3,
        )

        # -----------------------------
        # 6️⃣ Final OEM Recommendation Table
        # -----------------------------
        final_table = build_final_recommendation_table(
            scope_summary=raw_scope,
            ranked_oems=top_3_oems,
        )

        # -----------------------------
        # 7️⃣ RETURN TO MAIN AGENT
        # -----------------------------
        return {
            "scope_of_supply_summary": scope_summary,
            "normalized_scope": normalized_scope,
            "rfp_specs": enforced_specs,
            "top_3_oems": top_3_oems,
            "final_recommendation_table": final_table,
        }


# =================================================
# LOCAL TEST RUNNER
# =================================================
if __name__ == "__main__":

    with open("outputs/extracted_rfp.json") as f:
        extracted_rfp = json.load(f)

    with open("outputs/technical_summary_by_main_agent.json") as f:
        technical_summary = json.load(f)

    with open("schemas/scope_of_supply_schema.json") as f:
        scope_schema = json.load(f)

    with open("oem_datasheets/normalized_oem.json") as f:
        oem_repo = json.load(f)

    agent = TechnicalAgent()

    result = agent.run(
        extracted_rfp=extracted_rfp,
        technical_summary=technical_summary,
        scope_schema=scope_schema,
        oem_repo=oem_repo,
    )

    print("\nTOP 3 OEM RECOMMENDATIONS\n")
    for i, oem in enumerate(result["top_3_oems"], 1):
        print(f"#{i} {oem['product_sku']} — {oem['spec_match_pct']}%")

    print("\nFINAL OEM RECOMMENDATION TABLE\n")
    for row in result["final_recommendation_table"]:
        print(row)
