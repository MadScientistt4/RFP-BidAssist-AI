import json
import re
import fitz  # PyMuPDF
from typing import Optional
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# -----------------------
# 1. LLM CLIENT (Gemini)
# -----------------------
import google.generativeai as genai


import requests
import os

class LLMClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.url = (
            "https://generativelanguage.googleapis.com/v1beta/"
            "models/gemini-2.0-flash:generateContent"
        )

    def generate(self, prompt: str) -> str:
        headers = {
            "Content-Type": "application/json"
        }

        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt}
                    ]
                }
            ]
        }

        response = requests.post(
            f"{self.url}?key={self.api_key}",
            headers=headers,
            json=payload,
            timeout=60
        )

        response.raise_for_status()
        data = response.json()

        return data["candidates"][0]["content"]["parts"][0]["text"]



# -----------------------
# 2. PDF TEXT EXTRACTION
# -----------------------
class PDFProcessor:
    @staticmethod
    def extract_text(pdf_path: str) -> str:
        text = ""
        with fitz.open(pdf_path) as doc:
            for page in doc:
                text += page.get_text("text") + "\n"
        return text

    @staticmethod
    def clean_text(text: str) -> str:
        text = re.sub(r"\s+", " ", text)
        return text.strip()


# -----------------------
# 3. JSON VALIDATION / FIXING
# -----------------------
class JSONFixer:
    @staticmethod
    def try_parse(json_text: str) -> Optional[dict]:
        try:
            return json.loads(json_text)
        except json.JSONDecodeError:
            return None

    @staticmethod
    def extract_json_from_text(llm_output: str) -> Optional[dict]:
        match = re.search(r"\{.*\}", llm_output, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except:
                return None
        return None


# -----------------------
# 4. EXTRACTOR AGENT
# -----------------------
class ExtractorAgent:
    def __init__(self, llm_client: LLMClient, prompt_template: str):
        self.llm = llm_client
        self.prompt_template = prompt_template

    def build_prompt(self, text: str) -> str:
        """
        Builds the final prompt by injecting:
        1. Instructions
        2. Schema
        3. RFP content
        """

        # Load schema
        with open("agents/prompts/schema.json", "r", encoding="utf-8") as f:
            schema_json = f.read()

        prompt = (
            self.prompt_template
            + "\n\n---\n"
            + "SCHEMA (You must follow this structure EXACTLY):\n"
            + schema_json
            + "\n---\n\n"
            + "RFP CONTENT STARTS BELOW:\n\n"
            + text
        )

        return prompt

    def extract(self, pdf_path: str) -> dict:
        print("Extracting text from PDF...")
        raw_text = PDFProcessor.extract_text(pdf_path)
        cleaned_text = PDFProcessor.clean_text(raw_text)

        print("Building prompt...")
        prompt = self.build_prompt(cleaned_text)

        print("Sending to LLM...")
        llm_output = self.llm.generate(prompt)

        print("Parsing JSON...")
        result_json = JSONFixer.try_parse(llm_output)

        if result_json is None:
            print("Fixing JSON...")
            result_json = JSONFixer.extract_json_from_text(llm_output)

        if result_json is None:
            raise ValueError("ExtractorAgent: Could not parse JSON from LLM output.")

        return result_json


# -----------------------
# 5. RUN DIRECTLY
# -----------------------
if __name__ == "__main__":

    # Load extractor prompt
    with open("agents/prompts/extractor_prompt.txt", "r", encoding="utf-8") as f:
        extractor_prompt = f.read()

    llm = LLMClient(
        api_key=os.getenv("GEMINI_API_KEY")
    )

    agent = ExtractorAgent(llm, extractor_prompt)

    output = agent.extract("samples/24a1021.pdf")

    print(json.dumps(output, indent=4))
