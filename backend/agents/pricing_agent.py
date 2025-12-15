import json
from pathlib import Path
from typing import Dict, Any


class PricingAgent:
    def __init__(
        self,
        test_price_chart_path: str
    ):
        self.price_chart = self._load_price_chart(test_price_chart_path)

    def _load_price_chart(self, path: str) -> dict:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def generate_pricing_table(
        self,
        pricing_summary: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Converts Pricing Summary into a fully priced table
        using synthetic price chart
        """

        priced_items = []

        for item in pricing_summary["items_for_pricing"]:
            quantity = float(item["quantity"])
            unit = item["unit"]

            unit_price = self.price_chart["unit_prices"].get(unit, 0)
            base_cost = quantity * unit_price

            test_costs = []
            total_test_cost = 0

            for test in item["applicable_tests"]:
                if test["chargeable"]:
                    price = self.price_chart["test_prices"].get(
                        test["test_name"], 0
                    )
                else:
                    price = 0

                total_test_cost += price

                test_costs.append({
                    "test_name": test["test_name"],
                    "unit_price": price
                })

            priced_items.append({
                "item_id": item["item_id"],
                "item_name": item["item_name"],
                "oem": item["selected_oem"],
                "sku": item["selected_sku"],
                "quantity": quantity,
                "unit": unit,
                "unit_price": unit_price,
                "base_material_cost": base_cost,
                "tests": test_costs,
                "total_test_cost": total_test_cost,
                "total_item_cost": base_cost + total_test_cost
            })

        inspection_cost = (
            self.price_chart["inspection_cost"]
            if pricing_summary["testing_and_inspection"]["inspection_required"]
            else 0
        )

        grand_total = (
            sum(i["total_item_cost"] for i in priced_items)
            + inspection_cost
        )

        return {
            "currency": pricing_summary["rfp_context"]["currency"],
            "priced_items": priced_items,
            "inspection_cost": inspection_cost,
            "grand_total": grand_total
        }


if __name__ == "__main__":
    pricing_agent = PricingAgent(
        "main_agent/prompts/test_price_chart.json"
    )

    with open("main_agent/prompts/pricing_summary_output.json") as f:
        pricing_summary = json.load(f)

    final_price_sheet = pricing_agent.generate_pricing_table(pricing_summary)

    print(json.dumps(final_price_sheet, indent=2))
