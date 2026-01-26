
import sys

# Define required keys for the unified config (removed aliasing for strictness)
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
    """
    Validates the unified configuration dictionary.
    Enforces presence of required keys, list types for extensions, and dot prefixes.
    Returns the validated config.
    """
    if not isinstance(config_dict, dict):
        print_error_and_exit(f"Config file root must be a dictionary. File: {config_path}")

    # 1. Check required keys
    for key in REQUIRED_KEYS:
        if key not in config_dict:
             print_error_and_exit(f"Missing required configuration key: '{key}' in {config_path}")

    # 2. Validate extensions
    extension_keys = ["raw_file_extensions", "processed_file_extensions", "summarised_file_extensions"]
    for key in extension_keys:
        extensions = config_dict[key]
        if not isinstance(extensions, list):
            print_error_and_exit(f"Value for '{key}' must be a LIST of strings.")
        
        if not extensions:
             print_error_and_exit(f"List for '{key}' cannot be empty. Please specify at least one extension.")

        for ext in extensions:
            if not isinstance(ext, str):
                print_error_and_exit(f"Invalid extension in '{key}': {ext} (Must be a string)")
            
            # Allow wildcard for special cases if needed, but per rule: dot prefixed
            if not ext.startswith("."):
                print_error_and_exit(f"Invalid extension in '{key}': '{ext}' (Must start with a dot, e.g., '.fastq')")

    # 3. Validate mapping
    mapping = config_dict["sample_to_patient"]
    if not isinstance(mapping, dict):
         print_error_and_exit("Value for 'sample_to_patient' must be a dictionary mapping Sample IDs to Patient IDs.")

    # Optional: counts_format check
    if "counts_format" in config_dict:
        if not isinstance(config_dict["counts_format"], bool):
            print_error_and_exit("Value for 'counts_format' must be a boolean (true/false).")

    return config_dict
