import sys
import argparse
import json
from pathlib import Path
from rocrate.rocrate import ROCrate
from .params import *
from .generate_html import generate_html_from_json
from .config import find_config_path, load_config, normalize_and_validate_config
import pandas as pd
import numpy as np

def load_metadata(file_path):
    # Loads metadata from the JSON file and returns a dictionary keyed by the "Patient ID".
    if not file_path.exists():
        print(f"Warning: Metadata file not found at {file_path}")
        return {}
        
    with open(file_path, "r") as f:
        data = json.load(f)
    metadata_dict = {}
    for entry in data:
        key = entry.get("Patient ID")
        if key:
            metadata_dict[key] = entry
    return metadata_dict

def load_sample_tb(file_path):
    # Loads the JSON file including the pairs of samples and corresponding patients.
    # Returns a dictionary mapping sample_id to patient_id.
    if not file_path.exists():
        print(f"Warning: Sample to Patient mapping file not found at {file_path}")
        return {}

    with open(file_path) as f:
        data = json.load(f)
    return data

from .auxiliary import scan_dataset

def generate_json(directory, output_file):
    # Generates a JSON summary of files in the specified directory using RO-Crate.
    data_dir = Path(directory).resolve()
    if not data_dir.is_dir():
        print(f"\nERROR: The specified path '{directory}' does not exist or is not a directory.")
        sys.exit(1)
    
    # Init RO-Crate
    crate = ROCrate()
    crate.root_dataset.name = "Research Object"
    crate.root_dataset.description = f"Research object created from files in {directory}"
    
    # Load metadata
    metadata_dict = load_metadata(METADATA)
    sample_to_patient = load_sample_tb(SAMPLE_TO_PATIENT)
    
    # STRICT CONFIG enforcement
    # 1. Find config path
    config_path = find_config_path(data_dir)
    print(f" | Found configuration: {config_path}")
    
    # 2. Load config
    config_raw = load_config(config_path)
    
    # 3. Validate and normalize
    file_types = normalize_and_validate_config(config_raw)
    
    # Scan
    files_map = scan_dataset(data_dir, file_types, metadata_dict, sample_to_patient, ORGANIZATION, crate)
    
    # Build output
    output_data = {
        "data": {
            "location": str(data_dir),
            "file_size_unit": FILE_SIZE_UNIT,
            "files": files_map
        }
    }
    
    # Write RO-Crate
    rocrate_folder = Path(output_file).parent / "rocrate"
    crate.write(rocrate_folder)
    print(f"RO-Crate written to {rocrate_folder}")
    
    # Write JSON
    with open(output_file, "w") as f:
        json.dump(output_data, f, indent=4)
    
    print(f"\nJSON file generated at: {output_file}")

def main():
    parser = argparse.ArgumentParser(description="Generate metadata JSON and HTML report for a dataset.")
    parser.add_argument("--dataset", required=True, help="Path to the dataset directory.")
    
    args = parser.parse_args()
    
    target_directory = args.dataset
    print(f"\nProcess started for: {target_directory}")
    
    # Define output paths (Current Working Directory)
    output_file_path = Path.cwd() / OUTPUT_JSON_FILE_NAME
    output_html_path = Path.cwd() / OUTPUT_HTML_FILE_NAME
    
    try:
        generate_json(target_directory, output_file_path)
        generate_html_from_json(output_file_path, output_html_path)
    except SystemExit:
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
