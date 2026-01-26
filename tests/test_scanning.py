import pytest
from auxiliary import scan_dataset, extract_sample_id

def test_extract_sample_id():
    exts = [".fastq.gz", ".fastq"]
    assert extract_sample_id("sample1.fastq.gz", exts) == "sample1"
    assert extract_sample_id("sample2.fastq", exts) == "sample2"

def test_scan_dataset_structure(tmp_path):
    (tmp_path / "f.txt").touch()
    conf = {
        "raw_file_extensions": [".txt"],
        "processed_file_extensions": [],
        "summarised_file_extensions": [],
        "sample_to_patient": {"f": "p1"}
    }
    res, _ = scan_dataset(tmp_path, conf, "test")
    assert len(res["raw"]) == 1
    assert res["raw"][0]["sample_id"] == "f"
    assert res["raw"][0]["patient_id"] == "p1"

def test_scan_counts_tsv(tmp_path):
    (tmp_path / "c.tsv").write_text("ID\tS1\nG\t1", encoding="utf-8")
    conf = {
        "raw_file_extensions": [],
        "processed_file_extensions": [],
        "summarised_file_extensions": [".tsv"],
        "sample_to_patient": {"S1": "P1"},
        "counts_format": True
    }
    res, _ = scan_dataset(tmp_path, conf, "test")
    assert res["summarised"][0]["sample_id"] == "S1"
