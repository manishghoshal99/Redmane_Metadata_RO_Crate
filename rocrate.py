# Extracted rocrate parts from update_local_v1.py
# Have not ensured functionality as not priority
from rocrate.rocrate import ROCrate

                
                # establish crate
                crate.add_file(full_path, properties={
                    "fileSize": f"{file_size}{FILE_SIZE_UNIT}", 
                    "patient_id": cor_dict.get(sample_name, ""),
                    "sample_id": sample_name,
                    
                })

                    crate.add_file(full_path, properties={
                        "fileSize": f"{file_size}{FILE_SIZE_UNIT}",
                        "patient_id": list(set([cor_dict.get(sample, "") for sample in list(df.index)])),
                        "sample_id": list(df.index),
                    })
                
                # establish crate
                crate.add_file(full_path, properties={
                    "fileSize": f"{file_size}{FILE_SIZE_UNIT}", 
                    "patient_id": cor_dict.get(sample_name, ""),
                    "sample_id": sample_name,
                    
                })
    # Create a new RO‑Crate instance and set top-level metadata.
    crate = ROCrate()
    crate.root_dataset.name = "Research Object"
    crate.root_dataset.description = f"Research object created from files in {directory}"

    # Write out the full RO‑Crate package to a folder (e.g. "rocrate").
    rocrate_folder = Path(output_file).parent / "rocrate"
    crate.write(rocrate_folder)
    print(f"RO‑Crate written to {rocrate_folder}")