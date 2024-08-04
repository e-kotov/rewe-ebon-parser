[![Python package](https://github.com/e-kotov/rewe-ebon-parser/actions/workflows/python-package-test.yml/badge.svg)](https://github.com/e-kotov/rewe-ebon-parser/actions/workflows/python-package-test.yml)

# REWE eBon Parser

The REWE eBon Parser is a Python package designed to parse REWE eBons (receipts) from PDF files and convert them into structured JSON format or CSV. The package also provides functionality to output raw text extracted from the PDFs for debugging purposes. This project is a re-write of the the [`rewe-ebon-parser`](https://github.com/webD97/rewe-ebon-parser) TypeScript library, example PDFs are borrowed from the same library.

## Features

- Parse individual PDF files or entire folders containing PDF files.
- Output parsed data as JSON or CSV.
- Extract and output raw text from PDF files (bascially, the output of the underlying `pdfplumber`).
- Concurrent processing of multiple PDF files with adjustable threading.
- Detailed logging of processing results in CSV format.

## Installation

You can install the package using pip:

```bash
pip install rewe-ebon-parser
```

## Usage

*You can find PDF receipt files to test on in the `examples/eBons` folder in this repo borrowed from [`rewe-ebon-parser`](https://github.com/webD97/rewe-ebon-parser).*

### Command Line Interface (CLI)

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

#### Parse a Single PDF File and Save Items to CSV Table

```bash
rewe-ebon-parser [--file] <input_pdf_path> [output_csv_path] [--csv-table]
```

Example:

```bash
rewe-ebon-parser examples/eBons/1.pdf --csv-table
```

#### Parsing Multiple PDF Files in a Folder into a single CSV Table

```bash
rewe-ebon-parser [--folder] <input_folder> [output_folder] [--nthreads <number_of_threads>] [--csv-table]
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
- `--rawtext-file`: Output raw text extracted from the PDF files to .txt files (mostly for debugging).
- `--rawtext-stdout`: Print raw text extracted from the PDF files to the console (mostly for debugging).
- `--csv-table`: Output parsed data as a CSV table.
- `--version`: show module version.
- `-h`, `--help`: show help.

#### Auto-detection Mode

If neither `--file` nor `--folder` is specified, the script will automatically detect if the input path is a file or a folder and process accordingly.

#### Output

- If `output_json_path` is not specified for a single file, the output will be saved in the same directory as the input file with a `.json` extension.
- If `output_folder` is not specified for a folder, a subfolder named `rewe_json_out` will be created in the input folder, and the output JSON files will be saved there.

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


## License

This project is licensed under the MIT License. For details see [LICENSE](LICENSE) file.


## Caveats

So far the module reliably parses the items, but sometimes fails on PAYBACK points, as these are often presented differently in REWE receipts.

## Future Work

- Fix bugs with occasional parsing failures in datetime and PAYBACK points.