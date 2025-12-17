# backend/agents/technical_agent/spec_scorer.py

import json
from typing import Dict, List, Any, Tuple


# -------------------------------------------------
# Operator Compliance Checks
# -------------------------------------------------

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
    if op == "range":
        return val["min"] <= oem_value <= val["max"]
    if op == "pass_fail":
        return True  # already filtered upstream

    return False


# -------------------------------------------------
# Quality Score
# -------------------------------------------------

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

    if op == "range":
        mid = (val["min"] + val["max"]) / 2
        spread = (val["max"] - val["min"]) / 2
        return max(0.0, 1 - abs(oem_value - mid) / spread)

    return 1.0


# -------------------------------------------------
# Variant Match
# -------------------------------------------------

def variant_matches(rfp_spec: Dict[str, Any], oem_spec: Dict[str, Any]) -> bool:
    rfp_pair = rfp_spec["variant_scope"]["pair_count"]
    oem_pair = oem_spec["variant_scope"]["pair_count"]

    return rfp_pair is None or rfp_pair == oem_pair


# -------------------------------------------------
# Score One Spec
# -------------------------------------------------

def score_single_spec(
    rfp_spec: Dict[str, Any],
    oem_spec: Dict[str, Any],
    importance_weight: float = 1.0,
    confidence_weight: float = 1.0
) -> Dict[str, Any]:

    if not variant_matches(rfp_spec, oem_spec):
        return None

    oem_value = oem_spec["value"]

    passed = check_compliance(rfp_spec, oem_value)

    if not passed:
        return {
            "spec_key": rfp_spec["spec_key"],
            "passed": False,
            "score": 0.0,
            "reason": "Constraint not satisfied"
        }

    quality = compute_quality_score(rfp_spec, oem_value)

    final_score = quality * importance_weight * confidence_weight

    return {
        "spec_key": rfp_spec["spec_key"],
        "passed": True,
        "score": round(final_score, 4),
        "quality": round(quality, 4),
        "importance_weight": importance_weight
    }


# -------------------------------------------------
# Score SKU
# -------------------------------------------------

def score_sku(
    rfp_specs: List[Dict[str, Any]],
    oem_specs: List[Dict[str, Any]],
    reject_on_mandatory_fail: bool = True
) -> Tuple[str, float, List[Dict[str, Any]]]:

    results = []
    total_score = 0.0
    max_score = 0.0

    for rfp in rfp_specs:
        matched = [
            o for o in oem_specs
            if o["spec_key"] == rfp["spec_key"]
        ]

        if not matched:
            if rfp["mandatory"]:
                return "REJECTED", 0.0, []
            continue

        spec_result = score_single_spec(rfp, matched[0])

        if spec_result is None:
            continue

        if not spec_result["passed"] and rfp["mandatory"]:
            return "REJECTED", 0.0, []

        results.append(spec_result)

        total_score += spec_result["score"]
        max_score += spec_result.get("importance_weight", 1.0)

    final_score = round(total_score / max_score, 4) if max_score else 0.0

    return "ACCEPTED", final_score, results

if __name__ == "__main__":
    with open("oem_datasheets/normalized_oem.json") as f:
        oem_normalized_specs = json.load(f)

    with open("outputs/enforced_normalized_specs.json", "w") as f:
        normalized_rfp_specs = json.load(f)
    
    status, score, breakdown = score_sku(
        rfp_specs=normalized_rfp_specs,
        oem_specs=oem_normalized_specs
    )

    print(status)       # ACCEPTED / REJECTED
    print(score)        # 0.0 – 1.0
    print(breakdown)    # per-spec explainability

    print("✅ Scope normalized successfully")
