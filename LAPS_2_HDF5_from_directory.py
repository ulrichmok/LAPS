## LAPS project data convertion, storage, and plotting based on the .json schema file
# Ekaterina Bolotskaya
# 07/17/2023

def LAPS_2_HDF5_from_directory(scdir, data_folder, hdf5_file, json, os, np, h5py):
    """
    Convert the populated directory structure into HDF5 format for storage or exchange.
    The function will generate an HDF5 file, containing the data from the directory structure.

    Parameters:
    scdir (str): The path to the JSON schema file that defines the directory structure.
    data_folder (str): The path to the populated directory.
    hdf5_file (str): The output HDF5 file path where the data will be stored in HDF5 format.
    json (module): The JSON module to load and parse the JSON schema.
    os (module): The operating system module for file and directory operations.
    np (module): The NumPy module for numerical operations.
    h5py (module): The h5py module for working with HDF5 files.

    Returns:
    None

    This function reads the populated directory structure and converts it into HDF5 format.
    The directory structure is recursively traversed, and datasets are created in the HDF5 file
    based on the files present in the directories. The data is read from files and stored in the HDF5 file
    as binary datasets. The function handles various file extensions such as .csv, .txt, .xls, .xlsx, .jpg, .jpeg, .png, etc.
    The JSON schema is also saved as an attribute of the root group in the HDF5 file.
    """

    # Open JSON file and load metadata
    with open(scdir, 'r') as f:
        metadata = json.load(f)  # load metadata from the JSON file

    # Remove HDF5 file if it exists
    if os.path.exists(hdf5_file):
        os.remove(hdf5_file)  # delete the HDF5 file if it exists

    # Function to create nested groups based on directory structure
    def create_nested_groups(f, path):
        """
        Recursively create nested groups in the HDF5 file based on the directory structure.
        """
        groups = path.split(os.sep)
        for group_name in groups:
            if group_name:
                if group_name not in f:  # create a new group if it doesn't exist
                    f.create_group(group_name)
                f = f[group_name]

    # Open HDF5 file in append mode
    with h5py.File(hdf5_file, 'a') as f:
        # Save metadata JSON as an attribute of the root group
        metadata_str = json.dumps(metadata, indent=4)
        f.attrs['Schema_json'] = metadata_str

        # Loop through each directory and subdirectory
        for root, dirs, files in os.walk(data_folder):
            group_path = os.path.relpath(root, data_folder)
            create_nested_groups(f, group_path)
            group = f
            if group_path != '.':
                groups = group_path.split(os.sep)
                for sub_group_name in groups:
                    group = group[sub_group_name]

            for file_name in files:
                file_path = os.path.join(root, file_name)

                # Skip non-regular files
                if not os.path.isfile(file_path):
                    continue

                # Get the file extension
                extension = os.path.splitext(file_name)[1]

                # Check if dataset already exists and delete it
                if file_name in group:
                    del group[file_name]

                if extension in [".csv", ".txt", ".xls", ".xlsx"]:
                    # Read the file as binary
                    with open(file_path, "rb") as file:
                        binary_data = file.read()
                    binary_data_vla = np.asarray(binary_data)
                    group.create_dataset(file_name, data=binary_data_vla)

                elif extension in [".jpg", ".jpeg", ".png"]:
                    # Read the image file as binary
                    with open(file_path, 'rb') as img_f:
                        binary_data = img_f.read()  # read the image as python binary
                    binary_data_vla = np.asarray(binary_data)
                    group.create_dataset(file_name, data=binary_data_vla)

                else:
                    # Read other file types as binary
                    with open(file_path, "rb") as file:
                        binary_data = file.read()
                    binary_data_vla = np.asarray(binary_data)
                    group.create_dataset(file_name, data=binary_data_vla)

    print("HDF5 created successfully.")
    print(hdf5_file)