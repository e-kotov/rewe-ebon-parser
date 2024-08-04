# src/rewe_ebon_parser/cli.py
import sys
from pathlib import Path
import argparse
from .output import process_pdf, process_folder
from .table import dump_items_to_csv
from . import __version__
import json

def main():
    """
    Main function to parse REWE eBons from PDF to JSON or CSV table.
    """
    parser = argparse.ArgumentParser(description="Parse REWE eBons from PDF to JSON or CSV table.")
    parser.add_argument("input_path", type=str, nargs='?', help="Path to input PDF file or folder containing PDF files.")
    parser.add_argument("output_path", type=str, nargs='?', default=None, help="Path to output JSON/CSV file or folder for JSON files.")
    parser.add_argument("--file", action="store_true", help="Specify if the input and output paths are files.")
    parser.add_argument("--folder", action="store_true", help="Specify if the input and output paths are folders.")
    parser.add_argument("--nthreads", type=int, default=None, help="Number of concurrent threads to use for processing files. Defaults to maximum available CPU cores.")
    parser.add_argument("--rawtext-file", action="store_true", help="Output raw text extracted from the PDF files to .txt files.")
    parser.add_argument("--rawtext-stdout", action="store_true", help="Print raw text extracted from the PDF files to the console.")
    parser.add_argument("--csv-table", action="store_true", help="Output all items from all parsed receipts into a single CSV table.")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}", help="Show the version number and exit.")

    args = parser.parse_args()
    
    # Print help if no arguments are provided
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    input_path = Path(args.input_path) if args.input_path else None
    output_path = Path(args.output_path) if args.output_path else None
    max_workers = args.nthreads
    rawtext_file = args.rawtext_file
    rawtext_stdout = args.rawtext_stdout

    if args.csv_table:
        if not output_path:
            output_path = input_path.with_suffix('.csv')
        if input_path.is_file():
            if input_path.suffix.lower() == '.pdf':
                result = process_pdf(input_path, None, rawtext_file, rawtext_stdout)
                dump_items_to_csv([result], output_path)
            elif input_path.suffix.lower() == '.json':
                with open(input_path, 'r', encoding='utf-8') as f:
                    result = json.load(f)
                dump_items_to_csv([result], output_path)
            else:
                print("Error: Input file must be a PDF or JSON file when using --csv-table.")
                sys.exit(1)
        elif input_path.is_dir():
            pdf_files = list(input_path.glob("*.pdf"))
            json_files = list(input_path.glob("*.json"))
            if pdf_files and json_files:
                print("Error: Only one type of files (PDF or JSON) is allowed in the source folder at the same time.")
                sys.exit(1)
            elif pdf_files:
                parsed_receipts = process_folder(input_path, None, max_workers, rawtext_file, rawtext_stdout)
                dump_items_to_csv(parsed_receipts, output_path)
            elif json_files:
                parsed_receipts = []
                for json_file in json_files:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        parsed_receipts.append(json.load(f))
                dump_items_to_csv(parsed_receipts, output_path)
            else:
                print("Error: No valid input files found in the folder.")
                sys.exit(1)
        else:
            print("Error: Invalid input path.")
            sys.exit(1)
    else:
        if args.file:
            if not output_path:
                output_path = input_path.with_suffix('.json')
            if input_path.is_file() and (output_path.is_file() or not output_path.exists()):
                process_pdf(input_path, output_path, rawtext_file, rawtext_stdout)
            else:
                print("Error: Input and output paths must be files when using --file.")
                sys.exit(1)
        elif args.folder:
            if not output_path:
                output_path = input_path / 'rewe_json_out'
            if input_path.is_dir() and (output_path.is_dir() or not output_path.exists()):
                process_folder(input_path, output_path, max_workers, rawtext_file, rawtext_stdout)
            else:
                print("Error: Input and output paths must be directories when using --folder.")
                sys.exit(1)
        else:
            # Auto-detection mode
            if input_path:
                if input_path.is_dir():
                    if not output_path:
                        output_path = input_path / 'rewe_json_out'
                    if output_path.is_dir() or not output_path.exists():
                        process_folder(input_path, output_path, max_workers, rawtext_file, rawtext_stdout)
                    else:
                        print("Error: Output path should be a directory when the input path is a directory.")
                        sys.exit(1)
                elif input_path.is_file():
                    if not output_path:
                        output_path = input_path.with_suffix('.json')
                    if output_path.is_file() or not output_path.exists():
                        process_pdf(input_path, output_path, rawtext_file, rawtext_stdout)
                    else:
                        print("Error: Output path should be a file when the input path is a file.")
                        sys.exit(1)
                else:
                    print("Error: Invalid input or output path.")
                    sys.exit(1)
            else:
                print("Error: No input path provided.")
                sys.exit(1)

if __name__ == '__main__':
    main()
