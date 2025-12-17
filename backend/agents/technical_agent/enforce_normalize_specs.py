"""
enforce_normalized_specs.py

Applies final enforcement rules on normalized RFP technical specs:
1. Enforce operator for every spec
2. Canonicalize units
3. Deduplicate global specs
4. Normalize test condition ranges
"""

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

    # Minimal test example
    sample_specs = [
  {
    "spec_key": "conductor_diameter",
    "value": {
      "min": None,
      "max": None,
      "exact": 0.5
    },
    "unit": "mm",
    "operator": None,
    "test_conditions": {},
    "tolerance": None,
    "mandatory": True,
    "applies_to": "all_variants",
    "variant_scope": {
      "pair_count": None,
      "variant_id": None
    },
    "source_text": "0.5mm diameter"
  },
  {
    "spec_key": "armouring_thickness",
    "value": {
      "min": None,
      "max": None,
      "exact": 0.5
    },
    "unit": "mm",
    "operator": None,
    "test_conditions": {},
    "tolerance": 0.1,
    "mandatory": True,
    "applies_to": "all_variants",
    "variant_scope": {
      "pair_count": None,
      "variant_id": None
    },
    "source_text": "0.5mm \u00b110% thickness"
  },
  {
    "spec_key": "conductor_resistance",
    "value": {
      "min": None,
      "max": None,
      "exact": 86.0
    },
    "unit": "Ohms/ km",
    "operator": None,
    "test_conditions": {
      "frequency_hz": [
        None,
        None
      ],
      "temperature_c": [
        None,
        None
      ]
    },
    "tolerance": 6.0,
    "mandatory": True,
    "applies_to": "all_variants",
    "variant_scope": {
      "pair_count": None,
      "variant_id": None
    },
    "source_text": "Conductor resistance (86 Ohms/ km \u00b1 6 Ohms/ km)"
  },
  {
    "spec_key": "resistance_unbalance",
    "value": {
      "min": None,
      "max": None,
      "exact": 1.0
    },
    "unit": "avg/Individual",
    "operator": None,
    "test_conditions": {},
    "tolerance": 2.5,
    "mandatory": True,
    "applies_to": "all_variants",
    "variant_scope": {
      "pair_count": None,
      "variant_id": None
    },
    "source_text": "Resistance unbalance (1 (avg) / 2.5(Individual))"
  },
  {
    "spec_key": "mutual_capacitance",
    "value": {
      "min": None,
      "max": None,
      "exact": 52.0
    },
    "unit": "nF/km",
    "operator": None,
    "test_conditions": {
      "frequency_hz": [
        800,
        1000
      ],
      "temperature_c": [
        None,
        None
      ]
    },
    "tolerance": 3.0,
    "mandatory": True,
    "applies_to": "all_variants",
    "variant_scope": {
      "pair_count": None,
      "variant_id": None
    },
    "source_text": "Mutual capacitance (52 \u00b1 3 nF/km at 800 to 1000 Hz)"
  },
  {
    "spec_key": "capacitance_unbalance_pair_to_pair",
    "value": {
      "min": None,
      "max": 50.0,
      "exact": None
    },
    "unit": "pF/Km",
    "operator": "<=",
    "test_conditions": {
      "frequency_hz": [
        800,
        1000
      ],
      "temperature_c": [
        None,
        None
      ]
    },
    "tolerance": None,
    "mandatory": True,
    "applies_to": "all_variants",
    "variant_scope": {
      "pair_count": None,
      "variant_id": None
    },
    "source_text": "Capacitance unbalance (Pair to Pair) (\u2264 50 pF/Km (average) @800- 1000Hz)"
  },
  {
    "spec_key": "capacitance_unbalance_pair_to_ground",
    "value": {
      "min": None,
      "max": 750.0,
      "exact": None
    },
    "unit": "pF/Km",
    "operator": "<=",
    "test_conditions": {
      "frequency_hz": [
        800,
        1000
      ],
      "temperature_c": [
        None,
        None
      ]
    },
    "tolerance": None,
    "mandatory": True,
    "applies_to": "all_variants",
    "variant_scope": {
      "pair_count": None,
      "variant_id": None
    },
    "source_text": "Capacitance unbalance (Pair to Gnd) (\u2264 750 pF/Km (average) @800- 1000Hz)"
  },
  {
    "spec_key": "dielectric_strength_between_conductors",
    "value": {
      "min": None,
      "max": None,
      "exact": 2.4
    },
    "unit": "KV DC",
    "operator": None,
    "test_conditions": {
      "frequency_hz": [
        None,
        None
      ],
      "temperature_c": [
        None,
        None
      ]
    },
    "tolerance": None,
    "mandatory": True,
    "applies_to": "all_variants",
    "variant_scope": {
      "pair_count": None,
      "variant_id": None
    },
    "source_text": "Dielectric strength (High voltage) between conductors (At 2.4 KV DC for 3 Sec.)"
  },
  {
    "spec_key": "dielectric_strength_between_conductors_and_shield",
    "value": {
      "min": None,
      "max": None,
      "exact": 5.0
    },
    "unit": "KV DC",
    "operator": None,
    "test_conditions": {
      "frequency_hz": [
        None,
        None
      ],
      "temperature_c": [
        None,
        None
      ]
    },
    "tolerance": None,
    "mandatory": True,
    "applies_to": "all_variants",
    "variant_scope": {
      "pair_count": None,
      "variant_id": None
    },
    "source_text": "Dielectric strength (High voltage) between all conductors and shield (At 5.0 KV DC for 3 Sec.)"
  },
  {
    "spec_key": "insulation_resistance_conductor_to_conductor",
    "value": {
      "min": 5000.0,
      "max": None,
      "exact": None
    },
    "unit": "M\u2126-KM",
    "operator": ">=",
    "test_conditions": {
      "frequency_hz": [
        None,
        None
      ],
      "temperature_c": [
        None,
        None
      ]
    },
    "tolerance": None,
    "mandatory": True,
    "applies_to": "all_variants",
    "variant_scope": {
      "pair_count": None,
      "variant_id": None
    },
    "source_text": "Insulation resistance (Min 5000 M\u2126-KM at 500 V DC-1 Min (Conductor to conductor))"
  },
  {
    "spec_key": "insulation_resistance_conductor_to_shield",
    "value": {
      "min": 5000.0,
      "max": None,
      "exact": None
    },
    "unit": "M\u2126-KM",
    "operator": ">=",
    "test_conditions": {
      "frequency_hz": [
        None,
        None
      ],
      "temperature_c": [
        None,
        None
      ]
    },
    "tolerance": None,
    "mandatory": True,
    "applies_to": "all_variants",
    "variant_scope": {
      "pair_count": None,
      "variant_id": None
    },
    "source_text": "Insulation resistance (Min 5000 M\u2126-KM at 500 V DC-1 Min (Conductor to shield))"
  },
  {
    "spec_key": "dielectric_strength_sheath",
    "value": {
      "min": None,
      "max": None,
      "exact": 17.0
    },
    "unit": "KV dc",
    "operator": None,
    "test_conditions": {},
    "tolerance": None,
    "mandatory": True,
    "applies_to": "all_variants",
    "variant_scope": {
      "pair_count": None,
      "variant_id": None
    },
    "source_text": "Dielectric strength of the sheath (17KV dc or at 11KV RMS ac for sheath thickness 2.0 to 2.4mm)"
  },
  {
    "spec_key": "equal_level_far_end_crosstalk",
    "value": {
      "min": 55.0,
      "max": None,
      "exact": None
    },
    "unit": "dB/Km",
    "operator": ">=",
    "test_conditions": {
      "frequency_hz": [
        150000,
        None
      ],
      "temperature_c": [
        None,
        None
      ]
    },
    "tolerance": None,
    "mandatory": True,
    "applies_to": "all_variants",
    "variant_scope": {
      "pair_count": None,
      "variant_id": None
    },
    "source_text": "Equal level far end cross talk (Better than 55dB/Km (individual value))"
  },
  {
    "spec_key": "near_end_crosstalk",
    "value": {
      "min": 55.0,
      "max": None,
      "exact": None
    },
    "unit": "dB/Km",
    "operator": ">=",
    "test_conditions": {
      "frequency_hz": [
        150000,
        None
      ],
      "temperature_c": [
        None,
        None
      ]
    },
    "tolerance": None,
    "mandatory": True,
    "applies_to": "all_variants",
    "variant_scope": {
      "pair_count": None,
      "variant_id": None
    },
    "source_text": "Near end cross talk (Better than 55dB/Km (individual value))"
  },
  {
    "spec_key": "attenuation",
    "value": {
      "min": None,
      "max": 8.25,
      "exact": None
    },
    "unit": "dB/Km",
    "operator": "<=",
    "test_conditions": {
      "frequency_hz": [
        None,
        None
      ],
      "temperature_c": [
        20,
        None
      ]
    },
    "tolerance": None,
    "mandatory": True,
    "applies_to": "all_variants",
    "variant_scope": {
      "pair_count": None,
      "variant_id": None
    },
    "source_text": "Attenuation (8.25 dB/Km (maximum average) at 20 deg C)"
  },
  {
    "spec_key": "diameter_over_sheath",
    "value": {
      "min": None,
      "max": 37.5,
      "exact": None
    },
    "unit": "mm",
    "operator": "<=",
    "test_conditions": {},
    "tolerance": None,
    "mandatory": True,
    "applies_to": "specific_variant",
    "variant_scope": {
      "pair_count": 200,
      "variant_id": None
    },
    "source_text": "Diameter over sheath: Shall not exceed 37.5mm (Table-7 of TEC GR/CUG-01/03 Aug-2003)"
  },
  {
    "spec_key": "minimum_sheath_thickness",
    "value": {
      "min": 1.62,
      "max": None,
      "exact": None
    },
    "unit": "mm",
    "operator": ">=",
    "test_conditions": {},
    "tolerance": None,
    "mandatory": True,
    "applies_to": "specific_variant",
    "variant_scope": {
      "pair_count": 200,
      "variant_id": None
    },
    "source_text": "Minimum sheath thickness: Not less than 75% of nominal specified (As per Table-6 of TEC GR/CUG-01/03 Aug-2003); 1.62 mm (min) and 2.2 mm (nom) for 200P cable"
  },
  {
    "spec_key": "jacket_thickness",
    "value": {
      "min": 1.4,
      "max": None,
      "exact": None
    },
    "unit": "mm",
    "operator": ">=",
    "test_conditions": {},
    "tolerance": None,
    "mandatory": True,
    "applies_to": "all_variants",
    "variant_scope": {
      "pair_count": None,
      "variant_id": None
    },
    "source_text": "Jacket thickness: Shall not be less than 1.4mm"
  },
  {
    "spec_key": "diameter_over_jacket",
    "value": {
      "min": None,
      "max": 45.5,
      "exact": None
    },
    "unit": "mm",
    "operator": "<=",
    "test_conditions": {},
    "tolerance": None,
    "mandatory": True,
    "applies_to": "specific_variant",
    "variant_scope": {
      "pair_count": 200,
      "variant_id": None
    },
    "source_text": "Diameter over Jacket: For 200P, shall not exceed 45.5mm"
  },
  {
    "spec_key": "diameter_over_sheath",
    "value": {
      "min": None,
      "max": 28.0,
      "exact": None
    },
    "unit": "mm",
    "operator": "<=",
    "test_conditions": {},
    "tolerance": None,
    "mandatory": True,
    "applies_to": "specific_variant",
    "variant_scope": {
      "pair_count": 100,
      "variant_id": None
    },
    "source_text": "Diameter over sheath: Shall not exceed 28mm (Table-7 of TEC GR/CUG-01/03 Aug-2003)"
  },
  {
    "spec_key": "minimum_sheath_thickness",
    "value": {
      "min": 1.5,
      "max": None,
      "exact": None
    },
    "unit": "mm",
    "operator": ">=",
    "test_conditions": {},
    "tolerance": None,
    "mandatory": True,
    "applies_to": "specific_variant",
    "variant_scope": {
      "pair_count": 100,
      "variant_id": None
    },
    "source_text": "Minimum sheath thickness: Not less than 75% of nominal specified (As per Table-6 of TEC GR/CUG-01/03 Aug-2003); 1.50 mm (min) and 2.0 mm (nom) for 100P cable"
  },
  {
    "spec_key": "diameter_over_jacket",
    "value": {
      "min": None,
      "max": 36.0,
      "exact": None
    },
    "unit": "mm",
    "operator": "<=",
    "test_conditions": {},
    "tolerance": None,
    "mandatory": True,
    "applies_to": "specific_variant",
    "variant_scope": {
      "pair_count": 100,
      "variant_id": None
    },
    "source_text": "Diameter over Jacket: For 100P, shall not exceed 36mm"
  },
  {
    "spec_key": "diameter_over_sheath",
    "value": {
      "min": None,
      "max": 22.0,
      "exact": None
    },
    "unit": "mm",
    "operator": "<=",
    "test_conditions": {},
    "tolerance": None,
    "mandatory": True,
    "applies_to": "specific_variant",
    "variant_scope": {
      "pair_count": 50,
      "variant_id": None
    },
    "source_text": "Diameter over sheath: Shall not exceed 22mm (Table-7 of TEC GR/CUG-01/03 Aug-2003)"
  },
  {
    "spec_key": "minimum_sheath_thickness",
    "value": {
      "min": 1.5,
      "max": None,
      "exact": None
    },
    "unit": "mm",
    "operator": ">=",
    "test_conditions": {},
    "tolerance": None,
    "mandatory": True,
    "applies_to": "specific_variant",
    "variant_scope": {
      "pair_count": 50,
      "variant_id": None
    },
    "source_text": "Minimum sheath thickness: Not less than 75% of nominal specified (As per Table-6 of TEC GR/CUG-01/03 Aug-2003); 1.50 mm (min) and 2.0 mm (nom) for 50P cable"
  },
  {
    "spec_key": "diameter_over_jacket",
    "value": {
      "min": None,
      "max": 29.0,
      "exact": None
    },
    "unit": "mm",
    "operator": "<=",
    "test_conditions": {},
    "tolerance": None,
    "mandatory": True,
    "applies_to": "specific_variant",
    "variant_scope": {
      "pair_count": 50,
      "variant_id": None
    },
    "source_text": "Diameter over Jacket: For 50P, shall not exceed 29mm"
  },
  {
    "spec_key": "diameter_over_sheath",
    "value": {
      "min": None,
      "max": 17.0,
      "exact": None
    },
    "unit": "mm",
    "operator": "<=",
    "test_conditions": {},
    "tolerance": None,
    "mandatory": True,
    "applies_to": "specific_variant",
    "variant_scope": {
      "pair_count": 20,
      "variant_id": None
    },
    "source_text": "Diameter over sheath: Shall not exceed 17mm (Table-7 of TEC GR/CUG-01/03 Aug-2003)"
  },
  {
    "spec_key": "minimum_sheath_thickness",
    "value": {
      "min": 1.5,
      "max": None,
      "exact": None
    },
    "unit": "mm",
    "operator": ">=",
    "test_conditions": {},
    "tolerance": None,
    "mandatory": True,
    "applies_to": "specific_variant",
    "variant_scope": {
      "pair_count": 20,
      "variant_id": None
    },
    "source_text": "Minimum sheath thickness: Not less than 75% of nominal specified (As per Table-6 of TEC GR/CUG-01/03 Aug-2003); 1.50 mm (min) and 2.0 mm (nom) for 20P cable"
  },
  {
    "spec_key": "diameter_over_jacket",
    "value": {
      "min": None,
      "max": 24.0,
      "exact": None
    },
    "unit": "mm",
    "operator": "<=",
    "test_conditions": {},
    "tolerance": None,
    "mandatory": True,
    "applies_to": "specific_variant",
    "variant_scope": {
      "pair_count": 20,
      "variant_id": None
    },
    "source_text": "Diameter over Jacket: For 20P, shall not exceed 24mm"
  },
  {
    "spec_key": "diameter_over_sheath",
    "value": {
      "min": None,
      "max": 11.0,
      "exact": None
    },
    "unit": "mm",
    "operator": "<=",
    "test_conditions": {},
    "tolerance": None,
    "mandatory": True,
    "applies_to": "specific_variant",
    "variant_scope": {
      "pair_count": 10,
      "variant_id": None
    },
    "source_text": "Diameter over sheath: Shall not exceed 11mm (Table-7 of TEC GR/CUG-01/03 Aug-2003)"
  },
  {
    "spec_key": "minimum_sheath_thickness",
    "value": {
      "min": 1.5,
      "max": None,
      "exact": None
    },
    "unit": "mm",
    "operator": ">=",
    "test_conditions": {},
    "tolerance": None,
    "mandatory": True,
    "applies_to": "specific_variant",
    "variant_scope": {
      "pair_count": 10,
      "variant_id": None
    },
    "source_text": "Minimum sheath thickness: Not less than 75% of nominal specified (As per Table-6 of TEC GR/CUG-01/03 Aug-2003); 1.50 mm (min) and 2.0 mm (nom) for 10P cable"
  },
  {
    "spec_key": "diameter_over_jacket",
    "value": {
      "min": None,
      "max": 20.2,
      "exact": None
    },
    "unit": "mm",
    "operator": "<=",
    "test_conditions": {},
    "tolerance": None,
    "mandatory": True,
    "applies_to": "specific_variant",
    "variant_scope": {
      "pair_count": 10,
      "variant_id": None
    },
    "source_text": "Diameter over Jacket: For 10P, shall not exceed 20.2mm"
  },
  {
    "spec_key": "armouring_size",
    "value": {
      "min": 0.9,
      "max": None,
      "exact": None
    },
    "unit": "mm",
    "operator": ">=",
    "test_conditions": {},
    "tolerance": None,
    "mandatory": True,
    "applies_to": "specific_variant",
    "variant_scope": {
      "pair_count": 5,
      "variant_id": None
    },
    "source_text": "armouring: G S Round wire (IS: 3975), Single layer, \u2265 0.9 mm size"
  },
  {
    "spec_key": "lay_length_of_twisted_pair",
    "value": {
      "min": None,
      "max": 80.0,
      "exact": None
    },
    "unit": "mm",
    "operator": "<=",
    "test_conditions": {},
    "tolerance": None,
    "mandatory": True,
    "applies_to": "specific_variant",
    "variant_scope": {
      "pair_count": 5,
      "variant_id": None
    },
    "source_text": "Lay length of Twisted pair: \u2264 80mm"
  },
  {
    "spec_key": "inner_sheath_thickness",
    "value": {
      "min": 0.65,
      "max": None,
      "exact": None
    },
    "unit": "mm",
    "operator": ">=",
    "test_conditions": {},
    "tolerance": None,
    "mandatory": True,
    "applies_to": "specific_variant",
    "variant_scope": {
      "pair_count": 5,
      "variant_id": None
    },
    "source_text": "Inner sheath thickness: Minimum 0.65mm"
  },
  {
    "spec_key": "outer_sheath_thickness",
    "value": {
      "min": 1.24,
      "max": None,
      "exact": None
    },
    "unit": "mm",
    "operator": ">=",
    "test_conditions": {},
    "tolerance": None,
    "mandatory": True,
    "applies_to": "specific_variant",
    "variant_scope": {
      "pair_count": 5,
      "variant_id": None
    },
    "source_text": "Outer Sheath thickness: Minimum 1.24mm"
  },
  {
    "spec_key": "nominal_diameter_of_overall_cable",
    "value": {
      "min": None,
      "max": None,
      "exact": 11.5
    },
    "unit": "mm",
    "operator": None,
    "test_conditions": {},
    "tolerance": 2.0,
    "mandatory": True,
    "applies_to": "specific_variant",
    "variant_scope": {
      "pair_count": 5,
      "variant_id": None
    },
    "source_text": "Nominal diameter of overall cable: 11.5 \u00b1 2mm"
  },
  {
    "spec_key": "conductor_resistance",
    "value": {
      "min": None,
      "max": None,
      "exact": 86.0
    },
    "unit": "ohms/km",
    "operator": None,
    "test_conditions": {},
    "tolerance": 6.0,
    "mandatory": True,
    "applies_to": "specific_variant",
    "variant_scope": {
      "pair_count": 5,
      "variant_id": None
    },
    "source_text": "Conductor Resistance (86 \u00b1 6 ohms/km)"
  },
  {
    "spec_key": "insulation_resistance",
    "value": {
      "min": 50.0,
      "max": None,
      "exact": None
    },
    "unit": "M.ohms/km",
    "operator": ">=",
    "test_conditions": {},
    "tolerance": None,
    "mandatory": True,
    "applies_to": "specific_variant",
    "variant_scope": {
      "pair_count": 5,
      "variant_id": None
    },
    "source_text": "Min Insulation resistance (50M.ohms/km)"
  },
  {
    "spec_key": "high_voltage_test",
    "value": {
      "min": None,
      "max": None,
      "exact": 2.0
    },
    "unit": "KV RMS",
    "operator": None,
    "test_conditions": {
      "frequency_hz": [
        None,
        None
      ],
      "temperature_c": [
        None,
        None
      ]
    },
    "tolerance": None,
    "mandatory": True,
    "applies_to": "specific_variant",
    "variant_scope": {
      "pair_count": 5,
      "variant_id": None
    },
    "source_text": "High Voltage test (2KV RMS for 1 minute)"
  },
  {
    "spec_key": "capacitance_unbalance_pair_to_pair",
    "value": {
      "min": None,
      "max": 230.0,
      "exact": None
    },
    "unit": "PF",
    "operator": "<=",
    "test_conditions": {},
    "tolerance": None,
    "mandatory": True,
    "applies_to": "specific_variant",
    "variant_scope": {
      "pair_count": 5,
      "variant_id": None
    },
    "source_text": "Capacitance Unbalance (pair to pair) (Shall not exceed 230PF)"
  }
  
]
    print("\n--- BEFORE ENFORCEMENT ---")

    enforced = enforce_all(sample_specs)

    print("\n--- AFTER ENFORCEMENT ---")
    pprint(enforced)

if __name__ == "__main__":
    main()
