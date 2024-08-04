# src/rewe_ebon_parser/table.py
import csv
import json
from pathlib import Path
from typing import List, Dict

def dump_items_to_csv(parsed_receipts: List[Dict], output_path: Path):
    items = []
    for receipt in parsed_receipts:
        for item in receipt['items']:
            item['datetime_local'] = receipt['datetime_local']
            items.append(item)

    if items:
        # Define the desired field order
        fieldnames = [
            'datetime_local', 'name', 'subTotal', 'amount', 
            'pricePerUnit', 'unit', 'taxCategory', 'paybackQualified'
        ]

        # Ensure all keys are present in each item
        for item in items:
            for field in fieldnames:
                if field not in item:
                    item[field] = None

        with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(items)
    else:
        print("No items found in the parsed receipts.")
