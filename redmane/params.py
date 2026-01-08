from pathlib import Path

# Base directory where params.py resides
BASE_DIR = Path(__file__).resolve().parent

OUTPUT_JSON_FILE_NAME = "output.json"
OUTPUT_HTML_FILE_NAME = "output.html"

CONVERT_FROM_BYTES = 1024
FILE_SIZE_UNIT = "KB"

# Default file types REMOVED. Strict config via config.json is now mandatory.
# See config.py for validation logic.

# Paths relative to this file
SAMPLE_METADATA_DIR = BASE_DIR / "sample_metadata"
METADATA = SAMPLE_METADATA_DIR / "sample_metadata.json"
SAMPLE_TO_PATIENT = SAMPLE_METADATA_DIR / "sample_to_patient.json"
ORGANIZATION = "National Academy of Taiwan"
