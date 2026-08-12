#get_single_spectrum_h5_or_txt_file_scripts
import h5py
import create_complete_file_location_view_roots_or_txt_script
import pandas as pd
import re


def get_single_spectrum_h5_file(parameters, y_values_root, is_iteratable_file_number, iteratable_file_number):
    parameters, complete_file_location = create_complete_file_location_view_roots_or_txt_script.create_complete_file_location_view_roots_or_txt(parameters, is_iteratable_file_number, iteratable_file_number)
    raw_data_list=[]

    with h5py.File(complete_file_location, 'r') as file:
        try:
            group = file[str(y_values_root)][:]
            print(f"Group '{y_values_root}' exists in the HDF5 file.")
            raw_data_list.append(group)
            print("Data successfully added.")
        except KeyError:
            print(f"Group '{y_values_root}' does not exist in the HDF5 file.")

    return raw_data_list[0]

def get_single_spectrum_txt_file(parameters, is_single_data, data_row, data_column, is_iteratable_file_number, iteratable_file_number, combine_several_columns):
    parameters, complete_file_location = create_complete_file_location_view_roots_or_txt_script.create_complete_file_location_view_roots_or_txt(parameters, is_iteratable_file_number, iteratable_file_number)
    data_row = int(data_row)
    data_column= int(data_column)
    if parameters["txt_delimiter"] == "Tab":
        dataframe = pd.read_csv(complete_file_location, sep='\t', skiprows=data_row, usecols=[data_column], header=None)
        if combine_several_columns:
            for column in range(data_column +1, int(parameters["txt_intensity_data_last_column"]) +1):
                current_column_values= pd.read_csv(complete_file_location, sep='\t', skiprows=data_row, usecols=[column], header=None)
                dataframe = dataframe.add(current_column_values, fill_value=0)
    elif parameters["txt_delimiter"] == "Space":
        dataframe = pd.read_csv(complete_file_location, sep=' ', skiprows=data_row, usecols=[data_column], header=None)
    else:
        dataframe = pd.read_csv(complete_file_location, sep=parameters["txt_delimiter"], skiprows=data_row, usecols=[data_column], header=None)
# Access the values of the column
    if is_single_data:
        column_values = dataframe.iloc[0, 0]
        if isinstance(column_values, str):
            pattern = r'\d+(\.\d+)?'
            match = re.search(pattern, column_values)     
            if match:
                column_values= float(match.group())
            else:
                pattern = r'\d{1,20}'  # Match sequences of 1 to 20 digits
                match = re.search(pattern, column_values)
                if match:
                    column_values= float(match.group())
    else:
        column_values = dataframe.iloc[:, 0].values


    return column_values