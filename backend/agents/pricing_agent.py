import json
from pathlib import Path
from typing import Dict, Any


class PricingAgent:
    def __init__(
        self,
        test_price_chart_path: str,
        material_price_chart_path: str
    ):
        self.test_prices = self._load_and_index_test_prices(test_price_chart_path)
        self.material_prices = self._load_and_index_material_prices(material_price_chart_path)

    def _load_and_index_test_prices(self, path: str) -> Dict[str, float]:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        return {
            entry["test_name"]: entry["synthetic_price"]
            for entry in data.get("test_price_table", [])
        }

    def _load_and_index_material_prices(self, path: str) -> Dict[str, float]:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        return {
            entry["sku"]: entry["unit_price"]
            for entry in data.get("prices", [])
        }

    def _resolve_variant_sku(self, base_sku: str, item_name: str) -> str:
        name = item_name.lower()

        if "pijf" in name:
            if "200 pair" in name:
                return "TOPCABLE-PIJF-200P-0.5-ARM"
            if "100 pair" in name:
                return "TOPCABLE-PIJF-100P-0.5-ARM"
            if "50 pair" in name:
                return "TOPCABLE-PIJF-50P-0.5-ARM"
            if "20 pair" in name:
                return "TOPCABLE-PIJF-20P-0.5-ARM"
            if "10 pair" in name:
                return "TOPCABLE-PIJF-10P-0.5-ARM"

        if "frls" in name:
            if "5 pair" in name:
                return "TOPCABLE-FRLS-5P-0.5-ARM"
            if "10 pair" in name:
                return "TOPCABLE-FRLS-10P-0.5-ARM"
            if "20 pair" in name:
                return "TOPCABLE-FRLS-20P-0.5-ARM"

        return base_sku

    def generate_pricing_table(
        self,
        pricing_summary: Dict[str, Any]
    ) -> Dict[str, Any]:

        priced_items = []

        for item in pricing_summary.get("items_for_pricing", []):
            quantity = float(item["quantity"])
            unit = item["unit"]

            resolved_sku = self._resolve_variant_sku(
                item["selected_sku"],
                item["item_name"]
            )

            unit_price = self.material_prices.get(resolved_sku, 0.0)
            base_cost = quantity * unit_price

            test_costs = []
            total_test_cost = 0.0

            for test in item.get("applicable_tests", []):
                price = (
                    self.test_prices.get(test["test_name"], 0.0)
                    if test.get("chargeable", True)
                    else 0.0
                )

                total_test_cost += price
                test_costs.append({
                    "test_name": test["test_name"],
                    "unit_price": price
                })

            priced_items.append({
                "item_id": item["item_id"],
                "item_name": item["item_name"],
                "oem": item["selected_oem"],
                "sku": resolved_sku,
                "quantity": quantity,
                "unit": unit,
                "unit_price": unit_price,
                "base_material_cost": base_cost,
                "tests": test_costs,
                "total_test_cost": total_test_cost,
                "total_item_cost": base_cost + total_test_cost
            })

        inspection_cost = 0.0
        grand_total = sum(i["total_item_cost"] for i in priced_items)

        return {
            "currency": pricing_summary["rfp_context"]["currency"],
            "priced_items": priced_items,
            "inspection_cost": inspection_cost,
            "grand_total": grand_total
        }


# =========================
# ✅ PATH-SAFE ENTRY POINT
# =========================
if __name__ == "__main__":
    BASE_DIR = Path(__file__).resolve().parent

    test_price_chart_path = BASE_DIR / "main_agent" / "prompts" / "test_price_chart.json"
    material_price_chart_path = BASE_DIR / "main_agent" / "prompts" / "price_chart.json"
    pricing_summary_path = BASE_DIR.parent / "outputs" / "pricing_summary_Sample.json"

    pricing_agent = PricingAgent(
        test_price_chart_path=str(test_price_chart_path),
        material_price_chart_path=str(material_price_chart_path)
    )

    with open(pricing_summary_path, "r", encoding="utf-8") as f:
        pricing_summary = json.load(f)

    final_price_sheet = pricing_agent.generate_pricing_table(pricing_summary)

    print(json.dumps(final_price_sheet, indent=2))
