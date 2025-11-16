[![Python package](https://github.com/e-kotov/rewe-ebon-parser/actions/workflows/python-package-test.yml/badge.svg)](https://github.com/e-kotov/rewe-ebon-parser/actions/workflows/python-package-test.yml)
[![PyPI version](https://img.shields.io/pypi/v/rewe-ebon-parser?label=pypi%20package)](https://pypi.org/project/rewe-ebon-parser/)
[![PyPI Downloads](https://static.pepy.tech/personalized-badge/rewe-ebon-parser?period=total&units=INTERNATIONAL_SYSTEM&left_color=BLACK&right_color=GREEN&left_text=total+downloads)](https://pepy.tech/projects/rewe-ebon-parser)
[![PyPI Downloads](https://static.pepy.tech/personalized-badge/rewe-ebon-parser?period=monthly&units=INTERNATIONAL_SYSTEM&left_color=BLACK&right_color=GREEN&left_text=monthly+downloads)](https://pepy.tech/projects/rewe-ebon-parser)
[![License](https://img.shields.io/pypi/l/rewe-ebon-parser)](LICENSE)

**Homepage and Documentation**: [https://www.ekotov.pro/rewe-ebon-parser](https://www.ekotov.pro/rewe-ebon-parser)  
**PyPI**: [https://pypi.org/project/rewe-ebon-parser/](https://pypi.org/project/rewe-ebon-parser/)  
**Changelog**: [View Full Changelog](CHANGELOG.md)  
**Releases**: [View Release History on GitHub](https://github.com/e-kotov/rewe-ebon-parser/releases)

# REWE eBon Parser

The REWE eBon Parser is a Python package designed to parse REWE eBons (receipts) from PDF files and convert them into structured JSON format or CSV. It supports parsing receipts with both the older PAYBACK system and the new REWE Bonus loyalty program. The package also provides functionality to output raw text extracted from the PDFs for debugging purposes. This project is a re-write of the the [`rewe-ebon-parser`](https://github.com/webD97/rewe-ebon-parser) TypeScript library, example PDFs are borrowed from the same library.

## Features

- Parse individual PDF files or entire folders containing PDF files.
- Output parsed data as JSON or CSV.
- Extract and output raw text from PDF files (bascially, the output of the underlying `pdfplumber`).
- Concurrent processing of multiple PDF files with adjustable threading.
- Detailed logging of processing results in CSV format.
- Supports both PAYBACK and the new REWE Bonus loyalty programs.

## Installation

You can install the package using pip:

```bash
pip install rewe-ebon-parser
```

## Usage

*You can find PDF receipt files to test on in the `examples/eBons` folder in this repo borrowed from [`rewe-ebon-parser`](https://github.com/webD97/rewe-ebon-parser).*

### Command Line Interface (CLI)

#### Quick Start:


##### Parse a Single PDF File and Save Items to CSV Table

```bash
rewe-ebon-parser [--file] <input_pdf_path> [output_csv_path] [--csv-table]
```

Example:

```bash
rewe-ebon-parser examples/eBons/1.pdf --csv-table
```

This saves to a csv file in the same folder as the input PDF with the same name but `.csv` extension, but feel free to specify a different output path for the csv file by addin a path to it after the input PDF path.

##### Parse Multiple PDF Files in a Folder into a single CSV Table

```bash
rewe-ebon-parser [--folder] <input_folder> [output_folder] [--nthreads <number_of_threads>] [--csv-table]
```

Example:

```bash
rewe-ebon-parser examples/eBons/ --csv-table examples/all-purchases-table.csv
```


#### Parse a Single PDF File and save to JSON

```bash
rewe-ebon-parser [--file] <input_pdf_path> [output_json_path]
```

Example:

```bash
rewe-ebon-parser examples/eBons/1.pdf
```

#### Parsing Multiple PDF Files in a Folder into JSON files

```bash
rewe-ebon-parser [--folder] <input_folder> [output_folder] [--nthreads <number_of_threads>] 
```

Example:

```bash
rewe-ebon-parser examples/eBons/
```


Example (the module automatically detects if its a folder of PDFs or JSONs):

```bash
rewe-ebon-parser examples/eBons/ --csv-table
```

*Note: the module will fail if the folder contains both JSON and PDF files to avoid duplicating the same data.*

#### Combine a Folder with Multiple JSON Files (previously extracted with the module) into a single CSV Table

```bash
rewe-ebon-parser [--folder] <input_folder> [output_csv_path] [--combine-json] [--nthreads <number_of_threads>]
```

Example (the module automatically detects if its a folder of PDFs or JSONs):

```bash
rewe-ebon-parser examples/eBons/ --csv-table
```

*Note: the module will fail if the folder contains both JSON and PDF files to avoid duplicating the same data.*



#### Optional Arguments

- `--file`: Explicitly specify if the input and output paths are files.
- `--folder`: Explicitly specify if the input and output paths are folders.
- `--nthreads`: Number of concurrent threads to use for processing files.
- `--txt-dump`: Instead of parsing to JSON, this saves the raw extracted text from the PDF to a `.txt` file. Useful for debugging or inspection.
- `--preserve-privacy`: Anonymizes sensitive information (like addresses, payment details, and personal data) in the output. This works for both JSON and text dump modes.
- `--rawtext-file`: Output raw text extracted from the PDF files to .txt files (mostly for debugging).
- `--rawtext-stdout`: Print raw text extracted from the PDF files to the console (mostly for debugging).
- `--csv-table`: Output parsed data as a CSV table.
- `--version`: show module version.
- `-h`, `--help`: show help.

#### CSV Table Columns

When `--csv-table` is used, each row in the exported CSV contains:
- `datetime_local`: Localized timestamp of the receipt.
- `market`: REWE market identifier (store number).
- `marketStreet`, `marketZip`, `marketCity`: Address of the market from `marketAddress` in the JSON output.
- `name`, `subTotal`, `amount`, `pricePerUnit`, `unit`, `taxCategory`: Item-level data from the parsed receipt.
- `loyaltyProgramQualified`: Name of the qualifying loyalty program for the item or empty if not qualified.

#### Auto-detection Mode

If neither `--file` nor `--folder` is specified, the script will automatically detect if the input path is a file or a folder and process accordingly.

#### Output

- If `output_json_path` is not specified for a single file, the output will be saved in the same directory as the input file with a `.json` extension.
- If `output_folder` is not specified for a folder, a subfolder named `rewe_json_out` will be created in the input folder, and the output JSON files will be saved there.
- When using `--rawtext-file` with a folder, the output text files will be saved in a `rewe_txt_out` subfolder.

#### Logging

A detailed log of processing results will be saved in the output folder as `processing_log.csv`, containing information on which files were successfully processed and which failed, along with error messages if any.


### Use as a Python module in your own Python code

#### Direct use on files

```python
from rewe_ebon_parser.parse import parse_pdf_ebon

parse_pdf_ebon("examples/eBons/1.pdf")
```

#### Passing a data_buffer: bytes

```python
from rewe_ebon_parser.parse import parse_ebon

# here the function is once again getting the data from a file,
# but input can come from anywhere
def process_pdf(pdf_path):
    with open(pdf_path, 'rb') as f:
        data = f.read()
        result = parse_ebon(data)
        return result

process_pdf("examples/eBons/1.pdf")
```

## Output Format

> **Note: Breaking Changes**
>
> To support multiple loyalty programs, the JSON output format has been updated. These changes are breaking for users who rely on the old structure.

The parser now uses a generalized `loyalty` object instead of a hardcoded `payback` object.

### The `loyalty` Object

The top-level `payback` key in the JSON output has been replaced by a `loyalty` key. This new object contains a `program` field (`"PAYBACK"` or `"REWE Bonus"`) and a `details` field with the program-specific data.

**Old PAYBACK Format:**

```json
{
  "payback": {
    "card": "#########9334",
    "earnedPoints": 19
  }
}
```

**New PAYBACK Format:**

```json
{
  "loyalty": {
    "program": "PAYBACK",
    "details": {
      "card": "#########9334",
      "earnedPoints": 19
    }
  }
}
```

**New REWE Bonus Format:**

```json
{
  "loyalty": {
    "program": "REWE Bonus",
    "details": {
      "earnedCredit": 6.28,
      "newTotalCredit": 7.26,
      "usedCoupons": [
        {
          "name": "10% auf REWE Bio",
          "value": 1.53
        }
      ]
    }
  }
}
```

### The `items` Object

Within each item, the boolean `paybackQualified` field has been replaced by a string field named `loyaltyProgramQualified`. This field will contain the name of the loyalty program (`"PAYBACK"` or `"REWE Bonus"`) if the item qualifies, or it will be `null` if it does not.

**Old Item Format:**

```json
{
  "name": "SALAMI SPITZENQ.",
  "paybackQualified": true
}
```

**New Item Format:**

```json
{
  "name": "SALAMI SPITZENQ.",
  "loyaltyProgramQualified": "PAYBACK"
}
```


## License

This project is licensed under the MIT License. For details, see the [LICENSE](LICENSE) file.

## Changelog

For a detailed history of changes, see the [CHANGELOG.md](CHANGELOG.md) file.


## Caveats

While the parser is tested against several receipt formats, REWE occasionally updates the layout of their eBons. A new or unusual layout might cause parsing errors, especially in the loyalty program section.

## Future Work

- Continue to improve the robustness of coupon parsing for both loyalty programs.
- Add handling for more edge cases and receipt variations as they are discovered.
