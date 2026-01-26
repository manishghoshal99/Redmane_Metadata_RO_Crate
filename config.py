import sys

REQUIRED_KEYS = [
    "raw_file_extensions", 
    "processed_file_extensions", 
    "summarised_file_extensions",
    "sample_to_patient"
]

def print_error_and_exit(message):
    print(f"\n[ERROR] {message}")
    sys.exit(1)

def validate_config(config_dict, config_path):
    if not isinstance(config_dict, dict):
        print_error_and_exit(f"Config file must be a JSON object. File: {config_path}")

    for key in REQUIRED_KEYS:
        if key not in config_dict:
             print_error_and_exit(f"Missing required key: '{key}' in {config_path}")

    for key in ["raw_file_extensions", "processed_file_extensions", "summarised_file_extensions"]:
        extensions = config_dict[key]
        if not isinstance(extensions, list) or not extensions:
             print_error_and_exit(f"'{key}' must be a non-empty list of extensions (e.g., ['.fastq']).")

        for ext in extensions:
            if not isinstance(ext, str) or not ext.startswith("."):
                print_error_and_exit(f"Invalid extension '{ext}' in '{key}'. Must start with a dot.")

    if not isinstance(config_dict["sample_to_patient"], dict):
         print_error_and_exit("'sample_to_patient' must be a dictionary.")

    if "counts_format" in config_dict and not isinstance(config_dict["counts_format"], bool):
        print_error_and_exit("'counts_format' must be a boolean.")

    return config_dict
