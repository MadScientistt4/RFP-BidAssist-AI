"""import json
import re
from typing import List, Dict

normalized_scope = {
        "activities": ["supply", "installation", "testing", "commissioning"],
        "product_category": "telecom_cable",
        "quantities": {
            "pair_count": 200,
            "length_km": 120.0
        },
        "standards_required": ["DOT"],
        "oem_constraint": "approved",
        "mandatory": True
    }
class SKUMatcher:

    def __init__(
        self,
        normalized_scope: Dict,
        oem_products: List[Dict],
        oem_product_specs: List[Dict]
    ):
        self.scope = normalized_scope
        self.products = oem_products
        self.product_specs = oem_product_specs

    # ----------------------------
    # STEP 1: Filter eligible SKUs
    # ----------------------------
    def filter_eligible_skus(self) -> List[Dict]:
        eligible = []

        required_pair_count = self.scope["quantities"].get("pair_count")
        required_standards = set(self.scope["standards_required"])

        for product in self.products:
            # Pair count check
            if required_pair_count and product.get("pair_count", 0) < required_pair_count:
                continue

            # Standards check
            if required_standards:
                if not required_standards.issubset(set(product.get("standards_supported", []))):
                    continue

            eligible.append(product)

        return eligible

    # --------------------------------
    # STEP 2: Spec Match Calculation
    # --------------------------------
    def calculate_spec_match(self, sku: str, rfp_specs: List[Dict]) -> float:
        sku_specs = [
            s for s in self.product_specs if s["product_sku"] == sku
        ]

        if not rfp_specs:
            return 0.0

        matched = 0

        for rfp_spec in rfp_specs:
            for sku_spec in sku_specs:
                if self._specs_match(rfp_spec, sku_spec):
                    matched += 1
                    break

        return round((matched / len(rfp_specs)) * 100, 2)

    # --------------------------------
    # Spec Comparison Logic
    # --------------------------------
    def _specs_match(self, rfp_spec: Dict, sku_spec: Dict) -> bool:
        if rfp_spec["spec_key"] != sku_spec["spec_name"]:
            return False

        rfp_val = self._numeric_value(rfp_spec["value"])
        sku_val = self._numeric_value(sku_spec["spec_value"])

        if rfp_val is None or sku_val is None:
            return False

        operator = rfp_spec.get("operator", "<=")

        if operator == "<=":
            return sku_val <= rfp_val
        if operator == ">=":
            return sku_val >= rfp_val
        if operator == "==":
            return sku_val == rfp_val

        return False

    def _numeric_value(self, value: str) -> float:
        match = re.search(r"[\d.]+", value)
        return float(match.group()) if match else None

    # --------------------------------
    # STEP 3: Rank and Recommend
    # --------------------------------
    def recommend_top_skus(self, rfp_specs: List[Dict], top_n: int = 3) -> List[Dict]:
        eligible_skus = self.filter_eligible_skus()

        recommendations = []

        for product in eligible_skus:
            score = self.calculate_spec_match(
                product["product_sku"],
                rfp_specs
            )

            recommendations.append({
                "product_sku": product["product_sku"],
                "product_family": product["product_family"],
                "spec_match_percent": score
            })

        recommendations.sort(
            key=lambda x: x["spec_match_percent"],
            reverse=True
        )

        return recommendations[:top_n]


def main():
    with open("oem_datasheets/oem_products.json") as f:
        oem_products = json.load(f)
    with open("oem_datasheets/oem_product_sku.json") as f:
        oem_product_specs = json.load(f)
    with open("oem_datasheets/oem_product_sku.json") as f:
        oem_product_specs = json.load(f)
    matcher = SKUMatcher(
        normalized_scope,
        oem_products,
        oem_product_specs
    )

    top_3 = matcher.recommend_top_skus(rfp_specs)

    # -----------------------------
    # Output
    # -----------------------------
    print("\n🔹 TOP SKU RECOMMENDATIONS 🔹\n")
    print(json.dumps(top_3, indent=2))


if __name__ == "__main__":
    main()"""

# agents/technical_agent/sku_matcher.py

import re
from typing import List, Dict


class SKUMatcher:
    def __init__(self, normalized_scope, oem_products, oem_product_specs):
        self.scope = normalized_scope
        self.products = oem_products
        self.product_specs = oem_product_specs

    # ----------------------------
    # OEM Capability + SKU Filter
    # ----------------------------
    def filter_eligible_skus(self) -> List[Dict]:
        eligible = []

        required_pairs = self.scope["quantities"].get("pair_count")
        required_standards = set(self.scope["standards_required"])

        for product in self.products:
            if required_pairs and product["pair_count"] < required_pairs:
                continue

            if required_standards:
                if not required_standards.issubset(set(product["standards_supported"])):
                    continue

            eligible.append(product)

        return eligible

    # ----------------------------
    # Spec Match Matrix
    # ----------------------------
    def build_spec_match_matrix(self, rfp_specs: List[Dict]) -> Dict:
        matrix = {}

        for product in self.filter_eligible_skus():
            sku = product["product_sku"]
            matrix[sku] = {}

            sku_specs = [
                s for s in self.product_specs if s["product_sku"] == sku
            ]

            for rfp_spec in rfp_specs:
                matrix[sku][rfp_spec["spec_key"]] = self._spec_match(
                    rfp_spec, sku_specs
                )

        return matrix

    def _spec_match(self, rfp_spec, sku_specs) -> Dict:
        for sku_spec in sku_specs:
            if sku_spec["spec_name"] == rfp_spec["spec_key"]:
                rfp_val = self._num(rfp_spec["value"])
                sku_val = self._num(sku_spec["spec_value"])

                return {
                    "rfp": rfp_spec["value"],
                    "sku": sku_spec["spec_value"],
                    "pass": sku_val <= rfp_val
                }

        return {"rfp": rfp_spec["value"], "sku": None, "pass": False}

    def _num(self, value: str) -> float:
        match = re.search(r"[\d.]+", value)
        return float(match.group()) if match else float("inf")

    # ----------------------------
    # Ranking
    # ----------------------------
    def recommend_top_skus(self, rfp_specs: List[Dict], top_n=3):
        matrix = self.build_spec_match_matrix(rfp_specs)
        scores = []

        for sku, spec_results in matrix.items():
            passed = sum(1 for s in spec_results.values() if s["pass"])
            total = len(spec_results)
            score = round((passed / total) * 100, 2)

            scores.append({
                "product_sku": sku,
                "spec_match_percent": score
            })

        scores.sort(key=lambda x: x["spec_match_percent"], reverse=True)
        return scores[:top_n], matrix
