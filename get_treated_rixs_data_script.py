#get_treated_rixs_data_script
import pandas as pd
import numpy as np

def get_treated_rixs_data(complete_file_location):
    header_row = 0
    data_row = 1
    dataframe = pd.read_csv(complete_file_location, sep='\t', skiprows=header_row, header=None, low_memory= False)
    if str(dataframe.iloc[header_row, 1])[ : 17] == "Excitation energy" or str(dataframe.iloc[header_row, 1])[ : 15] == "Incoming energy":
        x_values_array= dataframe.iloc[data_row :, 0].values
        y_values_array= dataframe.iloc[data_row :, 1].values

        if y_values_array.dtype != np.float64:
            y_values_array = y_values_array.astype(float)

        y_values_array = y_values_array[~np.isnan(y_values_array)]
        #nan_mask = np.isnan(y_values_array)
        #y_values_array_length_without_nan = len(y_values_array) - np.sum(nan_mask)
        array_of_x_values_arrays = []
        array_of_intenisty_arrays=[]
        for column_index in range(len(y_values_array)):
            intensity_array= dataframe.iloc[data_row:, 2+ column_index].values
            array_of_intenisty_arrays.append(intensity_array)
            array_of_x_values_arrays.append(x_values_array)

        return np.array(array_of_x_values_arrays, dtype= float), np.array(y_values_array, dtype= float), np.array(array_of_intenisty_arrays, dtype= float)
    else:
        array_of_x_values_arrays = []
        array_of_intenisty_arrays = []
        y_values_array = []
        for array_index in range(int(len(dataframe.iloc[header_row, :]) / 2)):
            x_values_array= dataframe.iloc[data_row :, 2 * array_index].values
            intensity_array= dataframe.iloc[data_row :, 2 * array_index + 1].values
            y_value= str(dataframe.iloc[header_row, 2* array_index]).split("_")
            y_value= float(y_value[-1])
            array_of_x_values_arrays.append(x_values_array)
            array_of_intenisty_arrays.append(intensity_array)
            y_values_array.append(y_value)

        return np.array(array_of_x_values_arrays, dtype= float), np.array(y_values_array, dtype= float), np.array(array_of_intenisty_arrays, dtype= float)