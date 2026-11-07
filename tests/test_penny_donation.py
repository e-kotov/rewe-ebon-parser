"""Regression coverage for PENNY 'Stimmt so!' donation handling."""

import pytest

from rewe_ebon_parser.parse import parse_ebon, parse_text_ebon


@pytest.fixture(params=["text", "pdf"])
def parse_receipt(request, monkeypatch):
    """Exercise the text parser and the PDF-buffer parser with extracted text."""
    def parse(raw_text):
        if request.param == "pdf":
            monkeypatch.setattr(
                "rewe_ebon_parser.parse.extract_raw_text", lambda _: raw_text
            )
            return parse_ebon(b"synthetic-pdf-buffer")
        return parse_text_ebon(raw_text)

    return parse


def receipt_text(total, donation_line=None, bounded=True):
    """A synthetic PENNY-style eBon with two products worth EUR 4.29."""
    lines = ["PENNY"]
    if bounded:
        lines.extend(["UID Nr.: DE123456789", "EUR"])
    lines.extend(["MILCH 1,79 B", "BROT 2,50 A"])
    if bounded:
        lines.append("--------------------------------------")
    lines.append("SUMME EUR " + total)
    if donation_line is not None:
        lines.append(donation_line)
    lines.extend([
        "Geg. EC-Cash EUR " + total,
        "07.11.2026 12:34 Bon-Nr.: 42",
        "Markt: 1234 Kasse: 1 Bed.: 123",
    ])
    return "\n".join(lines)


@pytest.mark.parametrize(
    "donation_line,total,expected_donation",
    [
        ("Stimmt so! 0,05", "4,34", 0.05),
        ("Stimmt so!  1,50", "5,79", 1.50),
        ("Stimmt so! ,05", "4,34", 0.05),
        ("Stimmt so! 0,00", "4,29", 0.0),
    ],
)
def test_donation_is_separate_from_purchased_items(
    parse_receipt, donation_line, total, expected_donation
):
    receipt = parse_receipt(receipt_text(total, donation_line))
    assert receipt["donation"] == pytest.approx(expected_donation)
    assert receipt["total"] == pytest.approx(float(total.replace(",", ".")))
    assert [item["name"] for item in receipt["items"]] == ["MILCH", "BROT"]
    assert sum(item["subTotal"] for item in receipt["items"]) == pytest.approx(4.29)


def test_no_donation_keeps_existing_output(parse_receipt):
    receipt = parse_receipt(receipt_text("4,29"))
    assert receipt["total"] == pytest.approx(4.29)
    assert "donation" not in receipt


def test_donation_does_not_hide_real_total_mismatch(parse_receipt):
    with pytest.raises(ValueError, match="The eBon states a total sum"):
        parse_receipt(receipt_text("4,35", "Stimmt so! 0,05"))


def test_donation_with_fallback_item_detection(parse_receipt):
    receipt = parse_receipt(
        receipt_text("4,34", "Stimmt so! 0,05", bounded=False)
    )
    assert receipt["donation"] == pytest.approx(0.05)
    assert len(receipt["items"]) == 2
