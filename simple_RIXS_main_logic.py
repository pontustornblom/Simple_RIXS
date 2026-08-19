#simple_RIXS_main_logic
#Simple RIXS was developed by Pontus Törnblom from Uppsala University.
import parameter_scripts
import main_GUI_script
import input_raw_data_information_script
import is_view_roots_or_input_txt_GUI_script
import find_elastic_peak_center
import input_incoming_energy_script
import make_treated_RIXS_script_2
import plot_treated_spectra
import select_treated_file
import select_PFY_region
import make_PFY_spectra_from_several_treated_files
import select_multiple_treated_files
import add_treated_files_to_waterfall
import add_RIXS_map_intensities
import view_treated_plot_script
import add_multiple_RIXS_spectra_to_waterfall
import select_multiple_treated_files_to_integrate
import integrate_and_add_multiple_RIXS_spectra_to_waterfall
import input_energy_per_channel_script
import input_veritas_file_information_script
import make_treated_veritas_RIXS_script
import make_treated_species_RIXS_script
import input_spring_8_file_information_script
import find_elastic_peak_center_spring_8
import make_treated_spring_8_RIXS_script
import get_parameters_from_selected_treated_file_script
import select_integration_region
import select_integration_region_XAS
import add_multiple_treated_intensity_lines
import input_file_names_manually_script
import make_treated_RIXS_script_from_treated_data
import make_treated_XAS_script #this script is not finised, its mostly just a copy of make_PFY_spectra_from_several_treated_files
import input_species_XAS_file_information_script
import make_treated_XAS_script_for_species
import add_multiple_XAS_to_waterfall
import make_treated_galaxies_RIXS_script
import select_detector_range_galaxies
import find_elastic_peak_center_galaxies
import select_treated_files_to_subtract
import subtract_treated_files_script_2
import subtract_treated_RIXS_maps_script
import plot_subtracted_rixs_map_script
import make_treated_XAS_script_for_veritas
import veritas_time_resolved_RIXS_script
#import input_nanoterasu_file_information_script


