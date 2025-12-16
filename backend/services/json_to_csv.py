import json
import csv

def json_to_csv(json_file, csv_file):
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not data:
        print("Empty JSON file")
        return

    headers = data[0].keys()

    with open(csv_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(data)

    print(f"✅ Converted {json_file} → {csv_file}")


if __name__ == "__main__":
    json_to_csv("oem_products.json", "oem_products.csv")
    json_to_csv("oem_product_specs.json", "oem_product_specs.csv")
