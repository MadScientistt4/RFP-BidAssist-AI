# backend/main.py

from fastapi import FastAPI, UploadFile, File
import json

from agents.main_agent.main_agent import run_pipeline
from agents.technical_agent.normalize_scope_of_summary import normalize_scope
from agents.technical_agent.normalize_rfp_specs import normalize_rfp_specs
from agents.technical_agent.sku_matcher import SKUMatcher

app = FastAPI(title="RFP BidAssist AI Backend")

@app.post("/run-rfp")
async def run_rfp(file: UploadFile = File(...)):
    """
    Full RFP Pipeline:
    1. Extract RFP
    2. Create technical + pricing summaries
    3. Normalize scope & specs
    4. Match OEM SKUs
    5. Return everything for frontend
    """

    # ----------------------------
    # 1. Run main extraction pipeline
    # ----------------------------
    pipeline_output = run_pipeline(file)

    # Expected keys from run_pipeline
    scope_summary = pipeline_output["scope_of_supply_summary"]
    extracted_rfp = pipeline_output["extracted_rfp"]

    # ----------------------------
    # 2. Normalize for matching
    # ----------------------------
    normalized_scope = normalize_scope(scope_summary)
    normalized_specs = normalize_rfp_specs(extracted_rfp)

    # ----------------------------
    # 3. Load OEM data
    # ----------------------------
    with open("oem_datasheets/oem_products.json") as f:
        oem_products = json.load(f)

    with open("oem_datasheets/oem_product_sku.json") as f:
        oem_specs = json.load(f)

    # ----------------------------
    # 4. SKU Matching
    # ----------------------------
    matcher = SKUMatcher(
        normalized_scope=normalized_scope,
        oem_products=oem_products,
        oem_specs=oem_specs
    )

    top_3_skus, spec_match_matrix = matcher.recommend_top_skus(normalized_specs)

    # ----------------------------
    # 5. API Response (Frontend-ready)
    # ----------------------------
    return {
        "rfp_metadata": pipeline_output.get("rfp_metadata"),
        "technical_summary": pipeline_output.get("technical_summary"),
        "scope_of_supply_summary": scope_summary,
        "normalized_scope": normalized_scope,
        "normalized_specs": normalized_specs,
        "top_3_oem_recommendations": top_3_skus,
        "spec_match_matrix": spec_match_matrix
    }
