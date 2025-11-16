# src/rewe_ebon_parser/table.py
import csv
import json
from pathlib import Path
from typing import List, Dict

def dump_items_to_csv(parsed_receipts: List[Dict], output_path: Path):
    """
    Dump all items from parsed receipts into a CSV file.

    Args:
        parsed_receipts (List[Dict]): List of parsed receipt data.
        output_path (Path): Path to the output CSV file.
    """
    items = []
    for receipt in parsed_receipts:
        market_address = receipt.get('marketAddress') or {}
        for item in receipt['items']:
            # Attach receipt-level metadata used in the CSV table.
            item['datetime_local'] = receipt.get('datetime_local')
            item['market'] = receipt.get('market')
            item['marketStreet'] = market_address.get('street')
            item['marketZip'] = market_address.get('zip')
            item['marketCity'] = market_address.get('city')
            items.append(item)

    if items:
        # Define the desired field order
        fieldnames = [
            'datetime_local', 'market', 'marketStreet', 'marketZip', 'marketCity',
            'name', 'subTotal', 'amount', 
            'pricePerUnit', 'unit', 'taxCategory', 'loyaltyProgramQualified'
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
