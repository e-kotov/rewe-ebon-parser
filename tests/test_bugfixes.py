import pytest
from rewe_ebon_parser.parse import _parse_ebon_from_text


def test_cremeseife_bug():
    # This test case simulates the bug where an item at the end of the page was not parsed correctly.
    # The crafted ebon_text includes the "CREMESEIFE" item with a layout that might have caused the original issue.
    ebon_text = """
    11.08.2023 16:09 Bon-Nr.: 1234
    ODOL ZAHNCREME 1,39 A
    CREMESEIFE                         0,65 A
    SUMME EUR 2,04
    """

    parsed_ebon = _parse_ebon_from_text(ebon_text)

    assert len(parsed_ebon['items']) == 2

    cremeseife_item = parsed_ebon['items'][1]
    assert cremeseife_item['name'] == 'CREMESEIFE'
    assert cremeseife_item['subTotal'] == pytest.approx(0.65)

    # Verify that the total sum is correct
    assert parsed_ebon['total'] == pytest.approx(2.04)
