# to be cleaned into a function for extracting sample and patient ID from summarised file types 
# where sample ID is not in the file name

import os
import pandas as pd
from params import * 

def process_files_for_summarised(directory, file_types, organization, cor_dict):
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
                    # print("Processing the summarised files")
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