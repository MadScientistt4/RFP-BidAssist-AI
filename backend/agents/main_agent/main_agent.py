# agents/main_agent.py

import json
import subprocess
import sys
from pathlib import Path
from dotenv import load_dotenv
from google import genai
from google.genai import types

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
    # STEP 1: GENERATE TECHNICAL SUMMARY
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
    # STEP 2: RUN EXTERNAL TECHNICAL AGENT (BLOCKING)
    # -------------------------------------------------
    def run_external_technical_agent(self) -> dict:
        tech_agent_path = PROJECT_ROOT/ "agents" / "technical_agent" / "technical_agent.py"
        output_path = OUTPUT_DIR / "technical_agent_output.json"
        
        if not tech_agent_path.exists():
            raise FileNotFoundError("❌ technical_agent/technical_agent.py not found")

        # Run the external script (BLOCKING)
        result = subprocess.run(
                [sys.executable, str(tech_agent_path)],
                cwd=str(PROJECT_ROOT),
                text=True
        )


        if result.returncode != 0:
            print("STDOUT:\n", result.stdout)
            print("STDERR:\n", result.stderr)
            raise RuntimeError("❌ Technical agent execution failed")

        if not output_path.exists():
            raise RuntimeError("❌ technical_agent_output.json not generated")

        with open(output_path, "r", encoding="utf-8") as f:
            return json.load(f)
        
    # -------------------------------------------------
    # STEP 3: GENERATE PRICING SUMMARY
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
    # FULL PIPELINE
    # -------------------------------------------------
    def run_pipeline(self, extracted_rfp_json: dict) -> dict:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

        # 1. Technical summary
        technical_summary = self.generate_technical_summary(extracted_rfp_json)

        with open(OUTPUT_DIR / "technical_summary.json", "w", encoding="utf-8") as f:
            json.dump(technical_summary, f, indent=2)

        # 2. External technical agent (BLOCKING)
        technical_agent_output = self.run_external_technical_agent()

        # 3. Pricing summary
        pricing_summary = self.generate_pricing_summary(
            extracted_rfp_json,
            technical_agent_output
        )

        return {
            "technical_summary": technical_summary,
            "technical_agent_output": technical_agent_output,
            "pricing_summary": pricing_summary
        }


# -------------------------------------------------
# LOCAL EXECUTION
# -------------------------------------------------
if __name__ == "__main__":

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    extracted_rfp_path = OUTPUT_DIR / "extracted_rfp.json"

    if not extracted_rfp_path.exists():
        raise FileNotFoundError("❌ outputs/extracted_rfp.json not found")

    with open(extracted_rfp_path, "r", encoding="utf-8") as f:
        extracted_rfp = json.load(f)

    agent = MainAgent()
    results = agent.run_pipeline(extracted_rfp)

    with open(OUTPUT_DIR / "pricing_summary.json", "w", encoding="utf-8") as f:
        json.dump(results["pricing_summary"], f, indent=2)

    print("✅ Full pipeline executed successfully")
