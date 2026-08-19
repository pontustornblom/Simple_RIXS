#integrate_and_add_multiple_RIXS_spectra_to_waterfall

import sys
import os
import platform
import subprocess
from PyQt5.QtWidgets import QLabel, QMainWindow, QCheckBox, QComboBox, QLineEdit, QPushButton, QLayout, QApplication, QVBoxLayout, QHBoxLayout, QWidget, QDesktopWidget, QLabel, QTextEdit, QMessageBox, QScrollArea
#from PyQt5.QtGui import QPixmap
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from math import floor, ceil
import numpy as np
from PyQt5.QtCore import QEventLoop
from PyQt5.QtCore import pyqtSignal
import pandas as pd
import heapq
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
from matplotlib.pyplot import cm
import subprocess
from scipy.optimize import curve_fit
from scipy import stats
from scipy.ndimage import gaussian_filter1d
from scipy.interpolate import interp1d
import json
import h5py
import parameter_scripts
import get_single_spectrum_h5_or_txt_file_scripts
import iteratable_number_to_int_script
import iteratable_number_to_float_script
import find_elastic_peak_maximum_script
import create_complete_file_location_view_roots_or_txt_script
import create_complete_file_location_for_treated_data
import get_treated_rixs_data_script
import smoothing_scripts

def run_main_gui(parameters):
    # Check if an application instance already exists.
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    main_window = MainWindow(parameters)
    main_window.show()

    # Create a local event loop that waits until the main window is closed
    loop = QEventLoop()
    main_window.finished.connect(loop.quit)
    loop.exec_()

    parameters = main_window.get_inputted_parameters_from_gui()
    return parameters

