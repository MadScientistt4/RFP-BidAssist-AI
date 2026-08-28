# agents/main_agent/main_agent.py

import json
from pathlib import Path
from dotenv import load_dotenv
from google import genai
from google.genai import types

from agents.extractor_agent.extractor_agent import ExtractorAgent
from agents.technical_agent.technical_agent import TechnicalAgent
from agents.pricing_agent import PricingAgent

# -------------------------------------------------
# PATH SETUP
# -------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent.parent
OUTPUT_DIR = PROJECT_ROOT / "outputs"

# -------------------------------------------------
# ENV
# -------------------------------------------------
load_dotenv()

client = genai.Client()
MODEL = "gemini-2.5-flash-lite"


# -------------------------------------------------
# MAIN AGENT (ORCHESTRATOR)
# -------------------------------------------------
class MainAgent:
    def __init__(self):
        self.client = client
        self.model = MODEL

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
    # STEP 1: GENERATE TECHNICAL SUMMARY (for Technical Agent)
    # -------------------------------------------------
    def generate_technical_summary(self, extracted_rfp_json: dict) -> dict:
        prompt = (
            self.technical_prompt
            .replace(
                "{{TECHNICAL_SUMMARY_SCHEMA}}",
                json.dumps(self.technical_schema, indent=2)
            )
            .replace(
                "{{EXTRACTED_RFP_JSON}}",
                json.dumps(extracted_rfp_json, indent=2)
            )
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
    # STEP 2: GENERATE PRICING SUMMARY (for Pricing Agent)
    # -------------------------------------------------
    def generate_pricing_summary(
        self,
        extracted_rfp_json: dict,
        technical_agent_output_json: dict
    ) -> dict:

        prompt = (
            self.pricing_prompt
            .replace(
                "{{PRICING_SUMMARY_SCHEMA}}",
                json.dumps(self.pricing_schema, indent=2)
            )
            .replace(
                "{{EXTRACTED_RFP_JSON}}",
                json.dumps(extracted_rfp_json, indent=2)
            )
            .replace(
                "{{TECHNICAL_AGENT_OUTPUT_JSON}}",
                json.dumps(technical_agent_output_json, indent=2)
            )
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
# FULL PIPELINE (Extraction -> Technical -> Pricing)
# -------------------------------------------------
def run_pipeline(pdf_path: str) -> dict:
    """
    End-to-end RFP response pipeline, driven by the Main Agent:
      1. Extract structured data from the RFP PDF
      2. Summarize scope for the Technical Agent, get back SKU matches
      3. Summarize pricing inputs for the Pricing Agent, get back the priced table
      4. Consolidate everything into a single RFP response payload
    """
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    main_agent = MainAgent()

    # ----------------------------
    # 1. Extract RFP
    # ----------------------------
    with open(PROJECT_ROOT / "prompts" / "extractor_prompt.txt", encoding="utf-8") as f:
        extractor_prompt = f.read()

    with open(PROJECT_ROOT / "schemas" / "extraction_schema.json", encoding="utf-8") as f:
        extraction_schema = json.load(f)

    extracted_rfp = ExtractorAgent(
        prompt_template=extractor_prompt,
        schema=extraction_schema
    ).extract(pdf_path)

    with open(OUTPUT_DIR / "extracted_rfp.json", "w", encoding="utf-8") as f:
        json.dump(extracted_rfp, f, indent=2)

    # ----------------------------
    # 2. Technical summary (Main Agent -> Technical Agent)
    # ----------------------------
    technical_summary = main_agent.generate_technical_summary(extracted_rfp)

    with open(OUTPUT_DIR / "technical_summary.json", "w", encoding="utf-8") as f:
        json.dump(technical_summary, f, indent=2)

    # ----------------------------
    # 3. Technical Agent: scope of supply + SKU matching
    # ----------------------------
    with open(PROJECT_ROOT / "schemas" / "scope_of_supply_schema.json", encoding="utf-8") as f:
        scope_schema = json.load(f)

    with open(PROJECT_ROOT / "oem_datasheets" / "normalized_oem.json", encoding="utf-8") as f:
        oem_repo = json.load(f)

    technical_agent_output = TechnicalAgent().run(
        extracted_rfp=extracted_rfp,
        technical_summary=technical_summary,
        scope_schema=scope_schema,
        oem_repo=oem_repo,
    )

    with open(OUTPUT_DIR / "technical_agent_output.json", "w", encoding="utf-8") as f:
        json.dump(technical_agent_output, f, indent=2)

    # ----------------------------
    # 4. Pricing summary (Main Agent -> Pricing Agent)
    # ----------------------------
    pricing_summary = main_agent.generate_pricing_summary(
        extracted_rfp,
        technical_agent_output
    )

    with open(OUTPUT_DIR / "pricing_summary.json", "w", encoding="utf-8") as f:
        json.dump(pricing_summary, f, indent=2)

    # ----------------------------
    # 5. Pricing Agent: assign prices from synthetic price tables
    # ----------------------------
    pricing_agent = PricingAgent(
        test_price_chart_path=str(BASE_DIR / "prompts" / "test_price_chart.json"),
        material_price_chart_path=str(BASE_DIR / "prompts" / "price_chart.json"),
    )
    final_priced_output = pricing_agent.generate_pricing_table(pricing_summary)

    with open(OUTPUT_DIR / "final_priced_output.json", "w", encoding="utf-8") as f:
        json.dump(final_priced_output, f, indent=2)

    # ----------------------------
    # 6. Consolidated RFP response (Main Agent)
    # ----------------------------
    return {
        "extracted_rfp": extracted_rfp,
        "technical_summary": technical_summary,
        "technical_agent_output": technical_agent_output,
        "pricing_summary": pricing_summary,
        "final_priced_output": final_priced_output,
    }


# -------------------------------------------------
# LOCAL EXECUTION
# -------------------------------------------------
if __name__ == "__main__":
    sample_pdf = PROJECT_ROOT / "samples" / "rfp_2024.pdf"

    if not sample_pdf.exists():
        raise FileNotFoundError(f"❌ Sample RFP not found at {sample_pdf}")

    results = run_pipeline(str(sample_pdf))

    print("✅ Full pipeline executed successfully")
    print(f"Grand total: {results['final_priced_output'].get('grand_total')}")
