from agents.technical_agent.normalize_scope_of_summary import normalize_scope
from agents.technical_agent.normalize_rfp_specs import normalize_rfp_specs
from agents.technical_agent.sku_matcher import SKUMatcher
import json

# --- RFP INPUT ---

with open("outputs/scope_of_supply_summary.json") as f:
    scope_text = json.load(f)
with open("outputs/extracted_rfp.json") as f:
    spec_text = json.load(f)

# --- Normalize ---
normalized_scope = normalize_scope(scope_text)
normalized_specs = normalize_rfp_specs(spec_text)

# --- Load OEM Data ---
with open("oem_datasheets/oem_products.json") as f:
    oem_products = json.load(f)

with open("oem_datasheets/oem_product_sku.json") as f:
    oem_specs = json.load(f)

# --- Match ---
matcher = SKUMatcher(normalized_scope, oem_products, oem_specs)
top_3, spec_matrix = matcher.recommend_top_skus(normalized_specs)

print("\nTOP 3 SKUs")
print(json.dumps(top_3, indent=2))

print("\nSPEC MATCH MATRIX")
print(json.dumps(spec_matrix, indent=2))
