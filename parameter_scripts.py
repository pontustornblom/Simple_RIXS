#parameter_scripts
import os
import json

def save_parameters(parameters): 

    parameters_folder_adress = os.path.join(parameters["input_file_project_folder"], "Simple_RIXS_parameters")

    if not os.path.exists(parameters_folder_adress):
        os.makedirs(parameters_folder_adress)

    parameters_file_adress_and_name = os.path.join(parameters_folder_adress, 'parameters.txt')

    #with open(parameters_file_adress_and_name, "w") as parameters_file:
    #    json.dump(parameters, parameters_file)

    formatted_parameters = json.dumps(parameters, indent=0)
    with open(parameters_file_adress_and_name, "w") as parameters_file:
        parameters_file.write(formatted_parameters)

def get_treated_parameters(treated_file_complete_adress_and_name):
    with open(treated_file_complete_adress_and_name, "r") as parameters_file:
        treated_parameters = json.load(parameters_file)
    return treated_parameters


def get_parameters(input_file_project_folder):
    parameters_folder_adress = os.path.join(input_file_project_folder, "Simple_RIXS_parameters")
    #parameters_folder_adress = os.path.join(parameters["input_file_project_folder"], parameters["input_file_raw_data_folder"], "Simple_RIXS_parameters")

    if not os.path.exists(parameters_folder_adress):
        os.makedirs(parameters_folder_adress)

    parameters_file_adress_and_name = os.path.join(parameters_folder_adress, 'parameters.txt')
    
    if not os.path.exists(parameters_file_adress_and_name):
        #Delete current parameters file to create default file
        parameters = get_default_parameters()
        parameters["input_file_project_folder"] = input_file_project_folder
        save_parameters(parameters)
        return parameters
    
    with open(parameters_file_adress_and_name, "r") as parameters_file:
        parameters = json.load(parameters_file)

        default_parameters = get_default_parameters()
        for key in default_parameters:
            if key not in parameters:
                parameters[key] = default_parameters[key]
                
        parameters["is_view_roots_or_input_txt"] = False
    return parameters


