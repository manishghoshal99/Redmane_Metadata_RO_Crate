# Technical Diary: REDMANE Metadata Generator

### Configuration & Validation
- **Mandatory Configuration**: The tool strictly enforces the presence of `config.json` at the dataset root. No hardcoded defaults exist anymore to prevent hidden behavior.
- **Fail Loudly**: If `config.json` is missing, invalid, or lacks required keys, the tool exits immediately with a specific error message and an example of a valid config.
- **Validation Logic**: Implemented in `redmane/config.py`. It explicitly checks that values are non-empty lists of strings and that extensions start with a dot (e.g., `.fastq`).
- **Schema**: The keys `raw_file_extensions`, `processed_file_extensions`, and `summarised_file_extensions` are required. Backward compatibility aliases (e.g., `raw_file_types`) are supported but trigger warnings.

### Architecture
- **Entry Point**: `setup.py` defines the `redmane-ingest` console script, which points to `redmane.generator:main`.
- **Module Structure**: Code is modularized into `redmane/` (core logic) and `demo/` (verification data).
- **Scanning Logic**: Uses `pathlib.rglob('*')` for efficient recursive scanning. It matches files against the extensions defined in the loaded configuration.
- **Parsing**: logic used for naming the sample ID is generally `filename.split('.')[0]`, but for summarised files (`.csv`/`.tsv`), it attempts to parse the file index using pandas.
- **Robustness**: If parsing a summary file fails (e.g., empty file), the tool logs a warning and proceeds, ensuring a single bad file doesn't crash the entire run.

### Setup & Output
- **Installation**: Standard `pip install .` installs dependencies (`pandas`, `rocrate`, `numpy`) and the CLI tool.
- **Outputs**:
  - `output.json`: The RO-Crate metadata bundle.
  - `output.html`: A dynamic HTML viewer that fetches the JSON for display.
  - `rocrate/`: A folder containing the RO-Crate payload.
