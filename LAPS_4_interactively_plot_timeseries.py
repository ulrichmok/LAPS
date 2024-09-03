## LAPS project data convertion, storage, and plotting based on the .json schema file
# Ekaterina Bolotskaya
# 07/17/2023

def LAPS_4_interactively_plot_timeseries(scdir, ts_dir, json, os, np):
    """
    This function selectively prints out fields from a JSON schema file (original or recreated),
    gets header arrays from the schema, reads time series data from the specified .txt file,
    and then interactively plots the time series data.

    Parameters:
    scdir (str): The path to the JSON schema file (original or recreated).
    ts_dir (str): The path to the .txt file containing time series data.
    json (module): The 'json' module for JSON file handling.
    os (module): The 'os' module for operating system-related functions.
    np (module): The 'numpy' module for numerical computing.

    Returns:
    None

    This function creates an interactive plot to visualize time series data stored in the 'ts_dir' file.
    Users can select the data columns to be plotted against each other using a dropdown menu.

    The 'scdir' parameter should contain the path to the JSON schema file ('.json') that defines the structure
    of the data being plotted. The schema file is used to identify the headers of the data columns.

    The 'ts_dir' parameter should contain the path to the '.txt' file containing the time series data to be plotted.
    The data in the '.txt' file should be whitespace-separated, with each row representing a time step,
    and each column representing a different parameter.

    The function uses the 'ipywidgets' library for creating an interactive GUI, 'matplotlib' for plotting,
    and 'numpy' for numerical data processing.

    Note: This function assumes that the provided JSON schema file and time series data file are correctly formatted
    and correspond to each other.

    Usage example:
    LAPS_4_interactively_plot_timeseries('schema.json', 'time_series_data.txt', json, os, np)
    """

    # Import required libraries
    import ipywidgets as widgets
    from IPython.display import display, clear_output, HTML
    import matplotlib.pyplot as plt

    # Open the JSON file
    with open(scdir) as f:
        # Load the data from the file
        data = json.load(f)

    ## Print selected fields
    # Function to selectively print fields from the JSON schema
    def print_fields(data, field_name):
        if isinstance(data, dict):
            for key, value in data.items():
                if key == field_name:
                    print(value)
                else:
                    print_fields(value, field_name)
        elif isinstance(data, list):
            for item in data:
                print_fields(item, field_name)

    # Create an empty list to store project-related information
    p_name = []
    # Print and store project, apparatus, and sample names if available
    if 'project' in data['experiment']:
        print('Project:', data['experiment']['project'])
        p_name.append(data['experiment']['project']+', ')
    else:
        print('No project description')
    if 'name' in data['apparatus']:
        print('Apparatus:', data['apparatus']['name'])
        p_name.append(data['apparatus']['name'])
    else:
        print('No apparatus name')
    if 'name' in data['sample']['description']:
        print('Sample:', data['sample']['description']['name'])
    else:
        print('No sample name')

    # Initialize variables to store header information
    k = 0
    header_array = []
    # Print dataset information and headers if available
    if 'datasets' in data['data']:
        print('Datasets:')
        for item in data['data']['datasets']:
            print('   ', item['data'])
            if item['data'] == 'Time_Series' and 'headers' in item:
                ts_path = item['path']
                for it2 in item['headers']:
                    if 'header' in item['headers'][k]:
                        print('      ', item['headers'][k]['header']['type'],
                              item['headers'][k]['header']['spec_a'],
                              item['headers'][k]['header']['spec_b'],
                              item['headers'][k]['header']['spec_c'], ', ',
                              item['headers'][k]['header']['unit'])
                        header_array.append(item['headers'][k]['header']['type'] +
                                            ' ' + item['headers'][k]['header']['spec_a'] +
                                            ' ' + item['headers'][k]['header']['spec_b'] +
                                            ' ' + item['headers'][k]['header']['spec_c'] +
                                            ', ' + item['headers'][k]['header']['unit'])
                    k += 1
            else:
                print('      No headers')
    else:
        print('No datasets')

    # Read data from the provided time series data file
    with open(ts_dir, "r") as file:
        # Initialize an empty list to store the data
        data = []
        # Loop over each line in the file
        for line in file:
            # Strip any leading or trailing whitespace from the line
            line = line.strip()
            # Split the line by whitespace
            values = line.split()
            # Check if the line has the required number of values
            if len(values) == k:
                # Try to convert each value to a float
                try:
                    row = list(map(float, values))
                    # Append the row to the data list
                    data.append(row)
                except ValueError:
                    # Ignore lines with non-numeric values
                    pass
        # Convert the data list to a matrix
        matrix = np.array(data)

    class PlotGUI:
        """
        Class to create an interactive GUI for plotting time series data.

        Attributes:
        data_matrix (numpy.array): The matrix containing time series data.
        header_array (list): List of strings containing header names for plotting.

        Methods:
        plot(event): Function to handle the plot button click event and plot the selected data.
        """

        def __init__(self, data_matrix, header_array):
            self.data_matrix = data_matrix
            self.header_array = header_array

            # Create GUI elements
            self.x_dropdown = widgets.Dropdown(options=self.header_array, description='X-axis:',
                                               layout=widgets.Layout(width='auto'))
            self.y_dropdown = widgets.Dropdown(options=self.header_array, description='Y-axis:',
                                               layout=widgets.Layout(width='auto'))
            self.plot_button = widgets.Button(description='Plot',
                                               layout=widgets.Layout(width='auto', button_color='red'))
            self.output = widgets.Output()

            # Set default selections
            self.x_dropdown.value = self.header_array[0]
            self.y_dropdown.value = self.header_array[0]
        
            # Register event handlers
            self.plot_button.on_click(self.plot)

            # Display the GUI elements
            display(widgets.VBox([self.x_dropdown, self.y_dropdown, self.plot_button, self.output]))

        def plot(self, event):
            """
            Function to handle the plot button click event and plot the selected data.

            Parameters:
            event: The event object representing the click event on the plot button.

            Returns:
            None

            This function retrieves the selected x-axis and y-axis labels from the dropdown menus,
            extracts the corresponding data columns from the data_matrix, and plots them using matplotlib.
            """

            with self.output:
                # Clear previous output
                clear_output()

                # Get selected x and y labels
                x_label = self.x_dropdown.value
                y_label = self.y_dropdown.value

                # Get corresponding column indices
                x_index = self.header_array.index(x_label)
                y_index = self.header_array.index(y_label)

                # Get data for x and y axes
                x_data = self.data_matrix[:, x_index]
                y_data = self.data_matrix[:, y_index]

                # Plot the data
                plt.figure(figsize=(10, 5))
                plt.plot(x_data, y_data, '-')
                plt.xlabel(x_label)
                plt.ylabel(y_label)
                plt.grid(True)
                plt.tight_layout()
                plt.show()

    # Create an instance of PlotGUI to enable interactive plotting
    plot_gui = PlotGUI(matrix, header_array)
