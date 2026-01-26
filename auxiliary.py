
import os
from pathlib import Path
import pandas as pd

# Constants can be defined here or imported. 
# Since we removed params.py, we define them here or expect them passed.
CONVERT_FROM_BYTES = 1024
FILE_SIZE_UNIT = "KB"

def extract_sample_id(filename: str, extensions: list) -> str:
    # Extracts sample ID from filename by removing known extensions (longest match first).
    name_lower = filename.lower()
    # Sort extensions by length (descending) to match .fastq.gz before .gz
    sorted_exts = sorted(extensions, key=len, reverse=True)
    
    for ext in sorted_exts:
        if name_lower.endswith(ext.lower()):
            return filename[:-len(ext)]
            
    # Fallback: simple splitext
    return os.path.splitext(filename)[0]

def scan_dataset(data_dir: Path, config: dict, organization: str = "WEHI"):
    """
    Recursively scans the dataset directory, categorizes files based on unified config,
    and returns a structured list of file metadata.
    """
    # Map simpler keys for mapping logic
    file_types = {
        "raw": config["raw_file_extensions"],
        "processed": config["processed_file_extensions"],
        "summarised": config["summarised_file_extensions"]
    }
    sample_to_patient = config["sample_to_patient"]
    counts_format = config.get("counts_format", False)

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
            
            # Look up patient ID (default lookup)
            patient_id = sample_to_patient.get(sample_id, "")
            
            sample_ids_list = [sample_id]
            patient_ids_list = [patient_id] if patient_id else []
            
            # Special handling for summarised files
            if category == 'summarised' and file_path.suffix in ['.csv', '.tsv', '.maf']:
                try:
                    # Determine separator
                    sep = ','
                    if file_path.suffix == '.tsv':
                        sep = '\t'
                    elif file_path.suffix == '.maf':
                        sep = '\t' 
                    
                    extra_args = {}
                    if file_path.suffix == '.maf':
                         extra_args['comment'] = '#'

                    # If using counts_format for TSV, reading differs
                    if counts_format and file_path.suffix == '.tsv':
                         # Read first row (header) as samples
                         df = pd.read_csv(file_path, sep=sep, index_col=0, nrows=0)
                         curr_samples = list(df.columns)
                         if curr_samples:
                            sample_ids_list = curr_samples
                    else:
                        # Standard behaviour: read index column
                        df = pd.read_csv(file_path, index_col=0, sep=sep, **extra_args)
                        if not df.empty:
                            sample_ids_list = list(df.index.astype(str))

                    # Map all collected samples to patients
                    p_ids = set()
                    for s in sample_ids_list:
                        pid = sample_to_patient.get(s)
                        if pid:
                            p_ids.add(pid)
                    patient_ids_list = list(p_ids)

                except Exception as e:
                    # e.g. empty file or parsing error
                    # We continue gracefully, treating it as a single-sample file (bucketed by filename)
                    # print(f"   ! Could not read summary file {file_path.name}: {e}")
                    pass

            # Format for output
            final_sample_id = sample_ids_list if len(sample_ids_list) > 1 else sample_ids_list[0]
            final_patient_id = patient_ids_list if len(patient_ids_list) > 1 else (patient_ids_list[0] if patient_ids_list else "")
            
            try:
                rel_path = file_path.relative_to(data_dir)
            except ValueError:
                rel_path = file_path.name
            
            record = {
                "file_name": file_path.name,
                "file_size": size_kb,
                "directory": f"./{rel_path}",
                "organization": organization,
                "sample_id": final_sample_id,
                "patient_id": final_patient_id
            }
            
            files_by_category[category].append(record)
            
            # We can log here if needed, or rely on the main script's verbose flag to print the result

    print(f" | Total size: {total_size} {FILE_SIZE_UNIT}")
    return files_by_category