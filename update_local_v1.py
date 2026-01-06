#!/usr/bin/env python3
import os
import json
from pathlib import Path
from params import *  # Expects definitions for METADATA, RAW_FILE_TYPES, etc.
from generate_html import generate_html_from_json
from auxiliary import process_files_for_summarised
import pandas as pd
import numpy as np




def load_sample_tb(file_path):
    """
    Loads the JSON file including the pairs of samples and corresponding patients and return a dictionary.
    The keys are sample_id and values are patient_id in this dictionary.

    Args:
        file_path (str): Path to the metadata JSON file.

    Returns:
        dict: Mapping from "Patient ID" to the metadata entry.
    """
    with open(file_path, "r") as f:
        data = json.load(f)
    return data

with open("config.json", "r") as f:
    config = json.load(f)

def filter_files(directory):
    """   
    Recursively scans the given directory for raw data files whose names end with one of the specified file_types.
    Each found file has the fullpath appended to the relevant list.
    
    Args:
        directory (str): The directory to search.
        raw (list): List of raw file extensions to match.
    
    Returns:
        tuple: A tuple of lists containing the full paths for raw, processed and summarised files respectively.
    """    
    bucket_by_ext = {}

    for ext in config["raw_file_types"]:
        bucket_by_ext[ext.lower()] = "raw"

    for ext in config["processed_file_types"]:
        bucket_by_ext[ext.lower()] = "processed"

    for ext in config["summarised_file_types"]:
        bucket_by_ext[ext.lower()] = "summarised"

    file_path_dict = {
        bucket.replace("_file_types", ""): []
        for bucket in config
    }

    # file_path_dict = {"raw":[], "processed":[], "summarised":[]}

    for root, _, files in os.walk(directory):
        for file in files:
            ext = Path(file).suffix.lower()
            bucket = bucket_by_ext.get(ext)

            if bucket is None:
                continue
            full_path = Path(root) / file
            file_path_dict[bucket].append(full_path)

    for bucket, files in file_path_dict.items():
        if not files:
            print(f" | No files found for {bucket} file types")
         
    return file_path_dict

def process_files(directory, file_path_dict, file_type, organization, cor_dict):
    print(f"Processing the {file_type} files")
    file_list = []
    total_size = 0
    for full_path in file_path_dict[file_type]:

        relative_path = full_path.relative_to(directory)
        file_path = f"./{relative_path.as_posix()}"
        file_size = round(os.path.getsize(full_path) / CONVERT_FROM_BYTES)
        total_size += file_size
        file_name = Path(full_path).name
        sample_name = Path(full_path).stem

        # establish file name
        metadata_dict = {
            "file_name": file_name,
            "file_size": file_size, 
            "patient_id": cor_dict.get(sample_name, ""),
            "sample_id": sample_name,
            "directory": file_path,
            "organization": organization
        }

        print(f" | {file_path}  ~{file_size}{FILE_SIZE_UNIT}")

        # check here to prevent duplicates
        if metadata_dict not in file_list:
            file_list.append(metadata_dict)

    print(f" | Total size for these files: {total_size}{FILE_SIZE_UNIT}")
                        
    return file_list


def generate_json(directory, output_file):
    """
    Generates a JSON summary of files in the specified directory using RO‑Crate.
    The directory is recursively scanned for raw, processed, and summarised files.
    Each file is registered in the RO‑Crate with enriched metadata.
    
    Args:
        directory (str): The directory to analyze.
        output_file (str): The path where the JSON output will be saved.
    """
    if not os.path.isdir(directory):
        raise ValueError(f"The specified path '{directory}' is not a valid directory.")
    
  
    # Load metadata from the provided metadata file.
    cor_dict = load_sample_tb(SAMPLE_TO_PATIENT)
    organization = ORGANIZATION

    file_path_dict = filter_files(directory)

    print(f"\nProcessing raw files ({', '.join(RAW_FILE_TYPES)})")
    raw_files = process_files(target_directory, file_path_dict, "raw", organization, cor_dict) 

    print(f"\nProcessing processed files ({', '.join(PROCESSED_FILE_TYPES)})")
    processed_files = process_files(target_directory, file_path_dict, "processed", organization, cor_dict) 
   
    print(f"\nProcessing summarised files ({', '.join(SUMMARISED_FILE_TYPES)})")
    summarised_files = process_files_for_summarised(directory, SUMMARISED_FILE_TYPES, organization, cor_dict)
    
    # Build the final output structure.
    output_data = {
        "data": {
            "location": directory,
            "file_size_unit": FILE_SIZE_UNIT,
            "files": {
                "raw": raw_files,
                "processed": processed_files,
                "summarised": summarised_files
            }
        }
    }
    
    
    # Write the custom JSON summary.
    with open(output_file, "w") as f:
        json.dump(output_data, f, indent=4)
    
    print(f"\nJSON file generated at: {output_file}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: python update_local.py /path/to/files")
        sys.exit(1)
    
    # The target directory should be the 'files' subfolder.
    target_directory = sys.argv[1]
    print(f"\nSearching through {target_directory} .........")
    
    # Determine output file paths relative to the script's directory.
    script_directory = Path(__file__).parent
    output_file_path = script_directory / OUTPUT_JSON_FILE_NAME
    output_html_path = script_directory / OUTPUT_HTML_FILE_NAME
    
    try:
        generate_json(target_directory, output_file_path)
        generate_html_from_json(output_file_path, output_html_path)
    except Exception as e:
        print(f"Error: {e}")