def get_default_parameters():
    default_parameters = {
                              #All arrays must end with _array to be properly handled in the code
                                      "is_program_running": True,
                               "screen_to_display_program": "0",
                                   "is_program_fullscreen": False,
                                 "screen_to_display_plots": "0",
                                     "is_plots_fullscreen": False,
                                #Information on input file
                               "input_file_project_folder": "C:\\Users\\ponto479\\Documents\\02 Beamtime Data",
                              "input_file_raw_data_folder": "RIXS",
                                               "plot_type": "Make treated RIXS data",
                                    "nanoterasu_plot_type": "Make detector image from raw rotated data",
"nanoterasu_energy_range_above_and_below_selected_excitation_energy": "0.2236",
#"nanoterasu_number_of_points_on_detector_to_divide_into_polynomials": "1",
#"nanoterasu_approximate_pixel_of_elastic_peak_in_x_array": ["0"],
#"nanoterasu_approximate_pixel_of_elastic_peak_in_y_array": ["0"],
#"nanoterasu_is_do_linear_fit_for_small_detector_regions": False,
#"nanoterasu_pixel_limit_in_y_for_linear_fit": "10",
#"nanoterasu_number_of_detector_images_to_combine": "2",
"nanoterasu_is_plot_detector_image_as_energy_loss": True,
"nanoterasu_number_of_pixels_above_and_below_rough_elastic_peak_position_to_find_peak_maximum": "10",
                     "input_number_of_complete_file_names": "1",
                          "input_complete_file_name_array": [""],
                      "input_file_text_before_file_number": "O_",
                 "input_file_iteratable_file_number_start": "0001", #Write as string. For example:"0100"
                   "input_file_iteratable_file_number_end": "0005",
               "input_file_iteratable_file_number_start_2": "0001", #Write as string. For example:"0100"
                 "input_file_iteratable_file_number_end_2": "0005",
                            "iteratable_file_number_array": ["0001"], #Used when user is forced to make RIXS map from more than 1 file
                                   "is_multiple_detectors": False,
                          "input_file_number_of_detectors": "3",
                         "input_file_text_before_detector": "_d", #Can be left blank as ""
                             "input_file_detector_numbers": [1,2,3],
                             "input_file_text_end_of_name": "", #Can be left blank as ""
                    "input_file_number_of_files_to_ignore": "0",
                     "input_file_ignore_file_number_array": [""], 
                      "input_file_number_of_files_to_plot": "0",
                                   "is_input_file_treated": False, #remove
                     "is_set_negative_intensities_to_zero": False,
            "is_add_intensities_of_same_excitation_energy": False,
                               "energy_mismatch_tolerance": "0.05",
                        "is_subtract_background_from_RIXS": True,
       "energy_above_elastic_peak_to_fit_background_start": "1",
         "energy_above_elastic_peak_to_fit_background_end": "2",
                                       "input_file_format": "txt", #txt h5 csv data FLER??
                                       "is_detector_count": False, #if the data gives counts per channel in 2D detector
                                    "detector_range_start": "0",
                                      "detector_range_end": "1",
                           "is_x_values_available_in_file": True,
                            "is_data_x_values_energy_loss": False, #This might not be needed anymore. Just check if x is negative or not
                        "is_data_x_values_emission_energy": False, #This might not be needed anymore. Just check if x is negative or not
          "is_automatically_adjust_peak_to_correct_energy": True,
"energy_above_and_below_to_calculate_elastic_peak_weights": "1",
                                  "input_x_values_txt_row": "0",
                               "input_x_values_txt_column": "0",
                          "input_energy_per_channel_slope": "0.01", #Remove?
                               "input_energy_offset_value": "530", #Remove?
         "input_number_of_spectral_lines_per_file_to_plot": "1",
                  "input_energies_of_spectral_lines_array": [""],
                              "is_view_roots_or_input_txt": False,
                             "is_several_spectra_per_file": False,
                     "is_combine_several_spectra_per_file": False,
                            "number_of_spectra_to_combine": "2",
                     "index_frequency_of_plots_to_combine": "1", # 1 is every column after the first column 
                                   "h5_root_location_data": "entry/analysis/spectrum", 
                               "h5_root_location_x_values": "entry/analysis/spectrum",
                                           "txt_delimiter": "Tab",
                                  "txt_intensity_data_row": "0",
                               "txt_intensity_data_column": "0",
                          "txt_intensity_data_last_column": "0",
                    "is_incoming_energy_available_in_file": False,
           "is_incoming_energy_avialable_in_seperate_file": False,
                  "complete_incoming_energy_file_location": "",
                      "complete_incoming_energy_file_name": "",
                        "h5_root_location_incoming_energy": "entry/instrument/NDAttributes/PhotonEnergy", #["entry/instruments/NDAttributes/PhotonEnergy"] #Only used for h5 files
                     "is_txt_single_incoming_energy_value": False,
                         "txt_incoming_energy_row_in_file": "0",
                      "txt_incoming_energy_column_in_file": "1",
                                  "is_normalization_to_i0": True,
                                 "is_i0_available_in_file": False,
                        "is_i0_avialable_in_seperate_file": False,
          "is_use_same_file_for_i0_as_for_incoming_energy": False,
                               "complete_i0_file_location": "",
                                   "complete_i0_file_name": "",
                                   "i0_root_location_data": "entry/instrument/NDAttributes/BeamCurrent",
                                  "is_txt_single_i0_value": False,
                                      "txt_i0_row_in_file": "0",
                                   "txt_i0_column_in_file": "2",
                                #Additional information for name of output file
                         "output_file_date_of_measurement": "",
                                     "output_file_element": "O",
                                        "output_file_edge": "K-edge",
                                 "output_file_sample_name": "Pristine",
                          "output_file_additional_comment": "",
                    #Parameters for finding elastic peak. Displaying first and last spectrum is recommended
                    #"is_display_first_and_last_spectrum": True,
                            "is_input_file_names_manually": False,
      "is_input_energy_per_channel_and_intercept_manually": False,
   "is_use_converging_weighted_squared_peak_center_finder": False,
           "is_use_converging_weighted_peak_center_finder": True,
                            "is_weighted_elastic_peak_fit": False,
                       "is_full_gaussian_elastic_peak_fit": False,
                       "is_half_gaussian_elastic_peak_fit": False,
                      "is_intensity_weight_for_linear_fit": True,
               "approximate_channel_of_first_elastic_peak": "200",
                "approximate_channel_of_last_elastic_peak": "300",
            "channels_above_and_below_for_finding_elastic": "2",
                 "channels_above_and_below_elastic_to_fit": "2",
                            "energy_of_first_line_spectra": "530", 
                             "energy_of_last_line_spectra": "540", 
                     "is_equal_incoming_energy_difference": True,
         "is_segments_of_equal_incoming_energy_difference": False,
"is_segments_of_equal_incoming_energy_difference_with_gap": False,
                          "is_input_every_incoming_energy": False,
                    "input_first_and_last_incoming_energy":["",""], #Remove?
                "input_number_of_incoming_energy_segments": "",
       "input_number_of_incoming_energy_segments_with_gap": "",
                  "first_incoming_energy_of_segment_array": [""],
                   "last_incoming_energy_of_segment_array": [""],
             "incoming_energy_difference_in_segment_array": [""],
                         "incoming_energy_of_last_spectra": "",
                       "input_number_of_incoming_energies": "0",
                        "incoming_energy_of_spectra_array": [""],
                                   "number_of_pfy_regions": "0",
                                   "pfy_region_name_array": [""],
                         "pfy_incoming_energy_start_array": [""],
                           "pfy_incoming_energy_end_array": [""],
                             "pfy_energy_loss_start_array": [""],
                               "pfy_energy_loss_end_array": [""],
      #XAS normalization and background subtraction parameters
                                "is_invert_the_plot_array": [False],
                        "is_normalize_all_to_zero_and_one": False, #currently not used
     "approximate_energy_for_normalization_to_one_for_all": "540", #currently not used
     "energy_above_and_below_normalization_to_one_for_all": "0.1", #currently not used
    "approximate_energy_for_normalization_to_zero_for_all": "525", #currently not used
    "energy_above_and_below_finding_min_intensity_for_all": "1", #currently not used
    "energy_above_and_below_normalization_to_zero_for_all": "0.1", #currently not used
                      "is_normalize_to_zero_and_one_array": [True],
        #"incoming_energy_range_normalization_to_one_array": ["1"], #eV
       "approximate_energy_for_normalization_to_one_array": ["540"],
       "energy_above_and_below_normalization_to_one_array": ["0.1"],
   "is_approximate_energy_for_normalization_to_zero_array": [True],
      "approximate_energy_for_normalization_to_zero_array": ["525"],
      "energy_above_and_below_finding_min_intensity_array": ["1"],
      "energy_above_and_below_normalization_to_zero_array": ["0.1"],
                     #"is_subtract_fitted_background_array": [False],
                     #          "background_fit_type_array": ["Linear"],
               "number_of_functions_to_fit_background_xas": "0",
         "selected_functions_for_background_fit_xas_array": ["Polynomial of degree n"],
                     "value_of_n_for_background_fit_array": ["1"],            
         "number_of_energy_regions_to_fit_background_xas" : "1",
                       "background_fit_energy_start_array": ["520"],
                         "background_fit_energy_end_array": ["527"],
               "background_subtraction_coefficients_array": [""],
               #Subtract one line scan from another
               "how_data_points_will_be_subtracted": "Create a new x-axis that includes the emission energy of both x-axes and linearly interpolate to get intensities at each point",
"subtract_spectra_on_emission_energy_axis_instead_of_energy_loss": False,
                                  #Preferences for the plot
                                    "plot_colormap_choice": "turbo",
                                  "plot_display_color_bar": True,
                                  "is_log_scale_color_bar": False,
                          "plot_display_sample_name_title": True,
                                         "plot_title_size": "22",
                                   "plot_x_axis_text_size": "18",
                                   "plot_y_axis_text_size": "18",
                                 "plot_x_axis_number_size": "18",
                                 "plot_y_axis_number_size": "18",
                                      "plot_invert_x_axis": False,
                                      "plot_invert_y_axis": False,
             "plot_outgoing_energy_instead_of_energy_loss": False,
                      "plot_waterfall_instead_of_heat_map": False,
                   "plot_display_incoming_energy_by_lines": True,
                           "plot_incoming_energy_x_offset": "0",
                           "plot_incoming_energy_y_offset": "0",
                          "plot_incoming_energy_text_size": "18",
                "plot_incoming_energy_significant_numbers": "6",
                     "waterfall_plot_x_axis_type": "Energy loss",
          "veritas_time_rixs_file_name": "",
    "veritas_time_rixs_acquisition_number": "48",
       "veritas_time_rixs_incoming_energy": "531",
      "veritas_time_rixs_plot_energy_type": "Emission energy",
          "veritas_time_rixs_y_pixel_start": "2150",
            "veritas_time_rixs_y_pixel_end": "6350",
    "veritas_time_rixs_number_of_spectra": "8",
"veritas_time_rixs_time_per_spectra_minutes": "5.0",
    "veritas_time_rixs_start_time_minutes": "0",
        "veritas_time_rixs_map_time_bins": "100",
     "veritas_time_rixs_curvature_coeffs": "-0.0000033518618458794176, 0.012598028611163797, 1388.5048687275685",
               "waterfall_is_adjust_elastic_peak": False,
                           "is_hide_certain_spectra_array": [False],
                             "is_energy_window_used_array": [False],
                              "plot_energy_loss_min_array": ["-13"],
                              "plot_energy_loss_max_array": ["1"],
                        "plot_xmax_energy_to_elastic_peak": "0", #ta bort?
                          "plot_incoming_energy_min_array": ["525"],
                          "plot_incoming_energy_max_array": ["540"],
                     "is_plot_intensity_limits_used_array": [False],
                                "plot_intensity_min_array": ["5"],
                                "plot_intensity_max_array": ["200"],
       "is_normalize_intensity_at_certain_emission_energy": False,
             "emission_energy_for_intenisty_normalization": "530",
       "emission_energy_above_and_below_for_normalization": "0.1", #eV
              "is_plot_intensity_normalize_to_value_array": [False],
         "plot_value_to_normalize_highest_intensity_array": ["1"],
                            "is_manual_shift_elastic_peak": False,
                         "manual_shift_elastic_peak_array": ["0"],
                             "plot_intensity_offset_array": ["0"],
                "plot_is_scale_intensity_of_spectra_array": [False],
                                      "plot_scaling_array": ["1"],
                        "plot_scaling_text_x_offset_array": ["0"],
                        "plot_scaling_text_y_offset_array": ["0"],
                           "plot_y_distance_between_plots": "0", #använd den här eller "plot_line_scan_space_y"
                 "is_gaussian_smooth_data_for_all_spectra": False,
                           "is_gaussian_smooth_data_array": [False],
                      "sigma_for_gaussian_smoothing_array": ["2"],
                  "is_binning_smooth_data_for_all_spectra": False,
                            "is_binning_smooth_data_array": [False],
                      "number_of_bins_for_smoothing_array": ["2"],
         "is_savitzky_golay_smooth_data_for_all_spectra": False,
                   "is_savitzky_golay_smooth_data_array": [False],
                     "savitzky_golay_window_size_array": ["1.0"],
                     "savitzky_golay_poly_degree_array": ["3"],
                            "plot_waterfall_space_y_array": ["0"],
                              "plot_spectra_grouping_type": "No grouping",
                       "plot_distance_between_groups_in_y": "1",
               "plot_number_of_times_to_change_line_style": "0",
         "plot_file_name_index_to_change_line_style_array": ["1"],
             "plot_number_of_times_to_reset_color_palette": "0",
      "plot_file_name_index_to_change_color_palette_array": ["1"],
                                 "plot_legend_names_array": [""],
                                "plot_figure_format_array": ["png"],
                                "plot_figure_size_x_array": ["8"],
                                "plot_figure_size_y_array": ["5"],
                                            "is_plot_grid": True,
                                            "is_show_plot": True, #Ta bort?
                                            "is_save_plot": True, #Ta bort?
                                              "plot_title": "",
                                            "y_axis_title": "Intensity [a.u]", 
                                            "x_axis_title": "Excitation energy [eV]", 
                                       "is_display_legend": True,
                                   "plot_legend_text_size": "16",
                                    "plot_legend_position": ["10","10"],
                                        "plot_legend_size": ["30","30"],
                                         "plot_map_colors": "", #Ta bort? han en liknande med colormap
                                             "plot_colors": [],
                                           "is_inset_plot": False, 
                                         "inset_plot_name": "",
                                     "inset_plot_position": ["20","20"],
                                         "inset_plot_size": ["30","30"],
                                    "is_extra_plot_script": False,
                                  "extra_plot_script_name": "extra_plot_script_0", #Make a copy of the extra plot scipt and increase the number to save the unique script with your plot preferences.
                          #for subtraction of maps:
                             "is_normalize_maps_in_region": False,
                       "normalization_region_energy_scale": "Emission energy",  # or "Energy loss"
                            "normalization_excitation_min": "130",
                            "normalization_excitation_max": "136",
                                     "normalization_x_min": "140",
                                     "normalization_x_max": "145",
                "is_plot_difference_intensity_limits_used": False,
                           "plot_difference_intensity_min": "-1",
                           "plot_difference_intensity_max": "1",
                                "plot_difference_colormap": "bwr",
                                "plot_colorbar_label_size": "14",
                        "is_excitation_energy_window_used": False,
                          #Extra information
                #"energy_per_channel_slope_of_elastic_peak": "1",
            #"energy_per_channel_intercept_of_elastic_peak": "1",
                 "degree_of_energy_per_channel_polynomial": "1",
        "energy_per_channel_polynomial_coefficients_array": ["1", "1"] #c + bx + ax^2 + ...
        }
    return default_parameters
