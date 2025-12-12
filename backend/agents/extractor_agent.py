import json
import re
import fitz  # PyMuPDF
from typing import Optional
from dotenv import load_dotenv
import os
# -----------------------
# 1. LLM CLIENT (Gemini or GPT)
# -----------------------
import google.generativeai as genai


class LLMClient:
    def __init__(self, provider="gemini", api_key=None):
        self.provider = provider

        if provider == "gemini":
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel("gemini-1.5-flash")


    def generate(self, prompt: str) -> str:
        """Unified interface for generating text from either provider."""
        if self.provider == "gemini":
            response = self.model.generate_content(prompt)
            return response.text


# -----------------------
# 2. PDF TEXT EXTRACTION
# -----------------------
class PDFProcessor:
    @staticmethod
    def extract_text(pdf_path: str) -> str:
        """Extracts raw text from PDF using PyMuPDF."""
        text = ""
        with fitz.open(pdf_path) as doc:
            for page in doc:
                text += page.get_text("text") + "\n"
        return text

    @staticmethod
    def clean_text(text: str) -> str:
        """Basic cleaning: remove extra whitespace."""
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
        """Attempts to extract JSON if the model wrapped it in text."""
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
        """Insert RFP text into the predefined schema prompt."""
        return self.prompt_template + "\n\nRFP CONTENT STARTS BELOW:\n\n" + text

    def extract(self, pdf_path: str) -> dict:
        """Main pipeline: PDF → Text → Clean → Prompt → LLM → JSON."""
        print("Extracting text from PDF...")
        raw_text = PDFProcessor.extract_text(pdf_path)
        cleaned_text = PDFProcessor.clean_text(raw_text)

        print("Building prompt...")
        prompt = self.build_prompt(cleaned_text)

        print("Sending to LLM...")
        llm_output = self.llm.generate(prompt)

        print("Parsing JSON...")
        result_json = JSONFixer.try_parse(llm_output)

        # If JSON is not clean, try extracting embedded JSON
        if result_json is None:
            print("Fixing JSON...")
            result_json = JSONFixer.extract_json_from_text(llm_output)

        if result_json is None:
            raise ValueError("ExtractorAgent: Could not parse JSON from LLM output.")

        return result_json


# -----------------------
# 5. USAGE EXAMPLE
# -----------------------
if __name__ == "__main__":

    # Load prompt template from file for safety
    with open("agents/prompts/extractor_prompt.txt", "r", encoding="utf-8") as f:
        extractor_prompt = f.read()

    llm = LLMClient(
        provider="gemini",
        api_key=os.getenv("GEMINI_API_KEY")
    )

    agent = ExtractorAgent(llm, extractor_prompt)

    output = agent.extract("samples/sample_rfp.pdf")
    print(json.dumps(output, indent=4))
