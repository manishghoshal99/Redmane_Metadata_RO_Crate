#!/usr/bin/env python3
import os
import json
from pathlib import Path
from params import *  # Expects definitions for METADATA, RAW_FILE_TYPES, etc.
from generate_html import generate_html_from_json
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
    with open(file_path) as f:
        data = json.load(f)
    return data


def process_files_for_raw(directory, file_types, organization, cor_dict):
    """   
    Recursively scans the given directory for raw data files whose names end with one of the specified file_types.
    Each found file is registered in the RO‑Crate with enriched properties.
    The file’s base name (without extension) is used to look up its metadata record.
    
    Args:
        directory (str): The directory to search.
        file_types (list): List of file extensions to match.
        metadata_dict (dict): Dictionary mapping "Patient ID" to metadata entries.
        crate (ROCrate): The RO‑Crate instance in which to register files.
        organization (str): Organization that the data files are from, can be modified in params.py
        cor_dict: The dictionary containing the keys as sample_id and values as patient_id
    
    Returns:
        list: A list of dictionaries summarizing the file details.
    """
    file_list = []
    total_size = 0
    for root, _, files in os.walk(directory):
        for file in files:
            if os.path.splitext(file)[1] in RAW_FILE_TYPES:
                full_path = os.path.join(root, file)
                relative_path = os.path.relpath(full_path, directory)
                file_path = f"./{relative_path}"
                file_size = round(os.path.getsize(full_path) / CONVERT_FROM_BYTES)
                total_size += file_size

                sample_name, _ = os.path.splitext(file)  # name of FASTQ/FASTA is sample name

                # establish file name
                file_dict = {
                    "file_name": file,
                    "file_size": file_size, 
                    "patient_id": cor_dict.get(sample_name, ""),
                    "sample_id": sample_name,
                    "directory": file_path,
                    "organization": organization
                }
                # print("Processing the Raw files")
                print(f" | {file_path}  ~{file_size}{FILE_SIZE_UNIT}")

                # check here to prevent duplicates
                if file_dict not in file_list:
                    file_list.append(file_dict)

    if not file_list:
        print(" | No files found for file types:", file_types)
    else:
        print(f" | Total size for these files: {total_size}{FILE_SIZE_UNIT}")
                        
    return file_list



def process_files_for_summarized(directory, file_types, organization, cor_dict):
    """   
    Recursively scans the given directory for summary data files whose names end with one of the specified file_types.
    Each found file is registered in the RO‑Crate with enriched properties.
    The file’s base name (without extension) is used to look up its metadata record.
    
    Args:
        directory (str): The directory to search.
        file_types (list): List of file extensions to match.
        metadata_dict (dict): Dictionary mapping "Patient ID" to metadata entries.
        crate (ROCrate): The RO‑Crate instance in which to register files.
        organization (str): Organization that the data files are from, can be modified in params.py
        cor_dict: The dictionary containing the keys as sample_id and values as patient_id
    
    Returns:
        list: A list of dictionaries summarizing the file details.
    """
    file_list = []
    total_size = 0
    for root, _, files in os.walk(directory):
        for file in files:
            if os.path.splitext(file)[1] in SUMMARISED_FILE_TYPES:
                if  os.path.splitext(file)[1] == '.csv':                
                    full_path = os.path.join(root, file)
                    relative_path = os.path.relpath(full_path, directory)
                    file_path = f"./{relative_path}"
                    file_size = round(os.path.getsize(full_path) / CONVERT_FROM_BYTES)
                    total_size += file_size
                    
                    df = pd.read_csv(full_path, index_col=0)

                    file_dict = {
                        "file_name": file, 
                        "file_size": file_size, 
                        "patient_id": list(set([cor_dict.get(sample, "") for sample in list(df.index)])),
                        "sample_id": list(df.index),
                        "directory": file_path,
                        "organization": organization
                    }
                    # print("Processing the Summarized files")
                    print(f" | {file_path}  ~{file_size}{FILE_SIZE_UNIT}")

                    # check here to prevent duplpicates
                    if file_dict not in file_list:
                        file_list.append(file_dict)

                elif os.path.splitext(file)[1] == '.tsv':
                    full_path = os.path.join(root, file)
                    relative_path = os.path.relpath(full_path, directory)
                    file_path = f"./{relative_path}"
                    file_size = round(os.path.getsize(full_path) / CONVERT_FROM_BYTES)
                    total_size += file_size
                    
                    df = pd.read_csv(full_path, index_col=0, delimiter="\t")

                    file_dict = {
                        "file_name": file, 
                        "file_size": file_size, 
                        "patient_id": list(set([cor_dict.get(sample, "") for sample in list(df.index)])),
                        "sample_id": list(df.index),
                        "directory": file_path,
                        "organization": organization
                    }
                    print(f" | {file_path}  ~{file_size}{FILE_SIZE_UNIT}")

                    # check here to prevent duplpicates
                    if file_dict not in file_list:
                        file_list.append(file_dict)
                        
    if not file_list:
        print(" | No files found for file types:", file_types)
    else:
        print(f" | Total size for these files: {total_size}{FILE_SIZE_UNIT}")
    
    return file_list



def process_files_for_processed(directory, file_types, organization, cor_dict):
    """   
    Recursively scans the given directory for processed data files whose names end with one of the specified file_types.
    Each found file is registered in the RO‑Crate with enriched properties.
    The file’s base name (without extension) is used to look up its metadata record.
    
    Args:
        directory (str): The directory to search.
        file_types (list): List of file extensions to match.
        metadata_dict (dict): Dictionary mapping "Patient ID" to metadata entries.
        crate (ROCrate): The RO‑Crate instance in which to register files.
        organization (str): Organization that the data files are from, can be modified in params.py
        cor_dict: The dictionary containing the keys as sample_id and values as patient_id
    
    Returns:
        list: A list of dictionaries summarizing the file details.
    """
    file_list = []
    total_size = 0
    for root, _, files in os.walk(directory):
        for file in files:
            if os.path.splitext(file)[1] in PROCESSED_FILE_TYPES:
                full_path = os.path.join(root, file)
                relative_path = os.path.relpath(full_path, directory)
                file_path = f"./{relative_path}"
                file_size = round(os.path.getsize(full_path) / CONVERT_FROM_BYTES)
                total_size += file_size

                sample_name, _ = os.path.splitext(file)  # name of FASTQ/FASTA is sample name

                # establish file name
                file_dict = {
                    "file_name": file,
                    "file_size": file_size, 
                    "patient_id": cor_dict.get(sample_name, ""),
                    "sample_id": sample_name,
                    "directory": file_path,
                    "organization": organization
                }
                # print("Processing the Processed files")
                print(f" | {file_path}  ~{file_size}{FILE_SIZE_UNIT}")

                # check here to prevent duplpicates
                if file_dict not in file_list:
                    file_list.append(file_dict)

    if not file_list:
        print(" | No files found for file types:", file_types)
    else:
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
    
    print(f"\nProcessing raw files ({', '.join(RAW_FILE_TYPES)})")
    raw_files = process_files_for_raw(directory, RAW_FILE_TYPES, organization, cor_dict)
    
    print(f"\nProcessing processed files ({', '.join(PROCESSED_FILE_TYPES)})")
    processed_files = process_files_for_processed(directory, PROCESSED_FILE_TYPES, organization, cor_dict)
    
    print(f"\nProcessing summarised files ({', '.join(SUMMARISED_FILE_TYPES)})")
    summarised_files = process_files_for_summarized(directory, SUMMARISED_FILE_TYPES, organization, cor_dict)
    
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
