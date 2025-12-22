#!/usr/bin/env python3
import json
import sys
import argparse
from pathlib import Path
from rocrate.rocrate import ROCrate
from .params import *
from .generate_html import generate_html_from_json
import pandas as pd
import numpy as np

def load_file_types(config_path=None):
    """
    Load file types from a JSON file.
    If config_path is provided and exists, load from it.
    Otherwise, return DEFAULT_FILE_TYPES.
    """
    if config_path and config_path.exists():
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                print(f" | Loading file types from {config_path}")
                return json.load(f)
        except Exception as e:
            print(f" | Warning: Failed to load {config_path}: {e}. Using defaults.")
    
    print(" | Using default file types.")
    return DEFAULT_FILE_TYPES

def load_metadata(file_path):
    """
    Loads metadata from the JSON file and returns a dictionary keyed by the "Patient ID".
    """
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
    """
    Loads the JSON file including the pairs of samples and corresponding patients.
    Returns a dictionary mapping sample_id to patient_id.
    """
    if not file_path.exists():
        print(f"Warning: Sample to Patient mapping file not found at {file_path}")
        return {}

    with open(file_path) as f:
        data = json.load(f)
    return data

def scan_dataset(data_dir: Path, file_types: dict, metadata_dict: dict, sample_to_patient: dict, organization: str, crate: ROCrate):
    """
    Recursively scans the dataset directory and categorizes files.
    Registers files in the RO-Crate.
    """
    files_by_category = {cat: [] for cat in file_types}
    
    print(f" | Scanning {data_dir} recursively...")
    
    # Flatten file types for easy lookup
    ext_to_cat = {}
    for cat, extensions in file_types.items():
        for ext in extensions:
            ext_to_cat[ext.lower()] = cat

    total_size = 0
    
    for file_path in data_dir.rglob('*'):
        if file_path.is_file():
            # Check extension (handle .fastq.gz as well as .fastq)
            # We'll check the longest matching extension first
            name = file_path.name.lower()
            category = None
            
            # Sort extensions by length descending to match .fastq.gz before .gz
            sorted_exts = sorted(ext_to_cat.keys(), key=len, reverse=True)
            
            for ext in sorted_exts:
                if name.endswith(ext):
                    category = ext_to_cat[ext]
                    break
            
            if category is None:
                continue

            # Calculate size
            size_bytes = file_path.stat().st_size
            size_kb = round(size_bytes / CONVERT_FROM_BYTES)
            total_size += size_kb
            
            # Determine Sample ID and Patient ID
            sample_id = file_path.name.split('.')[0]
            
            # Look up patient ID
            patient_id = sample_to_patient.get(sample_id, "")
            
            sample_ids_list = [sample_id]
            patient_ids_list = [patient_id] if patient_id else []
            
            if category == 'summarised' and file_path.suffix in ['.csv', '.tsv']:
                try:
                    sep = '\t' if file_path.suffix == '.tsv' else ','
                    try:
                        df = pd.read_csv(file_path, index_col=0, sep=sep)
                        if not df.empty:
                            sample_ids_list = list(df.index.astype(str))
                            # Map all samples to patients
                            p_ids = set()
                            for s in sample_ids_list:
                                pid = sample_to_patient.get(s)
                                if pid:
                                    p_ids.add(pid)
                            patient_ids_list = list(p_ids)
                    except Exception as e:
                        print(f"   ! Could not read summary file {file_path.name}: {e}")
                except Exception:
                    pass

            # Format for output
            final_sample_id = sample_ids_list if len(sample_ids_list) > 1 else sample_ids_list[0]
            final_patient_id = patient_ids_list if len(patient_ids_list) > 1 else (patient_ids_list[0] if patient_ids_list else "")
            
            # Add to RO-Crate
            # Relative path for RO-Crate
            try:
                rel_path = file_path.relative_to(data_dir)
            except ValueError:
                rel_path = file_path.name # Should not happen if rglob is used on data_dir
            
            crate.add_file(file_path, properties={
                "fileSize": f"{size_kb}{FILE_SIZE_UNIT}",
                "patient_id": final_patient_id,
                "sample_id": final_sample_id
            })
            
            record = {
                "file_name": file_path.name,
                "file_size": size_kb,
                "directory": f"./{rel_path}",
                "organization": organization,
                "sample_id": final_sample_id,
                "patient_id": final_patient_id
            }
            
            files_by_category[category].append(record)
            print(f"   + Found {category}: {file_path.name} ({size_kb} {FILE_SIZE_UNIT})")

    print(f" | Total size: {total_size} {FILE_SIZE_UNIT}")
    return files_by_category

def generate_json(directory, output_file, file_types_path=None):
    """
    Generates a JSON summary of files in the specified directory using RO-Crate.
    """
    data_dir = Path(directory).resolve()
    if not data_dir.is_dir():
        raise ValueError(f"The specified path '{directory}' is not a valid directory.")
    
    # Init RO-Crate
    crate = ROCrate()
    crate.root_dataset.name = "Research Object"
    crate.root_dataset.description = f"Research object created from files in {directory}"
    
    # Load metadata and config
    metadata_dict = load_metadata(METADATA)
    sample_to_patient = load_sample_tb(SAMPLE_TO_PATIENT)
    
    # Load file types
    if file_types_path:
        file_types = load_file_types(Path(file_types_path))
    else:
        file_types = load_file_types(data_dir / "config.json")
    
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
    parser.add_argument("--file-types", help="Path to file_types.json configuration.")
    
    args = parser.parse_args()
    
    target_directory = args.dataset
    print(f"\nSearching through {target_directory} .........")
    
    # Define output paths (Current Working Directory)
    output_file_path = Path.cwd() / OUTPUT_JSON_FILE_NAME
    output_html_path = Path.cwd() / OUTPUT_HTML_FILE_NAME
    
    try:
        generate_json(target_directory, output_file_path, args.file_types)
        generate_html_from_json(output_file_path, output_html_path)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
