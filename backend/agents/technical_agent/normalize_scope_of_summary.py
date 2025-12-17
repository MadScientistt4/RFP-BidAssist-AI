# backend/agents/technical_agent/normalize_scope_of_summary.py

from typing import Dict, Any, List
import json


class ScopeNormalizer:
    def __init__(self, scope_data: Dict[str, Any]):
        self.scope = scope_data

    def normalize(self) -> Dict[str, Any]:
        normalized = {
            "activities": [],
            "product_families": [],
            "quantities": [],
            "standards_required": [],
            "mandatory": True
        }

        product_lines: List[Dict[str, Any]] = self.scope.get("product_lines", [])

        for line in product_lines:
            family_id = line.get("product_line_name")
            if not family_id:
                continue

            normalized["product_families"].append(family_id)

            for product in line.get("products", []):
                normalized["quantities"].append({
                    "family_id": family_id,
                    "variant_id": product.get("product_code"),
                    "pair_count": None,        # REQUIRED canonical field
                    "quantity": product.get("quantity"),
                    "unit": "nos"
                })

        return normalized


# -------------------------------------------------
# PUBLIC FUNCTION
# -------------------------------------------------
def normalize_scope(scope_json: Dict[str, Any]) -> Dict[str, Any]:
    return ScopeNormalizer(scope_json).normalize()


if __name__ == "__main__":
    with open("outputs/scope_of_supply_summary.json") as f:
        scope_data = json.load(f)

    normalized_scope = normalize_scope(scope_data)

    with open("outputs/normalized_scope.json", "w") as f:
        json.dump(normalized_scope, f, indent=2)

    print("✅ Scope normalized successfully")
