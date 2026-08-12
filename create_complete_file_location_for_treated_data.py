#create_complete_file_location_for_treated_data
import os

def create_complete_file_location_for_treated_data(input_file_project_folder, complete_file_name):
    complete_file_location = os.path.join(input_file_project_folder)
    if "Simple RIXS Figures" not in complete_file_location:
        simple_RIXS_figures_folder= os.path.join(input_file_project_folder, "Simple RIXS Figures")
    else:
        simple_RIXS_figures_folder=os.path.join(input_file_project_folder)
        #parameters["input_file_raw_data_folder"]= parameters["input_file_raw_data_folder"] + "\\Simple RIXS Figures"

    if complete_file_name[-4:] != ".txt" and complete_file_name[-4:] != ".svg" and complete_file_name[-4:] != ".png":
        complete_file_name = complete_file_name + ".txt"
        complete_file_location = os.path.join(simple_RIXS_figures_folder,complete_file_name)

    if complete_file_name[-8:] == "data.txt":
        complete_file_location = os.path.join(simple_RIXS_figures_folder,complete_file_name)
    elif complete_file_name[-10:] == "figure.svg" or complete_file_name[-10:] == "figure.png" or complete_file_name[-10:] == "figure.txt":
        complete_file_name= complete_file_name[:-10]
        complete_file_name= complete_file_name + "data.txt"
        complete_file_location = os.path.join(simple_RIXS_figures_folder, complete_file_name)
    elif complete_file_name[-14:] == "parameters.txt":
        complete_file_name= complete_file_name[:-14]
        complete_file_name= complete_file_name + "data.txt"
        complete_file_location = os.path.join(simple_RIXS_figures_folder, complete_file_name)                   

    return complete_file_location