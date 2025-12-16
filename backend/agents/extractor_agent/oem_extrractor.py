class OEMExtractorAgent:
    def __init__(self, model_client):
        self.model = model_client

    def extract(self, pdf_text: str, schema: dict, prompt: str) -> dict:
        full_prompt = f"""
{prompt}

SCHEMA:
{schema}

OEM DATASHEET TEXT:
{pdf_text}
"""

        response = self.model.generate(full_prompt)

        try:
            return json.loads(response)
        except Exception:
            raise ValueError("OEM Extraction failed: Invalid JSON")
