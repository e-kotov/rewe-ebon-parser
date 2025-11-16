import pytest
from pathlib import Path
from rewe_ebon_parser.parse import parse_text_ebon


@pytest.fixture(scope="module")
def rewe_bonus_ebon_1():
    """Parses the first REWE Bonus eBon example."""
    ebon_path = Path('./examples/eBons_txt_anonymized/5.txt')
    raw_text = ebon_path.read_text(encoding='utf-8')
    return parse_text_ebon(raw_text)


@pytest.fixture(scope="module")
def rewe_bonus_ebon_2():
    """Parses the second REWE Bonus eBon example."""
    ebon_path = Path('./examples/eBons_txt_anonymized/6.txt')
    raw_text = ebon_path.read_text(encoding='utf-8')
    return parse_text_ebon(raw_text)


def test_bonus_receipt_1_program_detection(rewe_bonus_ebon_1):
    """Tests that the loyalty program is correctly identified as 'REWE Bonus'."""
    assert 'loyalty' in rewe_bonus_ebon_1
    assert rewe_bonus_ebon_1['loyalty']['program'] == 'REWE Bonus'


def test_bonus_receipt_1_credit_values(rewe_bonus_ebon_1):
    """Tests the parsing of earned and total credit."""
    details = rewe_bonus_ebon_1['loyalty']['details']
    assert details['earnedCredit'] == pytest.approx(6.28)
    assert details['newTotalCredit'] == pytest.approx(7.26)
    assert 'usedCredit' not in details  # No credit was used in this receipt


def test_bonus_receipt_1_coupon_parsing(rewe_bonus_ebon_1):
    """Tests that all REWE Bonus coupons and their values are parsed correctly."""
    details = rewe_bonus_ebon_1['loyalty']['details']
    coupons = details['usedCoupons']

    assert len(coupons) == 5

    # Spot-check a few coupons
    assert coupons[0]['name'] == '10% auf REWE Bio'
    assert coupons[0]['value'] == pytest.approx(1.53)

    assert coupons[2]['name'] == '0,50EUR auf Dumet Ol'
    assert coupons[2]['value'] == pytest.approx(1.00)

    assert coupons[4]['name'] == '5% auf einen Einkauf'
    assert coupons[4]['value'] == pytest.approx(3.34)


def test_bonus_receipt_1_item_qualification(rewe_bonus_ebon_1):
    """Tests that an eligible item is correctly marked for the REWE Bonus program."""
    # The 'PANGASIUSFILET' item should be qualified
    item = rewe_bonus_ebon_1['items'][1]
    assert item['name'] == 'PANGASIUSFILET'
    assert item['loyaltyProgramQualified'] == 'REWE Bonus'

    # The 'LEERG. MW E. ST' item is marked with a '*' and should not be qualified
    item_not_qualified = rewe_bonus_ebon_1['items'][23]
    assert item_not_qualified['name'] == 'LEERG. MW E. ST'
    assert item_not_qualified['loyaltyProgramQualified'] is None


def test_bonus_receipt_2_program_detection(rewe_bonus_ebon_2):
    """Ensures the second receipt also identifies the REWE Bonus program."""
    assert 'loyalty' in rewe_bonus_ebon_2
    assert rewe_bonus_ebon_2['loyalty']['program'] == 'REWE Bonus'


def test_bonus_receipt_2_credit_values(rewe_bonus_ebon_2):
    """Validates the parsed credit information for the second receipt."""
    details = rewe_bonus_ebon_2['loyalty']['details']
    assert details['earnedCredit'] == pytest.approx(0.83)
    assert details['newTotalCredit'] == pytest.approx(7.66)
    assert 'usedCredit' not in details


def test_bonus_receipt_2_coupon_parsing(rewe_bonus_ebon_2):
    """Checks the coupon parsing for the smaller REWE Bonus receipt."""
    coupons = rewe_bonus_ebon_2['loyalty']['details']['usedCoupons']

    assert len(coupons) == 3

    assert coupons[0]['name'] == '10% auf REWE Regiona'
    assert coupons[0]['value'] == pytest.approx(0.18)

    assert coupons[1]['name'] == '0,50EUR auf Little L'
    assert coupons[1]['value'] == pytest.approx(0.50)

    assert coupons[2]['name'] == '10% auf REWE Beste W'
    assert coupons[2]['value'] == pytest.approx(0.15)
