import pytest
from config import validate_config

def test_valid_config():
    conf = {
        "raw_file_extensions": [".txt"],
        "processed_file_extensions": [".bam"],
        "summarised_file_extensions": [".csv"],
        "sample_to_patient": {"s": "p"}
    }
    assert validate_config(conf, "t") == conf

def test_alias_normalization():
    conf = {
        "raw_file_types": [".fastq"],  # Alias
        "processed_file_extensions": [".bam"],
        "summarised_file_extensions": [".csv"],
        "sample_to_patient": {}
    }
    validated = validate_config(conf, "t")
    assert "raw_file_extensions" in validated
    assert "raw_file_types" not in validated
    assert validated["raw_file_extensions"] == [".fastq"]

def test_invalid():
    with pytest.raises(SystemExit):
        validate_config({}, "t")
