import json
from typing import List, Dict, Any


# ============================================================
# 1️⃣ PRODUCT FAMILY CLASSIFIER
# ============================================================

def classify_rfp_product(product_name: str) -> str:
    name = product_name.lower()

    if "switch" in name:
        return "Switching"
    if "access point" in name or "wireless" in name:
        return "Wireless"
    if "cable" in name or "pijf" in name:
        return "Telecom Cable"

    return "Unknown"



def filter_oems_by_family(
    oem_products: List[Dict],
    oem_specs: List[Dict],
    family: str
) -> List[Dict]:

    keywords = {
        "Switching": ["switch"],
        "Wireless": ["wireless", "access point"],
        "Telecom Cable": ["cable", "pijf"]
    }

    allowed = keywords.get(family, [])
    if not allowed:
        return []

    # Step 1️⃣ Filter SKUs from product master
    allowed_skus = {
        p["product_sku"]
        for p in oem_products
        if any(k in p["product_family"].lower() for k in allowed)
    }

    # Step 2️⃣ Return only spec rows for allowed SKUs
    return [
        s for s in oem_specs
        if s["product_sku"] in allowed_skus
    ]

# ============================================================
# 2️⃣ SPEC SCORING (EQUAL WEIGHT)
# ============================================================

def extract_value(val):
    if val is None:
        return None
    if val.get("exact") is not None:
        return val["exact"]
    if val.get("max") is not None:
        return val["max"]
    if val.get("min") is not None:
        return val["min"]
    return None


def score_specs(rfp_specs, oem_specs):
    score = 0
    total = len(rfp_specs)

    oem_index = {o["spec_key"]: o for o in oem_specs}

    for rfp in rfp_specs:
        oem = oem_index.get(rfp["spec_key"])
        if not oem:
            continue

        rfp_val = rfp["value"]
        oem_val = extract_value(oem["value"])
        if oem_val is None:
            continue

        op = rfp["operator"]

        passed = False
        if op == "==":
            tol = rfp.get("tolerance")
            passed = abs(oem_val - rfp_val["exact"]) <= (tol or 0)
        elif op == "<=":
            passed = oem_val <= rfp_val["max"]
        elif op == ">=":
            passed = oem_val >= rfp_val["min"]

        if passed:
            score += 1

    return round(score / total, 4) if total else 0.0


# ============================================================
# 3️⃣ RANK OEMs FOR ONE RFP PRODUCT
# ============================================================

def rank_oems_for_product(rfp_specs, oem_repo):
    from collections import defaultdict

    grouped = defaultdict(list)
    for row in oem_repo:
        grouped[row["product_sku"]].append(row)

    ranked = []
    for sku, specs in grouped.items():
        s = score_specs(rfp_specs, specs)
        ranked.append({
            "product_sku": sku,
            "spec_match_score": s,
            "spec_match_pct": round(s * 100, 2)
        })

    ranked.sort(key=lambda x: x["spec_match_score"], reverse=True)
    return ranked[:3]


# ============================================================
# 4️⃣ MAIN DRIVER
# ============================================================

if __name__ == "__main__":

    with open("outputs/scope_of_supply_summary.json") as f:
        scope = json.load(f)

    with open("outputs/enforced_normalized_specs.json") as f:
        rfp_specs = json.load(f)["data"]

    with open("oem_datasheets/oem_products.json") as f:
        oem_products = json.load(f)

    with open("oem_datasheets/normalized_oem.json") as f:
        oem_specs = json.load(f)


    final_table = []

    print("\nFINAL OEM RECOMMENDATIONS\n")


    for line in scope["product_lines"]:
        product_line = line["product_line_name"]

        for product in line["products"]:
            rfp_name = product["product_name"]
            rfp_code = product["product_code"]
            quantity = product["quantity"]

            # --- family filtering ---
            compatible_oems = filter_oems_by_family(
                oem_products=oem_products,
                oem_specs=oem_specs,
                family = classify_rfp_product(rfp_name)

            )

            if not compatible_oems:
                continue
            print(f"🔍 RFP: {rfp_name} → classified as {family}, OEM candidates: {len(compatible_oems)}")

            # --- ranking ---
            top_oems = rank_oems_for_product(
                rfp_specs=rfp_specs,
                oem_repo=compatible_oems
            )


            if not top_oems:
                continue

            best = top_oems[0]
            print(f"✔ Matched {rfp_name} → {best['product_sku']} ({best['spec_match_pct']}%)")

            final_table.append({
                "product_line": product_line,
                "rfp_product_name": rfp_name,
                "rfp_product_code": rfp_code,
                "quantity": quantity,
                "recommended_oem_sku": best["product_sku"],
                "spec_match_pct": best["spec_match_pct"]
            })

    print("\nFINAL OEM RECOMMENDATION TABLE\n")
    for row in final_table:
        print(row)
