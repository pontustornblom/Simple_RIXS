#get_treated_XAS_data_script
import pandas as pd
import numpy as np

def get_treated_XAS_data(complete_file_location):
    header_row = 0
    data_row = 1
    dataframe = pd.read_csv(complete_file_location, sep='\t', skiprows=header_row, header=None, low_memory= False)
    if str(dataframe.iloc[header_row, 0])[ : 17] == "Excitation energy" or str(dataframe.iloc[header_row, 0])[ : 15] == "Incoming energy":
        array_of_x_values_arrays = []
        array_of_intenisty_arrays = []
        y_values_array = []
        for array_index in range(int(len(dataframe.iloc[header_row, :]) / 2)):
            x_values_array= dataframe.iloc[data_row :, 2 * array_index].values
            intensity_array= dataframe.iloc[data_row :, 2 * array_index + 1].values
            #y_value= str(dataframe.iloc[header_row, 2* array_index]).split("_")
            #y_value= float(y_value[-1])
            array_of_x_values_arrays.append(x_values_array)
            array_of_intenisty_arrays.append(intensity_array)
            #y_values_array.append(y_value)

        return np.array(array_of_x_values_arrays, dtype= float), np.array(array_of_intenisty_arrays, dtype= float)
    else:
        print("Warning, incorrect data structure in treated file. This is sent from get_treated_XAS_data_script")
        

        return np.array(array_of_x_values_arrays, dtype= float), np.array(array_of_intenisty_arrays, dtype= float)