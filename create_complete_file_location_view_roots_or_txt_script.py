#create_complete_file_location_view_roots_or_txt_script
import os

def create_complete_file_location_view_roots_or_txt(parameters, is_iteratable_file_number, iteratable_file_number):
    if parameters["plot_type"]=="Plot treated spectra" or parameters["plot_type"]== "Make PFY from treated RIXS":
        complete_file_location = os.path.join(parameters["input_file_project_folder"])
        if "Simple RIXS Figures" not in complete_file_location:
            simple_RIXS_figures_folder= os.path.join(parameters["input_file_project_folder"], "Simple RIXS Figures")
        else:
            simple_RIXS_figures_folder=os.path.join(parameters["input_file_project_folder"])
            #parameters["input_file_raw_data_folder"]= parameters["input_file_raw_data_folder"] + "\\Simple RIXS Figures"

        if parameters["input_complete_file_name_array"][0][-4:] != ".txt" and parameters["input_complete_file_name_array"][0][-4:] != ".svg" and parameters["input_complete_file_name_array"][0][-4:] != ".png":
            parameters["input_complete_file_name_array"][0] = parameters["input_complete_file_name_array"][0] + ".txt"
            complete_file_location = os.path.join(simple_RIXS_figures_folder,parameters["input_complete_file_name_array"][0])

        if parameters["input_complete_file_name_array"][0][-8:] == "data.txt":
            complete_file_location = os.path.join(simple_RIXS_figures_folder,parameters["input_complete_file_name_array"][0])
        elif parameters["input_complete_file_name_array"][0][-10:] == "figure.svg" or parameters["input_complete_file_name_array"][0][-10:] == "figure.png" or parameters["input_complete_file_name_array"][0][-10:] == "figure.txt":
            parameters["input_complete_file_name_array"][0]= parameters["input_complete_file_name_array"][0][:-10]
            parameters["input_complete_file_name_array"][0]= parameters["input_complete_file_name_array"][0] + "data.txt"
            complete_file_location = os.path.join(simple_RIXS_figures_folder, parameters["input_complete_file_name_array"][0])
        elif parameters["input_complete_file_name_array"][0][-14:] == "parameters.txt":
            parameters["input_complete_file_name_array"][0]= parameters["input_complete_file_name_array"][0][:-14]
            parameters["input_complete_file_name_array"][0]= parameters["input_complete_file_name_array"][0] + "data.txt"
            complete_file_location = os.path.join(simple_RIXS_figures_folder, parameters["input_complete_file_name_array"][0])                   

    elif is_iteratable_file_number:
        if parameters["input_file_format"] == "h5":
            if len(parameters["input_file_text_end_of_name"]) < 3:
                parameters["input_file_text_end_of_name"] = parameters["input_file_text_end_of_name"] + ".h5"
            if parameters["input_file_text_end_of_name"][-4:] == ".txt":
                parameters["input_file_text_end_of_name"]=parameters["input_file_text_end_of_name"][:-4]
            if parameters["input_file_text_end_of_name"][-3:] != ".h5":
                parameters["input_file_text_end_of_name"] = parameters["input_file_text_end_of_name"] + ".h5"
            
        elif  parameters["input_file_format"] == "txt":
            if len(parameters["input_file_text_end_of_name"]) < 4:
                parameters["input_file_text_end_of_name"] = parameters["input_file_text_end_of_name"] + ".txt"
            if parameters["input_file_text_end_of_name"][-3:] == ".h5":
                parameters["input_file_text_end_of_name"]=parameters["input_file_text_end_of_name"][:-3]
            if parameters["input_file_text_end_of_name"][-4:] != ".txt":
                parameters["input_file_text_end_of_name"] = parameters["input_file_text_end_of_name"] + ".txt"
        
        elif parameters["input_file_format"] == "dat":
            if len(parameters["input_file_text_end_of_name"]) < 4:
                parameters["input_file_text_end_of_name"] = parameters["input_file_text_end_of_name"] + ".dat"
            if parameters["input_file_text_end_of_name"][-4:] != ".dat":
                parameters["input_file_text_end_of_name"] = parameters["input_file_text_end_of_name"] + ".dat"
        
        elif parameters["input_file_format"] == "csv":
            if len(parameters["input_file_text_end_of_name"]) < 4:
                parameters["input_file_text_end_of_name"] = parameters["input_file_text_end_of_name"] + ".csv"
            if parameters["input_file_text_end_of_name"][-4:] != ".csv":
                parameters["input_file_text_end_of_name"] = parameters["input_file_text_end_of_name"] + ".csv"
        
        if parameters["is_multiple_detectors"]:
            complete_file_location = os.path.join(parameters["input_file_project_folder"], parameters["input_file_raw_data_folder"],parameters["input_file_text_before_file_number"] + iteratable_file_number + parameters["input_file_text_before_detector"] + "1" + parameters["input_file_text_end_of_name"])
    # USE THIS LATER complete_file_location = os.path.join(parameters["input_file_project_folder"], parameters["input_file_raw_data_folder"],parameters["input_file_text_before_file_number"] + iteratable_file_number + parameters["input_file_text_before_detector"] + "ALL_Detectors" + parameters["input_file_text_end_of_name"])
        else:
            complete_file_location = os.path.join(parameters["input_file_project_folder"], parameters["input_file_raw_data_folder"], parameters["input_file_text_before_file_number"] + iteratable_file_number + parameters["input_file_text_end_of_name"])
    else:
        if parameters["input_file_format"] == "h5":
            if parameters["input_complete_file_name_array"][0][-4:] == ".txt":
                parameters["input_complete_file_name_array"][0]=parameters["input_complete_file_name_array"][0][:-4]
            if parameters["input_complete_file_name_array"][0][-3:] != ".h5":
                parameters["input_complete_file_name_array"][0] = parameters["input_complete_file_name_array"][0] + ".h5"
            
        elif  parameters["input_file_format"] == "txt":
            if parameters["input_complete_file_name_array"][0][-3:] == ".h5":
                parameters["input_complete_file_name_array"][0]=parameters["input_complete_file_name_array"][0][:-3]
            if parameters["input_complete_file_name_array"][0][-4:] != ".txt":
                parameters["input_complete_file_name_array"][0] = parameters["input_complete_file_name_array"][0] + ".txt"
        
        elif parameters["input_file_format"] == "dat":
            if parameters["input_complete_file_name_array"][0][-4:] != ".dat":
                parameters["input_complete_file_name_array"][0] = parameters["input_complete_file_name_array"][0] + ".dat"
        
        elif parameters["input_file_format"] == "csv":
            if parameters["input_complete_file_name_array"][0][-4:] != ".csv":
                parameters["input_complete_file_name_array"][0] = parameters["input_complete_file_name_array"][0] + ".csv"
        complete_file_location = os.path.join(parameters["input_file_project_folder"], parameters["input_file_raw_data_folder"],parameters["input_complete_file_name_array"][0])
    
    return parameters, complete_file_location