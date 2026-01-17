# REDMANE Metadata Generator

*Created by REDMANE Data Ingestion Team Summer 2025*
*Updated by REDMANE Data Ingestion Team 2025 sem1*

A Python package for scanning datasets, extracting metadata, and generating RO-Crate compatible JSON outputs and HTML summaries.

## Overview

This tool allows researchers to ingest datasets (sequencing and imaging data), categorize files, and generate a standardized metadata report. It supports:
- **Recursive Scanning:** Automatically finds files in deep directory structures.
- **Configurable File Types:** Custom `config.json` to define file extensions.
- **Dynamic Reporting:** Generates an interactive HTML viewer for the metadata.
- **RO-Crate Support:** Outputs standard research object metadata.

## Quick Start (3-Minute Demo)

To see the tool in action using the included demo dataset:

```bash
# 1. Install the package (Optional, or run via wrapper)
pip install -e .

# 2. Run the wrapper script on the demo dataset
python3 update_local.py --dataset demo/demo_dataset
```

This will find the `config.json` in the demo folder and generate `output.json` and `output.html` in your current directory.

## Usage

**IMPORTANT:** A `config.json` file is **MANDATORY** and must be placed at the root of your dataset directory. The tool will fail if this file is missing or invalid.

### Running via Wrapper
We provide a wrapper script `update_local.py` for backward compatibility:

```bash
python3 update_local.py --dataset /path/to/your/data
```

### Running via CLI (if installed)
```bash
redmane-ingest --dataset /path/to/your/data
```

This will generate:
- `output.json`: The raw metadata (RO-Crate format).
- `output.html`: The human-readable report.

**Viewing the Report:**
The HTML report loads the JSON dynamically. To view it locally (bypassing browser security restrictions), strict browsers may require a local server:
```bash
python3 -m http.server
# Open http://localhost:8000/output.html
```

## Configuration (`config.json`)

You must define file extensions in `config.json` at the dataset root. No default fallbacks are used.

**Example `config.json`:**
```json
{
  "raw_file_extensions": [".fastq", ".czi", ".nd2"],
  "processed_file_extensions": [".bam", ".ome.tif"],
  "summarised_file_extensions": [".vcf", ".csv", ".tsv"]
}
```

**Schema Requirements:**
*   All keys are required: `raw_file_extensions`, `processed_file_extensions`, `summarised_file_extensions`.
*   Values must be non-empty lists of strings.
*   Extensions must start with a dot.

## Project Structure

- `redmane/` – Main package source code.
- `update_local.py` – Wrapper script for executing the generator.
- `files/` – Legacy sample data.
- `demo/` – Demo dataset.
- `test_imaging/`, `test_WGS/` – Test data placeholders.

## Development

- **Adding new defaults:** Edit `redmane/params.py`.
- **Changing HTML style:** Edit the template in `redmane/generate_html.py`.
