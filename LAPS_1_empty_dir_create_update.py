## LAPS project data convertion, storage, and plotting based on the .json schema file
# Ekaterina Bolotskaya
# 07/17/2023

def LAPS_1_empty_dir_create_update(schema_path, target_dir, json, os):
    """
    Update the directory structure based on the provided JSON schema file.
    If this folder already exists, it will be UPDATED. The folders that exist, but no longer correspond to the .json structure
    will be deleted if empty and kept if not empty.

    Parameters:
    schema_path (str): The path to the JSON schema file that defines the directory structure.
    target_dir (str): The path to the target directory where the directory structure will be created/updated.
    json (module): The JSON module to load and parse the JSON schema.
    os (module): The operating system module for directory operations.

    Returns:
    None

    This function reads the JSON schema file, creates directories, and subdirectories based on the schema.
    The function is designed to update the structure, preserving existing data.
    """

    # Directory creation function
    def create_directory(path):
        """
        Create a directory at the given path if it does not already exist.

        Parameters:
        path (str): The path to the directory that needs to be created.

        Returns:
        None
        """
        if not os.path.exists(path):
            os.makedirs(path)

    # Parse the JSON
    with open(schema_path, 'r') as f:
        json_data = json.load(f)

    # Create directories for the first tier of subfields within "object"
    create_directory(target_dir)

    if isinstance(json_data, dict):
        for key, value in json_data.items():
            sub_dir = os.path.join(target_dir, key)       # create a subdirectory path within the target directory
            create_directory(sub_dir)                     # create the subdirectory

            if key == "data" and isinstance(value, dict) and "datasets" in value:
                datasets_dir = os.path.join(sub_dir, "datasets")
                create_directory(datasets_dir)             # create the "datasets" subdirectory

                if "datasets" in value:
                    for dataset in value["datasets"]:
                        data_value = dataset.get("data", "")
                        dataset_id = dataset.get("index", "")
                        if data_value:
                            if dataset_id:
                                dataset_subdir = os.path.join(datasets_dir, data_value.replace(" ", "_") + "_" + dataset_id)
                            else:
                                dataset_subdir = os.path.join(datasets_dir, data_value)
                            create_directory(dataset_subdir)  # create subdirectories for datasets

                            #print(dataset_subdir)             # print the dataset subdirectory path

            elif isinstance(value, dict) and "documents" in value:
                documents_dir = os.path.join(sub_dir, "documents")
                create_directory(documents_dir)              # create the "documents" subdirectory
            
            # Add this part to handle the "daq" case
            elif key == "daq" and isinstance(value, dict) and "devices" in value:
                devices_dir = os.path.join(sub_dir, "devices")
                create_directory(devices_dir)              # create the "devices" subdirectory

                devices_value = value.get("devices", [])
                for device in devices_value:
                    device_name = device.get("name", "")
                    if device_name:
                        device_subdir = os.path.join(devices_dir, device_name)
                        create_directory(device_subdir)       # create subdirectory for device name
                    
                        # Create "documents" subdirectory within the device's subdirectory
                        device_documents_dir = os.path.join(device_subdir, "documents")
                        create_directory(device_documents_dir)

    print("Empty directory created successfully. Please populate it with data for further processing.")
    print(target_dir)