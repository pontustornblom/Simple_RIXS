#get_parameters_from_selected_treated_file_script
import create_complete_file_location_for_treated_data
import parameter_scripts

def get_parameters_from_selected_treated_file(parameters):
    complete_file_location= create_complete_file_location_for_treated_data.create_complete_file_location_for_treated_data(parameters["input_file_project_folder"], parameters["input_complete_file_name_array"][0])
    complete_file_location = complete_file_location[:-8] + "parameters.txt"

    parameters = parameter_scripts.get_treated_parameters(complete_file_location)
    if "degree_of_energy_per_channel_polynomial" not in parameters:
        if "energy_per_channel_intercept_of_elastic_peak" in parameters and "energy_per_channel_slope_of_elastic_peak" in parameters:
            parameters["degree_of_energy_per_channel_polynomial"] = "1"
            parameters["energy_per_channel_polynomial_coefficients_array"] = [parameters["energy_per_channel_intercept_of_elastic_peak"], parameters["energy_per_channel_slope_of_elastic_peak"]]

    default_parameters = parameter_scripts.get_default_parameters()
    for key in default_parameters:
        if key not in parameters:
            parameters[key] = default_parameters[key]

    if parameters["plot_type"] == "Find channel energy":
        parameters["plot_type"] = "Make treated RIXS data"

    return parameters