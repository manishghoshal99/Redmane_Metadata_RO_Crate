# Redmane Metadata Generator

Organise and enrich research files with metadata.

## Usage

1. Create `config.json` in your dataset directory:
   ```json
   {
       "raw_file_extensions": [".fastq"],
       "processed_file_extensions": [".bam"],
       "summarised_file_extensions": [".csv"],
       "sample_to_patient": {"SampleID": "PatientID"}
   }
   ```
2. Run the script:
   ```bash
   python update_local_v1.py /path/to/dataset --verbose
   ```
3. Check `output.html` in the dataset directory.

## Requirements
- Python 3
- Pandas
