# backend/main.py

import tempfile
from pathlib import Path

from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware

from agents.main_agent.main_agent import run_pipeline
from agents.sales_agent.sales_agent import SalesAgent

app = FastAPI(title="RFP BidAssist AI Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/scan-rfps")
async def scan_rfps():
    """
    Sales Agent: scans the predefined tender-listing URLs, identifies RFPs
    due for submission in the next 3 months, and selects one to respond to.
    Pure HTML/regex parsing - no LLM call, so this is free to call as often
    as needed.
    """
    return SalesAgent().run()


@app.post("/run-selected-rfp")
async def run_selected_rfp(payload: dict):
    """
    Runs the full Main Agent pipeline (extraction -> technical -> pricing)
    against the PDF the Sales Agent selected. Expects {"pdf_path": "..."}
    as returned by /scan-rfps' selected_rfp_pdf_path.
    """
    pdf_path = payload.get("pdf_path")
    if not pdf_path:
        return {"error": "pdf_path is required"}
    return run_pipeline(pdf_path)


@app.post("/run-rfp")
async def run_rfp(file: UploadFile = File(...)):
    """
    Full RFP Pipeline (Main Agent orchestrated):
      1. Extract RFP
      2. Technical Agent: scope of supply + OEM SKU matching
      3. Pricing Agent: material + test pricing
      4. Consolidated response for the frontend
    """
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    try:
        return run_pipeline(tmp_path)
    finally:
        Path(tmp_path).unlink(missing_ok=True)
