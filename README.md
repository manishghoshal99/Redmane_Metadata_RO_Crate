# Redmane Metadata Generator

*Created by REDMANE Data Ingestion Team*

## Overview

This project automates the organization and metadata enrichment of research files. The script `update_local_v1.py` scans files based on a strict configuration, associates metadata, and generates structured outputs in JSON and HTML formats for easy access and visualization.

## Key Features
- **Unified Configuration**: Single `config.json` defining file types and patient-sample mapping.
- **Strict Validation**: Fails loudly if configuration is invalid or missing.
- **Flexible Scanning**: Supports multiple file types and summarised data formats (including counts matrices).
- **Self-Contained Output**: Generates a standalone HTML report (`output.html`) and JSON summary (`output.json`).

## Project Structure

- `update_local_v1.py`: Main entry point script.
- `config.py`: Configuration validation logic.
- `auxiliary.py`: File scanning and sample extraction logic.
- `generate_html.py`: Generates the HTML report.
- `examples/`: Example datasets (`example_docx`, `example_counts`).

## Usage

1. **Prepare your dataset**:
   Ensure your dataset directory has a `config.json` (see Configuration below).

2. **Run the generator**:
   ```bash
   python update_local_v1.py /path/to/dataset --verbose
   ```
   
   Options:
   - `--verbose`: Print detailed scanning logs.
   - `--counts-tsv`: Treat summarised TSV files as counts matrices (header contains Sample IDs). Can also be set in `config.json` via `"counts_format": true`.

3. **View Output**:
   Open `/path/to/dataset/output.html` in your web browser.

## Configuration

Place a `config.json` file in the root of your dataset directory.
Example:

```json
{
    "raw_file_extensions": [".fastq", ".fastq.gz"],
    "processed_file_extensions": [".bam"],
    "summarised_file_extensions": [".csv", ".tsv"],
    "counts_format": false,
    "sample_to_patient": {
        "Sample1": "PatientA",
        "Sample2": "PatientA",
        "Sample3": "PatientB"
    }
}
```

## Requirements

- Python 3.x
- Pandas

## Improvements over Legacy Version
- Removed RO-Crate dependency for simpler deployment.
- Consolidated metadata mapping into `config.json`.
- Dropped local server requirement for HTML preview.
