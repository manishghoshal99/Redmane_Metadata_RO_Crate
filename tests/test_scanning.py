
import pytest
from pathlib import Path
from auxiliary import scan_dataset, extract_sample_id
import pandas as pd

def test_extract_sample_id():
    exts = [".fastq.gz", ".fastq", ".bam"]
    assert extract_sample_id("sample1.fastq.gz", exts) == "sample1"
    assert extract_sample_id("sample2.bam", exts) == "sample2"
    assert extract_sample_id("sample3.txt", exts) == "sample3" # Fallback

def test_scan_dataset_structure(tmp_path):
    # Setup dummy files
    (tmp_path / "raw").mkdir()
    (tmp_path / "raw" / "s1.fastq").touch()
    
    config = {
        "raw_file_extensions": [".fastq"],
        "processed_file_extensions": [],
        "summarised_file_extensions": [],
        "sample_to_patient": {}
    }
    
    result = scan_dataset(tmp_path, config)
    assert len(result["raw"]) == 1
    assert result["raw"][0]["file_name"] == "s1.fastq"
    assert result["raw"][0]["sample_id"] == "s1"

def test_scan_counts_tsv(tmp_path):
    # Setup counts TSV
    (tmp_path / "counts.tsv").write_text("GeneID\tS1\tS2\nGeneA\t10\t20", encoding="utf-8")
    
    config = {
        "raw_file_extensions": [],
        "processed_file_extensions": [],
        "summarised_file_extensions": [".tsv"],
        "sample_to_patient": {"S1": "P1"},
        "counts_format": True
    }
    
    result = scan_dataset(tmp_path, config)
    assert len(result["summarised"]) == 1
    entry = result["summarised"][0]
    assert entry["file_name"] == "counts.tsv"
    # Should detect S1 and S2
    assert "S1" in entry["sample_id"]
    assert "S2" in entry["sample_id"]
    # P1 matches S1, nothing for S2
    assert entry["patient_id"] == "P1"