def main_logic(input_file_project_folder):
    #input_file_location has to be changed when new project folder is chosen.
    #It is recomended to save the "Simple_RIXS" script under a different name for each project. Example: "Simple_RIXS_ALS_2022_RIXS"
    #Example of folder path: input_file_project_folder= "C:\\Users\\ponto479\\Documents\\02 Beamtime Data\\ALS 11-2022\\RIXS"
    #input_file_project_folder= "C:\\Users\\ponto479\\Documents\\02 Beamtime Data\\2024_02_Species"
    
    parameters= parameter_scripts.get_parameters(input_file_project_folder)
    #parameters["is_program_running"] = True
    parameters = main_GUI_script.run_main_gui(parameters)
    
    if parameters["plot_type"]== "Replot treated spectra" and parameters["is_program_running"]:
        parameters= select_treated_file.run_main_gui(parameters)
        if parameters["is_program_running"]:
            parameters= get_parameters_from_selected_treated_file_script.get_parameters_from_selected_treated_file(parameters)
            #temporary line:
            #parameters["plot_type"]= "Make treated RIXS data from Max IV Species"

    if parameters["is_view_roots_or_input_txt"] and parameters["is_program_running"]:
        parameters= is_view_roots_or_input_txt_GUI_script.run_main_gui(parameters)

        
    if parameters["is_program_running"]:
        if parameters["plot_type"]== "Make treated RIXS data":
            parameters= input_raw_data_information_script.run_main_gui(parameters)
            if parameters["is_program_running"] and parameters["is_data_x_values_energy_loss"]== False and parameters["is_data_x_values_emission_energy"]== False:
                parameters= find_elastic_peak_center.run_main_gui(parameters)
            if parameters["is_program_running"] and parameters["is_incoming_energy_available_in_file"]==False and parameters["is_incoming_energy_avialable_in_seperate_file"] == False:
                parameters= input_incoming_energy_script.run_main_gui(parameters)
            if parameters["is_program_running"] and parameters["is_input_energy_per_channel_and_intercept_manually"]== True:
                parameters= input_energy_per_channel_script.run_main_gui(parameters)

            if parameters["is_program_running"]:
                parameters= make_treated_RIXS_script_2.run_main_gui(parameters)

        
        elif parameters["plot_type"]== "Make treated RIXS data from Max IV Veritas":
            parameters= input_veritas_file_information_script.run_main_gui(parameters)
            if parameters["is_program_running"]:
                parameters= make_treated_veritas_RIXS_script.run_main_gui(parameters)

        elif parameters["plot_type"]== "Treat Veritas raw data using time information":
            if parameters["is_program_running"]:
                parameters= veritas_time_resolved_RIXS_script.run_main_gui(parameters)
        
        elif parameters["plot_type"]== "Make treated RIXS data from Max IV Species":
            parameters= input_veritas_file_information_script.run_main_gui(parameters)

            if parameters["is_program_running"] and parameters["is_input_file_names_manually"]:
                parameters= input_file_names_manually_script.run_main_gui(parameters)
                
                parameters["is_incoming_energy_available_in_file"] = False 
                parameters["is_incoming_energy_avialable_in_seperate_file"] = False

                parameters= input_incoming_energy_script.run_main_gui(parameters)
            if parameters["is_program_running"]:
                parameters= make_treated_species_RIXS_script.run_main_gui(parameters)
        
        elif parameters["plot_type"]== "Make treated RIXS data from Soleil Galaxies":
            parameters= input_raw_data_information_script.run_main_gui(parameters)

            if parameters["is_program_running"] and parameters["is_input_file_names_manually"]:
                parameters= input_file_names_manually_script.run_main_gui(parameters)
                
                parameters["is_incoming_energy_available_in_file"] = False 
                parameters["is_incoming_energy_avialable_in_seperate_file"] = False

                parameters= input_incoming_energy_script.run_main_gui(parameters)

            if parameters["is_program_running"] and parameters["is_incoming_energy_available_in_file"]==False and parameters["is_incoming_energy_avialable_in_seperate_file"] == False:
                parameters= input_incoming_energy_script.run_main_gui(parameters)
            
            if parameters["is_program_running"]:
                parameters= select_detector_range_galaxies.run_main_gui(parameters)

            if parameters["is_program_running"] and parameters["is_input_energy_per_channel_and_intercept_manually"] == False and parameters["is_x_values_available_in_file"] == False:
                parameters = find_elastic_peak_center_galaxies.run_main_gui(parameters)
            
            if parameters["is_program_running"] and parameters["is_input_energy_per_channel_and_intercept_manually"]== True:
                parameters= input_energy_per_channel_script.run_main_gui(parameters)

            if parameters["is_program_running"]:
                parameters= make_treated_galaxies_RIXS_script.run_main_gui(parameters)

        elif parameters["plot_type"]== "Make treated RIXS data from SPring-8 BL27SU":
            parameters= input_spring_8_file_information_script.run_main_gui(parameters)

            if parameters["is_program_running"] and parameters["is_input_energy_per_channel_and_intercept_manually"]== True:
                parameters= input_energy_per_channel_script.run_main_gui(parameters)

            if parameters["is_program_running"] and parameters["is_input_energy_per_channel_and_intercept_manually"] == False and parameters["is_x_values_available_in_file"] == False:
                parameters = find_elastic_peak_center_spring_8.run_main_gui(parameters)
            
            if parameters["is_program_running"]:
                parameters= make_treated_spring_8_RIXS_script.run_main_gui(parameters)
        
        #elif parameters["plot_type"]== "Make treated RIXS data from NanoTerasu BL02U":
            #parameters= input_nanoterasu_file_information_script.run_main_gui(parameters)

        
        elif parameters["plot_type"]== "Make treated RIXS data from treated RIXS data":
            parameters= select_treated_file.run_main_gui(parameters)
            if parameters["is_program_running"]:
                parameters= make_treated_RIXS_script_from_treated_data.run_main_gui(parameters)

        elif parameters["plot_type"]== "Make treated XAS data from Max IV Veritas":
            if parameters["is_program_running"]:
                parameters= input_species_XAS_file_information_script.run_main_gui(parameters)
            #if parameters["is_program_running"] and parameters["is_incoming_energy_available_in_file"]==False and parameters["is_i0_avialable_in_seperate_file"] == False:
            #    parameters= input_incoming_energy_script.run_main_gui(parameters)

            if parameters["is_program_running"]:
                parameters= make_treated_XAS_script_for_veritas.run_main_gui(parameters)
        elif parameters["plot_type"]== "Make treated XAS data from Max IV Species":
            if parameters["is_program_running"]:
                parameters= input_species_XAS_file_information_script.run_main_gui(parameters)
            if parameters["is_program_running"] and parameters["is_incoming_energy_available_in_file"]==False and parameters["is_i0_avialable_in_seperate_file"] == False:
                parameters= input_incoming_energy_script.run_main_gui(parameters)
            
            if parameters["is_program_running"]:
                parameters= make_treated_XAS_script_for_species.run_main_gui(parameters)

        elif parameters["plot_type"][:3]=="XAS":
            if parameters["is_program_running"]:
                parameters= input_raw_data_information_script.run_main_gui(parameters)
            if parameters["is_program_running"] and parameters["is_incoming_energy_available_in_file"]==False and parameters["is_i0_avialable_in_seperate_file"] == False:
                parameters= input_incoming_energy_script.run_main_gui(parameters)
            
            if parameters["is_program_running"]:
                parameters= make_treated_XAS_script.run_main_gui(parameters)
        
        elif parameters["plot_type"] == "Apply emission energy scale to RIXS map":
            #temporary: input_emission_energy_scale_script is not yet implemented
            print("Apply emission energy scale to RIXS map is not yet implemented.")
            parameters["is_program_running"] = False



        elif parameters["plot_type"]=="Plot treated spectra":
            parameters= select_treated_file.run_main_gui(parameters)
            if parameters["is_program_running"]:
                parameters= plot_treated_spectra.run_main_gui(parameters)
        
        elif parameters["plot_type"]== "Make PFY from several treated RIXS files":
            parameters= select_multiple_treated_files.run_main_gui(parameters)
            if parameters["is_program_running"]:
                parameters= select_PFY_region.run_main_gui(parameters)
            if parameters["is_program_running"]:
                parameters= make_PFY_spectra_from_several_treated_files.run_main_gui(parameters)
        
        elif parameters["plot_type"]== "Add plots to waterfall plot":
            parameters= select_multiple_treated_files.run_main_gui(parameters)
            if parameters["is_program_running"]:
                parameters= add_treated_files_to_waterfall.run_main_gui(parameters)
        
        elif parameters["plot_type"]== "Add multiple XAS to waterfall plot":
            parameters= select_multiple_treated_files.run_main_gui(parameters)
            if parameters["is_program_running"]:
                parameters= add_multiple_XAS_to_waterfall.run_main_gui(parameters)
        
        elif parameters["plot_type"]== "Add intensities from RIXS maps":
            parameters= select_multiple_treated_files.run_main_gui(parameters)
            if parameters["is_program_running"]:
                parameters= add_RIXS_map_intensities.run_main_gui(parameters)
            #parameters= view_plot_GUI_script.run_main_gui(parameters)

        elif parameters["plot_type"]=="Add multiple treated intensity lines":
            parameters= select_multiple_treated_files.run_main_gui(parameters)
            if parameters["is_program_running"]:
                parameters= add_multiple_treated_intensity_lines.run_main_gui(parameters)

        elif parameters["plot_type"] == "Subtract treated line scans":
            parameters= select_treated_files_to_subtract.run_main_gui(parameters)
            if parameters["is_program_running"]:
                parameters = subtract_treated_files_script_2.run_main_gui(parameters)
            
        elif parameters["plot_type"] == "Subtract RIXS maps":
            parameters= select_treated_files_to_subtract.run_main_gui(parameters)
            if parameters["is_program_running"]:
                parameters = subtract_treated_RIXS_maps_script.run_main_gui(parameters)
            if parameters["is_program_running"]:
                parameters = plot_subtracted_rixs_map_script.run_main_gui(parameters)
        elif parameters["plot_type"]== "View treated plot":
            parameters= select_treated_file.run_main_gui(parameters)
            if parameters["is_program_running"]:
                parameters= view_treated_plot_script.run_main_gui(parameters)

        elif parameters["plot_type"]== "Add several RIXS spectra from different files to waterfall plot":
            parameters= select_multiple_treated_files.run_main_gui(parameters)
            if parameters["is_program_running"]:
                parameters= add_multiple_RIXS_spectra_to_waterfall.run_main_gui(parameters)
            #parameters= view_plot_GUI_script.run_main_gui(parameters)
    
        elif parameters["plot_type"]== "Integrate and add several RIXS spectra from different files to waterfall plot":
            parameters= select_multiple_treated_files_to_integrate.run_main_gui(parameters)
            if parameters["is_program_running"]:
                parameters= integrate_and_add_multiple_RIXS_spectra_to_waterfall.run_main_gui(parameters)

        elif parameters["plot_type"]== "Integrate multiple RIXS maps to values":
            #parameters = select_multiple_treated_files.run_main_gui(parameters)
            parameters= select_multiple_treated_files.run_main_gui(parameters)
            if parameters["is_program_running"]:
                parameters= select_integration_region.run_main_gui(parameters)

        elif parameters["plot_type"]== "Integrate multiple XAS to values":
            #parameters = select_multiple_treated_files.run_main_gui(parameters)
            parameters= select_treated_file.run_main_gui(parameters)
            if parameters["is_program_running"]:
                parameters= select_integration_region_XAS.run_main_gui(parameters)
    
    if parameters["is_program_running"] == False:
        print("Simple RIXS was cancelled")

    return parameters  