import pytest
from pathlib import Path
from rewe_ebon_parser.parse import parse_pdf_ebon, parse_text_ebon

# --- Ground Truth Data ---
# To add a new test, add a tuple to the appropriate list below.
# Format: (filename, file_type, expected_number_of_items)

PDF_CASES = [
    ('1.pdf', 'pdf', 10),
    ('2.pdf', 'pdf', 32),
    ('3.pdf', 'pdf', 31),
    ('4.pdf', 'pdf', 18),
    ('5.pdf', 'pdf', 18),
]

# This list assumes you have run the CLI tool on the PDFs to generate
# these corresponding .txt files in the 'eBons_txt_anonymized' folder.
TXT_CASES = [
    ('1.txt', 'txt', 5),
]

# Combine all test cases for the parameterizer (gracefully handle undefined lists)
try:
    PDF_CASES
except NameError:
    PDF_CASES = []

try:
    TXT_CASES
except NameError:
    TXT_CASES = []

EBON_TEST_CASES = [*PDF_CASES, *TXT_CASES]

if not EBON_TEST_CASES:
    pytestmark = pytest.mark.skip("No PDF_CASES or TXT_CASES defined for item count tests.")
# -------------------------


@pytest.mark.parametrize("filename, file_type, expected_count", EBON_TEST_CASES)
def test_correct_item_count_from_multiple_sources(filename: str, file_type: str, expected_count: int):
    """
    Tests that the parser correctly counts items from different sources
    (PDFs and pre-processed TXT files). The test is parameterized to run
    for every entry in the EBON_TEST_CASES list.
    """
    parsed_receipt = None

    if file_type == 'pdf':
        ebon_path = Path('./examples/eBons') / filename
        parsed_receipt = parse_pdf_ebon(str(ebon_path))

    elif file_type == 'txt':
        ebon_path = Path('./examples/eBons_txt_anonymized') / filename
        raw_text = ebon_path.read_text(encoding='utf-8')
        parsed_receipt = parse_text_ebon(raw_text)

    else:
        pytest.fail(f"Unsupported file type '{file_type}' in test configuration.")

    parsed_items = parsed_receipt.get('items', [])
    actual_item_count = len(parsed_items)

    assert actual_item_count == expected_count, (
        f"Validation failed for '{filename}' (type: {file_type}). "
        f"Expected {expected_count} items, but the parser found {actual_item_count}."
    )


def test_fallback_logic_on_malformed_ebon():
    """
    Tests that the parser can still extract items using the fallback mechanism
    when the standard 'EUR' and '---' block markers are missing.
    """
    malformed_text = """
        Dein Markt
        EinStrasse 22
        19011 City
        UID Nr.: DE939006014
        BIO PU SCHNI 3,52 B
        SALATBAR. 1,49 B
        TOMATE CHERRYRIS 2,29 B
        SUMME EUR 7,30
        ======================================
        Geg. Geldgeräte EUR 10,00
        Rückgeld Geldgeräte EUR 2,70
    """

    parsed_receipt = parse_text_ebon(malformed_text)

    parsed_items = parsed_receipt.get('items', [])
    actual_item_count = len(parsed_items)
    expected_count = 3

    assert actual_item_count == expected_count, (
        "Fallback item counting failed. "
        f"Expected {expected_count} items, but the parser found {actual_item_count}."
    )
