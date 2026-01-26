
import pytest
from config import validate_config

def test_valid_config():
    valid = {
        "raw_file_extensions": [".fastq"],
        "processed_file_extensions": [".bam"],
        "summarised_file_extensions": [".csv"],
        "sample_to_patient": {"S1": "P1"}
    }
    # Should not raise
    assert validate_config(valid, "test.json") == valid

def test_missing_key():
    invalid = {
        "raw_file_extensions": [".fastq"]
        # Missing others
    }
    with pytest.raises(SystemExit):
        validate_config(invalid, "test.json")

def test_invalid_extension_type():
    invalid = {
        "raw_file_extensions": "not-a-list",
        "processed_file_extensions": [],
        "summarised_file_extensions": [],
        "sample_to_patient": {}
    }
    with pytest.raises(SystemExit):
        validate_config(invalid, "test.json")

def test_invalid_extension_format():
    invalid = {
        "raw_file_extensions": ["fastq"], # Missing dot
        "processed_file_extensions": [],
        "summarised_file_extensions": [],
        "sample_to_patient": {}
    }
    with pytest.raises(SystemExit):
        validate_config(invalid, "test.json")

def test_counts_format_validity():
    valid = {
        "raw_file_extensions": [".fastq"],
        "processed_file_extensions": [".bam"],
        "summarised_file_extensions": [".tsv"],
        "sample_to_patient": {},
        "counts_format": True
    }
    assert validate_config(valid, "test.json")["counts_format"] is True

    invalid = valid.copy()
    invalid["counts_format"] = "yes" # Not bool
    with pytest.raises(SystemExit):
        validate_config(invalid, "test.json")
