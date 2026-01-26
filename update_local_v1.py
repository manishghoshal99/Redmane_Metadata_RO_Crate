#!/usr/bin/env python3
import json
import argparse
import sys
from pathlib import Path

from config import validate_config
from auxiliary import scan_dataset
from generate_html import generate_html

ORGANIZATION = "WEHI"

def main():
    parser = argparse.ArgumentParser(description="Redmane Metadata Generator")
    parser.add_argument("dataset", type=Path, help="Dataset directory")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    parser.add_argument("--counts-tsv", action="store_true", help="Treat TSV as counts matrix (samples in header)")
    args = parser.parse_args()
    
    data_dir = args.dataset.resolve()
    if not data_dir.is_dir():
        sys.exit(f"[ERROR] Directory not found: {data_dir}")
        
    # Config
    try:
        with open(data_dir / "config.json") as f:
            raw_config = json.load(f)
        config = validate_config(raw_config, str(data_dir / "config.json"))
    except Exception as e:
        sys.exit(f"[ERROR] Config error: {e}")

    if args.counts_tsv:
        config["counts_format"] = True
        
    # Scan
    files, size = scan_dataset(data_dir, config, ORGANIZATION)
    
    # Output
    out_data = {
        "data": {
            "location": str(data_dir),
            "file_size_unit": "KB",
            "files": files
        }
    }
    
    json_path = data_dir / "output.json"
    with open(json_path, "w") as f:
        json.dump(out_data, f, indent=4)
        
    print(f"\nJSON output: {json_path}")
    if args.verbose:
        print(f"Total size: {size} KB")
        
    # HMTL
    generate_html(json_path, data_dir / "output.html", ORGANIZATION)

if __name__ == "__main__":
    main()
