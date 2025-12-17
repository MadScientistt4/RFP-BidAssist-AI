"""
enforce_normalized_specs.py

Applies final enforcement rules on normalized RFP technical specs:
1. Enforce operator for every spec
2. Canonicalize units
3. Deduplicate global specs
4. Normalize test condition ranges
"""
import json
from copy import deepcopy
from typing import List, Dict, Any

# -----------------------------
# Unit Canonicalization Map
# -----------------------------
UNIT_MAP = {
    "Ohms/ km": "ohm_per_km",
    "ohms/km": "ohm_per_km",
    "Ohms/km": "ohm_per_km",
    "MΩ-KM": "megaohm_per_km",
    "M.ohms/km": "megaohm_per_km",
    "MΩ-KM": "megaohm_per_km",
    "KV DC": "kv_dc",
    "KV dc": "kv_dc",
    "KV RMS": "kv_rms",
    "kV RMS": "kv_rms",
    "PF": "pf",
    "pF/Km": "pf_per_km",
    "pF/km": "pf_per_km",
    "dB/Km": "db_per_km",
    "dB/km": "db_per_km",
    "mm": "mm",
    "%": "percent",
    "nF/km" : "nf_per_km",
    "avg/Individual" : "ratio"

}

# -----------------------------
# Operator Enforcement
# -----------------------------
def enforce_operator(spec: Dict[str, Any]) -> None:
    value = spec.get("value", {})

    if spec.get("operator"):
        return

    if value.get("exact") is not None:
        spec["operator"] = "=="
    elif value.get("min") is not None and value.get("max") is not None:
        spec["operator"] = "between"
    elif value.get("min") is not None:
        spec["operator"] = ">="
    elif value.get("max") is not None:
        spec["operator"] = "<="
    else:
        spec["operator"] = "unspecified"


# -----------------------------
# Unit Canonicalization
# -----------------------------
def canonicalize_unit(spec: Dict[str, Any]) -> None:
    unit = spec.get("unit")
    if unit in UNIT_MAP:
        spec["unit"] = UNIT_MAP[unit]


# -----------------------------
# Test Condition Normalization
# -----------------------------
def normalize_test_conditions(spec: Dict[str, Any]) -> None:
    test_conditions = spec.get("test_conditions", {})

    normalized = {}
    for key, value in test_conditions.items():
        if not isinstance(value, list) or len(value) != 2:
            continue

        lo, hi = value

        # Drop None-None ranges
        if lo is None and hi is None:
            continue

        # Single value normalization
        if lo is not None and hi is None:
            normalized[key] = [lo, lo]
        elif lo is None and hi is not None:
            normalized[key] = [hi, hi]
        else:
            normalized[key] = [lo, hi]

    spec["test_conditions"] = normalized


# -----------------------------
# Deduplicate Global Specs
# -----------------------------
def deduplicate_global_specs(specs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    global_specs = {}
    final_specs = []

    for spec in specs:
        key = spec["spec_key"]

        if spec["applies_to"] == "all_variants":
            global_specs[key] = spec
            final_specs.append(spec)
            continue

        # specific variant
        global_spec = global_specs.get(key)
        if not global_spec:
            final_specs.append(spec)
            continue

        # compare values
        if spec.get("value") == global_spec.get("value") and spec.get("operator") == global_spec.get("operator"):
            continue  # redundant
        else:
            final_specs.append(spec)

    return final_specs


# -----------------------------
# Main Enforcement Pipeline
# -----------------------------
def enforce_all(specs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    enforced = deepcopy(specs)

    for spec in enforced:
        enforce_operator(spec)
        canonicalize_unit(spec)
        normalize_test_conditions(spec)

    enforced = deduplicate_global_specs(enforced)

    return enforced


# -----------------------------
# Test / Demo
# -----------------------------
def main():
    from pprint import pprint

    with open("outputs/normalize_specs_llm.json", "r", encoding="utf-8") as f:
        payload = json.load(f)

    sample_specs = payload["data"]

    enforced = enforce_all(sample_specs)

    with open("outputs/enforced_normalized_specs.json", "w", encoding="utf-8") as f:
        json.dump(
            {"data": enforced},
            f,
            indent=2
        )

if __name__ == "__main__":
    main()
