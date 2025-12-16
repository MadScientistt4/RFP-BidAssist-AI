from agents.technical_agent.normalize_scope_of_summary import normalize_scope
from agents.technical_agent.normalize_rfp_specs import normalize_rfp_specs
from agents.technical_agent.sku_matcher import SKUMatcher
import json

# --- RFP INPUT ---
scope_text = """
Supply, installation, testing and commissioning of
200 pair underground telecom cable for 120 km as per DOT standards.
"""

spec_text = """
Conductor resistance shall not exceed 85 Ohms/km.
Mutual capacitance ≤ 50 nF/km.
"""

# --- Normalize ---
normalized_scope = normalize_scope(scope_text)
normalized_specs = normalize_rfp_specs(spec_text)

# --- Load OEM Data ---
with open("backend/oem_datasheets/oem_products.json") as f:
    oem_products = json.load(f)

with open("backend/oem_datasheets/oem_product_sku.json") as f:
    oem_specs = json.load(f)

# --- Match ---
matcher = SKUMatcher(normalized_scope, oem_products, oem_specs)
top_3, spec_matrix = matcher.recommend_top_skus(normalized_specs)

print("\nTOP 3 SKUs")
print(json.dumps(top_3, indent=2))

print("\nSPEC MATCH MATRIX")
print(json.dumps(spec_matrix, indent=2))
