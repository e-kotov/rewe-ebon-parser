# src/rewe_ebon_parser/output.py
import json
import time
import csv
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed
from tqdm import tqdm
from .parse import extract_raw_text, parse_ebon

def process_pdf(pdf_path, output_path=None, rawtext_file=False, rawtext_stdout=False):
    """
    Process a single PDF file to extract receipt data.

    Args:
        pdf_path (Path): Path to the input PDF file.
        output_path (Optional[Path]): Path to the output JSON file.
        rawtext_file (bool): If True, output raw text to a file.
        rawtext_stdout (bool): If True, print raw text to the console.

    Returns:
        dict: Parsed receipt data.
    """
    output_path = Path(output_path) if output_path else None
    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)  # Ensure the output directory exists

    try:
        with open(pdf_path, 'rb') as f:
            data = f.read()

            if rawtext_file or rawtext_stdout:
                raw_text = extract_raw_text(data)
                if rawtext_file:
                    rawtext_path = output_path.with_suffix('.txt') if output_path else pdf_path.with_suffix('.txt')
                    rawtext_path.write_text(raw_text, encoding='utf-8')
                if rawtext_stdout:
                    print(raw_text)
                return

            result = parse_ebon(data)

            if result and output_path:
                with open(output_path, 'w', encoding='utf-8') as json_file:
                    json.dump(result, json_file, default=str, indent=2, ensure_ascii=False)
            
            return result
    except Exception as e:
        print(f"Failed to process {pdf_path}: {e}")
        raise

def process_folder(input_folder, output_folder=None, max_workers=None, rawtext_file=False, rawtext_stdout=False):
    """
    Process all PDF files in a folder to extract receipt data.

    Args:
        input_folder (Path): Path to the input folder containing PDF files.
        output_folder (Optional[Path]): Path to the output folder for JSON files.
        max_workers (Optional[int]): Maximum number of concurrent threads to use.
        rawtext_file (bool): If True, output raw text to files.
        rawtext_stdout (bool): If True, print raw text to the console.

    Returns:
        List[dict]: List of parsed receipt data dictionaries.
    
    Raises:
        ValueError: If both JSON and PDF files are found in the input folder.
    """
    if output_folder:
        output_folder.mkdir(parents=True, exist_ok=True)

    start_time = time.time()
    success_count = 0
    failure_count = 0
    log_entries = []

    pdf_files = list(input_folder.glob("*.pdf"))
    json_files = list(input_folder.glob("*.json"))
    total_files = len(pdf_files)
    parsed_receipts = []

    if pdf_files and json_files:
        raise ValueError("Only one type of files (PDF or JSON) is allowed in the source folder at the same time.")
    
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = {}
        for pdf_file in pdf_files:
            output_file = (output_folder / (pdf_file.stem + ".json")) if output_folder else None
            future = executor.submit(process_pdf, pdf_file, output_file, rawtext_file, rawtext_stdout)
            futures[future] = pdf_file

        with tqdm(total=total_files, desc="Processing PDFs", unit="file") as pbar:
            for future in as_completed(futures):
                pdf_file = futures[future]
                try:
                    result = future.result()
                    if result:
                        parsed_receipts.append(result)
                    log_entries.append((pdf_file.name, "Success", ""))
                    success_count += 1
                except Exception as exc:
                    log_entries.append((pdf_file.name, "Failure", str(exc)))
                    failure_count += 1
                pbar.update(1)

    for json_file in json_files:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                parsed_receipts.append(json.load(f))
            log_entries.append((json_file.name, "Success", ""))
            success_count += 1
        except Exception as exc:
            log_entries.append((json_file.name, "Failure", str(exc)))
            failure_count += 1

    end_time = time.time()
    elapsed_time = end_time - start_time

    # Print summary
    print(f"Processed {success_count + failure_count} files in {elapsed_time:.2f} seconds.")
    print(f"Successfully processed: {success_count}")
    print(f"Failed to process: {failure_count}")

    # Save log to CSV
    if output_folder:
        log_file_path = output_folder / 'processing_log.csv'
        with open(log_file_path, 'w', newline='', encoding='utf-8') as csvfile:
            log_writer = csv.writer(csvfile)
            log_writer.writerow(["File Name", "Status", "Error Message"])
            log_writer.writerows(log_entries)
    
    return parsed_receipts
