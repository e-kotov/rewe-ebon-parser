import pytest
from datetime import datetime
import pytz
from rewe_ebon_parser.parse import _parse_date

def test_parse_date_with_text_before_it():
    """Test that a valid date string is parsed correctly."""
    line = "some text 17.04.2024 15:39 Bon-Nr.:2333 and more text"
    expected_date = datetime(2024, 4, 17, 15, 39)
    local_tz = pytz.timezone('Europe/Berlin')
    expected_date = local_tz.localize(expected_date)
    
    assert _parse_date(line) == expected_date

def test_parse_date_on_new_line():
    """Test that another valid date string is parsed correctly."""
    line = "11.08.2023 16:09 Bon-Nr.:12345"
    expected_date = datetime(2023, 8, 11, 16, 9)
    local_tz = pytz.timezone('Europe/Berlin')
    expected_date = local_tz.localize(expected_date)
    
    assert _parse_date(line) == expected_date

def test_parse_date_with_prepended_garbage():
    """Test that another valid date string is parsed correctly."""
    line = "f0:0011.08.2023 16:09 Bon-Nr.:12345"
    expected_date = datetime(2023, 8, 11, 16, 9)
    local_tz = pytz.timezone('Europe/Berlin')
    expected_date = local_tz.localize(expected_date)
    
    assert _parse_date(line) == expected_date

def test_parse_date_failure():
    """Test that a string without a date returns None."""
    line = "this line has no date"
    assert _parse_date(line) is None

def test_parse_date_empty_string():
    """Test that an empty string returns None."""
    line = ""
    assert _parse_date(line) is None

def test_parse_date_malformed():
    """Test that a malformed date string returns None."""
    line = "17.04.24 15:39 Bon-Nr.:2333"
    assert _parse_date(line) is None
