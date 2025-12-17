import json
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)
from reportlab.lib import colors 


def generate_pricing_pdf(pricing_json: dict, output_path: str):
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    elements = []

    # -------------------------
    # Title
    # -------------------------
    elements.append(Paragraph(
        "<b>Pricing Summary - Supply of Copper Cables</b>",
        styles["Title"]
    ))
    elements.append(Spacer(1, 12))

    elements.append(Paragraph(
        f"Currency: {pricing_json['currency']}",
        styles["Normal"]
    ))
    elements.append(Spacer(1, 12))

    # -------------------------
    # Iterate items
    # -------------------------
    for item in pricing_json["priced_items"]:
        # Item heading
        elements.append(Paragraph(
            f"<b>{item['item_name']}</b>",
            styles["Heading2"]
        ))

        elements.append(Paragraph(
            f"""
            OEM: {item['oem']}<br/>
            SKU: {item['sku']}<br/>
            Quantity: {item['quantity']} {item['unit']}<br/>
            Unit Price: Rs {item['unit_price']:,}<br/>
            Base Material Cost: Rs {item['base_material_cost']:,}
            """,
            styles["Normal"]
        ))

        elements.append(Spacer(1, 8))

        # -------------------------
        # Test table
        # -------------------------
        test_table_data = [
            ["Test Name", "Unit Price (Rs )"]
        ]

        for test in item["tests"]:
            test_table_data.append([
                test["test_name"],
                f"{test['unit_price']:,}"
            ])

        test_table_data.append([
            "Total Test Cost",
            f"{item['total_test_cost']:,}"
        ])

        test_table = Table(
            test_table_data,
            colWidths=[350, 120]
        )

        test_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors .lightgrey),
            ("GRID", (0, 0), (-1, -1), 0.5, colors .grey),
            ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
            ("FONT", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONT", (0, -1), (-1, -1), "Helvetica-Bold"),
            ("BACKGROUND", (0, -1), (-1, -1), colors .whitesmoke),
        ]))

        elements.append(test_table)
        elements.append(Spacer(1, 8))

        elements.append(Paragraph(
            f"<b>Total Item Cost:</b> Rs {item['total_item_cost']:,}",
            styles["Normal"]
        ))

        elements.append(Spacer(1, 18))

    # -------------------------
    # Grand Total
    # -------------------------
    elements.append(Spacer(1, 12))
    elements.append(Paragraph(
        f"<b>Grand Total Cost: Rs {pricing_json['grand_total']:,}</b>",
        styles["Heading1"]
    ))

    # -------------------------
    # Footer note
    # -------------------------
    elements.append(Spacer(1, 12))
    elements.append(Paragraph(
        "Note: Prices are indicative and generated using synthetic pricing tables "
        "for demonstration purposes only.",
        styles["Italic"]
    ))

    doc.build(elements)


if __name__ == "__main__":
    BASE_DIR = Path(__file__).resolve().parent

    input_json_path = BASE_DIR.parent / "outputs" / "final_priced_output.json"
    output_pdf_path = BASE_DIR.parent / "outputs" / "Final_Summary.pdf"

    with open(input_json_path, "r", encoding="utf-8") as f:
        pricing_data = json.load(f)

    generate_pricing_pdf(pricing_data, str(output_pdf_path))

    print(f"PDF generated at: {output_pdf_path}")

