import pytest
import csv
import sys
from pathlib import Path
from rewe_ebon_parser.cli import main as cli_main

@pytest.fixture
def examples_ebons_dir():
    return Path('examples/eBons')

def test_csv_table_cli(tmp_path, examples_ebons_dir, monkeypatch):
    # Path to save the CSV file
    output_csv = tmp_path / "output.csv"
    
    # Set up command line arguments
    test_args = [
        "rewe-ebon-parser",
        str(examples_ebons_dir),
        str(output_csv),
        "--csv-table"
    ]
    
    # Monkeypatch sys.argv
    monkeypatch.setattr(sys, 'argv', test_args)
    
    # Run the CLI
    cli_main()
    
    # Read and validate the CSV content
    with open(output_csv, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        rows = list(reader)
        
        # Ensure some rows are present
        assert len(rows) > 0
        
        expected_fields = ['datetime_local', 'name', 'subTotal', 'amount', 'pricePerUnit', 'unit', 'taxCategory', 'loyaltyProgramQualified']
        assert reader.fieldnames == expected_fields
        
        # Check some values in the first row as an example
        first_row = rows[0]
        assert first_row['datetime_local']
        assert first_row['name']
        assert first_row['subTotal']
        assert first_row['amount']
        assert first_row['taxCategory']
        assert first_row['loyaltyProgramQualified']

        # Ensure no fields are missing
        for row in rows:
            for field in expected_fields:
                assert field in row

def test_csv_table_cli_with_mixed_files(tmp_path, examples_ebons_dir, monkeypatch):
    # Path to save the CSV file
    output_csv = tmp_path / "output.csv"
    
    # Simulate the condition with both PDF and JSON files in the same directory
    test_json_file = examples_ebons_dir / "test_receipt.json"
    try:
        test_json_file.write_text('{}')
        
        # Set up command line arguments
        test_args = [
            "rewe-ebon-parser",
            str(examples_ebons_dir),
            str(output_csv),
            "--csv-table"
        ]
        
        # Monkeypatch sys.argv
        monkeypatch.setattr(sys, 'argv', test_args)
        
        # Run the CLI and expect it to fail
        with pytest.raises(SystemExit):
            cli_main()
    finally:
        # Clean up the test JSON file
        if test_json_file.exists():
            test_json_file.unlink()
