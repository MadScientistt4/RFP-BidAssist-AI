import json
from typing import Dict, Any, List
from google import genai
from google.genai import types
import os
from dotenv import load_dotenv

load_dotenv()

MODEL_NAME = "gemini-2.5-flash-lite"


class RFPTechSpecNormalizer:
    """
    Converts extracted RFP technical specifications into
    canonical, OEM-comparable normalized specs.
    """

    def __init__(self):
        self.client = genai.Client()

    # -------------------------------------------------
    # LLM STEP: Technical Spec Normalization
    # -------------------------------------------------
    def normalize_rfp_specs(
        self,
        extracted_rfp_technical_specs: List[str],
        canonical_spec_schema: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Inputs:
        - extracted_rfp_technical_specs: list of raw RFP spec sentences
        - canonical_spec_schema: allowed spec keys + expected structure
        - technical_summary: optional context (non-authoritative)

        Output:
        - List of normalized technical spec constraints
        """

        prompt = f"""
You are a TECHNICAL SPECIFICATION NORMALIZATION AGENT.

Your task is to convert RFP technical requirements into
STRUCTURED, MACHINE-COMPARABLE ENGINEERING CONSTRAINTS.

CRITICAL RULES (MUST FOLLOW):
- Follow the schema EXACTLY
- Use ONLY canonical spec keys from the schema
- DO NOT invent specifications
- DO NOT relax limits or merge constraints
- Preserve numeric limits, operators, tolerances, and test conditions
- Each spec MUST reference its original source text
- Output VALID JSON ONLY

VARIANT HANDLING RULES (VERY IMPORTANT):
- If a specification applies to a specific cable variant, size, or pair count,
  you MUST attach the correct variant scope.
- NEVER merge specs belonging to different pair counts or variants.
- If the RFP lists multiple diameters, resistances, or limits for different
  pair counts, they MUST appear as SEPARATE spec objects.
- Each spec object MUST belong to exactly ONE variant scope.

VARIANT SCOPE RULES (MANDATORY FOR EVERY SPEC OBJECT):
- EVERY spec object MUST include a "variant_scope" field.
- If a specification applies to ALL cable sizes or pair counts,
  you MUST still include "variant_scope" with:
    {{ "pair_count": None }}
- If the specification applies to a specific cable size, pair count,
  or variant, set the correct numeric "pair_count" value.
- NEVER omit the "variant_scope" field.
- NEVER guess a pair count.
- If variant scope cannot be confidently determined from the RFP text,
  set "pair_count" to None.

CANONICAL SPEC SCHEMA:
{json.dumps(canonical_spec_schema, indent=2)}

EXTRACTED RFP TECHNICAL SPECS:
{json.dumps(extracted_rfp_technical_specs, indent=2)}

OUTPUT FORMAT:
Return a JSON array.
Each item MUST strictly follow the canonical spec schema.
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
# PUBLIC FUNCTION (Pipeline-friendly)
# -------------------------------------------------
def normalize_rfp_specs(
    extracted_rfp_technical_specs,
    canonical_spec_schema=None,
):
    """
    Wrapper for pipeline usage.
    """

    # Canonical spec schema (OEM-aligned)
    with open("schemas/canonical_spec_schema.json") as f:
        canonical_spec_schema = json.load(f)

    # Technical summary (for context)
    with open("outputs/technical_summary_by_main_agent.json") as f:
        technical_summary = json.load(f)

    normalizer = RFPTechSpecNormalizer()

    return normalizer.normalize_rfp_specs(
        extracted_rfp_technical_specs=extracted_rfp_technical_specs,
        canonical_spec_schema=canonical_spec_schema,
        technical_summary=technical_summary
    )

def main():
    """
    Local test for RFP technical spec normalization.
    Replace sample data with extraction-agent output later.
    """
    with open("outputs/extracted_rfp.json") as f:
        extracted_rfp_technical_specs = json.load(f)
    # Sample extracted RFP technical spec lines

    # Canonical spec schema (OEM-aligned)
    with open("schemas/canonical_spec_schema.json") as f:
        canonical_spec_schema = json.load(f)

    # Technical summary (for context)
    with open("outputs/technical_summary_by_main_agent.json") as f:
        technical_summary = json.load(f)

    normalizer = RFPTechSpecNormalizer()

    normalized_specs = normalizer.normalize_rfp_specs(
        extracted_rfp_technical_specs=extracted_rfp_technical_specs,
        canonical_spec_schema=canonical_spec_schema
    )

    # -----------------------------
    # Output
    # -----------------------------
    print("\n🔹 NORMALIZED RFP TECHNICAL SPECS 🔹\n")
    print(json.dumps(normalized_specs, indent=2))


if __name__ == "__main__":
    main()