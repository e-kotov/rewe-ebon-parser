
# REWE eBon Parser

The REWE eBon Parser is a Python package designed to parse REWE eBons (receipts) from PDF files and convert them into structured JSON format. The package also provides functionality to output raw text extracted from the PDFs for debugging purposes. This project is a re-write of the the [`rewe-ebon-parser`](https://github.com/webD97/rewe-ebon-parser) TypeScript library.

## Features

- Parse individual PDF files or entire folders containing PDF files.
- Output parsed data as JSON.
- Extract and output raw text from PDF files.
- Concurrent processing of multiple PDF files with adjustable threading.
- Detailed logging of processing results in CSV format.

## Installation

You can install the package using pip:

```bash
pip install rewe-ebon-parser
```

## Usage

### Command Line Interface (CLI)

#### Parse a Single PDF File and save to JSON

```bash
rewe-ebon-parser [--file] <input_pdf_path> [output_json_path]
```


#### Parsing Multiple PDF Files in a Folder

```bash
rewe-ebon-parser [--folder] <input_folder> [output_folder] [--nthreads <number_of_threads>] 
```

#### Optional Arguments

- `--file`: Explicitly specify if the input and output paths are files.
- `--folder`: Explicitly specify if the input and output paths are folders.
- `--nthreads`: Number of concurrent threads to use for processing files.
- `--rawtext-file`: Output raw text extracted from the PDF files to .txt files (mostly for debugging).
- `--rawtext-stdout`: Print raw text extracted from the PDF files to the console (mostly for debugging).

### Auto-detection Mode

If neither `--file` nor `--folder` is specified, the script will automatically detect if the input path is a file or a folder and process accordingly.

### Output

- If `output_json_path` is not specified for a single file, the output will be saved in the same directory as the input file with a `.json` extension.
- If `output_folder` is not specified for a folder, a subfolder named `rewe_json_out` will be created in the input folder, and the output JSON files will be saved there.

### Logging

A detailed log of processing results will be saved in the output folder as `processing_log.csv`, containing information on which files were successfully processed and which failed, along with error messages if any.


## License

This project is licensed under the MIT License. For details see [LICENSE](LICENSE) file.