# Redmane Metadata Generator

Organise and enrich research files with metadata.

## Features
- **Strict Configuration**: Validates `config.json` against a unified schema.
- **Legacy Support**: Falls back to `patient_sample_mapping.json` if `sample_to_patient` is missing in config.
- **Flexible Scanning**: robust sample ID extraction (handles `.fastq.gz`) and categorisation.
- **Summarised Data**: Supports CSV, TSV, and **MAF** formats.
- **Counts Matrices**: Supports TSV counts tables (samples in header) via CLI flag.
- **Static Reports**: Generates self-contained HTML reports.

## Usage

1. Create `config.json` in your dataset directory:
   ```json
   {
       "raw_file_extensions": [".fastq", ".fastq.gz"],
       "processed_file_extensions": [".bam"],
       "summarised_file_extensions": [".vcf", ".maf", ".tsv"],
       "sample_to_patient": {"SampleID": "PatientID"}
   }
   ```
   *(Note: Aliases like `raw_file_types` are supported with warnings.)*

2. Run the script:
   ```bash
   python update_local_v1.py /path/to/dataset --verbose
   ```

   **Options**:
   - `--counts-tsv`: Treat TSV files as counts matrices (Sample IDs in header).

3. Check `output.html` in the dataset directory.

## Requirements
- Python 3
- Pandas