class MainWindow(QMainWindow):
    finished = pyqtSignal()
    def __init__(self, parameters):
        super().__init__()
        self.parameters = parameters
        self.initUI()

    def initUI(self):      
        screen_geometry = QDesktopWidget().screenGeometry()
        #self.setFixedSize(floor(screen_geometry.width()/2 -5), screen_geometry.height()-160)
        #self.setFixedWidth(floor(screen_geometry.width()/2 -5))
        self.setMinimumWidth(floor(screen_geometry.width()/2 -20))
        self.setFixedHeight(floor(screen_geometry.height() -floor(screen_geometry.height()/9)))
        #self.setMinimumWidth(self.width())
        #self.adjustSize()
        self.move(floor(screen_geometry.width()/2 +10), 10)

        #parameters, complete_file_location = create_complete_file_location_view_roots_or_txt_script.create_complete_file_location_view_roots_or_txt(self.parameters, False, self.parameters["input_complete_file_name_array"][0])
        #complete_file_location= complete_file_location[:-8] + "parameters.txt"
        #self.treated_parameters = parameter_scripts.get_treated_parameters(complete_file_location)
        

        #self.is_first_and_last_spectrum_displayed= False
        #self.is_approximate_energy_for_normalization_to_zero_displayed= False 
        #self.is_subtract_fitted_background_displayed= False 
        #self.is_energy_window_used_displayed= False
        #self.is_plot_intensity_limits_used_displayed= False

        self.vbox = QVBoxLayout()

        self.vbox.addLayout(self.create_gui_item("input_file_project_folder", "Folder of the current project: ", "q_line_edit", [""]))
        self.vbox.addLayout(self.create_gui_item("input_file_raw_data_folder", "Subfolder where the raw data is stored: ", "q_line_edit", [""]))
        self.vbox.addLayout(self.create_gui_item("open file location", "Open raw data file location", "q_push_button",  [""]))   

        self.vbox.addLayout(self.create_gui_item("Update the plot", "Update the plot", "q_push_button",  [""]))

        self.vbox.addLayout(self.create_bottom_buttons())

        self.vbox.addLayout(self.create_gui_item("", "The following four inputs does not effect the calculation, it affects the saved file name", "q_text_label", [""]))
        self.vbox.addLayout(self.create_gui_item("output_file_element", "Element that is being studied: ", "q_line_edit", [""]))
        self.vbox.addLayout(self.create_gui_item("output_file_edge", "Edge that is being studied: ", "q_combo_box", ["K-edge", "L-edge", "L1-edge", "L2-edge", "L3-edge", "M-edge", "M1-edge", "M5-edge"]))
        self.vbox.addLayout(self.create_gui_item("output_file_sample_name", "Sample series name: ", "q_line_edit", [""]))
        self.vbox.addLayout(self.create_gui_item("output_file_additional_comment", "Addional comment that will be saved with the file name: ", "q_line_edit", [""]))

        self.vbox.addLayout(self.create_gui_item("plot_figure_size_x_array_0", "What figure size in the x direction would you like? ", "q_line_edit", [""]))
        self.vbox.addLayout(self.create_gui_item("plot_figure_size_y_array_0", "What figure size in the y direction would you like? ", "q_line_edit", [""]))

        self.vbox.addLayout(self.create_gui_item("x_axis_title", "What is the title of the x-axis? ", "q_line_edit", [""]))
        self.vbox.addLayout(self.create_gui_item("y_axis_title", "What is the title of the y-axis? ", "q_line_edit", [""]))

        self.vbox.addLayout(self.create_gui_item("plot_x_axis_text_size", "What is the text size of the x-axis? ", "q_line_edit", [""]))
        self.vbox.addLayout(self.create_gui_item("plot_y_axis_text_size", "What is the text size of the y-axis? ", "q_line_edit", [""]))
        
        self.vbox.addLayout(self.create_gui_item("plot_x_axis_number_size", "What is the number size of the x-axis? ", "q_line_edit", [""]))
        self.vbox.addLayout(self.create_gui_item("plot_y_axis_number_size", "What is the number size of the y-axis? ", "q_line_edit", [""]))


        self.vbox.addLayout(self.create_gui_item("plot_display_sample_name_title", "Would you like to display a title of the plot? ", "q_check_box", [""]))
        self.vbox.addLayout(self.create_gui_item("plot_title", "Input the title of the plot: ", "q_line_edit", [""]))
        self.vbox.addLayout(self.create_gui_item("plot_title_size", "What text size of the title would you like? ", "q_line_edit", [""]))

        self.vbox.addLayout(self.create_gui_item("is_display_legend", "Would you like to display the legend? ", "q_check_box", [""]))
        self.vbox.addLayout(self.create_gui_item("plot_legend_text_size", "What text size of the legend would you like? ", "q_line_edit", [""]))

        self.vbox.addLayout(self.create_gui_item("is_plot_grid", "Would you like to display vertical grid lines? ", "q_check_box", [""]))

        self.vbox.addLayout(self.create_gui_item("is_energy_window_used_array_0", "Would you like to zoom in on the plot in the x-direction? ", "q_check_box", [""]))
        if self.parameters["is_energy_window_used_array"][0]:
            self.vbox.addLayout(self.create_gui_item("plot_energy_loss_min_array_0", "Input the lower cut off for the x-axis: ", "q_line_edit", [""]))
            self.vbox.addLayout(self.create_gui_item("plot_energy_loss_max_array_0", "Input the upper cut off for the x-axis: ", "q_line_edit", [""]))

        self.vbox.addLayout(self.create_gui_item("is_plot_intensity_limits_used_array_0", "Would you like to zoom in on the plot in the y-direction? ", "q_check_box", [""]))
        if self.parameters["is_plot_intensity_limits_used_array"][0]:
            self.vbox.addLayout(self.create_gui_item("plot_intensity_min_array_0", "Input the lower cut off for the y-axis: ", "q_line_edit", [""]))
            self.vbox.addLayout(self.create_gui_item("plot_intensity_max_array_0", "Input the upper cut off for the y-axis: ", "q_line_edit", [""]))

        self.vbox.addLayout(self.create_gui_item("plot_spectra_grouping_type", "How would you like to group the spectra together? ", "q_combo_box", ["No grouping", "Group by integration region", "Group by file"]))
        self.vbox.addLayout(self.create_gui_item("plot_distance_between_groups_in_y", "Input the distance the groups should have along the y-axis: ", "q_line_edit", [""]))
        self.vbox.addLayout(self.create_gui_item("plot_y_distance_between_plots", "Input the distance the spectra within a group should have along the y-axis: ", "q_line_edit", [""]))

        self.vbox.addLayout(self.create_gui_item("plot_number_of_times_to_change_line_style", "How many times do you want to change the line style? ", "q_line_edit", [""]))
        if self.parameters["plot_number_of_times_to_change_line_style"] != "0" and self.parameters["plot_number_of_times_to_change_line_style"] != "":
            for linestyle_change_index in range(int(self.parameters["plot_number_of_times_to_change_line_style"])):
                self.vbox.addLayout(self.create_gui_item("plot_file_name_index_to_change_line_style_array_" + str(linestyle_change_index), "Input the file name index of when to change line style (Input a number): ", "q_line_edit", [""]))
        
        self.vbox.addLayout(self.create_gui_item("plot_number_of_times_to_reset_color_palette", "How many times do you want to reset the color palette? ", "q_line_edit", [""]))
        if self.parameters["plot_number_of_times_to_reset_color_palette"] != "0" and self.parameters["plot_number_of_times_to_reset_color_palette"] != "":
            for color_palette_change_number in range(int(self.parameters["plot_number_of_times_to_reset_color_palette"])):
                self.vbox.addLayout(self.create_gui_item("plot_file_name_index_to_change_color_palette_array_" + str(color_palette_change_number), "Input the file name index of when to reset the color palette (Input a number): ", "q_line_edit", [""]))

        self.vbox.addLayout(self.create_gui_item("plot_display_incoming_energy_by_lines", "Would you like to display the incoming energy next to the spectra? ", "q_check_box", [""]))
        self.vbox.addLayout(self.create_gui_item("plot_incoming_energy_x_offset", "Input value to adjust the x cooridnate of the incoming energy text: ", "q_line_edit", [""]))
        self.vbox.addLayout(self.create_gui_item("plot_incoming_energy_y_offset", "Input value to adjust the y cooridnate of the incoming energy text: ", "q_line_edit", [""]))
        self.vbox.addLayout(self.create_gui_item("plot_incoming_energy_text_size", "What text size of the incoming energy text would you like: ", "q_line_edit", [""]))
        self.vbox.addLayout(self.create_gui_item("plot_incoming_energy_significant_numbers", "What many significant numbers of the incoming energy text would you like to display? ", "q_line_edit", [""]))

        self.vbox.addLayout(self.create_gui_item("is_automatically_adjust_peak_to_correct_energy", "Would you like the program to automatically shift the elastic peak along the x-axis to its correct energy for each spectra?\n(Not recommended for low intensity, very low resolution, noisy or very nonsymmetric elastic peaks!)\n(OBS! Your manual shift will be applied after the automatical shift if you have that box checked)\n(OBS! Make sure that you have selected the correct degree of polynomial to fit the x axis values to!)\nThis is currently using a squared weighted fit to the elastic peak ", "q_check_box", [""]))

        self.vbox.addLayout(self.create_gui_item("is_binning_smooth_data_for_all_spectra", "Would you like to do bin datapoints together to smooth the data for all spectra? \n(This will override any selection of smoothening of an individual spectra below) ", "q_check_box", [""]))
        if self.parameters["is_binning_smooth_data_for_all_spectra"]:
            self.vbox.addLayout(self.create_gui_item("number_of_bins_for_smoothing_array_0", "How many datapoints would you like to bin together for this spectra? ", "q_line_edit", [""]))
   
        self.vbox.addLayout(self.create_gui_item("is_gaussian_smooth_data_for_all_spectra", "Would you like to do gaussian smoothening for all spectra? \n(This will override any selection of smoothening of an individual spectra below) ", "q_check_box", [""]))
        if self.parameters["is_gaussian_smooth_data_for_all_spectra"]:
            self.vbox.addLayout(self.create_gui_item("sigma_for_gaussian_smoothing_array_0", "What value of sigma would you like for the gaussian smoothing? ", "q_line_edit", [""]))


        self.vbox.addLayout(self.create_gui_item("is_normalize_intensity_at_certain_emission_energy", "Would you like to do normalize the intenisty at a certain emission energy for all spectra? ", "q_check_box", [""]))
        if self.parameters["is_normalize_intensity_at_certain_emission_energy"]:
            self.vbox.addLayout(self.create_gui_item("emission_energy_for_intenisty_normalization", "What emission energy would you like to normalize to? ", "q_line_edit", [""]))
            self.vbox.addLayout(self.create_gui_item("emission_energy_above_and_below_for_normalization", "What energy above and below the selected emission energy would like you average over? ", "q_line_edit", [""]))

        self.create_dynamic_gui_item_for_waterfall_inputs()

        self.vbox.addLayout(self.create_gui_item("Update the plot", "Update the plot", "q_push_button",  [""]))

        self.vbox.addLayout(self.create_gui_item("", "If everything looks good then a figure will be saved when you hit Save and continue", "q_text_label", [""]))

        self.vbox.addLayout(self.create_bottom_buttons())

        self.central_widget = QWidget()
        self.central_widget.setLayout(self.vbox)
        self.setCentralWidget(self.central_widget)

        #Scrollstuff:
        self.scroll = QScrollArea()
        self.scroll.setWidget(self.central_widget)
        self.scroll.setWidgetResizable(True)
        self.setCentralWidget(self.scroll)

        self.setWindowTitle("Simple RIXS integrate and add multiple spectra to waterfall")
        self.show()

        #if self.is_first_and_last_spectrum_displayed== False:
        
        #This line below has to b etoggleed manually (If this script actually needs to plot something)
        self.plot_inputted_data(self.parameters, "")
        #try:
        #    self.plot_inputted_data(self.parameters, "")
        #except (IndexError, ValueError):
        #    print("Exception happened")
        #    self.plot_only_raw_data(self.parameters)
        
        #parameters, complete_file_location = create_complete_file_location_view_roots_or_txt_script.create_complete_file_location_view_roots_or_txt(self.parameters)


    def create_gui_item(self, key, item_label_text, item_type, combo_box_options):
        hbox = QHBoxLayout()
        item_label = QLabel(item_label_text)
        if item_type =="q_line_edit":
            hbox.addWidget(item_label)
            if "array" in key:
                split_key_list = key.split('_')
                array_key = '_'.join(split_key_list[:-1])
                array_index = int(split_key_list[-1])
                #complete_treated_file_location= create_complete_file_location_for_treated_data.create_complete_file_location_for_treated_data(self.parameters["input_file_project_folder"], self.parameters["input_complete_file_name_array"][array_index])
                #complete_file_location= complete_file_location[:-8] + "parameters.txt"
                #self.treated_parameters = parameter_scripts.get_treated_parameters(complete_file_location)
                condition = True
                while condition:
                    try:
                        item = QLineEdit(self.parameters[array_key][array_index])
                        condition = False
                    except (IndexError):
                        self.parameters[array_key].append(self.parameters[array_key][0])
                hbox.addWidget(item)
                item.editingFinished.connect(lambda item=item: self.update_dictionary_array(array_key, array_index, item))
            elif key == "plot_number_of_times_to_change_line_style" or key == "plot_number_of_times_to_reset_color_palette":
                item = QLineEdit(self.parameters[key])
                hbox.addWidget(item)
                item.editingFinished.connect(lambda: self.create_dynamic_gui_items_from_line_edit(item, item.text(), key, hbox))
            elif key != "input_file_project_folder" and key != "input_file_raw_data_folder" and key[:22] != "pfy_region_name_array_" and key != "y_axis_title" and key != "x_axis_title" and key != "output_file_element" and key != "output_file_sample_name" and key != "output_file_additional_comment" and key != "plot_title":
                item = QLineEdit(self.parameters[key])
                hbox.addWidget(item)
                item.editingFinished.connect(lambda item=item, key=key: self.validate_input(item, key))
            else:
                item = QLineEdit(self.parameters[key])
                hbox.addWidget(item)
                item.textChanged.connect(lambda: self.update_dictionary(key, item.text()))
        elif item_type == "q_combo_box":
            hbox.addWidget(item_label)
            if "array" in key:
                split_key_list = key.split('_')
                array_key = '_'.join(split_key_list[:-1])
                array_index = int(split_key_list[-1])
                item = QComboBox()
                item.addItems(combo_box_options)
                condition = True
                while condition:
                    try:
                        item.setCurrentText(self.parameters[array_key][array_index])
                        condition = False
                    except (IndexError):
                        self.parameters[array_key].append(self.parameters[array_key][0])
                hbox.addWidget(item)
                item.currentTextChanged.connect(lambda: self.update_dictionary_combobox_array(array_key, array_index, item))
            else:
                item = QComboBox()
                item.addItems(combo_box_options)
                item.setCurrentText(self.parameters[key])
                hbox.addWidget(item)
                item.currentTextChanged.connect(lambda: self.update_dictionary(key, item.currentText()))
        elif item_type == "q_check_box":
            hbox.addWidget(item_label)
            item = QCheckBox()
            if key == "is_approximate_energy_for_normalization_to_zero":
                item.setChecked(self.parameters[key])
                hbox.addWidget(item)
                item.clicked.connect(lambda: self.create_multiple_gui_items_from_checkboxes(item, key, hbox))          
            elif key == "is_subtract_fitted_background":
                item.setChecked(self.parameters[key])
                hbox.addWidget(item)
                item.clicked.connect(lambda: self.create_multiple_gui_items_from_checkboxes(item, key, hbox))          
            elif key == "is_energy_window_used":
                item.setChecked(self.parameters[key])
                hbox.addWidget(item)
                item.clicked.connect(lambda: self.create_multiple_gui_items_from_checkboxes(item, key, hbox))
            elif key == "is_binning_smooth_data_for_all_spectra":
                item.setChecked(self.parameters[key])
                hbox.addWidget(item)
                item.clicked.connect(lambda: self.create_multiple_gui_items_from_checkboxes(item, key, hbox))
            elif key == "is_gaussian_smooth_data_for_all_spectra":
                item.setChecked(self.parameters[key])
                hbox.addWidget(item)
                item.clicked.connect(lambda: self.create_multiple_gui_items_from_checkboxes(item, key, hbox))
            elif key == "is_normalize_intensity_at_certain_emission_energy":
                item.setChecked(self.parameters[key])
                hbox.addWidget(item)
                item.clicked.connect(lambda: self.create_multiple_gui_items_from_checkboxes(item, key, hbox))
            elif "array" in key:
                split_key_list = key.split('_')
                array_key = '_'.join(split_key_list[:-1])
                array_index = int(split_key_list[-1])
                item = QCheckBox()
                condition = True
                while condition:
                    try:
                        item.setChecked(self.parameters[array_key][array_index])
                        condition = False
                    except (IndexError):
                        self.parameters[array_key].append(self.parameters[array_key][0])
                hbox.addWidget(item)
                item.clicked.connect(lambda: self.create_multiple_gui_items_from_checkbox_arrays(array_key, array_index, item, hbox))
            else:
                item.setChecked(self.parameters[key])
                hbox.addWidget(item)
                item.clicked.connect(lambda: self.update_dictionary_checkbox(key, item))
        elif item_type =="q_push_button":
            item_label = QLabel("")
            hbox.addWidget(item_label)
            item= QPushButton(item_label_text)
            hbox.addWidget(item)
            if key== "open file location":
                item.clicked.connect(lambda: self.open_folder(self.parameters["input_file_project_folder"], self.parameters["input_file_raw_data_folder"]))
            elif key=="Zoom in on elastic peak":
                item.clicked.connect(lambda: self.plot_inputted_data(self.parameters, "zoom_in_on_plot"))
            elif key== "Update the plot":
                item.clicked.connect(lambda: self.plot_inputted_data(self.parameters, "update_plot"))
        elif item_type=="q_text_label":
            hbox.addWidget(item_label)
        else:
            print("Error: Item was not added to the GUI")
        return hbox

    def update_dictionary(self, key, updated_value):
        self.parameters[key] = updated_value

    def update_dictionary_checkbox(self, key, item):
                if item.isChecked():
                    self.parameters[key] = True
                    if key== "is_view_roots_or_input_txt":
                        self.vbox.insertLayout(self.vbox.count()-1,self.create_gui_item("input_complete_file_name_array_0", "Input example file name to view roots/txt ", "q_line_edit", [""]))                
                else:
                    self.parameters[key] = False
    
    def update_dictionary_combobox_array(self, key, array_index, item):
        self.parameters[key][array_index] = item.currentText()

    def update_dictionary_checkbox_array(self, key, array_index, item):
            #if self.validate_input_for_array(key, array_index, item):
            self.parameters[key][array_index] = item.isChecked()

    def update_dictionary_array(self, key, array_index, item):
            if self.validate_input_for_array(key, array_index, item):
                self.parameters[key][array_index] = item.text()

    def validate_input_for_array(self, key, array_index, item):
        if item.text() != self.parameters[key][array_index]:
            if key == "plot_legend_names_array" or key == "input_complete_file_name_array":
                return True
            if item.text()== "":
                try:
                    float(item.text())
                    return True
                except:
                    QMessageBox.warning(
                            self, "Invalid Input", "Do not leave blank"
                        )
                    item.clear()
                    return False
            else:
                try:
                    if item.text()[0] =="0":
                        float(iteratable_number_to_float_script.iteratable_number_to_float(item.text()))
                        return True
                    else:
                        float(item.text())
                        return True
                except ValueError:
                    QMessageBox.warning(
                        self, "Invalid Input", "Input must be an integer or float."
                    )
                    item.clear()
                    return False

    def validate_input(self, item, key):
        if item.text() != self.parameters[key]:
            self.update_dictionary(key, item.text())
            if item.text()== "":
                try:
                    float(item.text())
                    return True
                except:
                    QMessageBox.warning(
                            self, "Invalid Input", "Do not leave blank"
                        )
                    item.clear()
                    return False
            else:
                try:
                    if item.text()[0] =="0":
                        float(iteratable_number_to_float_script.iteratable_number_to_float(item.text()))
                        return True
                    else:
                        float(item.text())
                        return True
                except ValueError:
                    QMessageBox.warning(
                        self, "Invalid Input", "Input must be an integer or float."
                    )
                    item.clear()
                    return False
                

    def create_dynamic_gui_items_from_line_edit(self, item, item_text, key, hbox):
        if self.parameters[key] == "":
            old_number_of_changes = 0
        else:
            old_number_of_changes= int(self.parameters[key])
        if self.validate_input(item, key):
            if key == "plot_number_of_times_to_change_line_style":
                if old_number_of_changes > 0:
                    for line_style_change_number in range(old_number_of_changes):
                        self.remove_item(self.vbox.indexOf(hbox)+line_style_change_number+1)
                if int(item_text) != 0:
                    for linestyle_change_index in range(int(item_text)):
                        self.vbox.insertLayout(self.vbox.indexOf(hbox)+1, self.create_gui_item("plot_file_name_index_to_change_line_style_array_" + str(linestyle_change_index), "Input the file name index of when to change line style (Input a number): ", "q_line_edit", [""]))

            elif key == "plot_number_of_times_to_reset_color_palette":
                if old_number_of_changes > 0:
                    for color_palette_change_number in range(old_number_of_changes):
                        self.remove_item(self.vbox.indexOf(hbox)+color_palette_change_number+1)
                if int(item_text) != 0:
                    for color_palette_change_number in range(int(item_text)):
                        self.vbox.insertLayout(self.vbox.indexOf(hbox)+1, self.create_gui_item("plot_file_name_index_to_change_color_palette_array_" + str(color_palette_change_number), "Input the file name index of when to reset the color palette (Input a number): ", "q_line_edit", [""]))

    def create_multiple_gui_items_from_checkboxes(self, item, key, hbox):
        self.update_dictionary_checkbox(key, item)
        
        if key == "is_approximate_energy_for_normalization_to_zero":
            if self.is_approximate_energy_for_normalization_to_zero_displayed== False and self.parameters["is_approximate_energy_for_normalization_to_zero"]:
                self.vbox.insertLayout(self.vbox.indexOf(hbox)+1,self.create_gui_item("approximate_energy_for_normalization_to_zero", "Approximate incoming energy of lowest intenisty: ", "q_line_edit", [""]))
                self.is_approximate_energy_for_normalization_to_zero_displayed =True
            elif self.is_approximate_energy_for_normalization_to_zero_displayed == True and self.parameters["is_approximate_energy_for_normalization_to_zero"] == False:
                self.remove_item(self.vbox.indexOf(hbox)+1)
                self.is_approximate_energy_for_normalization_to_zero_displayed =False
        elif key == "is_subtract_fitted_background":
            if self.is_subtract_fitted_background_displayed== False and self.parameters["is_subtract_fitted_background"]:
                self.vbox.insertLayout(self.vbox.indexOf(hbox)+1,self.create_gui_item("background_fit_type", "What type of graph would you like to fit? ", "q_combo_box", ["Linear", "ln(x)", "log(x)", "Gaussian", "x^(-2)"]))
                self.vbox.insertLayout(self.vbox.indexOf(hbox)+2,self.create_gui_item("background_fit_energy_start", "From what energy should the graph be fitted? ", "q_line_edit", [""]))
                self.vbox.insertLayout(self.vbox.indexOf(hbox)+3,self.create_gui_item("background_fit_energy_end", "To what energy should the graph be fitted? ", "q_line_edit", [""]))
                self.is_subtract_fitted_background_displayed =True
            elif self.is_subtract_fitted_background_displayed == True and self.parameters["is_subtract_fitted_background"] == False:
                self.remove_item(self.vbox.indexOf(hbox)+1)
                self.remove_item(self.vbox.indexOf(hbox)+2)
                self.remove_item(self.vbox.indexOf(hbox)+3)
                self.is_subtract_fitted_background_displayed =False
        elif key == "is_energy_window_used":
            if self.is_energy_window_used_displayed== False and self.parameters["is_energy_window_used"]:
                self.vbox.insertLayout(self.vbox.indexOf(hbox)+1, self.create_gui_item("plot_incoming_energy_min", "Input the lower cut off for the incoming energy window: ", "q_line_edit", [""]))
                self.vbox.insertLayout(self.vbox.indexOf(hbox)+2, self.create_gui_item("plot_incoming_energy_max", "Input the upper cut off for the incoming energy window: ", "q_line_edit", [""]))            
                self.is_energy_window_used_displayed =True
            elif self.is_energy_window_used_displayed == True and self.parameters["is_energy_window_used"] == False:
                self.remove_item(self.vbox.indexOf(hbox)+1)
                self.remove_item(self.vbox.indexOf(hbox)+2)
                self.is_energy_window_used_displayed =False
        elif key == "is_plot_intensity_limits_used":
            if self.is_plot_intensity_limits_used_displayed== False and self.parameters["is_plot_intensity_limits_used"]:
                self.vbox.insertLayout(self.vbox.indexOf(hbox)+1, self.create_gui_item("plot_intensity_min", "Input the lower cut off for the intensity window: ", "q_line_edit", [""]))
                self.vbox.insertLayout(self.vbox.indexOf(hbox)+2, self.create_gui_item("plot_intensity_max", "Input the upper cut off for the intensity window: ", "q_line_edit", [""]))
                self.is_plot_intensity_limits_used_displayed =True
            elif self.is_plot_intensity_limits_used_displayed == True and self.parameters["is_plot_intensity_limits_used"] == False:
                self.remove_item(self.vbox.indexOf(hbox)+1)
                self.remove_item(self.vbox.indexOf(hbox)+2)
                self.is_plot_intensity_limits_used_displayed =False
        elif key == "is_binning_smooth_data_for_all_spectra":
            if self.parameters["is_binning_smooth_data_for_all_spectra"]:
                self.vbox.insertLayout(self.vbox.indexOf(hbox)+1, self.create_gui_item("number_of_bins_for_smoothing_array_0", "What how many datapoints would you like to bin together? ", "q_line_edit", [""]))
            elif self.parameters["is_binning_smooth_data_for_all_spectra"]== False:
                self.remove_item(self.vbox.indexOf(hbox)+1)
        elif key == "is_gaussian_smooth_data_for_all_spectra":
            if self.parameters["is_gaussian_smooth_data_for_all_spectra"]:
                self.vbox.insertLayout(self.vbox.indexOf(hbox)+1, self.create_gui_item("sigma_for_gaussian_smoothing_array_0", "What value of sigma would you like for the gaussian smoothing? ", "q_line_edit", [""]))
            elif self.parameters["is_gaussian_smooth_data_for_all_spectra"]== False:
                self.remove_item(self.vbox.indexOf(hbox)+1)
        elif key == "is_normalize_intensity_at_certain_emission_energy":
            if self.parameters["is_normalize_intensity_at_certain_emission_energy"]:
                self.vbox.insertLayout(self.vbox.indexOf(hbox)+1, self.create_gui_item("emission_energy_for_intenisty_normalization", "What emission energy would you like to normalize to? ", "q_line_edit", [""]))
                self.vbox.insertLayout(self.vbox.indexOf(hbox)+2, self.create_gui_item("emission_energy_above_and_below_for_normalization", "What energy above and below the selected emission energy would like you average over? ", "q_line_edit", [""]))
            elif self.parameters["is_normalize_intensity_at_certain_emission_energy"] == False:
                self.remove_item(self.vbox.indexOf(hbox)+1)
                self.remove_item(self.vbox.indexOf(hbox)+2)

    def create_multiple_gui_items_from_checkbox_arrays(self, key, array_index, item, hbox):
        self.update_dictionary_checkbox_array(key, array_index, item)
        if key == "is_approximate_energy_for_normalization_to_zero_array":
            if self.parameters["is_approximate_energy_for_normalization_to_zero_array"][array_index]:
                self.vbox.insertLayout(self.vbox.indexOf(hbox)+1,self.create_gui_item("approximate_energy_for_normalization_to_zero_array_" + str(array_index), "Approximate incoming energy of lowest intenisty for region " + self.parameters["pfy_region_name_array"][array_index] + ":", "q_line_edit", [""]))
                self.vbox.insertLayout(self.vbox.indexOf(hbox)+2,self.create_gui_item("energy_above_and_below_finding_min_intensity_array_" + str(array_index), "How many eV above and below the approximate intensity should \nthe lowest intensity be searched over for region " +self.parameters["pfy_region_name_array"][array_index] +"? ", "q_line_edit", [""]))

            elif self.parameters["is_approximate_energy_for_normalization_to_zero_array"][array_index] == False:
                self.remove_item(self.vbox.indexOf(hbox)+1)
                self.remove_item(self.vbox.indexOf(hbox)+2)
        elif key == "is_subtract_fitted_background_array":
            if self.parameters["is_subtract_fitted_background_array"][array_index]:
                self.vbox.insertLayout(self.vbox.indexOf(hbox)+1,self.create_gui_item("background_fit_type_array_" + str(array_index), "What type of graph would you like to fit? ", "q_combo_box", ["Linear", "ln(x)", "log(x)", "Gaussian", "x^(-2)"]))
                self.vbox.insertLayout(self.vbox.indexOf(hbox)+2,self.create_gui_item("background_fit_energy_start_array_" + str(array_index), "From what energy should the graph be fitted? ", "q_line_edit", [""]))
                self.vbox.insertLayout(self.vbox.indexOf(hbox)+3,self.create_gui_item("background_fit_energy_end_array_" + str(array_index), "To what energy should the graph be fitted? ", "q_line_edit", [""]))
                
            elif self.parameters["is_subtract_fitted_background_array"][array_index] == False:
                self.remove_item(self.vbox.indexOf(hbox)+1)
                self.remove_item(self.vbox.indexOf(hbox)+2)
                self.remove_item(self.vbox.indexOf(hbox)+3)
                
        elif key == "is_energy_window_used_array":
            if self.parameters["is_energy_window_used_array"][array_index]:
                self.vbox.insertLayout(self.vbox.indexOf(hbox)+1,self.create_gui_item("plot_energy_loss_min_array_" + str(array_index), "Input the lower cut off for the x-axis: ", "q_line_edit", [""]))
                self.vbox.insertLayout(self.vbox.indexOf(hbox)+2,self.create_gui_item("plot_energy_loss_max_array_" + str(array_index), "Input the upper cut off for the x-axis: ", "q_line_edit", [""]))
            elif self.parameters["is_energy_window_used_array"][array_index] == False:
                self.remove_item(self.vbox.indexOf(hbox)+1)
                self.remove_item(self.vbox.indexOf(hbox)+2)
        elif key == "is_plot_intensity_limits_used_array":
            if self.parameters["is_plot_intensity_limits_used_array"][array_index]:
                self.vbox.insertLayout(self.vbox.indexOf(hbox)+1, self.create_gui_item("plot_intensity_min_array_" + str(array_index), "Input the lower cut off for the intensity window: ", "q_line_edit", [""]))
                self.vbox.insertLayout(self.vbox.indexOf(hbox)+2, self.create_gui_item("plot_intensity_max_array_" + str(array_index), "Input the upper cut off for the intensity window: ", "q_line_edit", [""]))
            elif self.parameters["is_plot_intensity_limits_used_array"][array_index] == False:
                self.remove_item(self.vbox.indexOf(hbox)+1)
                self.remove_item(self.vbox.indexOf(hbox)+2)
        elif key =="is_binning_smooth_data_array":
            if self.parameters[key][array_index]:
                self.vbox.insertLayout(self.vbox.indexOf(hbox)+1, self.create_gui_item("number_of_bins_for_smoothing_array_" + str(array_index), "How many datapoints would you like to bin together? ", "q_line_edit", [""]))
            elif self.parameters[key][array_index]== False:
                self.remove_item(self.vbox.indexOf(hbox)+1)
        elif key =="is_gaussian_smooth_data_array":
            if self.parameters[key][array_index]:
                self.vbox.insertLayout(self.vbox.indexOf(hbox)+1, self.create_gui_item("sigma_for_gaussian_smoothing_array_" + str(array_index), "What value of sigma would you like for the gaussian smoothing? ", "q_line_edit", [""]))
            elif self.parameters[key][array_index]== False:
                self.remove_item(self.vbox.indexOf(hbox)+1)


    def create_dynamic_gui_item_for_waterfall_inputs(self):
        array_index = 0
        for file_name_index in range(int(self.parameters["input_number_of_complete_file_names"])):
            for incoming_energy_region_index in range(int(self.parameters["number_of_pfy_regions"])):
                #self.vbox.insertLayout(self.vbox.indexOf(hbox)+2*pfy_region+1,self.create_gui_item("incoming_energy_segment_"+ str(pfy_region), "First incoming energy of segment "+ str(pfy_region)+":                     ", "q_line_edit", [""]))
                #self.vbox.insertLayout(self.vbox.indexOf(hbox)+2*pfy_region+2,self.create_gui_item("incoming_energy_difference_in_segment_"+ str(pfy_region), "Excitation energy difference of spectra in segment "+ str(pfy_region)+ ":", "q_line_edit", [""]))
                #self.vbox.insertLayout(self.vbox.indexOf(hbox)+2*int(item_text)+1,self.create_gui_item("incoming_energy_of_last_spectra", "Excitation energy of last spectra: ", "q_line_edit", [""]))
                
                self.vbox.addLayout(self.create_gui_item("", "------------ Inputs for file " + self.parameters["plot_legend_names_array"][file_name_index] + " between " + self.parameters["pfy_incoming_energy_start_array"][incoming_energy_region_index] + "-" +self.parameters["pfy_incoming_energy_end_array"][incoming_energy_region_index] + " eV ------------" , "q_text_label", [""]))

                #self.vbox.addLayout(self.create_gui_item("plot_legend_names_array_" + str(file_name_index), "Name of this data: ", "q_line_edit", [""]))
            
                #self.vbox.addLayout(self.create_gui_item("plot_waterfall_space_y_array_" + str(file_name_index), "How much should the plot be translated in the y-direction: ", "q_line_edit", [""]))           

                #self.vbox.addLayout(self.create_gui_item("is_invert_the_plot_array_" + str(array_index), "Would you like to invert the plot? ", "q_check_box", [""]))
                
                self.vbox.addLayout(self.create_gui_item("plot_is_scale_intensity_of_spectra_array_" + str(array_index), "Would you like to scale the intensity of this spectra? ", "q_check_box", [""]))
                self.vbox.addLayout(self.create_gui_item("plot_scaling_array_" + str(array_index), "Input value that you want to multiply the intensity by: ", "q_line_edit", [""]))
                self.vbox.addLayout(self.create_gui_item("plot_scaling_text_x_offset_array_" + str(array_index), "How much do you want to offset the scaling text in the x direction? ", "q_line_edit", [""]))
                self.vbox.addLayout(self.create_gui_item("plot_scaling_text_y_offset_array_" + str(array_index), "How much do you want to offset the scaling text in the y direction? ", "q_line_edit", [""]))
                
                self.vbox.addLayout(self.create_gui_item("is_binning_smooth_data_array_" + str(array_index), "Would you like to bin together the datapoints in this spectra? ", "q_check_box", [""]))
                if self.parameters["is_binning_smooth_data_array"][array_index]:
                    self.vbox.addLayout(self.create_gui_item("number_of_bins_for_smoothing_array_" + str(array_index), "How many datapoints would you like to bin together for this spectra? ", "q_line_edit", [""]))

                self.vbox.addLayout(self.create_gui_item("is_gaussian_smooth_data_array_" + str(array_index), "Would you like to do a gaussian smoothening for this spectra? ", "q_check_box", [""]))
                if self.parameters["is_gaussian_smooth_data_array"][array_index]:
                    self.vbox.addLayout(self.create_gui_item("sigma_for_gaussian_smoothing_array_" + str(array_index), "What value of sigma would you like for the gaussian smoothing? ", "q_line_edit", [""]))
                #self.vbox.addLayout(self.create_gui_item("number_of_points_to_combine_array_" + str(array_index), "How many data points do you want to bin together? ", "q_line_edit", [""]))
                
                self.vbox.addLayout(self.create_gui_item("plot_intensity_offset_array_" + str(array_index), "Input value that you want to offset the intensity by: ", "q_line_edit", [""]))

                self.vbox.addLayout(self.create_gui_item("is_hide_certain_spectra_array_" + str(array_index), "Would you like to hide this spectra? ", "q_check_box", [""]))

                array_index += 1
                #self.vbox.addLayout(self.create_gui_item("is_normalize_to_zero_and_one_array_" + str(file_name_index), "Would you like to normalize the data by setting the lowest intensity \nto zero and the end intensity to one? \n(This normalization will happen if the plot is inverted)", "q_check_box", [""]))

                #self.vbox.addLayout(self.create_gui_item("incoming_energy_range_normalization_to_one_array_" + str(file_name_index), "How many incoming eV to average over at the end of the spectra \nto normalize the intensity to one: ", "q_line_edit", [""]))
                
                #self.vbox.addLayout(self.create_gui_item("is_approximate_energy_for_normalization_to_zero_array_" + str(file_name_index), "Would you like to set an approximate energy of where to find the minimum intensity? ", "q_check_box", [""]))
                #if self.parameters["is_approximate_energy_for_normalization_to_zero_array"][file_name_index]:
                #    self.vbox.addLayout(self.create_gui_item("approximate_energy_for_normalization_to_zero_array_" + str(file_name_index), "Approximate incoming energy of lowest intenisty: ", "q_line_edit", [""]))
                #    self.vbox.addLayout(self.create_gui_item("energy_above_and_below_finding_min_intensity_array_" + str(file_name_index), "How many eV above and below the approximate intensity should \nthe lowest intensity be searched over? ", "q_line_edit", [""]))

                    #self.is_approximate_energy_for_normalization_to_zero_displayed= True

                #self.vbox.addLayout(self.create_gui_item("energy_above_and_below_normalization_to_zero_array_" + str(file_name_index), "How many eV above and below the lowest intensity point should \nbe included to average over? ", "q_line_edit", [""]))

                #self.vbox.addLayout(self.create_gui_item("is_subtract_fitted_background_array_" + str(file_name_index), "Would you like to fit a graph to the background to subtract from the spectra? ", "q_check_box", [""]))
                #if self.parameters["is_subtract_fitted_background_array"][file_name_index]:
                #    self.vbox.addLayout(self.create_gui_item("background_fit_type_array_" + str(file_name_index), "What type of graph would you like to fit? ", "q_combo_box", ["Linear", "ln(x)", "log(x)", "Gaussian"]))
                #    self.vbox.addLayout(self.create_gui_item("background_fit_energy_start_array_" + str(file_name_index), "From what energy should the graph be fitted for region " +self.parameters["pfy_region_name_array"][file_name_index] +"? ", "q_line_edit", [""]))
                #    self.vbox.addLayout(self.create_gui_item("background_fit_energy_end_array_" + str(file_name_index), "To what energy should the graph be fitted? ", "q_line_edit", [""]))
                    #self.is_subtract_fitted_background_displayed= True 
                
                #self.vbox.addLayout(self.create_gui_item("is_combine_datapoints_array_" + str(file_name_index), "Would you like to bin datapoints together to smoothen the data? \n(Not implemented yet)", "q_check_box", [""]))
                #if self.parameters["is_combine_datapoints_array"][file_name_index]:
                #    self.vbox.addLayout(self.create_gui_item("number_of_points_to_combine_array_" + str(file_name_index), "How many datapoints would you like to bin together? ", "q_line_edit", [""]))

                               
    def remove_item(self, hbox_index):
        next_hbox = self.vbox.itemAt(hbox_index).layout()
        self.deleteItemsOfLayout(next_hbox.layout())

    def deleteItemsOfLayout(self, layout):
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.setParent(None)
                else:
                    self.deleteItemsOfLayout(item.layout())

    def create_bottom_buttons(self):
        save_and_continue_button = QPushButton("Save and Continue")
        save_and_close_button = QPushButton("Save and Close")
        close_program_button = QPushButton("Close")
        save_and_continue_button.clicked.connect(self.save_and_continue)
        save_and_close_button.clicked.connect(self.save_and_close)
        close_program_button.clicked.connect(self.close_program)
        hbox_bottom_buttons = QHBoxLayout()
        hbox_bottom_buttons.addWidget(save_and_continue_button)
        hbox_bottom_buttons.addWidget(save_and_close_button)
        hbox_bottom_buttons.addWidget(close_program_button)
        hbox_bottom_buttons.setSpacing(50)
        hbox_bottom_buttons.setSizeConstraint(QLayout.SetFixedSize)
        return hbox_bottom_buttons

    def closeEvent(self, event):
        if event.spontaneous():
            self.parameters["is_program_running"] = False
            self.finished.emit()
        event.accept()

    def save_and_continue(self):
        parameter_scripts.save_parameters(self.parameters)
        self.save_treated_data()
        plt.close()
        self.finished.emit()
        self.close()

    def save_and_close(self):
        parameter_scripts.save_parameters(self.parameters)
        self.parameters["is_program_running"]=False
        plt.close()
        self.finished.emit()
        self.close()

    def close_program(self): 
        self.parameters["is_program_running"]=False
        plt.close()
        self.finished.emit()
        self.close()

    def save_treated_data(self):
        figure_name= "Integrated_RIXS_spectra_comparison_waterfall"
        figure_name+="_" + self.parameters["output_file_element"]
        figure_name+="_" + self.parameters["output_file_edge"]
        figure_name+="_" + self.parameters["output_file_sample_name"]
        #if self.parameters["plot_display_sample_name_title"]:
        #    figure_name+="_" + self.parameters["plot_title"]
        figure_name+="_" + self.parameters["input_number_of_complete_file_names"] + "_files"
        figure_name+="_energy_ranges"
        for spectra_index in range(int(self.parameters["number_of_pfy_regions"])):
            figure_name+="_" + str(round(float(self.parameters["pfy_incoming_energy_start_array"][spectra_index])))
            figure_name+="_" + str(round(float(self.parameters["pfy_incoming_energy_end_array"][spectra_index])))
        if self.parameters["is_energy_window_used_array"][0]:
            figure_name+="_plotted_to_" + self.parameters["plot_energy_loss_min_array"][0]
        if True in self.parameters["is_gaussian_smooth_data_array"][0:int(self.parameters["input_number_of_complete_file_names"]) * int(self.parameters["number_of_pfy_regions"])] or self.parameters["is_gaussian_smooth_data_for_all_spectra"] or self.parameters["is_binning_smooth_data_for_all_spectra"] or self.parameters["is_binning_smooth_data_array"][0:int(self.parameters["input_number_of_complete_file_names"]) * int(self.parameters["number_of_pfy_regions"])]:
            figure_name+="_" + "smoothed"
        if True in self.parameters["plot_is_scale_intensity_of_spectra_array"][0:int(self.parameters["input_number_of_complete_file_names"]) * int(self.parameters["number_of_pfy_regions"])]:
            figure_name+="_" + "scaled"
        if self.parameters["output_file_additional_comment"] != "":
            figure_name+="_" + self.parameters["output_file_additional_comment"]
        figure_parameters_name= figure_name
        figure_data_name= figure_name
        figure_name+="_figure.png"
        figure_parameters_name+="_parameters.txt"
        figure_data_name+= "_data.txt"
        figure_path= os.path.join(self.parameters["input_file_project_folder"], 'Simple RIXS Figures')
        if not os.path.exists(figure_path):
            os.makedirs(figure_path)
        
        #figure_name= "test.svg"
        
        full_figure_path= os.path.join(figure_path, figure_name)
        #plt.rcParams['figure.dpi'] = 300
        self.figure_to_save.savefig(full_figure_path, dpi=600) #, dpi=600
        
        #extent = self.axs[pfy_region].get_window_extent().transformed(self.figure_to_save.dpi_scale_trans.inverted())
        #fig.savefig('ax2_figure.png', bbox_inches=extent)

        # Pad the saved area by 10% in the x-direction and 20% in the y-direction
        #self.figure_to_save.savefig(full_figure_path, bbox_inches=extent.expanded(1.1, 1.2))

        full_parameters_path=os.path.join(figure_path, figure_parameters_name)
        formatted_parameters = json.dumps(self.parameters, indent=0)
        with open(full_parameters_path, "w") as parameters_file:
            parameters_file.write(formatted_parameters)

        full_data_path=os.path.join(figure_path, figure_data_name) 
        data_dictionary= {}
        array_index = 0
        for file_name_index in range(int(self.parameters["input_number_of_complete_file_names"])):
            for energy_index in range(int(self.parameters["number_of_pfy_regions"])):
                data_dictionary[self.parameters["x_axis_title"] + '_' + self.parameters["plot_legend_names_array"][file_name_index] + '_' + self.parameters["pfy_incoming_energy_start_array"][energy_index]+ '_' + self.parameters["pfy_incoming_energy_end_array"][energy_index]]= self.array_of_x_values_arrays[array_index]
                data_dictionary[self.parameters["y_axis_title"] + "_" + self.parameters["plot_legend_names_array"][file_name_index] + "_" + self.parameters["pfy_incoming_energy_start_array"][energy_index]+ '_' + self.parameters["pfy_incoming_energy_end_array"][energy_index]]= self.array_of_intensity_arrays[array_index]
                array_index+= 1
        data_dataframe = pd.DataFrame.from_dict(data_dictionary, orient='index').transpose().fillna('')
        data_dataframe.to_csv(full_data_path, sep= '\t', index=False)

    def open_folder(self, project_folder, raw_data_folder):
        folder_path = os.path.join(project_folder, raw_data_folder)
        if platform.system() == "Darwin":
            subprocess.call(["open", folder_path])
        else:
            subprocess.call(["explorer", folder_path])
    
    def open_txt_file(self, folder_path):
        if platform.system() == "Windows":
            subprocess.Popen(["notepad.exe", folder_path], close_fds=True)
        elif platform.system() == "Darwin":
            subprocess.Popen(["open", "-a", "TextEdit", folder_path], close_fds=True)        

    def get_iteratable_file_number_array(self, parameters):
        iteratable_file_number_array= []

        ignored_numbers_array= []
        for string_number in parameters["input_file_ignore_file_number"]:
            if string_number != "":
                ignored_numbers_array.append(iteratable_number_to_int_script.iteratable_number_to_int(string_number))

        first_iteratable_int= iteratable_number_to_int_script.iteratable_number_to_int(parameters["input_file_iteratable_file_number_start"])
        last_iteratable_int= iteratable_number_to_int_script.iteratable_number_to_int(parameters["input_file_iteratable_file_number_end"])
        
        for iteratable_int in range(first_iteratable_int, last_iteratable_int +1):
            if iteratable_int not in ignored_numbers_array:
                iteratable_string= str(iteratable_int)
                while len(parameters["input_file_iteratable_file_number_start"]) > len(iteratable_string):
                    iteratable_string = "0" + iteratable_string
                iteratable_file_number_array.append(iteratable_string)
        
        return iteratable_file_number_array

    def get_incoming_energy_array(self, parameters):
        
        if parameters["input_file_format"] =="h5":
            y_values = get_single_spectrum_h5_or_txt_file_scripts.get_single_spectrum_h5_file(parameters, parameters["h5_root_location_data"], False, "")
        elif parameters["input_file_format"] =="txt":
            y_values = get_single_spectrum_h5_or_txt_file_scripts.get_single_spectrum_txt_file(parameters, False, parameters["txt_intensity_data_row"], parameters["txt_intensity_data_column"], False, "", parameters["is_several_spectra_per_file"])

        if parameters["is_incoming_energy_avialable_in_seperate_file"]:
            #A lot of code here since the "Get singel spectrum script" is aimed at getting data from the datafile.
            if parameters["input_file_format"]== "h5":
                complete_file_location = os.path.join(parameters["complete_incoming_energy_file_location"], parameters["complete_incoming_energy_file_name"])
                if complete_file_location[-4:] == ".txt":
                    complete_file_location=complete_file_location[:-4]
                if complete_file_location[-3:] != ".h5":
                    complete_file_location = complete_file_location + ".h5"
                raw_data_list=[]
                with h5py.File(complete_file_location,'r') as file:
                    raw_data_list.append(file[parameters["h5_root_location_incoming_energy"]][:])
                incoming_energy_array= raw_data_list[0][:]
                
            elif parameters["input_file_format"]== "txt":
                complete_file_location = os.path.join(parameters["complete_incoming_energy_file_location"], parameters["complete_incoming_energy_file_name"])
                if complete_file_location[-3:] == ".h5":
                    complete_file_location=complete_file_location[:-3]
                if complete_file_location[-4:] != ".txt":
                    complete_file_location = complete_file_location + ".txt"

                data_row = int(parameters["txt_incoming_energy_row_in_file"])
                data_column= int(parameters["txt_incoming_energy_column_in_file"])
                if parameters["txt_delimiter"] == "Tab":
                    dataframe = pd.read_csv(complete_file_location, sep='\t', skiprows=data_row, usecols=[data_column], header=None)
                elif parameters["txt_delimiter"] == " ":
                    dataframe = pd.read_csv(complete_file_location, sep=' ', skiprows=data_row, usecols=[data_column], header=None)
                else:
                    dataframe = pd.read_csv(complete_file_location, sep=parameters["txt_delimiter"], skiprows=data_row, usecols=[data_column], header=None)
            # Access the values of the column
                incoming_energy_array = dataframe.iloc[:, 0].values

            if isinstance(incoming_energy_array[0], np.ndarray) or isinstance(incoming_energy_array[0], list):
                if len(incoming_energy_array[0]) >1: 
                    for iteratable_number in range(len(incoming_energy_array)):
                        incoming_energy_array[iteratable_number]= np.mean(incoming_energy_array[iteratable_number])
                else:
                    for iteratable_number in range(len(incoming_energy_array)):
                        incoming_energy_array[iteratable_number]= incoming_energy_array[iteratable_number][0]

        elif parameters["is_incoming_energy_available_in_file"]:
            if parameters["input_file_format"]== "h5":
                incoming_energy = get_single_spectrum_h5_or_txt_file_scripts.get_single_spectrum_h5_file(parameters, parameters["h5_root_location_incoming_energy"], False, "")
            elif parameters["input_file_format"]== "txt":
                incoming_energy = get_single_spectrum_h5_or_txt_file_scripts.get_single_spectrum_txt_file(parameters, parameters["is_txt_single_incoming_energy_value"], parameters["txt_incoming_energy_row_in_file"], parameters["txt_incoming_energy_column_in_file"], False, "", False)

        elif parameters["is_equal_incoming_energy_difference"]:
            incoming_energy= np.linspace( int(parameters["energy_of_first_line_spectra"]), int(parameters["energy_of_last_line_spectra"]), len(y_values))
        
        elif parameters["is_segments_of_equal_incoming_energy_difference"]:
            current_energy= 0
            incoming_energy=[]
            for segment in range(int(parameters["input_number_of_incoming_energy_segments"])):
                array_index_in_segment= 0
                if segment != len(int(parameters["input_number_of_incoming_energy_segments"])):
                    while current_energy < int(parameters["first_incoming_energy_of_segment_array"][segment + 1]):
                        current_energy=int(parameters["first_incoming_energy_of_segment_array"][segment])+ array_index_in_segment*int(parameters["incoming_energy_difference_in_segment_array"][segment])
                        incoming_energy.append(current_energy)
                        array_index_in_segment+=1
                else:
                    while current_energy <= int(parameters["incoming_energy_of_last_spectra"]):
                        current_energy= int(parameters["first_incoming_energy_of_segment_array"][segment])+ array_index_in_segment*int(parameters["incoming_energy_difference_in_segment_array"][segment])
                        incoming_energy.append(current_energy)
                        array_index_in_segment+=1

        elif parameters["is_input_every_incoming_energy"]:
            for data_point in range(len(y_values)):
                incoming_energy.append(int(parameters["incoming_energy_of_spectra_array"][data_point]))
            
        return np.asarray(incoming_energy)

    def gaussian(self, x, A, mu, sigma):
        return A * np.exp(-(x - mu)**2 / (2 * sigma**2))
    
    def get_intensity_array(self, parameters, incoming_energy_array):

        #iteratable_int= iteratable_number_to_int_script.iteratable_number_to_int(iteratable_number)
        if parameters["input_file_format"] =="h5":
            y_values = get_single_spectrum_h5_or_txt_file_scripts.get_single_spectrum_h5_file(parameters, parameters["h5_root_location_data"], True, iteratable_number)
            y_values_raw= y_values
            if parameters["is_i0_avialable_in_seperate_file"]:
                #A lot of code here since the "Get singel spectrum script" is aimed at getting data from the datafile.
                complete_file_location = os.path.join(parameters["complete_i0_file_location"], parameters["complete_i0_file_name"])
                if complete_file_location[-4:] == ".txt":
                    complete_file_location=complete_file_location[:-4]
                if complete_file_location[-3:] != ".h5":
                    complete_file_location = complete_file_location + ".h5"
                raw_data_list=[]
                with h5py.File(complete_file_location,'r') as file:
                    raw_data_list.append(file[parameters["i0_root_location_data"]][:])
                i0_values= raw_data_list[0][:]
                i0_mean= np.mean(i0_values)
                y_values= y_values/i0_mean
                
            elif parameters["is_i0_available_in_file"]:
                i0_values = get_single_spectrum_h5_or_txt_file_scripts.get_single_spectrum_h5_file(parameters, parameters["i0_root_location_data"], True, iteratable_number)
                i0_mean= np.mean(i0_values)
                y_values= y_values/i0_mean
            
        elif parameters["input_file_format"] =="txt":
            y_values = get_single_spectrum_h5_or_txt_file_scripts.get_single_spectrum_txt_file(parameters, False, parameters["txt_intensity_data_row"], parameters["txt_intensity_data_column"], True, iteratable_number, parameters["is_several_spectra_per_file"])
            y_values_raw= y_values

            if parameters["is_i0_avialable_in_seperate_file"]:
                complete_file_location = os.path.join(parameters["complete_i0_file_location"], parameters["complete_i0_file_name"])
                if complete_file_location[-3:] == ".h5":
                    complete_file_location=complete_file_location[:-3]
                if complete_file_location[-4:] != ".txt":
                    complete_file_location = complete_file_location + ".txt"

                data_row = int(parameters["txt_i0_row_in_file"])
                data_column= int(parameters["txt_i0_column_in_file"])
                if parameters["txt_delimiter"] == "Tab":
                    dataframe = pd.read_csv(complete_file_location, sep='\t', skiprows=data_row, usecols=[data_column], header=None)
                elif parameters["txt_delimiter"] == " ":
                    dataframe = pd.read_csv(complete_file_location, sep=' ', skiprows=data_row, usecols=[data_column], header=None)
                else:
                    dataframe = pd.read_csv(complete_file_location, sep=parameters["txt_delimiter"], skiprows=data_row, usecols=[data_column], header=None)
            # Access the values of the column
                i0_values = dataframe.iloc[:, 0].values

            if isinstance(i0_values[0], np.ndarray) or isinstance(i0_values[0], list):
                if len(i0_values[0]) >1: 
                    for iteratable_number in range(len(incoming_energy_array)):
                        i0_values[iteratable_number]= np.mean(i0_values[iteratable_number])
                else:
                    for iteratable_number in range(len(incoming_energy_array)):
                        i0_values[iteratable_number]= i0_values[iteratable_number][0]

                i0_mean= np.mean(i0_values)
                y_values= y_values/i0_mean
            elif parameters["is_i0_available_in_file"]:
                i0_values = get_single_spectrum_h5_or_txt_file_scripts.get_single_spectrum_txt_file(parameters, parameters["is_txt_single_i0_value"], parameters["txt_i0_row_in_file"], parameters["txt_i0_column_in_file"], False, "", False)
                i0_mean= np.mean(i0_values)
                y_values= y_values_raw/i0_mean

        if parameters["is_subtract_fitted_background"]:
            index_start= np.abs(incoming_energy_array - float(parameters["background_fit_energy_start"])).argmin()
            index_end= np.abs(incoming_energy_array - float(parameters["background_fit_energy_end"])).argmin()
            x_values_fit= incoming_energy_array[index_start:index_end]
            y_values_fit= y_values[index_start:index_end]
            if parameters["background_fit_type"] == "Linear":
                coeffs = np.polyfit(x_values_fit, y_values_fit, deg=1)
                y_trend_values = np.polyval(coeffs, incoming_energy_array)
            elif parameters["background_fit_type"] == "ln(x)":
                x_values_fit = np.log(x_values_fit)
                coeffs = np.polyfit(x_values_fit, y_values_fit, deg=1)
                y_trend_values = np.polyval(coeffs, np.log(incoming_energy_array))
            elif parameters["background_fit_type"] == "log(x)":
                x_values_fit = np.log10(x_values_fit)
                coeffs = np.polyfit(x_values_fit, y_values_fit, deg=1)
                y_trend_values = np.polyval(coeffs, np.log10(incoming_energy_array))
            elif parameters["background_fit_type"] == "x^(-2)":
                x_values_fit = 1 / x_values_fit
                coeffs = np.polyfit(x_values_fit, y_values_fit, deg=1)
                inverse_incoming_energy_array = 1 / incoming_energy_array
                y_trend_values = np.polyval(coeffs, inverse_incoming_energy_array)
            elif parameters["background_fit_type"] == "Gaussian":
                gaussian_parameters, covariance = curve_fit(self.gaussian, x_values_fit, y_values_fit)
                y_trend_values= self.gaussian(incoming_energy_array, *gaussian_parameters)
            y_values = y_values - y_trend_values

        if parameters["is_approximate_energy_for_normalization_to_zero"]:
            index_start = np.abs(incoming_energy_array - (float(parameters["approximate_energy_for_normalization_to_zero"]) - float(parameters["energy_above_and_below_finding_min_intensity"]))).argmin()
            index_end = np.abs(incoming_energy_array - (float(parameters["approximate_energy_for_normalization_to_zero"]) + float(parameters["energy_above_and_below_finding_min_intensity"]))).argmin()

            if index_start == index_end:
                y_min= y_values[index_start]
            else:
                y_min = np.min(y_values[index_start: index_end])
        else:
            y_min= np.min(y_values)
        array_index_y_min = np.abs(y_values - y_min).argmin()
        #index_start = array_index_y_min - np.abs(incoming_energy_array - (incoming_energy_array[array_index_y_min] - float(parameters["energy_above_and_below_normalization_to_zero"]))).argmin()
        #index_end = array_index_y_min + np.abs(incoming_energy_array - (incoming_energy_array[array_index_y_min] + float(parameters["energy_above_and_below_normalization_to_zero"]))).argmin()
        index_start = np.abs(incoming_energy_array - (incoming_energy_array[array_index_y_min] - float(parameters["energy_above_and_below_normalization_to_zero"]))).argmin()
        index_end = np.abs(incoming_energy_array - (incoming_energy_array[array_index_y_min] + float(parameters["energy_above_and_below_normalization_to_zero"]))).argmin()

        if index_start == index_end:
            y_zero_intensity= y_values[index_start]
        else:
            y_zero_intensity= np.mean(y_values[index_start:index_end])
        
        index_start =np.abs(incoming_energy_array - (incoming_energy_array[-1] - float(parameters["incoming_energy_range_normalization_to_one"]))).argmin()
        if index_start == y_values[-1]:
            y_one_intensity = y_values[-1]
        else:
            y_one_intensity = np.mean(y_values[index_start:])

        intensity_normalized = (y_values - y_zero_intensity) / (y_one_intensity - y_zero_intensity)

        return intensity_normalized, y_values_raw

    def get_arrays_of_x_values_and_intenisty_arrays(self, parameters):
        #parameters, complete_file_location = create_complete_file_location_view_roots_or_txt_script.create_complete_file_location_view_roots_or_txt(parameters, False, "")
        data_row= 1
        #main_dataframe = pd.read_csv(complete_file_location, sep='\t', skiprows=data_row, header=None) 
        #x_values_array= main_dataframe.iloc[:, 0].values
        #incoming_energy_array= main_dataframe.iloc[:, 1].values  
        #print("you are here. The script has to be adjusted for the new file format with and x_array for each intensity. But do the intepolation first.")
        #print("if the x_axis is not linear you also have to do an interpolation of the intenisty points and make a common linear x_axis with lipe 10 times more points to make the interpolation good")

        array_of_x_values_arrays = []
        array_of_intensity_arrays = []
        for file_name_index in range(int(self.parameters["input_number_of_complete_file_names"])):
            complete_file_location= create_complete_file_location_for_treated_data.create_complete_file_location_for_treated_data(parameters["input_file_project_folder"], self.parameters["input_complete_file_name_array"][file_name_index])
            array_of_x_values_arrays_from_one_file, incoming_energy_array, array_of_intensity_arrays_from_one_file = get_treated_rixs_data_script.get_treated_rixs_data(complete_file_location)
            
            for region_index in range(int(parameters["number_of_pfy_regions"])):
                incoming_energy_index_of_first_spectra= np.nanargmin(np.abs(incoming_energy_array - float(parameters["pfy_incoming_energy_start_array"][region_index])))
                incoming_energy_index_of_last_spectra= np.nanargmin(np.abs(incoming_energy_array - float(parameters["pfy_incoming_energy_end_array"][region_index])))
                intensity_array= np.zeros(len(array_of_x_values_arrays_from_one_file[0]))
                for spectra_index in range(incoming_energy_index_of_first_spectra, incoming_energy_index_of_last_spectra + 1):
                    intensity_array += array_of_intensity_arrays_from_one_file[spectra_index]
                array_of_x_values_arrays.append(array_of_x_values_arrays_from_one_file[spectra_index])
                array_of_intensity_arrays.append(intensity_array)

        return array_of_intensity_arrays, array_of_x_values_arrays

    def treat_intensity_data(self, parameters, y_values_array, x_values_array):
        for file_name_index in range(int(parameters["input_number_of_complete_file_names"])):
            incoming_energy_array = x_values_array[file_name_index]
            y_values = y_values_array[file_name_index]

            if parameters["is_invert_the_plot_array"][file_name_index]== True:
                if parameters["is_approximate_energy_for_normalization_to_zero_array"][file_name_index]:
                    index_start = np.abs(incoming_energy_array - (float(parameters["approximate_energy_for_normalization_to_zero_array"][file_name_index]) - float(parameters["energy_above_and_below_finding_min_intensity_array"][file_name_index]))).argmin()
                    index_end = np.abs(incoming_energy_array - (float(parameters["approximate_energy_for_normalization_to_zero_array"][file_name_index]) + float(parameters["energy_above_and_below_finding_min_intensity_array"][file_name_index]))).argmin()
                    if index_start == index_end:
                        y_min= y_values[index_start]
                    else:
                        #using np.max to get y_min to get the plot inverted.
                        y_min = np.max(y_values[index_start: index_end])
                else:
                    y_min= np.max(y_values)
                array_index_y_min = np.abs(y_values - y_min).argmin()
                #index_start = array_index_y_min - np.abs(incoming_energy_array - (incoming_energy_array[array_index_y_min] - float(parameters["energy_above_and_below_normalization_to_zero"]))).argmin()
                #index_end = array_index_y_min + np.abs(incoming_energy_array - (incoming_energy_array[array_index_y_min] + float(parameters["energy_above_and_below_normalization_to_zero"]))).argmin()
                
                index_start = np.abs(incoming_energy_array - (incoming_energy_array[array_index_y_min] - float(parameters["energy_above_and_below_normalization_to_zero_array"][file_name_index]))).argmin()
                index_end = np.abs(incoming_energy_array - (incoming_energy_array[array_index_y_min] + float(parameters["energy_above_and_below_normalization_to_zero_array"][file_name_index]))).argmin()
                
                if index_start == index_end:
                    y_zero_intensity= y_values[index_start]
                else:
                    y_zero_intensity= np.mean(y_values[index_start:index_end])
                
                index_start =np.abs(incoming_energy_array - (incoming_energy_array[-1] - float(parameters["incoming_energy_range_normalization_to_one_array"][file_name_index]))).argmin()
                if index_start == y_values[-1]:
                    y_one_intensity = y_values[-1]
                else:
                    y_one_intensity = np.mean(y_values[index_start:])

                y_values = (y_values - y_zero_intensity) / (y_one_intensity - y_zero_intensity)
                
                if parameters["is_subtract_fitted_background_array"][file_name_index]:
                    index_start= np.abs(incoming_energy_array - float(parameters["background_fit_energy_start_array"][file_name_index])).argmin()
                    index_end= np.abs(incoming_energy_array - float(parameters["background_fit_energy_end_array"][file_name_index])).argmin()
                    x_values_fit= incoming_energy_array[index_start:index_end]
                    y_values_fit= y_values[index_start:index_end]
                    if parameters["background_fit_type_array"][file_name_index] == "Linear":
                        coeffs = np.polyfit(x_values_fit, y_values_fit, deg=1)
                        y_trend_values = np.polyval(coeffs, incoming_energy_array)
                    elif parameters["background_fit_type_array"][file_name_index] == "ln(x)":
                        x_values_fit = np.log(x_values_fit)
                        coeffs = np.polyfit(x_values_fit, y_values_fit, deg=1)
                        y_trend_values = np.polyval(coeffs, np.log(incoming_energy_array))
                    elif parameters["background_fit_type_array"][file_name_index] == "log(x)":
                        x_values_fit = np.log10(x_values_fit)
                        coeffs = np.polyfit(x_values_fit, y_values_fit, deg=1)
                        y_trend_values = np.polyval(coeffs, np.log10(incoming_energy_array))
                    elif parameters["background_fit_type_array"][file_name_index] == "x^(-2)":
                        x_values_fit = 1 / x_values_fit
                        coeffs = np.polyfit(x_values_fit, y_values_fit, deg=1)
                        inverse_incoming_energy_array = 1 / incoming_energy_array
                        y_trend_values = np.polyval(coeffs, inverse_incoming_energy_array)
                    elif parameters["background_fit_type_array"][file_name_index] == "Gaussian":
                        gaussian_parameters, covariance = curve_fit(self.gaussian, x_values_fit, y_values_fit)
                        y_trend_values= self.gaussian(incoming_energy_array, *gaussian_parameters)
                    y_values = y_values - y_trend_values

            else:
                if parameters["is_subtract_fitted_background_array"][file_name_index]:
                    index_start= np.abs(incoming_energy_array - float(parameters["background_fit_energy_start_array"][file_name_index])).argmin()
                    index_end= np.abs(incoming_energy_array - float(parameters["background_fit_energy_end_array"][file_name_index])).argmin()
                    x_values_fit= incoming_energy_array[index_start:index_end]
                    y_values_fit= y_values[index_start:index_end]
                    if parameters["background_fit_type_array"][file_name_index] == "Linear":
                        coeffs = np.polyfit(x_values_fit, y_values_fit, deg=1)
                        y_trend_values = np.polyval(coeffs, incoming_energy_array)
                    elif parameters["background_fit_type_array"][file_name_index] == "ln(x)":
                        x_values_fit = np.log(x_values_fit)
                        coeffs = np.polyfit(x_values_fit, y_values_fit, deg=1)
                        y_trend_values = np.polyval(coeffs, np.log(incoming_energy_array))
                    elif parameters["background_fit_type_array"][file_name_index] == "log(x)":
                        x_values_fit = np.log10(x_values_fit)
                        coeffs = np.polyfit(x_values_fit, y_values_fit, deg=1)
                        y_trend_values = np.polyval(coeffs, np.log10(incoming_energy_array))
                    elif parameters["background_fit_type_array"][file_name_index] == "x^(-2)":
                        x_values_fit = 1 / x_values_fit
                        coeffs = np.polyfit(x_values_fit, y_values_fit, deg=1)
                        inverse_incoming_energy_array = 1 / incoming_energy_array
                        y_trend_values = np.polyval(coeffs, inverse_incoming_energy_array)
                    elif parameters["background_fit_type_array"][file_name_index] == "Gaussian":
                        gaussian_parameters, covariance = curve_fit(self.gaussian, x_values_fit, y_values_fit)
                        y_trend_values= self.gaussian(incoming_energy_array, *gaussian_parameters)
                    y_values = y_values - y_trend_values

                if parameters["is_normalize_to_zero_and_one_array"][file_name_index]:
                    if parameters["is_approximate_energy_for_normalization_to_zero_array"][file_name_index]:
                        index_start = np.abs(incoming_energy_array - (float(parameters["approximate_energy_for_normalization_to_zero_array"][file_name_index]) - float(parameters["energy_above_and_below_finding_min_intensity_array"][file_name_index]))).argmin()
                        index_end = np.abs(incoming_energy_array - (float(parameters["approximate_energy_for_normalization_to_zero_array"][file_name_index]) + float(parameters["energy_above_and_below_finding_min_intensity_array"][file_name_index]))).argmin()

                        if index_start == index_end:
                            y_min= y_values[index_start]
                        else:
                            y_min = np.min(y_values[index_start: index_end])
                    else:
                        y_min= np.min(y_values)
                    array_index_y_min = np.abs(y_values - y_min).argmin()
                    #index_start = array_index_y_min - np.abs(incoming_energy_array - (incoming_energy_array[array_index_y_min] - float(parameters["energy_above_and_below_normalization_to_zero"]))).argmin()
                    #index_end = array_index_y_min + np.abs(incoming_energy_array - (incoming_energy_array[array_index_y_min] + float(parameters["energy_above_and_below_normalization_to_zero"]))).argmin()
                    
                    index_start = np.abs(incoming_energy_array - (incoming_energy_array[array_index_y_min] - float(parameters["energy_above_and_below_normalization_to_zero_array"][file_name_index]))).argmin()
                    index_end = np.abs(incoming_energy_array - (incoming_energy_array[array_index_y_min] + float(parameters["energy_above_and_below_normalization_to_zero_array"][file_name_index]))).argmin()
                    
                    if index_start == index_end:
                        y_zero_intensity= y_values[index_start]
                    else:
                        y_zero_intensity= np.mean(y_values[index_start:index_end])
                    
                    index_start =np.abs(incoming_energy_array - (incoming_energy_array[-1] - float(parameters["incoming_energy_range_normalization_to_one_array"][file_name_index]))).argmin()
                    if index_start == y_values[-1]:
                        y_one_intensity = y_values[-1]
                    else:
                        y_one_intensity = np.mean(y_values[index_start:])
                        
                    y_values = (y_values - y_zero_intensity) / (y_one_intensity - y_zero_intensity)
            
            y_values_array[file_name_index] = y_values

        return y_values_array

        
    def get_plot_color_and_linestyle_array(self, parameters):
        linestyles_array= ["solid", "dashed", "dashdot", "dotted", (0, (5, 1)), (0, (10, 3)), (0, (3, 1, 1, 1), (0, (3, 1, 1, 1, 1)))]
        if parameters["plot_spectra_grouping_type"]== "No grouping":
            plot_color_array = list(cm.rainbow(np.linspace(0, 1, int(parameters["input_number_of_complete_file_names"]))))

            final_plot_color_array=[]
            final_linestyles_array=[]
            for file_name_index in range(int(self.parameters["input_number_of_complete_file_names"])):
                for incoming_energy_index in range(int(self.parameters["input_number_of_incoming_energies"])):
                    final_plot_color_array.append(plot_color_array[file_name_index])
                    final_linestyles_array.append(linestyles_array[incoming_energy_index])

        elif parameters["plot_spectra_grouping_type"]== "Group by excitation energy" or parameters["plot_spectra_grouping_type"]== "Group by PFY region" or parameters["plot_spectra_grouping_type"]== "Group by integration region":
            if int(parameters["plot_number_of_times_to_reset_color_palette"]) > 0:
                previous_color_index= 0
                color_reset_index_difference= 0
                color_reset_index_difference_array= []
                sorted_color_reset_index_array= sorted(parameters["plot_file_name_index_to_change_color_palette_array"][ : int(parameters["plot_number_of_times_to_reset_color_palette"])], key=int)
                for color_reset_index in sorted_color_reset_index_array:
                    color_reset_index_difference = int(color_reset_index) - previous_color_index
                    previous_color_index = int(color_reset_index)
                    color_reset_index_difference_array.append(color_reset_index_difference)
                color_reset_index_difference = int(parameters["input_number_of_complete_file_names"]) - int(color_reset_index) 
                color_reset_index_difference_array.append(color_reset_index_difference)
                maximum_color_range= max(color_reset_index_difference_array)
                plot_color_array = list(cm.rainbow(np.linspace(0, 1, maximum_color_range)))
            else:
                plot_color_array = list(cm.rainbow(np.linspace(0, 1, int(parameters["input_number_of_complete_file_names"]))))

            plot_color_index= 0
            linesstyles_index= 0
            final_plot_color_array=[]
            final_linestyles_array=[]
            for file_name_index in range(int(self.parameters["input_number_of_complete_file_names"])):
                for incoming_energy_index in range(int(self.parameters["number_of_pfy_regions"])):
                    if int(parameters["plot_number_of_times_to_reset_color_palette"]) > 0 and str(file_name_index) in parameters["plot_file_name_index_to_change_color_palette_array"][ : int(parameters["plot_number_of_times_to_reset_color_palette"])]:
                        plot_color_index = 0
                    if int(parameters["plot_number_of_times_to_change_line_style"]) > 0 and str(file_name_index) in parameters["plot_file_name_index_to_change_line_style_array"][ : int(parameters["plot_number_of_times_to_change_line_style"])]:
                        linesstyles_index+= 1
                    final_plot_color_array.append(plot_color_array[plot_color_index])
                    final_linestyles_array.append(linestyles_array[linesstyles_index])
                plot_color_index+=1

        elif parameters["plot_spectra_grouping_type"]== "Group by file":
            plot_color_array = list(cm.rainbow(np.linspace(0, 1, int(parameters["input_number_of_complete_file_names"]))))

            final_plot_color_array=[]
            final_linestyles_array=[]
            for file_name_index in range(int(self.parameters["input_number_of_complete_file_names"])):
                for incoming_energy_index in range(int(self.parameters["number_of_pfy_regions"])):
                    final_plot_color_array.append(plot_color_array[file_name_index])
                    final_linestyles_array.append(linestyles_array[incoming_energy_index])
        return final_plot_color_array, final_linestyles_array

    def move_elastic_peak_center_to_correct_energy(self, array_of_intensity_arrays, incoming_energy_array, array_of_x_value_arrays):
        #elastic_peak_center_array = np.asarray(elastic_peak_center_array)
        is_original_x_values_energy_loss = self.nested_array_contains_negative_floats(array_of_x_value_arrays)
        
        if is_original_x_values_energy_loss == False:
            for spectra_index in range(len(array_of_intensity_arrays)):
                array_of_x_value_arrays[spectra_index] = array_of_x_value_arrays[spectra_index] - incoming_energy_array[spectra_index]
        
        energy_above_and_below_elastic_peak_to_fit_elastic_peak = float(self.parameters["energy_above_and_below_to_calculate_elastic_peak_weights"])
        #elastic_energy_mismatch_tolerance = 0.0001
        for spectra_index in range(len(array_of_intensity_arrays)):
            previous_elastic_peak_channel_center = np.abs(array_of_x_value_arrays[spectra_index] - 0).argmin()
            original_elastic_peak_channel_center = np.abs(array_of_x_value_arrays[spectra_index] - 0).argmin()
            channels_above_and_below_elastic_to_fit = np.abs(previous_elastic_peak_channel_center - np.abs(array_of_x_value_arrays[spectra_index] - energy_above_and_below_elastic_peak_to_fit_elastic_peak).argmin() )
            #print(np.abs(array_of_x_value_arrays[spectra_index] - 0).argmin())

            condition = True
            while condition:
                peak_channel_center=0
                sum_of_intensity_weight= 0
                
                for channel in range(previous_elastic_peak_channel_center - channels_above_and_below_elastic_to_fit, previous_elastic_peak_channel_center + channels_above_and_below_elastic_to_fit +1):
                    #peak_channel_center+= array_of_intensity_arrays[spectra_index][channel] * channel
                    #sum_of_intensity_weight+= array_of_intensity_arrays[spectra_index][channel]
                    peak_channel_center+= ((array_of_intensity_arrays[spectra_index][channel]) ** 2 ) * channel
                    sum_of_intensity_weight+= (array_of_intensity_arrays[spectra_index][channel]) ** 2
                peak_channel_center = peak_channel_center/sum_of_intensity_weight
                #intensity_weights_array[array_index]=sum_of_intensity_weight
                change_in_peak_channel_center = previous_elastic_peak_channel_center - peak_channel_center
                
                previous_elastic_peak_channel_center = round(peak_channel_center)
                #if abs(array_of_x_value_arrays[spectra_index][previous_elastic_peak_channel_center]) <= elastic_energy_mismatch_tolerance:
                #    array_of_x_value_arrays[spectra_index] = array_of_x_value_arrays[spectra_index] - peak_center_in_energy
                if abs(change_in_peak_channel_center) <= 0.5:
                    if self.parameters["degree_of_energy_per_channel_polynomial"] == "0":
                        x_channel_array = np.arange(1, len(array_of_x_value_arrays[spectra_index]) + 1)
                        initial_guess_a = max(array_of_x_value_arrays[spectra_index]) - min(array_of_x_value_arrays[spectra_index])  # Estimate for parameter 'a' based on the range of y values
                        initial_guess_b = x_channel_array[np.argmin(array_of_x_value_arrays[spectra_index])]  # Estimate for parameter 'b' based on the x value corresponding to the minimum y value
                        initial_guess_c = min(array_of_x_value_arrays[spectra_index])
                        initial_guess = [initial_guess_a, initial_guess_b, initial_guess_c]  # Initial guess for the parameters a, b, and c
                        optimized_params, _ = curve_fit(self.one_over_x_function, np.arange(1, len(array_of_x_value_arrays[spectra_index]) + 1), array_of_x_value_arrays[spectra_index], p0=initial_guess)

                        # Extract the optimized parameters
                        optimized_a, optimized_b, optimized_c = optimized_params

                        energy_shift = self.one_over_x_function(peak_channel_center - 1, optimized_a, optimized_b, optimized_c)
                        #energy_shift = 0
                        
                        if spectra_index == 0:
                            if False and self.parameters["is_input_energy_per_channel_and_intercept_manually"] == False or self.parameters["is_x_values_available_in_file"] == False:
                                figure, ax1 = plt.subplots(2)
                                ax1.plot(x_channel_array, self.one_over_x_function(x_channel_array, optimized_a, optimized_b, optimized_c), label=f'Fitted Curve: y = {optimized_a}/(x + {optimized_b}) + {optimized_c}', color='red')
                                ax1.plot(np.arange(len(array_of_x_value_arrays[spectra_index])), array_of_x_value_arrays[spectra_index], color= 'blue', label= "Actual energy per channel of x axis")
                                ax1.title('Energy per channel of x axis for the first spectra and its y= a/(x+b) + c fit')
                                ax1.xlabel('Channel')
                                ax1.ylabel('Energy [eV]')
                                ax1.show()
                    else:
                        polynomial_coefficients = self.weighted_polynomial_fit_for_x_axis(np.arange(len(array_of_x_value_arrays[spectra_index])), array_of_x_value_arrays[spectra_index])
                        energy_shift = np.polyval(polynomial_coefficients, peak_channel_center)
                        if spectra_index == 0:
                            if False and self.parameters["is_input_energy_per_channel_and_intercept_manually"] == False or self.parameters["is_x_values_available_in_file"] == False:
                                y1 = np.polyval(polynomial_coefficients, np.arange(len(array_of_x_value_arrays[spectra_index])))
                                y2 = array_of_x_value_arrays[spectra_index]
                                y_2_1_difference = np.subtract(y2, y1)
                                figure, (ax1, ax2) = plt.subplots(2, 1)
                                ax1.plot(np.arange(len(array_of_x_value_arrays[spectra_index])), y1, color = 'red', label= "Fitted polynomial")
                                ax1.plot(np.arange(len(array_of_x_value_arrays[spectra_index])), y2, color= 'blue', label= "Actual energy per channel of x axis")
                                ax1.set_title('Energy per channel of x axis for the first spectra and its polynomial fit')
                                ax1.set_xlabel('Channel')
                                ax1.set_ylabel('Energy [eV]')
                                ax1.legend()
                                #ax2.twinax(ax1)
                                ax2.plot(y2, y_2_1_difference)
                                ax2.set_title('Difference between energy per channel of x axis for the first spectra\nand its polynomial fit')
                                ax2.set_xlabel('Energy [eV]')
                                ax2.set_ylabel('X axis minus polynomial fit [eV]')
                                figure.tight_layout()
                                figure.show()
                                #plt.close()
                    if False:
                        channel_fraction_mismatch = peak_channel_center - previous_elastic_peak_channel_center
                        if channel_fraction_mismatch < 0:
                            energy_difference_to_closest_datapoint =  abs(array_of_x_value_arrays[spectra_index][previous_elastic_peak_channel_center] - array_of_x_value_arrays[spectra_index][previous_elastic_peak_channel_center - 1])

                        #intensity_weights_array[array_index]=sum_of_intensity_weight
                        else:
                            energy_difference_to_closest_datapoint =  abs(array_of_x_value_arrays[spectra_index][previous_elastic_peak_channel_center] - array_of_x_value_arrays[spectra_index][previous_elastic_peak_channel_center + 1])
                        
                        

                        energy_shift =  array_of_x_value_arrays[spectra_index][previous_elastic_peak_channel_center] + energy_difference_to_closest_datapoint * channel_fraction_mismatch
                    
                    array_of_x_value_arrays[spectra_index] = array_of_x_value_arrays[spectra_index] - energy_shift
                    #array_of_x_value_arrays[spectra_index] = array_of_x_value_arrays[spectra_index] - array_of_x_value_arrays[spectra_index][previous_elastic_peak_channel_center]
                    condition = False
            
        if is_original_x_values_energy_loss == False:
            for spectra_index in range(len(array_of_intensity_arrays)):
                array_of_x_value_arrays[spectra_index] = array_of_x_value_arrays[spectra_index] + incoming_energy_array[spectra_index]
        

        #for spectra_index in range(len(array_of_intensity_arrays)):
        #    array_of_x_value_arrays[spectra_index] = array_of_x_value_arrays[spectra_index] + (incoming_energy_array[spectra_index] - array_of_x_value_arrays[spectra_index][elastic_peak_center_array[spectra_index]])
        
        return array_of_x_value_arrays
    
    def nested_array_contains_negative_floats(self, nested_array):
        for array in nested_array:
            if np.any(array < 0):
                return True
        return False
    
    def weighted_polynomial_fit_for_x_axis(self, x, y):
        coefficients = np.polyfit(x, y, int(self.parameters["degree_of_energy_per_channel_polynomial"]), w= 1 / (1 + np.abs(y)))
        return coefficients

    def add_intensities(self, parameters):
        #array_of_x_value_arrays, incoming_energy_array, array_of_intensity_arrays
        #array_of_x_values_arrays = []
        #array_of_intensity_arrays = []
        #nested_array_of_x_value_arrays = []
        #nested_array_of_intensity_arrays = []
        array_of_combined_intensity_arrays = []
        final_array_of_x_values_arrays = []
        for file_name_index in range(int(parameters["input_number_of_complete_file_names"])):
            complete_file_location= create_complete_file_location_for_treated_data.create_complete_file_location_for_treated_data(parameters["input_file_project_folder"], self.parameters["input_complete_file_name_array"][file_name_index])
            array_of_x_values_arrays_from_one_file, incoming_energy_array, array_of_intensity_arrays_from_one_file = get_treated_rixs_data_script.get_treated_rixs_data(complete_file_location)
            
            if parameters["plot_outgoing_energy_instead_of_energy_loss"]:
                if self.nested_array_contains_negative_floats(array_of_x_values_arrays_from_one_file):
                    for spectra_index in range(len(array_of_x_values_arrays_from_one_file)):
                        array_of_x_values_arrays_from_one_file[spectra_index]= array_of_x_values_arrays_from_one_file[spectra_index] + incoming_energy_array[spectra_index]
                #ax.set_xlabel("Emission energy [eV]", fontsize= parameters["plot_x_axis_text_size"])
            else:
                if self.nested_array_contains_negative_floats(array_of_x_values_arrays_from_one_file) == False:
                    for spectra_index in range(len(array_of_x_values_arrays_from_one_file)):
                        array_of_x_values_arrays_from_one_file[spectra_index]= array_of_x_values_arrays_from_one_file[spectra_index] - incoming_energy_array[spectra_index]
                #ax.set_xlabel("Energy loss [eV]", fontsize= parameters["plot_x_axis_text_size"])


            if self.parameters["is_automatically_adjust_peak_to_correct_energy"]:
                array_of_x_values_arrays_from_one_file = self.move_elastic_peak_center_to_correct_energy(array_of_intensity_arrays_from_one_file, incoming_energy_array, array_of_x_values_arrays_from_one_file)
        
            if parameters["plot_outgoing_energy_instead_of_energy_loss"] == False:
                is_original_x_values_energy_loss = self.nested_array_contains_negative_floats(array_of_x_values_arrays_from_one_file)
                if is_original_x_values_energy_loss == False:
                    for spectra_index in range(len(array_of_x_values_arrays_from_one_file)):
                        array_of_x_values_arrays_from_one_file[spectra_index] = array_of_x_values_arrays_from_one_file[spectra_index] - incoming_energy_array[spectra_index]
            else:
                is_original_x_values_energy_loss = self.nested_array_contains_negative_floats(array_of_x_values_arrays_from_one_file)
                if is_original_x_values_energy_loss:
                    for spectra_index in range(len(array_of_x_values_arrays_from_one_file)):
                        array_of_x_values_arrays_from_one_file[spectra_index] = array_of_x_values_arrays_from_one_file[spectra_index] + incoming_energy_array[spectra_index]

            
            for region_index in range(int(parameters["number_of_pfy_regions"])):
                incoming_energy_index_of_first_spectra= np.nanargmin(np.abs(incoming_energy_array - float(parameters["pfy_incoming_energy_start_array"][region_index])))
                incoming_energy_index_of_last_spectra= np.nanargmin(np.abs(incoming_energy_array - float(parameters["pfy_incoming_energy_end_array"][region_index])))
                incoming_energy_index_array = np.arange(incoming_energy_index_of_first_spectra, incoming_energy_index_of_last_spectra + 1)

                array_of_x_value_arrays_to_combine = []
                for spectra_index in incoming_energy_index_array:
                    array_of_x_value_arrays_to_combine.append(array_of_x_values_arrays_from_one_file[spectra_index])

                combined_x_values_array = np.asarray(list(heapq.merge(*array_of_x_value_arrays_to_combine)))
                combined_intensity_array = np.zeros(len(combined_x_values_array), dtype=float)
                for spectra_index in incoming_energy_index_array:
                    interpolating_function = interp1d(array_of_x_values_arrays_from_one_file[spectra_index], array_of_intensity_arrays_from_one_file[spectra_index], kind='linear', fill_value="extrapolate")
                    combined_intensity_array += interpolating_function(combined_x_values_array)
                final_array_of_x_values_arrays.append(combined_x_values_array)
                array_of_combined_intensity_arrays.append(combined_intensity_array)

        #final_array_of_x_values_arrays = np.asarray(final_array_of_x_values_arrays, dtype=float)
        #unique_excitation_energies_list = np.asarray(unique_excitation_energies_list, dtype=float)
        #array_of_combined_intensity_arrays = np.asarray(array_of_combined_intensity_arrays, dtype=float)
        
            #nested_array_of_x_value_arrays.append(final_array_of_x_values_arrays)
            #nested_array_of_intensity_arrays.append(array_of_combined_intensity_arrays)
        
        
        #nested_array_of_x_value_arrays = np.asarray(nested_array_of_x_value_arrays, dtype=float)
        #nested_array_of_intensity_arrays = np.asarray(nested_array_of_intensity_arrays, dtype=float)
        
        return final_array_of_x_values_arrays, array_of_combined_intensity_arrays


    def plot_inputted_data(self, parameters, extra_plot_parameters):
        plt.close()

        #complete_treated_file_location= create_complete_file_location_for_treated_data.create_complete_file_location_for_treated_data(self.parameters["input_file_project_folder"], self.parameters["input_complete_file_name_array"][array_index])
        
        #array_of_intensity_arrays, array_of_x_values_arrays = self.get_arrays_of_x_values_and_intenisty_arrays(parameters)

        self.array_of_x_values_arrays, self.array_of_intensity_arrays = self.add_intensities(parameters)

        #self.array_of_y_values_arrays = self.treat_intensity_data(parameters, self.array_of_y_values_arrays, self.array_of_x_values_arrays)

        self.figure_to_save, ax = plt.subplots(1)
        self.figure_to_save.set_frameon(False)
        #plot_color_array = list(cm.rainbow(np.linspace(0, 1, ceil(int(parameters["input_number_of_complete_file_names"])/2))))
        
        #plot_color_array, linestyles_array = self.get_plot_color_and_linestyle_array(parameters)
        #temporary lines below
        plot_color_array = ['blue', 'red', 'blue', 'red','blue', 'red','blue', 'red', 'blue']
        linestyles_array = ['-', '-', '-', '-', '-', '-', '-', '-', '-']

        #Saves the arrays as the _to_plot so we can scale and bin the intensities without having the scaling in the outputted datafile.
        array_of_intensity_arrays_to_plot = self.array_of_intensity_arrays
        array_of_x_values_arrays_to_plot = self.array_of_x_values_arrays
        if parameters["plot_spectra_grouping_type"]== "No grouping":
            legend_array = []
            for file_name_index in range(int(self.parameters["input_number_of_complete_file_names"])):
                #The line below does not work if there are more than one PFY region per file
                array_of_intensity_arrays_to_plot[file_name_index]= np.asarray(array_of_intensity_arrays_to_plot[file_name_index]) + float(parameters["plot_intensity_offset_array"][file_name_index]) 

                if int(self.parameters["number_of_pfy_regions"]) == 1:
                    legend_array.append(parameters["plot_legend_names_array"][file_name_index])
                    
                    if parameters["plot_display_incoming_energy_by_lines"]:
                        formatted_incoming_energy_start = "{:.{}g}".format(float(parameters["pfy_incoming_energy_start_array"][0]) , int(parameters["plot_incoming_energy_significant_numbers"]))
                        formatted_incoming_energy_end = "{:.{}g}".format(float(parameters["pfy_incoming_energy_end_array"][0]) , int(parameters["plot_incoming_energy_significant_numbers"]))
                        #text = f'y={exact_energy_per_channel_slope:.8f}x+{exact_energy_per_channel_intercept:.2f}\nR={exact_energy_per_channel_r_value:.8f} \nStandard error={exact_energy_per_channel_std_err:.8f}'
                        ax.text(float(parameters["plot_incoming_energy_x_offset"]), float(parameters["plot_incoming_energy_y_offset"]) + float(parameters["plot_y_distance_between_plots"]) * file_name_index, formatted_incoming_energy_start + "-" + formatted_incoming_energy_end + " eV", fontsize= float(parameters["plot_incoming_energy_text_size"]))
                        
                else:
                    for incoming_energy_index in range(int(self.parameters["number_of_pfy_regions"])):
                        legend_array.append(parameters["plot_legend_names_array"][file_name_index] + " " + parameters["pfy_incoming_energy_start_array"][incoming_energy_index] + "-" + parameters["pfy_incoming_energy_end_array"][incoming_energy_index] + " eV")
            for array_index in range(int(parameters["input_number_of_complete_file_names"])*int(parameters["number_of_pfy_regions"])):
               ax.plot(array_of_x_values_arrays_to_plot[array_index], array_of_intensity_arrays_to_plot[array_index] + float(parameters["plot_y_distance_between_plots"])*array_index,  color=plot_color_array[array_index], linestyle= linestyles_array[array_index]) 
        
        elif parameters["plot_spectra_grouping_type"]== "Group by excitation energy" or parameters["plot_spectra_grouping_type"]== "Group by PFY region" or parameters["plot_spectra_grouping_type"]== "Group by integration region":
            array_index = 0
            legend_array = []
            for file_name_index in range(int(self.parameters["input_number_of_complete_file_names"])):
                for incoming_energy_index in range(int(self.parameters["number_of_pfy_regions"])):
                    if parameters["is_hide_certain_spectra_array"][array_index] == False:
                        if parameters["is_normalize_intensity_at_certain_emission_energy"]:
                            emission_energy_normalization_start= np.nanargmin(np.abs(array_of_x_values_arrays_to_plot[array_index] - float(parameters["emission_energy_for_intenisty_normalization"]) + float(parameters["emission_energy_above_and_below_for_normalization"])))
                            emission_energy_normalization_end= np.nanargmin(np.abs(array_of_x_values_arrays_to_plot[array_index] - float(parameters["emission_energy_for_intenisty_normalization"]) - float(parameters["emission_energy_above_and_below_for_normalization"])))
                        
                            average_intensity_of_range = np.average(array_of_intensity_arrays_to_plot[array_index][emission_energy_normalization_start : emission_energy_normalization_end])
                            if average_intensity_of_range != 0:
                                array_of_intensity_arrays_to_plot[array_index]= array_of_intensity_arrays_to_plot[array_index] / average_intensity_of_range 
                        
                        if parameters["plot_is_scale_intensity_of_spectra_array"][array_index] == True:
                            array_of_intensity_arrays_to_plot[array_index]= array_of_intensity_arrays_to_plot[array_index] * float(parameters["plot_scaling_array"][array_index]) 
                            formatted_scaling_text = "{:.{}g}".format(float(parameters["plot_scaling_array"][array_index]), 8)
                            ax.text(float(parameters["plot_scaling_text_x_offset_array"][array_index]), float(parameters["plot_scaling_text_y_offset_array"][array_index]) + float(parameters["plot_distance_between_groups_in_y"]) * incoming_energy_index + float(parameters["plot_y_distance_between_plots"]) * file_name_index, "x" + formatted_scaling_text, fontsize= float(parameters["plot_incoming_energy_text_size"]),  color=plot_color_array[array_index])
                        

                        if parameters["is_binning_smooth_data_for_all_spectra"]:
                            array_of_intensity_arrays_to_plot[array_index]= smoothing_scripts.bin_intensity_array(array_of_intensity_arrays_to_plot[array_index], int(parameters["number_of_bins_for_smoothing_array"][0]))
                            array_of_x_values_arrays_to_plot[array_index]= smoothing_scripts.bin_energy_array(array_of_x_values_arrays_to_plot[array_index], int(parameters["number_of_bins_for_smoothing_array"][0]))
                        elif parameters["is_binning_smooth_data_array"][array_index]:
                            array_of_intensity_arrays_to_plot[array_index]= smoothing_scripts.bin_intensity_array(array_of_intensity_arrays_to_plot[array_index], int(parameters["number_of_bins_for_smoothing_array"][array_index]))
                            array_of_x_values_arrays_to_plot[array_index]= smoothing_scripts.bin_energy_array(array_of_x_values_arrays_to_plot[array_index], int(parameters["number_of_bins_for_smoothing_array"][array_index]))

                        elif parameters["is_gaussian_smooth_data_for_all_spectra"]:
                            sigma = float(parameters["sigma_for_gaussian_smoothing_array"][0])
                            array_of_intensity_arrays_to_plot[array_index]= gaussian_filter1d(array_of_intensity_arrays_to_plot[array_index], sigma)
                        elif parameters["is_gaussian_smooth_data_array"][array_index]:
                            array_of_intensity_arrays_to_plot[array_index]= gaussian_filter1d(array_of_intensity_arrays_to_plot[array_index], float(parameters["sigma_for_gaussian_smoothing_array"][array_index]))
                        
                        array_of_intensity_arrays_to_plot[array_index]= np.asarray(array_of_intensity_arrays_to_plot[array_index]) + float(parameters["plot_intensity_offset_array"][array_index]) 

                        if incoming_energy_index == 0:
                            ax.plot(array_of_x_values_arrays_to_plot[array_index], array_of_intensity_arrays_to_plot[array_index] + float(parameters["plot_distance_between_groups_in_y"]) * incoming_energy_index + float(parameters["plot_y_distance_between_plots"]) * file_name_index, label = parameters["plot_legend_names_array"][file_name_index], color=plot_color_array[array_index], linestyle= linestyles_array[array_index])
                        else:
                            ax.plot(array_of_x_values_arrays_to_plot[array_index], array_of_intensity_arrays_to_plot[array_index] + float(parameters["plot_distance_between_groups_in_y"]) * incoming_energy_index + float(parameters["plot_y_distance_between_plots"]) * file_name_index, color=plot_color_array[array_index], linestyle= linestyles_array[array_index])


                    if file_name_index == 0:
                        if parameters["plot_display_incoming_energy_by_lines"]:
                            formatted_incoming_energy_start = "{:.{}g}".format(float(parameters["pfy_incoming_energy_start_array"][incoming_energy_index]) , int(parameters["plot_incoming_energy_significant_numbers"]))
                            formatted_incoming_energy_end = "{:.{}g}".format(float(parameters["pfy_incoming_energy_end_array"][incoming_energy_index]) , int(parameters["plot_incoming_energy_significant_numbers"]))
                            #text = f'y={exact_energy_per_channel_slope:.8f}x+{exact_energy_per_channel_intercept:.2f}\nR={exact_energy_per_channel_r_value:.8f} \nStandard error={exact_energy_per_channel_std_err:.8f}'
                            ax.text(float(parameters["plot_incoming_energy_x_offset"]), float(parameters["plot_incoming_energy_y_offset"]) + float(parameters["plot_distance_between_groups_in_y"]) * incoming_energy_index + float(parameters["plot_y_distance_between_plots"]) * file_name_index, formatted_incoming_energy_start + "-" + formatted_incoming_energy_end + " eV", fontsize= float(parameters["plot_incoming_energy_text_size"]))
                    
                    #if incoming_energy_index == 0:
                    #    legend_array.append(parameters["plot_legend_names_array"][file_name_index])
                    array_index += 1
        elif parameters["plot_spectra_grouping_type"]== "Group by file":
            pass

        #for file_name_index in range(int(parameters["input_number_of_complete_file_names"])):
        #    if file_name_index < ceil(int(parameters["input_number_of_complete_file_names"])/2) -1:
        #        ax.plot(self.array_of_x_values_arrays[file_name_index], self.array_of_y_values_arrays[file_name_index] + float(parameters["plot_waterfall_space_y_array"][file_name_index]), label= parameters["plot_legend_names_array"][file_name_index], color=plot_color_array[file_name_index])
        #    elif file_name_index == int(parameters["input_number_of_complete_file_names"]) - 1:
        #        ax.plot(self.array_of_x_values_arrays[file_name_index], self.array_of_y_values_arrays[file_name_index] + float(parameters["plot_waterfall_space_y_array"][file_name_index]), label= parameters["plot_legend_names_array"][file_name_index], color=plot_color_array[0], linestyle="dashdot")   
        #    else:
        #        ax.plot(self.array_of_x_values_arrays[file_name_index], self.array_of_y_values_arrays[file_name_index] + float(parameters["plot_waterfall_space_y_array"][file_name_index]), label= parameters["plot_legend_names_array"][file_name_index], color=plot_color_array[file_name_index - ceil(int(parameters["input_number_of_complete_file_names"])/2) + 1], linestyle="dashed")



        if parameters["is_energy_window_used_array"][0]:
            ax.set_xlim(float(parameters["plot_energy_loss_min_array"][0]), float(parameters["plot_energy_loss_max_array"][0]))

        if parameters["is_plot_intensity_limits_used_array"][0]:
            ax.set_ylim(float(parameters["plot_intensity_min_array"][0]), float(parameters["plot_intensity_max_array"][0]))
            
        if parameters["plot_display_sample_name_title"]:
            ax.set_title(parameters["plot_title"], fontsize= parameters["plot_title_size"])
        
        if parameters["is_plot_grid"]:
            ax.grid(which='both', axis='x')

        if parameters["is_display_legend"]:
            if parameters["plot_spectra_grouping_type"]== "No grouping":
                plt.legend(legend_array, fontsize= parameters["plot_legend_text_size"], loc="best")
            else:
                plt.legend(fontsize= parameters["plot_legend_text_size"], loc='best')


            #temporary lines below
            if True:
                #black_solid = mlines.Line2D([], [], color='black', linestyle='-', label='NFPP')
                #black_dashed = mlines.Line2D([], [], color='black', linestyle='--', label='Mn-NFPP')
                #black_dashdot = mlines.Line2D([], [], color='black', linestyle='-.', label='Ni-NFPP')
                #black_solid = mlines.Line2D([], [], color='blue', linestyle='-', label='NFPP')
                #black_dashed = mlines.Line2D([], [], color='red', linestyle='-', label='Mn-NFPP')
                #black_dashdot = mlines.Line2D([], [], color='green', linestyle='-', label='Ni-NFPP')
                #FePO4_linestyle = mlines.Line2D([], [], color='magenta', linestyle='-', label=r'FePO$_4$')
                #LiFePO4_linestyle = mlines.Line2D([], [], color='magenta', linestyle='-.', label=r'LiFePO$_4$')
                #FeP2O7_linestyle = mlines.Line2D([], [], color='black', linestyle='-', label=r'Fe$_4$(P$_2$O$_7$)$_3$')
                black_solid = mlines.Line2D([], [], color='blue', linestyle='-', label='CH')
                black_dashed = mlines.Line2D([], [], color='red', linestyle='-', label='DCH')

                plt.legend(handles=[black_solid, black_dashed], fontsize= parameters["plot_legend_text_size"], loc=(0.03, 0.85)) #loc="best"

        ax.set_xlabel(parameters["x_axis_title"], fontsize= parameters["plot_x_axis_text_size"])
        ax.set_ylabel(parameters["y_axis_title"], fontsize= parameters["plot_y_axis_text_size"])

        ax.xaxis.set_tick_params(labelsize= parameters["plot_x_axis_number_size"])
        ax.yaxis.set_tick_params(labelsize= parameters["plot_y_axis_number_size"])

        #intensity_array = np.vstack(intensity_array).astype(float)
 
        plots_manager = plt.get_current_fig_manager()
        screen_geometry = QDesktopWidget().screenGeometry()
        #plots_manager.window.setGeometry(50,80,floor(screen_geometry.width()/2 -50), floor(screen_geometry.height()-200))
        plots_manager.window.setGeometry(10,80,floor(screen_geometry.width()/2 -50), floor(screen_geometry.height()-200))
        self.figure_to_save.set_figwidth(float(parameters["plot_figure_size_x_array"][0]))
        self.figure_to_save.set_figheight(float(parameters["plot_figure_size_y_array"][0]))
            
        #self.figure_to_save.tight_layout()

        self.figure_to_save.show()


    def plot_only_raw_data(self, parameters):
        plt.close()

        incoming_energy_array = self.get_incoming_energy_array(parameters)
        
        if parameters["input_file_format"] =="h5":
            raw_intensity_array = get_single_spectrum_h5_or_txt_file_scripts.get_single_spectrum_h5_file(parameters, parameters["h5_root_location_data"], False, "")
        elif parameters["input_file_format"] =="txt":
            raw_intensity_array = get_single_spectrum_h5_or_txt_file_scripts.get_single_spectrum_txt_file(parameters, False, parameters["txt_intensity_data_row"], parameters["txt_intensity_data_column"], False, "", parameters["is_several_spectra_per_file"])
        
        fig, ax = plt.subplots(1)

        im = ax.plot(incoming_energy_array, raw_intensity_array)
        ax.set_xlabel('Excitation energy [eV]')
        ax.set_ylabel('Intensity [a.u]')
        
        plots_manager = plt.get_current_fig_manager()
        screen_geometry = QDesktopWidget().screenGeometry()
        plots_manager.window.setGeometry(50,80,floor(screen_geometry.width()/2 -50), floor(screen_geometry.height()-200))
        #fig.tight_layout()
        
        fig.show()


    def get_inputted_parameters_from_gui(self):
        return self.parameters

if __name__ == '__main__':
    input_file_location= "C:\\Users\\ponto479\\Documents\\02 Beamtime Data\\SLS Adress 03-2022\\RIXS"
    parameters= parameter_scripts.get_parameters(input_file_location)
    #parameters={"input_file_location": "C:\\Users\\ponto479\\Documents\\02 Beamtime Data\\SLS Adress 03-2022\\RIXS",
                #"is_program_running":True, "input_file_iteratable_file_number_start":"0100", "input_file_iteratable_file_number_end": "0120" }
    parameters["is_view_roots_or_input_txt"]
    parameters = run_main_gui(parameters)
    #print(parameters)
