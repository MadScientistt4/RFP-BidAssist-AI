import json
from typing import Dict, List, Any, Tuple
from pathlib import Path
import csv

OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)


def save_json(filename: str, data):
    path = OUTPUT_DIR / filename
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"✅ Saved {path}")

# =================================================
# BASIC UTILITIES
# =================================================

def extract_oem_numeric_value(oem_value: Dict[str, Any]) -> float | None:
    if not oem_value:
        return None
    if oem_value.get("exact") is not None:
        return oem_value["exact"]
    if oem_value.get("max") is not None:
        return oem_value["max"]
    if oem_value.get("min") is not None:
        return oem_value["min"]
    return None


def variant_matches(rfp_spec: Dict[str, Any], oem_spec: Dict[str, Any]) -> bool:
    return (
        rfp_spec["variant_scope"]["pair_count"] is None
        or rfp_spec["variant_scope"]["pair_count"]
        == oem_spec["variant_scope"]["pair_count"]
    )


# =================================================
# COMPLIANCE + SCORING
# =================================================

def check_compliance(rfp_spec: Dict[str, Any], oem_value: float) -> bool:
    op = rfp_spec["operator"]
    val = rfp_spec["value"]

    if op == "<=":
        return oem_value <= val["max"]
    if op == ">=":
        return oem_value >= val["min"]
    if op == "==":
        tol = rfp_spec.get("tolerance")
        if tol is None:
            return oem_value == val["exact"]
        return abs(oem_value - val["exact"]) <= tol

    return False


def compute_quality_score(rfp_spec: Dict[str, Any], oem_value: float) -> float:
    op = rfp_spec["operator"]
    val = rfp_spec["value"]

    if op == "<=":
        return min(1.0, val["max"] / oem_value)

    if op == ">=":
        return min(1.0, oem_value / val["min"])

    if op == "==":
        tol = rfp_spec.get("tolerance")
        if tol is None:
            return 1.0 if oem_value == val["exact"] else 0.0
        delta = abs(oem_value - val["exact"])
        return max(0.0, 1 - (delta / tol))

    return 0.0


# =================================================
# SCORE ONE SKU
# =================================================

def score_sku(
    rfp_specs: List[Dict[str, Any]],
    oem_specs: List[Dict[str, Any]],
) -> float:

    # Deduplicate RFP specs (spec_key + pair_count)
    unique = {}
    for rfp in rfp_specs:
        key = (rfp["spec_key"], rfp["variant_scope"]["pair_count"])
        unique[key] = rfp
    rfp_specs = list(unique.values())

    total_score = 0.0
    total_required = len(rfp_specs)

    for rfp in rfp_specs:
        matched = [
            o for o in oem_specs
            if o["spec_key"] == rfp["spec_key"]
            and variant_matches(rfp, o)
        ]

        if not matched:
            continue

        oem_value = extract_oem_numeric_value(matched[0]["value"])
        if oem_value is None:
            continue

        if not check_compliance(rfp, oem_value):
            continue

        total_score += compute_quality_score(rfp, oem_value)

    return round(total_score / total_required, 4) if total_required else 0.0


# =================================================
# OEM RANKING
# =================================================

def group_oem_by_sku(oem_rows: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    grouped = {}
    for row in oem_rows:
        grouped.setdefault(row["product_sku"], []).append(row)
    return grouped


def rank_oem_skus(
    rfp_specs: List[Dict[str, Any]],
    oem_repo: List[Dict[str, Any]],
    top_k: int = 3
) -> List[Dict[str, Any]]:

    ranked = []
    grouped = group_oem_by_sku(oem_repo)

    for sku, oem_specs in grouped.items():
        score = score_sku(rfp_specs, oem_specs)
        ranked.append({
            "product_sku": sku,
            "spec_match_score": score,
            "spec_match_pct": round(score * 100, 2)
        })

    ranked.sort(key=lambda x: x["spec_match_score"], reverse=True)
    return ranked[:top_k]


# =================================================
# FINAL OEM SELECTION PER RFP PRODUCT
# =================================================

def build_final_recommendation_table(
    scope_summary: Dict[str, Any],
    ranked_oems: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:

    final_table = []

    for line in scope_summary["product_lines"]:
        for product in line["products"]:
            best_oem = ranked_oems[0]

            final_table.append({
                "product_line": line["product_line_name"],
                "rfp_product_name": product["product_name"],
                "rfp_product_code": product["product_code"],
                "quantity": product["quantity"],
                "recommended_oem_sku": best_oem["product_sku"],
                "spec_match_pct": best_oem["spec_match_pct"]
            })

    return final_table

# =================================================
# COMPARISON TABLE
# =================================================

def build_comparison_table(
    rfp_specs: List[Dict[str, Any]],
    top_oems: List[Dict[str, Any]],
    oem_repo: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:

    # index OEM specs as: SKU → spec_key → spec
    oem_index = {}
    for row in oem_repo:
        sku = row["product_sku"]
        oem_index.setdefault(sku, {})[row["spec_key"]] = row

    table = []

    for rfp in rfp_specs:
        row = {
            "spec_key": rfp["spec_key"],
            "pair_count": rfp["variant_scope"]["pair_count"],
            "rfp_requirement": rfp["value"]
        }

        for i, oem in enumerate(top_oems, start=1):
            sku = oem["product_sku"]
            oem_spec = oem_index.get(sku, {}).get(rfp["spec_key"])

            if not oem_spec:
                row[f"OEM_{i}"] = "N/A"
                continue

            oem_value = extract_oem_numeric_value(oem_spec["value"])
            passed = (
                check_compliance(rfp, oem_value)
                if oem_value is not None
                else False
            )

            row[f"OEM_{i}"] = {
                "value": oem_value,
                "passed": passed
            }

        table.append(row)

    return table

# =================================================
# MAIN RUNNER
# =================================================

if __name__ == "__main__":

    # ---- LOAD FILES ----
    with open("outputs/enforced_normalized_specs.json", "r") as f:
        rfp_specs = json.load(f)["data"]

    with open("oem_datasheets/normalized_oem.json", "r") as f:
        oem_repo = json.load(f)

    with open("outputs/scope_of_supply_summary.json", "r") as f:
        scope_summary = json.load(f)

    # ---- RANK OEMs ----
    top_3 = rank_oem_skus(
        rfp_specs=rfp_specs,
        oem_repo=oem_repo,
        top_k=3
    )

    # ---- FINAL TABLE ----
    final_table = build_final_recommendation_table(
        scope_summary=scope_summary,
        ranked_oems=top_3
    )

    # ---- COMPARISON TABLE ----
    comparison_table = build_comparison_table(
        rfp_specs=rfp_specs,
        top_oems=top_3,
        oem_repo=oem_repo
    )
    save_json("final_oem_recommendation_table.json", final_table)
    save_json("comparison_table.json", comparison_table)
    # ---- PRINT OUTPUT ----
    print("\nTOP 3 OEM RECOMMENDATIONS\n")
    for i, oem in enumerate(top_3, 1):
        print(f"#{i} SKU: {oem['product_sku']} — Spec Match: {oem['spec_match_pct']}%")

    print("\nFINAL OEM RECOMMENDATION TABLE\n")
    for row in final_table:
        print(row)

    print("\nCOMPARISON TABLE\n")
    for row in comparison_table:
        print(row)
