This folder contains metadata and sample-to-patient documents. All of the files are in .json format, except the script.

1. sample_metadata_ori.json: This file is made by the previous intake, including 100 samples and 100 patients.  One patient corresponds to one sample (ex: Patient-ICGC_0001, Sample-LC_Sample1)

2. sample_metadata.json: This file is the updated metadata, expanding the sample size from 100 to 500. One patient has multiple samples. The detailed update procedure can be found in mimic_rawfiles_generator.ipynb

3. sample_to_patient.json: This file provide the mapping information between samples and patients. Key is sample and value is patient.

4. mimic_rawfiles_generator.ipynb: Script for updating the metadata made by previous intake and generating the counts.csv files. (When running this script in your environment, remember to change the file path)
