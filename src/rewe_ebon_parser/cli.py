# src/rewe_ebon_parser/cli.py
import sys
from pathlib import Path
import argparse
from .output import process_pdf, process_folder
from . import __version__

def main():
    parser = argparse.ArgumentParser(description="Parse REWE eBons from PDF to JSON.")
    parser.add_argument("input_path", type=str, nargs='?', help="Path to input PDF file or folder containing PDF files.")
    parser.add_argument("output_path", type=str, nargs='?', default=None, help="Path to output JSON file or folder for JSON files.")
    parser.add_argument("--file", action="store_true", help="Specify if the input and output paths are files.")
    parser.add_argument("--folder", action="store_true", help="Specify if the input and output paths are folders.")
    parser.add_argument("--nthreads", type=int, default=None, help="Number of concurrent threads to use for processing files. Defaults to maximum available cpu cores.")
    parser.add_argument("--rawtext-file", action="store_true", help="Output raw text extracted from the PDF files to .txt files.")
    parser.add_argument("--rawtext-stdout", action="store_true", help="Print raw text extracted from the PDF files to the console.")
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
