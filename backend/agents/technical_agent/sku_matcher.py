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

        required_variants = self.scope.get("quantities", [])
        required_standards = set(self.scope.get("standards_required", []))

        for product in self.products:
            product_pair_count = product.get("pair_count", 0)
            product_standards = set(product.get("standards_supported", []))

            # --- Standards check ---
            if required_standards and not required_standards.issubset(product_standards):
                continue

            # --- Pair count check (match ANY variant) ---
            pair_match = False
            for variant in required_variants:
                required_pairs = variant.get("pair_count")
                if required_pairs and product_pair_count >= required_pairs:
                    pair_match = True
                    break

            if not pair_match:
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
