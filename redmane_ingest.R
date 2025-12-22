#!/usr/bin/env Rscript

# Dependencies check
if (!requireNamespace("jsonlite", quietly = TRUE)) stop("Package 'jsonlite' needed for this script to work. Please install it.", call. = FALSE)
if (!requireNamespace("fs", quietly = TRUE)) stop("Package 'fs' needed for this script to work. Please install it.", call. = FALSE)
if (!requireNamespace("optparse", quietly = TRUE)) stop("Package 'optparse' needed for this script to work. Please install it.", call. = FALSE)

library(jsonlite)
library(fs)
library(optparse)

# Default configuration
DEFAULT_FILE_TYPES <- list(
  raw = c(".fastq", ".fastq.gz", ".bam", ".cram", ".czi", ".tif", ".tiff", ".nd2", ".lif", ".lsm", ".oib", ".oif"),
  processed = c(".bam", ".cram", ".ome.tif", ".ome.tiff"),
  summarised = c(".vcf", ".maf", ".csv", ".tsv")
)

# Constants
ORGANIZATION <- "National Academy of Taiwan"
FILE_SIZE_UNIT <- "KB"
CONVERT_FROM_BYTES <- 1024
OUTPUT_JSON <- "output.json"

# Helper functions
load_file_types <- function(path) {
  if (!is.null(path) && file.exists(path)) {
    message(" | Loading file types from ", path)
    return(fromJSON(path))
  }

  # Check if file_types.json exists in dataset dir (passed as context usually, but here we might need to handle it)
  # For now, return default
  return(DEFAULT_FILE_TYPES)
}

scan_dataset <- function(data_dir, file_types, sample_to_patient) {
  message(" | Scanning ", data_dir, " recursively...")

  # Flatten extensions for easier lookup
  ext_map <- list()
  for (cat in names(file_types)) {
    for (ext in file_types[[cat]]) {
      ext_map[[tolower(ext)]] <- cat
    }
  }

  # Sort extensions by length (longest first) to handle .fastq.gz vs .gz
  sorted_exts <- names(ext_map)[order(nchar(names(ext_map)), decreasing = TRUE)]

  all_files <- dir_ls(data_dir, recurse = TRUE, type = "file")

  files_by_category <- list(
    raw = list(),
    processed = list(),
    summarised = list()
  )

  total_size <- 0

  for (file_path in all_files) {
    fname <- path_file(file_path)
    fname_lower <- tolower(fname)

    category <- NULL
    for (ext in sorted_exts) {
      if (endsWith(fname_lower, ext)) {
        category <- ext_map[[ext]]
        break
      }
    }

    if (is.null(category)) next

    # File info
    info <- file_info(file_path)
    size_kb <- round(info$size / CONVERT_FROM_BYTES)
    total_size <- total_size + size_kb

    # Sample/Patient ID
    # Simple logic: split by first dot
    sample_id <- strsplit(fname, "\\.")[[1]][1]

    patient_id <- ""
    if (!is.null(sample_to_patient[[sample_id]])) {
      patient_id <- sample_to_patient[[sample_id]]
    }

    # Prepare record
    record <- list(
      file_name = fname,
      file_size = size_kb,
      directory = as.character(path_rel(file_path, start = data_dir)),
      organization = ORGANIZATION,
      sample_id = sample_id,
      patient_id = patient_id
    )

    # To mimic Python output structure which uses lists of records
    files_by_category[[category]] <- append(files_by_category[[category]], list(record))

    message(sprintf("   + Found %s: %s (%d KB)", category, fname, size_kb))
  }

  message(" | Total size: ", total_size, " KB")
  return(files_by_category)
}


# Main logic
main <- function() {
  option_list <- list(
    make_option(c("-d", "--dataset"),
      type = "character", default = NULL,
      help = "Path to dataset directory", metavar = "DIR"
    ),
    make_option(c("-f", "--filetypes"),
      type = "character", default = NULL,
      help = "Path to file_types.json", metavar = "FILE"
    )
  )

  opt_parser <- OptionParser(option_list = option_list)
  opt <- parse_args(opt_parser)

  if (is.null(opt$dataset)) {
    print_help(opt_parser)
    stop("Dataset directory must be provided", call. = FALSE)
  }

  data_dir <- opt$dataset
  if (!dir_exists(data_dir)) stop("Directory does not exist: ", data_dir)

  # Load configs
  # Try to find file_types.json in data_dir if not specified
  ft_path <- opt$filetypes
  if (is.null(ft_path)) {
    pot_path <- file.path(data_dir, "file_types.json")
    if (file.exists(pot_path)) ft_path <- pot_path
  }
  file_types <- load_file_types(ft_path)

  # Load metadata mappings (assuming they are in known locations relative to script or data?)
  # The Python script expected them in 'sample_metadata' relative to script.
  # We will look in data_dir for simplicity or hardcode for now as per params.py
  # or relative to this script location.

  # Let's check typical location
  script_dir <- dirname(sub("--file=", "", commandArgs(trailingOnly = FALSE)[4]))
  # Adjust for run via Rscript/interactive
  if (length(script_dir) == 0 || script_dir == ".") script_dir <- getwd()

  # Try look for mapping in redmane/sample_metadata/ relative to CWD if script path fails
  map_path <- file.path(script_dir, "redmane", "sample_metadata", "sample_to_patient.json")
  if (!file.exists(map_path)) {
    # Fallback to CWD
    map_path <- "redmane/sample_metadata/sample_to_patient.json"
  }

  sample_to_patient <- list()
  if (file.exists(map_path)) {
    sample_to_patient <- fromJSON(map_path)
  } else {
    warning("Sample to Patient mapping not found at ", map_path)
  }

  # Scan
  files_map <- scan_dataset(data_dir, file_types, sample_to_patient)

  # Build JSON
  output_data <- list(
    data = list(
      location = as.character(fs::path_abs(data_dir)),
      file_size_unit = FILE_SIZE_UNIT,
      files = files_map
    )
  )

  # Write JSON
  write_json(output_data, OUTPUT_JSON, pretty = TRUE, auto_unbox = TRUE)
  message("\nJSON file generated at: ", file.path(getwd(), OUTPUT_JSON))

  # Generate HTML viewer
  # Creates a simple HTML file that fetches the generated JSON.

  message("Generating HTML viewer...")
  # Embed template for standalone R script
  tpl <- '<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>REDMANE Data Summary</title>
    <style>body{font-family:sans-serif;margin:20px;line-height:1.6}.container{max-width:1200px;margin:0 auto}h1{color:#2c3e50}.loading{text-align:center;padding:50px}</style>
</head>
<body>
    <div class="container">
        <h1>Files Summary</h1>
        <div id="content"><div class="loading">Loading metadata from <code>output.json</code>...</div></div>
    </div>
    <script>
        fetch("output.json").then(r=>r.json()).then(d=>{
            document.getElementById("content").innerHTML = `<pre>${JSON.stringify(d, null, 2)}</pre>`;
            // Basic stats rendering
            const f = d.data.files;
            const count = (f.raw?f.raw.length:0) + (f.processed?f.processed.length:0) + (f.summarised?f.summarised.length:0);
            document.getElementById("content").innerHTML = `<h2>Total Files: ${count}</h2><p>Data loaded successfully. See JSON response for details.</p>`;
        }).catch(e=>document.getElementById("content").innerHTML=`Error: ${e.message}<br>Try python -m http.server`);
    </script>
</body></html>'

  # Write HTML file
  writeLines(tpl, "output.html")
  message("HTML viewer generated at: ", file.path(getwd(), "output.html"))
}

main()
