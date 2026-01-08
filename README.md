# REDMANE Metadata Generator

A Python package for scanning datasets, extracting metadata, and generating RO-Crate compatible JSON outputs and HTML summaries.

## Overview

This tool allows researchers to ingest datasets (sequencing and imaging data), categorize files, and generate a standardized metadata report. It supports:
- **Recursive Scanning:** Automatically finds files in deep directory structures.
- **Configurable File Types:** Custom `config.json` to define file extensions.
- **Dynamic Reporting:** Generates an interactive HTML viewer for the metadata.
- **RO-Crate Support:** Outputs standard research object metadata.

## Quick Start (For Future Intakes)

### 1. Quick Start (3-Minute Demo)

To see the tool in action using the included demo dataset:

```bash
# 1. Install the package
pip install -e .

# 2. Run the demo
redmane-ingest --dataset demo/demo_dataset
```

This will find the `config.json` in the demo folder and generate `output.json` and `output.html`.

### 2. Usage (Your Data)

**IMPORTANT:** A `config.json` file is **MANDATORY** and must be placed at the root of your dataset directory. The tool will fail if this file is missing or invalid.

```bash
redmane-ingest --dataset /path/to/your/data
```

This will generate two files in your current directory:
- `output.json`: The raw metadata (RO-Crate format).
- `output.html`: The human-readable report.

**Viewing the Report:**
The HTML report loads the JSON dynamically. To view it locally (bypassing browser security restrictions), run a simple server:

```bash
python -m http.server
# Open http://localhost:8000/output.html
```

### 3. Configuration (`config.json`)
You can define which file extensions correspond to which category (Raw, Processed, Summarised) by placing a `config.json` file in your dataset directory.

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
*   Extensions must start with a dot (e.g., `.fastq`).
*   **Fail Loudly:** The tool will exit with an error if validation fails. No defaults are used.

## Project Structure

```
.
├── redmane/                 # Main package source code
│   ├── generator.py         # Core scanning and logic
│   ├── generate_html.py     # HTML report generation
│   ├── params.py            # Default constants
│   └── sample_metadata/     # Internal reference data
├── setup.py                 # Package installation config
├── config.json              # Default configuration example
└── README.md                # This documentation
```

## Development
- **Adding new defaults:** Edit `redmane/params.py`.
- **Changing HTML style:** Edit the template in `redmane/generate_html.py`.
