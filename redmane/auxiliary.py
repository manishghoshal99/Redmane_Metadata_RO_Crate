
import os
from pathlib import Path
import pandas as pd
from .params import CONVERT_FROM_BYTES, FILE_SIZE_UNIT

def extract_sample_id(filename: str, extensions: list) -> str:
    """
    Extracts sample ID from filename by removing known extensions.
    Handles multi-dot extensions like .tar.gz if they are in the list.
    If no known extension is matched, falls back to splitting off the last dot.
    """
    name_lower = filename.lower()
    # Sort extensions by length (descending) to match .fastq.gz before .gz
    sorted_exts = sorted(extensions, key=len, reverse=True)
    
    for ext in sorted_exts:
        if name_lower.endswith(ext.lower()):
            return filename[:-len(ext)]
            
    # Fallback: simple splitext
    return os.path.splitext(filename)[0]

def scan_dataset(data_dir: Path, file_types: dict, metadata_dict: dict, sample_to_patient: dict, organization: str, crate):
    """
    Recursively scans the dataset directory and categorizes files.
    Registers files in the RO-Crate.
    """
    files_by_category = {cat: [] for cat in file_types}
    
    print(f" | Scanning {data_dir} recursively...")
    
    # Flatten file types for easy lookup and extraction
    all_extensions = []
    ext_to_cat = {}
    for cat, extensions in file_types.items():
        files_by_category[cat] = [] # Ensure keys exist
        for ext in extensions:
            ext_to_cat[ext.lower()] = cat
            all_extensions.append(ext)

    total_size = 0
    
    # Sort extensions for matching
    sorted_exts_match = sorted(ext_to_cat.keys(), key=len, reverse=True)

    for file_path in data_dir.rglob('*'):
        if file_path.is_file():
            if file_path.name.startswith('.'):
                continue
                
            name = file_path.name.lower()
            category = None
            
            for ext in sorted_exts_match:
                if name.endswith(ext):
                    category = ext_to_cat[ext]
                    break
            
            if category is None:
                continue

            # Calculate size
            size_bytes = file_path.stat().st_size
            size_kb = round(size_bytes / CONVERT_FROM_BYTES)
            total_size += size_kb
            
            # Determine Sample ID using robust extraction
            sample_id = extract_sample_id(file_path.name, all_extensions)
            
            # Look up patient ID
            patient_id = sample_to_patient.get(sample_id, "")
            
            sample_ids_list = [sample_id]
            patient_ids_list = [patient_id] if patient_id else []
            
            # Special handling for summarised files (lookup internal CSV IDs)
            if category == 'summarised' and file_path.suffix in ['.csv', '.tsv']:
                try:
                    sep = '\t' if file_path.suffix == '.tsv' else ','
                    try:
                        # Attempt to read index
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
            try:
                rel_path = file_path.relative_to(data_dir)
            except ValueError:
                rel_path = file_path.name
            
            # Crate registration disabled/commented or minimal? 
            # Prompt says "Separate RO-Crate functionality... but ensure the generator’s core logic does not require RO-Crate to run."
            # We will keep it safe for now:
            if crate:
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
