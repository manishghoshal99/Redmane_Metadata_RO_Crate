# REDMANE Metadata Generator

A tool to generate RO-Crate metadata and HTML reports for REDMANE datasets.

## Installation

```bash
pip install .
```

## Usage

```bash
redmane-ingest --dataset /path/to/data
```

### Optional Arguments

- `--file-types /path/to/file_types.json`: Specify a custom file types configuration. If not provided, the tool looks for `file_types.json` in the dataset directory, or uses built-in defaults.

## Configuration

You can place a `file_types.json` in your dataset directory to override default file extensions:

```json
{
  "raw": [".fastq", ".fastq.gz", ".bam"],
  "processed": [".bam", ".cram"],
  "summarised": [".vcf", ".csv"]
}
```
