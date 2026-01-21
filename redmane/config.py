import json
import sys
# Config module: Implements 'Fail Loudly' policy for missing configurations.
from pathlib import Path

REQUIRED_KEYS = [
    "raw_file_extensions",
    "processed_file_extensions",
    "summarised_file_extensions"
]

# Backward compatibility aliases
ALIASES = {
    "raw_file_types": "raw_file_extensions",
    "processed_file_types": "processed_file_extensions",
    "summarised_file_types": "summarised_file_extensions"
}

EXAMPLE_CONFIG = {
    "raw_file_extensions": [".fastq", ".fasta"],
    "processed_file_extensions": [".bam", ".cram"],
    "summarised_file_extensions": [".vcf", ".csv", ".tsv"]
}

def print_error_and_exit(message):
    # Prints a clear error message and exits with status 1.
    print("\n" + "="*60)
    print("CONFIGURATION ERROR")
    print("="*60)
    print(message)
    print("\nExample valid config.json:")
    print(json.dumps(EXAMPLE_CONFIG, indent=4))
    print("="*60 + "\n")
    sys.exit(1)

def find_config_path(dataset_dir):
    # Locates config.json in the dataset root and fails loudly if missing.
    config_path = dataset_dir / "config.json"
    if not config_path.exists():
        print_error_and_exit(
            f"Missing configuration file!\n"
            f"Checked path: {config_path.resolve()}\n\n"
            f"config.json is MANDATORY and must be placed at the root of your dataset directory."
        )
    return config_path

def load_config(config_path):
    # Parses config.json and fails loudly on JSON syntax errors.
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print_error_and_exit(
            f"Invalid JSON format in: {config_path}\n"
            f"Error: {e}"
        )
    except Exception as e:
        print_error_and_exit(
            f"Could not read config file: {config_path}\n"
            f"Error: {e}"
        )

def normalize_and_validate_config(config_dict):
    # Validates keys, handles aliases, and returns a normalized dictionary.
    normalized = {}
    
    # Check for required keys or aliases
    for key in REQUIRED_KEYS:
        # Check standard key
        if key in config_dict:
            normalized[key] = config_dict[key]
        else:
            # Check alias
            alias_found = False
            for alias, target in ALIASES.items():
                if target == key and alias in config_dict:
                    print(f"WARNING: '{alias}' is deprecated. Please use '{key}' instead.")
                    normalized[key] = config_dict[alias]
                    alias_found = True
                    break
            
            if not alias_found:
                print_error_and_exit(f"Missing required configuration key: '{key}'")

    # Validate values
    for key, extensions in normalized.items():
        if not isinstance(extensions, list):
            print_error_and_exit(f"Value for '{key}' must be a LIST of strings.")
        
        if not extensions:
             print_error_and_exit(f"List for '{key}' cannot be empty. Please specify at least one extension.")

        for ext in extensions:
            if not isinstance(ext, str):
                print_error_and_exit(f"Invalid extension in '{key}': {ext} (Must be a string)")
            if not ext.startswith("."):
                print_error_and_exit(f"Invalid extension in '{key}': '{ext}' (Must start with a dot, e.g., '.fastq')")

    # Map to simpler keys for internal usage (raw, processed, summarised)
    # This matches expectations in check_dataset (raw, processed, summarised)
    internal_map = {
        "raw_file_extensions": "raw",
        "processed_file_extensions": "processed",
        "summarised_file_extensions": "summarised"
    }
    
    final_config = {}
    for conf_key, internal_key in internal_map.items():
        final_config[internal_key] = normalized[conf_key]

    return final_config
