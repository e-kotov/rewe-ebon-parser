import pytest
from datetime import datetime
from rewe_ebon_parser.parse import parse_pdf_ebon

@pytest.fixture(scope="module")
def example_ebon():
    ebon_dict = parse_pdf_ebon('./examples/eBons/5.pdf')
    return ebon_dict

def test_correct_date(example_ebon):
    assert 'datetime_local' in example_ebon
    assert isinstance(example_ebon['datetime_local'], str)
    assert example_ebon['datetime_local'] == "2023-08-11T16:09:00+02:00"

def test_correct_cashier(example_ebon):
    assert example_ebon['cashier'] == '303030'

def test_correct_checkout(example_ebon):
    assert example_ebon['checkout'] == '3'

def test_correct_store(example_ebon):
    assert example_ebon['market'] == '5472'

def test_correct_store_address(example_ebon):
    assert example_ebon['marketAddress'] == {
        'street': "Im Weidenbruch 136",
        'zip': "51061",
        'city': "Köln"
    }

def test_correct_amount_of_items(example_ebon):
    assert len(example_ebon['items']) == 18

def test_correctly_identifies_item_1(example_ebon):
    item = example_ebon['items'][0]
    assert item['name'] == 'SALAMI SPITZENQ.'
    assert item['amount'] == 1
    assert item['paybackQualified'] is True
    assert item.get('pricePerUnit') is None
    assert item['taxCategory'] == 'B'
    assert item.get('unit') is None
    assert item['subTotal'] == pytest.approx(1.79)

def test_correctly_identifies_item_7(example_ebon):
    item = example_ebon['items'][6]
    assert item['name'] == 'BAG. SPECIALE'
    assert item['amount'] == 2
    assert item['paybackQualified'] is True
    assert item['pricePerUnit'] == pytest.approx(2.29)
    assert item['taxCategory'] == 'B'
    assert item['unit'] == 'Stk'
    assert item['subTotal'] == pytest.approx(4.58)

def test_correctly_identifies_item_17(example_ebon):
    item = example_ebon['items'][16]
    assert item['name'] == 'Mitarbeiterrabatt 5%'
    assert item['paybackQualified'] is False
    assert item['taxCategory'] == 'A'
    assert item['subTotal'] == pytest.approx(-0.29)

def test_payout_is_undefined(example_ebon):
    assert example_ebon.get('payout') is None

def test_correct_total(example_ebon):
    assert example_ebon['total'] == pytest.approx(39.44)

def test_correct_payback_info(example_ebon):
    payback = example_ebon.get('payback', {})
    assert payback['card'] == '#########9334'
    assert payback['basePoints'] == 19
    assert payback['couponPoints'] == 0
    assert payback['earnedPoints'] == 19
    assert payback['pointsBefore'] == 7638
    assert payback['qualifiedRevenue'] == pytest.approx(39.44)
    assert payback['usedCoupons'] == []
    assert payback.get('usedREWECredit') is None
    assert payback.get('newREWECredit') is None

def test_correct_given_money(example_ebon):
    assert len(example_ebon['given']) == 2

def test_correct_handles_inflationspraemie(example_ebon):
    given = example_ebon['given'][0]
    assert given['type'] == "Inflationsprämie"
    assert given['value'] == pytest.approx(2.08)

def test_correct_handles_ec_cash(example_ebon):
    given = example_ebon['given'][1]
    assert given['type'] == "EC-Cash"
    assert given['value'] == pytest.approx(37.36)

def test_change_is_undefined(example_ebon):
    assert example_ebon.get('change') is None
