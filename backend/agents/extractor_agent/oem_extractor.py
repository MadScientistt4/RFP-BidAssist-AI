import os
import json
import re
import time
import fitz  # PyMuPDF
from typing import Optional, Dict, Any, List

from dotenv import load_dotenv
from google import genai
from google.genai import types
from google.genai.errors import ServerError

# -------------------------------------------------
# ENV
# -------------------------------------------------
load_dotenv()

# -------------------------------------------------
# GEMINI CLIENT
# -------------------------------------------------
client = genai.Client()
GEMINI_MODEL = "gemini-2.5-flash"  # fast + stable

# -------------------------------------------------
# CONSTANTS
# -------------------------------------------------
MAX_CHARS_PER_CHUNK = 10_000
MAX_RETRIES = 5
TIMEOUT_SECONDS = 30

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

    @staticmethod
    def chunk_text(text: str) -> List[str]:
        return [
            text[i:i + MAX_CHARS_PER_CHUNK]
            for i in range(0, len(text), MAX_CHARS_PER_CHUNK)
        ]


# -------------------------------------------------
# JSON UTIL
# -------------------------------------------------
class JSONFixer:
    @staticmethod
    def extract_json(text: str) -> Optional[Dict[str, Any]]:
        match = re.search(r"\{[\s\S]*\}", text)
        if not match:
            return None
        try:
            return json.loads(match.group(0))
        except Exception:
            return None


# -------------------------------------------------
# GEMINI CALL WITH RETRY
# -------------------------------------------------
def call_gemini(prompt: str) -> Dict[str, Any]:
    for attempt in range(MAX_RETRIES):
        try:
            response = client.models.generate_content(
                model=GEMINI_MODEL,
                contents=[prompt],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    system_instruction=(
                        "You are an expert OEM datasheet parser. "
                        "Extract ONLY fields found in the text. "
                        "Return VALID JSON ONLY."
                    )
                )
            )

            parsed = JSONFixer.extract_json(response.text)
            if not parsed:
                raise ValueError("Invalid JSON returned")

            return parsed

        except ServerError as e:
            if "503" in str(e) or "UNAVAILABLE" in str(e):
                wait = 2 ** attempt
                print(f"⚠️ Gemini overloaded. Retry in {wait}s...")
                time.sleep(wait)
            else:
                raise


    raise RuntimeError("Gemini failed after retries")


# -------------------------------------------------
# EXTRACTOR AGENT
# -------------------------------------------------
class OEMExtractorAgent:
    def __init__(self, prompt_template: str, schema: Dict[str, Any]):
        self.prompt_template = prompt_template
        self.schema = schema

    def build_prompt(self, text_chunk: str) -> str:
        return f"""
{self.prompt_template}

JSON SCHEMA (follow strictly):
{json.dumps(self.schema, indent=2)}

DOCUMENT TEXT:
--------------
{text_chunk}
--------------
"""

    def extract(self, pdf_path: str) -> Dict[str, Any]:
        print("📄 Extracting PDF text...")
        full_text = PDFProcessor.extract_text(pdf_path)

        print("✂️ Chunking document...")
        chunks = PDFProcessor.chunk_text(full_text)

        partial_results = []

        for idx, chunk in enumerate(chunks):
            print(f"🚀 Processing chunk {idx+1}/{len(chunks)}")
            prompt = self.build_prompt(chunk)
            partial = call_gemini(prompt)
            partial_results.append(partial)

        print("🧠 Merging partial results...")
        return self.merge_results(partial_results)

    def merge_results(self, partials: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Simple deterministic merge:
        - First non-null value wins
        - Lists are merged uniquely
        """
        final = {}

        for part in partials:
            for key, value in part.items():
                if value in (None, "", [], {}):
                    continue

                if key not in final:
                    final[key] = value
                elif isinstance(value, list):
                    final[key] = list(set(final[key]) | set(value))

        return final


# -------------------------------------------------
# RUN DIRECTLY
# -------------------------------------------------
if __name__ == "__main__":

    with open("agents/extractor_agent/prompts/oem_extraction_prompt.txt", "r", encoding="utf-8") as f:
        extractor_prompt = f.read()

    with open("agents/extractor_agent/prompts/oem_datasheet_normalized_schema.json", "r", encoding="utf-8") as f:
        schema = json.load(f)

    agent = OEMExtractorAgent(
        prompt_template=extractor_prompt,
        schema=schema
    )

    result = agent.extract("samples/TopCable_General_OEM.pdf")

    print("\n✅ FINAL EXTRACTED JSON")
    print(json.dumps(result, indent=2))
