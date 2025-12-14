import os
import json
import re
import fitz  # PyMuPDF
from typing import Optional, Dict, Any

from dotenv import load_dotenv
from google import genai
from google.genai import types

# -------------------------------------------------
# ENV
# -------------------------------------------------
load_dotenv()

# -------------------------------------------------
# GEMINI CLIENT
# -------------------------------------------------
try:
    client = genai.Client()
    GEMINI_MODEL = "gemini-2.5-flash"   # ✅ WORKING MODEL
except Exception as e:
    raise RuntimeError("Failed to initialize Gemini client. Check API key.") from e


# -------------------------------------------------
# PDF PROCESSOR
# -------------------------------------------------
class PDFProcessor:
    @staticmethod
    def extract_text(pdf_path: str) -> str:
        text = ""
        with fitz.open(pdf_path) as doc:
            for page in doc:
                text += page.get_text("text") + "\n"
        return text.strip()


# -------------------------------------------------
# JSON FIXER
# -------------------------------------------------
class JSONFixer:
    @staticmethod
    def try_parse(text: str) -> Optional[Dict[str, Any]]:
        try:
            return json.loads(text)
        except Exception:
            return None

    @staticmethod
    def extract_json(text: str) -> Optional[Dict[str, Any]]:
        match = re.search(r"\{[\s\S]*\}", text)
        if match:
            try:
                return json.loads(match.group(0))
            except Exception:
                return None
        return None


# -------------------------------------------------
# EXTRACTOR AGENT
# -------------------------------------------------
class ExtractorAgent:
    def __init__(self, prompt_template: str, schema: Dict[str, Any]):
        self.prompt_template = prompt_template
        self.schema = schema

    def build_prompt(self, rfp_text: str) -> str:
        return f"""
{self.prompt_template}

JSON Schema (STRICTLY FOLLOW):
{json.dumps(self.schema, indent=2)}

RFP DOCUMENT TEXT:
------------------
{rfp_text}
------------------
"""

    def extract(self, pdf_path: str) -> Dict[str, Any]:
        print("📄 Extracting PDF text...")
        document_text = PDFProcessor.extract_text(pdf_path)

        print("🧠 Building prompt...")
        prompt = self.build_prompt(document_text)

        print("🚀 Calling Gemini...")
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=[prompt],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                system_instruction="You are an expert RFP parser. Respond ONLY with valid JSON."
            )
        )

        raw_output = response.text
        print("📦 Raw Gemini Output received")

        parsed = JSONFixer.try_parse(raw_output)
        if not parsed:
            parsed = JSONFixer.extract_json(raw_output)

        if not parsed:
            raise ValueError("❌ Failed to parse JSON from Gemini response")

        return parsed


# -------------------------------------------------
# RUN DIRECTLY
# -------------------------------------------------
if __name__ == "__main__":

    with open("agents/prompts/extractor_prompt.txt", "r", encoding="utf-8") as f:
        extractor_prompt = f.read()

    with open("agents/prompts/schema.json", "r", encoding="utf-8") as f:
        schema = json.load(f)

    agent = ExtractorAgent(
        prompt_template=extractor_prompt,
        schema=schema
    )

    result = agent.extract("samples/rfp_2024.pdf")

    print("\n✅ FINAL EXTRACTED JSON:")
    print(json.dumps(result, indent=2))
