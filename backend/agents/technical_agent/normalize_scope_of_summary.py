# agents/technical_agent/normalize_scope_of_summary.py

import re
from typing import Dict, List


class ScopeNormalizer:
    def __init__(self, scope_text: str):
        self.text = scope_text.lower()

    def normalize(self) -> Dict:
        return {
            "activities": self._extract_activities(),
            "product_category": "telecom_cable",
            "quantities": self._extract_quantities(),
            "standards_required": self._extract_standards(),
            "mandatory": True
        }

    def _extract_activities(self) -> List[str]:
        activities = []
        for act in ["supply", "installation", "testing", "commissioning"]:
            if act in self.text:
                activities.append(act)
        return activities

    def _extract_quantities(self) -> Dict:
        pair_match = re.search(r"(\d+)\s*pair", self.text)
        length_match = re.search(r"(\d+)\s*(km|kilometer)", self.text)

        return {
            "pair_count": int(pair_match.group(1)) if pair_match else None,
            "length_km": float(length_match.group(1)) if length_match else None
        }

    def _extract_standards(self) -> List[str]:
        standards = []
        if "dot" in self.text:
            standards.append("DOT")
        if "bs" in self.text:
            standards.append("BS")
        return standards


def normalize_scope(scope_text: str) -> Dict:
    return ScopeNormalizer(scope_text).normalize()

"""import re
import json
from typing import List, Dict, Optional


# =========================
# Canonical Dictionaries
# =========================

CANONICAL_ACTIVITIES = {
    "supply": ["supply", "provide", "procure"],
    "installation": ["install", "installation", "laying", "erection"],
    "testing": ["test", "testing"],
    "commissioning": ["commission", "commissioning"]
}

PRODUCT_CATEGORIES = {
    "telecom_cable": [
        "telecom cable",
        "telephone cable",
        "copper cable",
        "pijf",
        "armoured cable"
    ]
}

STANDARDS_KEYWORDS = {
    "DOT": ["dot", "tec"],
    "BS": ["bs"],
    "IEC": ["iec"]
}

OEM_CONSTRAINT_KEYWORDS = {
    "approved": ["approved oem", "oem shall be approved"],
    "preferred": ["preferred oem"],
    "open": ["any oem", "no oem restriction"]
}


# =========================
# OEM Capability Repository (Synthetic)
# =========================

OEM_CAPABILITIES = {
    "telecom_cable": {
        "max_pair_count": 2400,
        "supported_armouring": ["steel tape", "steel wire"],
        "max_length_km": 500,
        "supported_standards": ["DOT", "BS"]
    }
}


# =========================
# Utility
# =========================

def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()


# =========================
# Scope Normalizer Class
# =========================

class ScopeNormalizer:

    def __init__(self, raw_text: str):
        self.raw_text = raw_text
        self.text = normalize_text(raw_text)

    # ---------- Activity ----------
    def extract_activities(self) -> List[str]:
        activities = []
        for canonical, variants in CANONICAL_ACTIVITIES.items():
            if any(v in self.text for v in variants):
                activities.append(canonical)
        return activities

    # ---------- Product ----------
    def extract_product_category(self) -> Optional[str]:
        for category, keywords in PRODUCT_CATEGORIES.items():
            if any(k in self.text for k in keywords):
                return category
        return None

    # ---------- Quantity ----------
    def extract_quantities(self) -> Dict:
        quantities = {}

        pair_match = re.search(r"(\d+)\s*pair", self.text)
        if pair_match:
            quantities["pair_count"] = int(pair_match.group(1))

        length_km_match = re.search(r"(\d+(\.\d+)?)\s*km", self.text)
        length_m_match = re.search(r"(\d+(\.\d+)?)\s*m(?!m)", self.text)

        if length_km_match:
            quantities["length_km"] = float(length_km_match.group(1))
        elif length_m_match:
            quantities["length_km"] = float(length_m_match.group(1)) / 1000

        return quantities

    # ---------- Standards ----------
    def extract_standards(self) -> List[str]:
        standards = []
        for std, keys in STANDARDS_KEYWORDS.items():
            if any(k in self.text for k in keys):
                standards.append(std)
        return standards

    # ---------- OEM Constraint ----------
    def extract_oem_constraint(self) -> str:
        for constraint, keys in OEM_CONSTRAINT_KEYWORDS.items():
            if any(k in self.text for k in keys):
                return constraint
        return "unspecified"

    # ---------- Mandatory ----------
    def is_mandatory(self) -> bool:
        return any(k in self.text for k in ["shall", "must", "required", "mandatory"])

    # ---------- Normalize ----------
    def normalize(self) -> Dict:
        return {
            "activities": self.extract_activities(),
            "product_category": self.extract_product_category(),
            "quantities": self.extract_quantities(),
            "standards_required": self.extract_standards(),
            "oem_constraint": self.extract_oem_constraint(),
            "mandatory": self.is_mandatory()
        }


# =========================
# OEM Capability Matching
# =========================

class OEMCapabilityMatcher:

    def __init__(self, scope: Dict):
        self.scope = scope
        self.capability = OEM_CAPABILITIES.get(scope["product_category"])

    def match(self) -> Dict:
        if not self.capability:
            return {
                "capable": False,
                "reason": "No OEM capability for product category"
            }

        issues = []

        # Pair count
        pair_count = self.scope["quantities"].get("pair_count")
        if pair_count and pair_count > self.capability["max_pair_count"]:
            issues.append("Pair count exceeds OEM capability")

        # Length
        length_km = self.scope["quantities"].get("length_km")
        if length_km and length_km > self.capability["max_length_km"]:
            issues.append("Cable length exceeds OEM capability")

        # Standards
        for std in self.scope["standards_required"]:
            if std not in self.capability["supported_standards"]:
                issues.append(f"Standard {std} not supported")

        return {
            "capable": len(issues) == 0,
            "issues": issues
        }


# =========================
# MAIN FUNCTION
# =========================

def main():
    scope_text = """
"""Supply, installation, testing and commissioning of
    200 pair armoured copper telecom cable of length 120 km
    conforming to DOT TEC standards.
    OEM shall be approved."""
"""

    normalizer = ScopeNormalizer(scope_text)
    normalized_scope = normalizer.normalize()

    matcher = OEMCapabilityMatcher(normalized_scope)
    capability_result = matcher.match()

    output = {
        "normalized_scope": normalized_scope,
        "oem_capability_match": capability_result
    }

    print(json.dumps(output, indent=2))


# =========================
# Entry Point
# =========================

if __name__ == "__main__":
    main()
"""