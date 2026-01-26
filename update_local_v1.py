#!/usr/bin/env python3
import os
import json
import argparse
import sys
from pathlib import Path

# Imports from refactored modules
from config import validate_config
from auxiliary import scan_dataset, FILE_SIZE_UNIT
from generate_html import generate_html_from_json

# Default constants (previously in params.py)
ORGANIZATION = "WEHI"
OUTPUT_JSON_FILE_NAME = "output.json"
OUTPUT_HTML_FILE_NAME = "output.html"

def load_json(file_path):
    try:
        with open(file_path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"\n[ERROR] Configuration file not found: {file_path}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"\n[ERROR] Invalid JSON in {file_path}:\n{e}")
        sys.exit(1)

def generate_json(data_dir, output_file, verbose=False, counts_tsv=False):
    """
    Generates a JSON summary of files in the specified directory.
    Uses unified config.json and improved scanning logic.
    """
    if not data_dir.is_dir():
        print(f"[ERROR] The specified path '{data_dir}' is not a valid directory.")
        sys.exit(1)
    
    # 1. Load and Validate Config
    config_path = data_dir / "config.json"
    raw_config = load_json(config_path)
    config = validate_config(raw_config, str(config_path))
    
    # Override/Set counts_format if CLI flag is present
    if counts_tsv:
        config["counts_format"] = True
        if verbose:
            print(" | CLI flag active: counts_format set to True")

    # 2. Scan Dataset
    files_by_category = scan_dataset(data_dir, config, organization=ORGANIZATION)
    
    # 3. Build Output Structure
    output_data = {
        "data": {
            "location": data_dir.as_posix(),
            "file_size_unit": FILE_SIZE_UNIT,
            "files": files_by_category
        }
    }
    
    # 4. Write Output
    with open(output_file, "w") as f:
        json.dump(output_data, f, indent=4)
    
    print(f"\nJSON file generated at: {output_file}")
    if verbose:
        print(" | Summary generation complete.")

def main():
    parser = argparse.ArgumentParser(description="Redmane Metadata Generator")
    parser.add_argument("dataset", type=Path, help="Path to the dataset directory")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    parser.add_argument("--counts-tsv", action="store_true", help="Treat summarised TSV files as counts tables (header=samples)")
    
    # Handle legacy call where argparse wasn't used or minimal
    # If users pass only a path, argparse handles it.
    
    args = parser.parse_args()
    
    target_directory = args.dataset.resolve()
    print(f"\nSearching through {target_directory} ...")
    
    output_file_path = target_directory / OUTPUT_JSON_FILE_NAME
    output_html_path = target_directory / OUTPUT_HTML_FILE_NAME
    
    try:
        generate_json(target_directory, output_file_path, verbose=args.verbose, counts_tsv=args.counts_tsv)
        
        # Verify if generate_html_from_json supports the new output structure?
        # It usually expects 'data' -> 'files' -> 'raw'/'processed'/'summarised' lists, which we preserved.
        generate_html_from_json(output_file_path, output_html_path, organization=ORGANIZATION)
        print(f"HTML report generated at: {output_html_path}")
        
    except Exception as e:
        print(f"[ERROR] Execution failed: {e}")
        import traceback
        if args.verbose:
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
