# src/rewe_ebon_parser/privacy.py
import re
from typing import Dict

def anonymize_text_content(text: str) -> str:
    """
    Anonymizes sensitive information within the raw extracted text from an eBon.
    This version redacts the entire header and footer blocks containing PII.

    Args:
        text (str): The raw text content.

    Returns:
        str: Anonymized text content.
    """
    # Redact the entire header block. We define the header as everything
    # from the start of the file until the standalone "EUR" line that
    # precedes the item list. The `(?s)` flag makes `.` match newlines.
    # The `(?=^EUR$)` is a positive lookahead to find the boundary without consuming it.
    text = re.sub(r'(?s)\A.*?(?=^EUR$)', '[HEADER REDACTED]\n', text, count=1, flags=re.MULTILINE)

    # Redact the entire customer receipt block for payment details
    text = re.sub(r'(?s)(\* \* Kundenbeleg \* \*).*?(Zahlung erfolgt)', r'\1\n[PAYMENT DETAILS REDACTED]\n\2', text)
    
    # Redact the entire TSE (technical security device) block
    text = re.sub(r'(?s)TSE-Signatur:.*Seriennnummer Kasse:.*', '[TSE DATA REDACTED]', text)

    # Redact main date, market, cashier, and receipt number line in the footer
    text = re.sub(r'^\d{2}\.\d{2}\.\d{4} \d{2}:\d{2} Bon-Nr\.:\d+\n', 'DD.MM.YYYY HH:MM Bon-Nr.: [REDACTED]\n', text, flags=re.MULTILINE)
    text = re.sub(r'^Markt:.* Kasse:.* Bed\.:.*\n', 'Markt: [REDACTED] Kasse: [REDACTED] Bed.: [REDACTED]\n', text, flags=re.MULTILINE)

    # Redact all PAYBACK and Bonus Coupon information in the footer
    text = re.sub(r'(?s)Deine REWE PAYBACK Vorteile heute.*?(?=REWE Markt GmbH)', '[PAYBACK & COUPON DATA REDACTED]\n', text)

    return text

def anonymize_receipt_dict(receipt_dict: Dict) -> Dict:
    """
    Anonymizes sensitive information within a parsed receipt dictionary.

    Args:
        receipt_dict (Dict): The dictionary representation of a receipt.

    Returns:
        Dict: Anonymized receipt dictionary.
    """
    if not receipt_dict:
        return receipt_dict

    # Anonymize top-level fields
    receipt_dict['datetime_local'] = "YYYY-MM-DDTHH:MM:SS+ZZ:ZZ"
    receipt_dict['datetime_utc'] = "YYYY-MM-DDTHH:MM:SS+00:00"
    receipt_dict['market'] = "[REDACTED]"
    receipt_dict['cashier'] = "[REDACTED]"
    receipt_dict['checkout'] = "[REDACTED]"
    receipt_dict['vatin'] = "[REDACTED]"

    # Anonymize market address
    if 'marketAddress' in receipt_dict and receipt_dict['marketAddress']:
        receipt_dict['marketAddress'] = {
            'street': "[REDACTED]",
            'zip': "[REDACTED]",
            'city': "[REDACTED]"
        }

    # Remove payback data entirely
    if 'payback' in receipt_dict:
        receipt_dict['payback'] = None

    # Remove keys that became None
    receipt_dict = {k: v for k, v in receipt_dict.items() if v is not None}
    
    return receipt_dict
