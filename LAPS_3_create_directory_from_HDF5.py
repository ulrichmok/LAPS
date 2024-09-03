## LAPS project data convertion, storage, and plotting based on the .json schema file
# Ekaterina Bolotskaya
# 07/17/2023

def LAPS_3_create_directory_from_HDF5(hdf5_file, output_directory, schema_file_path, json, os, np, h5py):
    """
    Recreate the original directory structure from the HDF5 file.
    The function will recreate the directory structure and populate it with the data stored in the HDF5 file.

    Parameters:
    hdf5_file (str): The path to the HDF5 file that contains the data and group structure.
    output_directory (str): The path to the output directory where the recreated directory structure will be stored.
    schema_file_path (str): The path where the recreated JSON schema file will be saved.
    json (module): The JSON module to load and parse the metadata JSON from the HDF5 attribute.
    os (module): The operating system module for file and directory operations.
    np (module): The NumPy module for numerical operations.
    h5py (module): The h5py module for working with HDF5 files.

    Returns:
    None

    This function reads the HDF5 file, recreates the directory structure, and populates it with the data stored in the HDF5 file.
    It recursively processes groups and datasets in the HDF5 file and creates the corresponding directory structure and files on the disk.
    The metadata JSON is retrieved from the attribute of the root group in the HDF5 file and saved to a separate JSON file.
    """

    # Function to create nested directories based on group structure
    def create_nested_directories(path):
        """
        Recursively create nested directories based on the group structure.
        """
        if not os.path.exists(path):
            os.makedirs(path)

    # Recursive function to handle groups and datasets
    def process_group(group, group_path):
        """
        Recursively process groups and datasets.
        """
        create_nested_directories(group_path)

        for name, item in group.items():
            if isinstance(item, h5py.Dataset):
                dataset_name = name
                _, extension = os.path.splitext(dataset_name)
                file_path = os.path.join(group_path, dataset_name)

                if extension in [".csv", ".txt", ".xls", ".xlsx"]:
                    data = item[()]
                    with open(file_path, "wb") as file:
                        file.write(data)  # write the dataset data to a file

                elif extension in [".jpg", ".jpeg", ".png"]:
                    data = item[()]
                    with open(file_path, "wb") as file:
                        file.write(data.tobytes())  # write the image data to a file

                else:
                    data = item[()]
                    with open(file_path, "wb") as file:
                        file.write(data)  # write the data to a file

            elif isinstance(item, h5py.Group):
                sub_group_path = os.path.join(group_path, name)
                process_group(item, sub_group_path)  # recursively process the sub-group

    # Open HDF5 file in read mode
    with h5py.File(hdf5_file, "r") as f:
        # Retrieve the metadata JSON from the attribute
        metadata_str = f.attrs.get("Schema_json", "")  # get the metadata JSON as a string from the attribute
        metadata = json.loads(metadata_str)  # convert the metadata JSON string to a dictionary

        # Recreate the directory structure
        for group_name, group in f.items():
            group_path = os.path.join(output_directory, group_name)
            process_group(group, group_path)  # process each group in the HDF5 file

    # Write the metadata JSON to a file next to the Recreated_Directory
    with open(schema_file_path, "w") as schema_file:
        json.dump(metadata, schema_file, indent=4)  # write the metadata dictionary to a JSON file

    print("Directory recreated successfully.")
    print(output_directory)