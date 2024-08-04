# src/rewe_ebon_parser/parse.py

import re
from datetime import datetime
from typing import List, Optional
import pdfplumber
import io
import math
import pytz
from collections import OrderedDict
from .classes import *

def extract_raw_text(data_buffer: bytes) -> str:
    """
    Extract raw text from a PDF data buffer.

    Args:
        data_buffer (bytes): The PDF data buffer.

    Returns:
        str: The extracted raw text.
    """
    raw_text = ''
    with pdfplumber.open(io.BytesIO(data_buffer)) as pdf:
        for page in pdf.pages:
            raw_text += page.extract_text()
    return raw_text

def parse_ebon(data_buffer: bytes) -> dict:
    """
    Parse receipt data from a PDF data buffer.

    Args:
        data_buffer (bytes): The PDF data buffer.

    Returns:
        dict: The parsed receipt data.
    """
    data_text = extract_raw_text(data_buffer)

    lines = list(filter(None, map(str.strip, data_text.replace('  ', ' ').split('\n'))))

    date = None
    market = '?'
    market_address = None
    cashier = '?'
    checkout = '?'
    uid = '?'
    items = []
    total = float('nan')
    given = []
    change = float('nan')
    payout = float('nan')
    payback_points_before = float('nan')
    payback_points = float('nan')
    payback_revenue = float('nan')
    payback_card_number = '?'
    payback_coupons = []
    used_rewe_credit = float('nan')
    new_rewe_credit = float('nan')
    tax_details_total = TaxDetailsEntry(float('nan'), float('nan'), float('nan'), float('nan'))
    tax_details_A = None
    tax_details_B = None

    # Improved address extraction logic to handle both formats
    address_match_1 = re.search(r'[\s\*]*([a-zäöüß \d.,-]+?)\s*[\s\*]*(\d{5})\s*([a-zäöüß \d.,-]+)[\s\*]*', data_text, re.IGNORECASE)
    address_match_2 = re.search(r'([\wäöüß \d.,-]+),\s*(\d{5})\s*([\wäöüß \d.,-]+)', data_text, re.IGNORECASE)
    if address_match_1:
        market_address = MarketAddress(
            street=address_match_1.group(1).replace('  ', ' ').replace(',', '').strip(),
            zip=address_match_1.group(2),
            city=address_match_1.group(3).strip()
        )
    elif address_match_2:
        market_address = MarketAddress(
            street=address_match_2.group(1).replace('  ', ' ').replace(',', '').strip(),
            zip=address_match_2.group(2),
            city=address_match_2.group(3).strip()
        )

    for line in lines:
        item_hit = re.match(r'([0-9A-Za-zäöüß &%.!+,\-]*) (-?\d*,\d\d) ([AB]) ?(\*?)', line)
        if item_hit:
            item = item_hit.group(1)
            price = float(item_hit.group(2).replace(',', '.'))
            category = item_hit.group(3)
            payback_qualified = not item_hit.group(4) and price > 0

            items.append(ReceiptItem(
                tax_category=category,
                name=item,
                sub_total=price,
                payback_qualified=payback_qualified,
                amount=1
            ))
            continue

        menge_hit = re.match(r'(.*) (.*) x (.*).*', line)
        if menge_hit:
            amount = float(menge_hit.group(1).replace(',', '.'))
            unit = menge_hit.group(2)
            price_per_unit_str = re.search(r'(\d+,\d+)', menge_hit.group(3))
            price_per_unit = float(price_per_unit_str.group(1).replace(',', '.')) if price_per_unit_str else None
            if unit == 'Stk':
                amount = int(amount)
            if items:
                items[-1].amount = amount
                items[-1].unit = unit
                items[-1].price_per_unit = price_per_unit
            continue

        total_hit = re.match(r'SUMME EUR (-?\d*,\d\d)', line)
        if total_hit:
            total = float(total_hit.group(1).replace(',', '.'))
            continue

        gegeben_hit = re.match(r'Geg\.(.*) EUR ([0-9,]*)', line)
        if gegeben_hit:
            given.append(Payment(
                type=gegeben_hit.group(1).strip(),
                value=float(gegeben_hit.group(2).replace(',', '.'))
            ))
            continue

        return_hit = re.match(r'Rückgeld BAR EUR ([0-9,]*)', line)
        if return_hit:
            change = float(return_hit.group(1).replace(',', '.'))
            continue

        payout_match = re.match(r'AUSZAHLUNG EUR ([0-9,]*)', line)
        if payout_match:
            payout = float(payout_match.group(1).replace(',', '.'))
            continue

        timestamp_hit = re.match(r'(\d{2})\.(\d{2})\.(\d{4}) (\d{2}):(\d{2}) Bon-Nr\.:.*', line)
        if timestamp_hit:
            date = datetime(
                year=int(timestamp_hit.group(3)),
                month=int(timestamp_hit.group(2)),
                day=int(timestamp_hit.group(1)),
                hour=int(timestamp_hit.group(4)),
                minute=int(timestamp_hit.group(5)),
                second=0
            )
            local_tz = pytz.timezone('Europe/Berlin')
            date = local_tz.localize(date)
            continue

        markt_match = re.match(r'Markt:(.*) Kasse:(.*) Bed\.:(.*)', line)
        if markt_match:
            market = markt_match.group(1).strip()
            checkout = markt_match.group(2).strip()
            cashier = markt_match.group(3).strip()
            continue

        uid_match = re.match(r'UID Nr.: (.*)', line)
        if uid_match:
            uid = uid_match.group(1).strip()
            continue

        payback_info_match = re.match(r'PAYBACK Karten-Nr\.: ([0-9#]*)Punkte vor dem Einkauf: ([0-9.,]*) Punkte', line)
        if payback_info_match:
            payback_card_number = payback_info_match.group(1)
            payback_points_before = int(payback_info_match.group(2).replace('.', '').replace(',', ''))
            continue

        payback_points_match = re.match(r'Sie erhalten (\d*) PAYBACK Punkte? auf|Mit diesem Einkauf gesammelt: (\d*) Punkte?', line)
        if payback_points_match:
            match = next(group for group in payback_points_match.groups() if group is not None)
            payback_points = int(match)
            continue

        payback_revenue_match = re.match(r'einen PAYBACK Umsatz von (.*) EUR!', line)
        if payback_revenue_match:
            payback_revenue = float(payback_revenue_match.group(1).replace(',', '.'))
            continue

        payback_points_before_match = re.match(r'Punktestand vor Einkauf: ([0-9.]*)|Punkte vor dem Einkauf: ([0-9.]*)', line)
        if payback_points_before_match:
            match = next(group for group in payback_points_before_match.groups() if group is not None)
            payback_points_before = int(match.replace('.', ''))
            continue

        payback_card_number_match = re.match(r'PAYBACK Karten-Nr\.: ([0-9#]*)', line)
        if payback_card_number_match:
            payback_card_number = payback_card_number_match.group(1)
            continue

        payback_coupon_match = re.match(r'(.*) ([0-9.]*) Punkte?', line)
        if payback_coupon_match:
            payback_coupons.append(PaybackCoupon(
                name=payback_coupon_match.group(1),
                points=int(payback_coupon_match.group(2).replace('.', ''))
            ))
            continue

        tax_details_match = re.match(r'([AB])= ([0-9,]*)% ([0-9,]*) ([0-9,]*) ([0-9,]*)', line)
        if tax_details_match:
            category = tax_details_match.group(1)
            tax_details_entry = TaxDetailsEntry(
                tax_percent=float(tax_details_match.group(2).replace(',', '.')),
                net=float(tax_details_match.group(3).replace(',', '.')),
                tax=float(tax_details_match.group(4).replace(',', '.')),
                gross=float(tax_details_match.group(5).replace(',', '.'))
            )
            if category == 'A':
                tax_details_A = tax_details_entry
            elif category == 'B':
                tax_details_B = tax_details_entry
            continue

        total_tax_match = re.match(r'Gesamtbetrag ([0-9,]*) ([0-9,]*) ([0-9,]*)', line)
        if total_tax_match:
            tax_details_total = TaxDetailsEntry(
                tax_percent=float('nan'),
                net=float(total_tax_match.group(1).replace(',', '.')),
                tax=float(total_tax_match.group(2).replace(',', '.')),
                gross=float(total_tax_match.group(3).replace(',', '.'))
            )
            continue

        used_rewe_credit_match = re.match(r'Eingesetztes REWE Guthaben: ([0-9,]*) EUR', line)
        if used_rewe_credit_match:
            used_rewe_credit = float(used_rewe_credit_match.group(1).replace(',', '.'))

        new_rewe_credit_match = re.match(r'Neues REWE Guthaben: ([0-9,]*) EUR', line)
        if new_rewe_credit_match:
            new_rewe_credit = float(new_rewe_credit_match.group(1).replace(',', '.'))

    if date is None:
        raise ValueError("Date not found in the receipt")

    real_total_in_cents = sum(item.sub_total * 100 for item in items)
    total_in_cents = total * 100

    if round(real_total_in_cents, 2) != round(total_in_cents, 2):
        raise ValueError(f"Something went wrong when parsing the eBon: The eBon states a total sum of {total_in_cents} but the parser only found items worth {real_total_in_cents}.")

    qualified_revenue = payback_revenue if not math.isnan(payback_revenue) else sum(item.sub_total for item in items if item.payback_qualified or item.sub_total < 0)

    receipt = Receipt(
        date=date,
        market=market,
        market_address=market_address,
        cashier=cashier,
        checkout=checkout,
        vatin=uid,
        items=items,
        total=total,
        given=given,
        change=change if not math.isnan(change) else None,
        payout=payout if not math.isnan(payout) else None,
        payback=PaybackData(
            card=payback_card_number,
            points_before=payback_points_before,
            earned_points=payback_points,
            used_coupons=payback_coupons,
            used_rewe_credit=used_rewe_credit if not math.isnan(used_rewe_credit) else None,
            new_rewe_credit=new_rewe_credit if not math.isnan(new_rewe_credit) else None,
            payback_revenue=qualified_revenue
        ) if payback_card_number != '?' else None,
        tax_details=TaxDetails(
            total=tax_details_total,
            A=tax_details_A,
            B=tax_details_B
        )
    )

    # Create an ordered dictionary to ensure specific order of keys
    receipt_dict = receipt.to_dict()
    ordered_receipt_dict = OrderedDict([
        ('datetime_local', receipt_dict.get('datetime_local')),
        ('datetime_utc', receipt_dict.get('datetime_utc')),
        ('market', receipt_dict.get('market')),
        ('marketAddress', receipt_dict.get('marketAddress')),
        ('cashier', receipt_dict.get('cashier')),
        ('checkout', receipt_dict.get('checkout')),
        ('vatin', receipt_dict.get('vatin')),
        ('items', receipt_dict.get('items')),
        ('total', receipt_dict.get('total')),
        ('given', receipt_dict.get('given')),
        ('change', receipt_dict.get('change')),
        ('payout', receipt_dict.get('payout')),
        ('payback', receipt_dict.get('payback')),
        ('taxDetails', receipt_dict.get('taxDetails')),
    ])

    # Remove None values to clean up the dictionary
    ordered_receipt_dict = {k: v for k, v in ordered_receipt_dict.items() if v is not None}

    return ordered_receipt_dict

def parse_pdf_ebon(pdf_path: str) -> dict:
    """
    Parse receipt data from a PDF file.

    Args:
        pdf_path (str): Path to the input PDF file.

    Returns:
        dict: The parsed receipt data.
    """
    with open(pdf_path, 'rb') as f:
        data = f.read()
        result = parse_ebon(data)
        return result
