# R Implementation Outline for REDMANE Metadata Generator

This document outlines the high-level approach to replicating the Python metadata generator's functionality using R.

## Core Logic

### 1. File Scanning
- Use `fs::dir_ls(recurse = TRUE)` or `list.files(recursive = TRUE, full.names = TRUE)` to scan the dataset directory.
- `fs::dir_ls` is recommended for better handling of paths and metadata.

### 2. Configuration
- Use `jsonlite::fromJSON("file_types.json")` to load configurable file extensions.
- If the file doesn't exist, use a named list as a default (similar to the Python `DEFAULT_FILE_TYPES`).

### 3. Categorization
- Iterate through files and check extensions against the loaded configuration.
- Use `tools::file_ext()` to extract extensions.
- Map extensions to categories ("raw", "processed", "summarised").

### 4. Metadata Extraction
- **File Size:** Use `file.size()` or `file.info()$size`. Convert to KB.
- **Patient/Sample Mapping:**
    - Load `sample_to_patient.json` using `jsonlite::fromJSON()`.
    - Extract sample ID from filename (e.g., using `strsplit` or `stringr::str_extract`).
    - Look up Patient ID in the mapping list/dataframe.

### 5. RO-Crate Generation
- Construct a list structure mirroring the RO-Crate JSON format.
- Use `jsonlite::toJSON(metadata, auto_unbox = TRUE, pretty = TRUE)` to generate the final JSON output.

### 6. HTML Report
- **Summary Statistics:** Calculate totals using `dplyr` (e.g., `n_distinct` for patients/samples, `sum` for sizes).
- **Templating:**
    - Use `htmltools` to build the page programmatically.
    - OR use `rmarkdown::render()` with a parameterized Rmd template.
    - OR use `shiny` for an interactive report if needed.
- **Output:** Write the HTML to `output.html`.

## Example Snippets

```r
library(jsonlite)
library(fs)
library(dplyr)

# Load config
file_types <- fromJSON("file_types.json")

# Scan files
files <- dir_ls("path/to/data", recurse = TRUE, type = "file")

# Process a single file
process_file <- function(file_path) {
  info <- file_info(file_path)
  ext <- tools::file_ext(file_path)
  
  # Determine category...
  # Determine sample/patient ID...
  
  list(
    file_name = path_file(file_path),
    file_size = round(info$size / 1024),
    directory = as.character(file_path)
    # ...
  )
}
```

## Coordination & Next Steps
- **File Extensions:** Confirm with the workflows team that `file_types.json` covers all expected formats.
- **Logging:** Coordinate with web dev to implement metadata upload logging (e.g., POST to an API endpoint).
- **Styling:** Ensure the R output uses the same CSS (`output.css`) as the Python version for consistency.
