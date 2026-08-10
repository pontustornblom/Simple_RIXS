#add_RIXS_map_intensities

import sys
import os
import platform
import subprocess
from PyQt5.QtWidgets import QLabel, QMainWindow, QCheckBox, QComboBox, QLineEdit, QPushButton, QLayout, QApplication, QVBoxLayout, QHBoxLayout, QWidget, QDesktopWidget, QLabel, QTextEdit, QMessageBox, QScrollArea
#from PyQt5.QtGui import QPixmap
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from math import floor
import numpy as np
from PyQt5.QtCore import QEventLoop
from PyQt5.QtCore import pyqtSignal
import pandas as pd
import heapq
import matplotlib.pyplot as plt
from matplotlib.pyplot import cm
from matplotlib.colors import LogNorm, Normalize
import subprocess
from scipy.optimize import curve_fit
from scipy import stats
from scipy.interpolate import interp1d
import json
import h5py
import parameter_scripts
import get_single_spectrum_h5_or_txt_file_scripts
import iteratable_number_to_int_script
import iteratable_number_to_float_script
import find_elastic_peak_maximum_script
import create_complete_file_location_for_treated_data
import get_treated_rixs_data_script
import adjust_excitation_energy_for_pcolormesh_plot_script

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
        self.is_energy_window_used_displayed= False
        self.is_plot_intensity_limits_used_displayed= False
        self.is_first_time_creating_waterfall_items= True

        #self.is_first_and_last_spectrum_displayed= False

        self.vbox = QVBoxLayout()

        self.vbox.addLayout(self.create_gui_item("input_file_project_folder", "Folder of the current project: ", "q_line_edit", [""]))
        self.vbox.addLayout(self.create_gui_item("input_file_raw_data_folder", "Subfolder where the raw data is stored: ", "q_line_edit", [""]))
        self.vbox.addLayout(self.create_gui_item("open file location", "Open raw data file location", "q_push_button",  [""]))   

        self.vbox.addLayout(self.create_bottom_buttons())
        self.vbox.addLayout(self.create_gui_item("Update the plot", "Update the plot", "q_push_button",  [""]))

        self.vbox.addLayout(self.create_gui_item("plot_colormap_choice", "Which colormap would you like to have? \n (turbo is recommended) ", "q_combo_box", ["turbo", "viridis", "gist_earth", "gist_stern", "inferno", "plasma", "gray", "gnuplot", "gist_rainbow"]))
        self.vbox.addLayout(self.create_gui_item("plot_figure_size_x_array_0", "What figure size in the x direction would you like? ", "q_line_edit", [""]))
        self.vbox.addLayout(self.create_gui_item("plot_figure_size_y_array_0", "What figure size in the y direction would you like? ", "q_line_edit", [""]))

        self.vbox.addLayout(self.create_gui_item("plot_display_color_bar", "Would you like to display the colorbar? ", "q_check_box", [""]))
        self.vbox.addLayout(self.create_gui_item("is_log_scale_color_bar", "Would you like the intensity to be on a logaritmic scale? (when plotting as a heat map) ", "q_check_box", [""]))

        self.vbox.addLayout(self.create_gui_item("plot_display_sample_name_title", "Would you like to display the sample name as a title of the plot? ", "q_check_box", [""]))
        self.vbox.addLayout(self.create_gui_item("plot_title_size", "What text size of the title would you like? ", "q_line_edit", [""]))
        self.vbox.addLayout(self.create_gui_item("plot_outgoing_energy_instead_of_energy_loss", "Would you like the x-axis to be emission energy instead of energy loss? ", "q_check_box", [""]))                
        self.vbox.addLayout(self.create_gui_item("plot_waterfall_instead_of_heat_map", "Would you like to plot the data as a waterfall plot instead of a heat map? ", "q_check_box", [""]))
        if self.parameters["plot_waterfall_instead_of_heat_map"] == True:
            self.create_waterfall_gui_items(self.item_plot_waterfall_instead_of_heat_map, self.parameters["plot_waterfall_instead_of_heat_map"], "plot_waterfall_instead_of_heat_map", self.hbox_plot_waterfall_instead_of_heat_map)
        self.is_first_time_creating_waterfall_items=False

        self.vbox.addLayout(self.create_gui_item("is_set_negative_intensities_to_zero", "If there are negative intensites, do you want to set the lowest intensity to zero? ", "q_check_box", [""]))
        self.vbox.addLayout(self.create_gui_item("is_subtract_background_from_RIXS", "Do you want to set the intensity above the elastic peak to zero? \n(Background subtraction) ", "q_check_box", [""]))
        self.vbox.addLayout(self.create_gui_item("energy_above_elastic_peak_to_fit_background_start", "If you are doing background subtraction, how many eV above the elastic peak should the first \ndata point be chosen to for averaging the background intensity? ", "q_line_edit", [""]))
        self.vbox.addLayout(self.create_gui_item("energy_above_elastic_peak_to_fit_background_end", "If you are doing background subtraction, how many eV above the elastic peak should the last \ndata point be chosen to for averaging the background intensity? ", "q_line_edit", [""]))

        self.vbox.addLayout(self.create_gui_item("energy_mismatch_tolerance", "How many eV appart are can the excitation energies be to determine which spectra that should be combined? ", "q_line_edit", [""]))
        
        self.vbox.addLayout(self.create_gui_item("plot_invert_x_axis", "Would you like to invert the x axis? ", "q_check_box", [""]))                
        self.vbox.addLayout(self.create_gui_item("plot_invert_y_axis", "Would you like to invert the y axis? ", "q_check_box", [""]))                
        self.vbox.addLayout(self.create_gui_item("plot_x_axis_text_size", "What text size of the x axis would you like? ", "q_line_edit", [""]))
        self.vbox.addLayout(self.create_gui_item("plot_y_axis_text_size", "What text size of the y axis would you like? ", "q_line_edit", [""]))
        self.vbox.addLayout(self.create_gui_item("plot_x_axis_number_size", "What is the number size of the x-axis? ", "q_line_edit", [""]))
        self.vbox.addLayout(self.create_gui_item("plot_y_axis_number_size", "What is the number size of the y-axis? ", "q_line_edit", [""]))

        self.vbox.addLayout(self.create_gui_item("is_energy_window_used_array_0", "Would you like to set a window in the x-y plane for the plot? ", "q_check_box", [""]))
        if self.parameters["is_energy_window_used_array"][0]:
            self.vbox.addLayout(self.create_gui_item("plot_energy_loss_min_array_0", "Input the lower cut off on the x axis: ", "q_line_edit", [""]))
            self.vbox.addLayout(self.create_gui_item("plot_energy_loss_max_array_0", "Input the upper cut off  on the x axis: ", "q_line_edit", [""]))
            self.vbox.addLayout(self.create_gui_item("plot_incoming_energy_min_array_0", "Input the lower cut off on the y axis: ", "q_line_edit", [""]))
            self.vbox.addLayout(self.create_gui_item("plot_incoming_energy_max_array_0", "Input the upper cut off on the y axis: ", "q_line_edit", [""]))
            self.is_energy_window_used_displayed= True 

        self.vbox.addLayout(self.create_gui_item("is_plot_intensity_limits_used_array_0", "Would you like to set a window in the z direction for the plot? ", "q_check_box", [""]))
        if self.parameters["is_plot_intensity_limits_used_array"][0]:
            self.vbox.addLayout(self.create_gui_item("plot_intensity_min_array_0", "Input the lower cut off on the z axis: ", "q_line_edit", [""]))
            self.vbox.addLayout(self.create_gui_item("plot_intensity_max_array_0", "Input the upper cut off on the z axis: ", "q_line_edit", [""]))
            self.is_plot_intensity_limits_used_displayed= True 
        
        self.vbox.addLayout(self.create_gui_item("is_plot_intensity_normalize_to_value_array_0", "Would you like to normalize the plot by setting the highest intensity to a certain value? ", "q_check_box", [""]))
        self.vbox.addLayout(self.create_gui_item("plot_value_to_normalize_highest_intensity_array_0", "What value do you want to set the highest intensity to? ", "q_line_edit", [""]))
        
        self.vbox.addLayout(self.create_gui_item("is_automatically_adjust_peak_to_correct_energy", "Would you like the program to automatically shift the elastic peak along the x-axis to its correct energy for each spectra?\n(OBS! Your manual shift will be applied after the automatical shift if you have that box checked)\nThis is currently using a squared weighted fit to the elastic peak followed by a gaussian \nfit that both are fitted to the values of the elastic part of the elastic peak. ", "q_check_box", [""]))
        self.vbox.addLayout(self.create_gui_item("energy_above_and_below_to_calculate_elastic_peak_weights", "Energy above and below elastic peak to get the intensity from to automatically adjust the position:\n(0.5 to 2 times the FWHM is a good approximated value) ", "q_line_edit", [""]))
        #self.vbox.addLayout(self.create_gui_item("degree_of_energy_per_channel_polynomial", "What degree polynomial do you want to fit the elastic peaks to? (Set to 1 for linear) ", "q_line_edit", [""]))        

        self.vbox.addLayout(self.create_gui_item("is_manual_shift_elastic_peak", "Would you like to manually shift the elastic peak along the x-axis? ", "q_check_box", [""]))
        iteratable_file_number_array = self.get_iteratable_file_number_array(self.parameters)
        #incoming_energy_array = self.get_incoming_energy_array(self.parameters, iteratable_file_number_array)
        #if self.parameters["is_manual_shift_elastic_peak"]:
        for spectra_index in range(int(self.parameters["input_number_of_complete_file_names"])):
            self.vbox.addLayout(self.create_gui_item("manual_shift_elastic_peak_array_" + str(spectra_index), "How many eV to shift the elastic peak of spectra " + str(spectra_index) + ": ", "q_line_edit", [""]))

        self.vbox.addLayout(self.create_gui_item("Update the plot", "Update the plot", "q_push_button",  [""]))

        self.vbox.addLayout(self.create_gui_item("", "The following inputs does not effect the calculation, it affects the saved file name", "q_text_label", [""]))
        self.vbox.addLayout(self.create_gui_item("output_file_element", "Element that is being studied: ", "q_line_edit", [""]))
        self.vbox.addLayout(self.create_gui_item("output_file_edge", "Edge that is being studied: ", "q_combo_box", ["K-edge", "L-edge", "L1-edge", "L2-edge", "L3-edge", "M-edge", "M1-edge", "M5-edge"]))
        self.vbox.addLayout(self.create_gui_item("output_file_sample_name", "Sample name: ", "q_line_edit", [""]))
        self.vbox.addLayout(self.create_gui_item("output_file_additional_comment", "Addional comment that will be saved with the file name: ", "q_line_edit", [""]))
        
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

        self.setWindowTitle("Simple RIXS Add RIXS map intensities")
        self.show()

        #if self.is_first_and_last_spectrum_displayed== False:
        
        #This line below has to be toggleed manually (If this script actually needs to plot something)
        #self.try_to_plot(self.parameters,"")
        self.plot_inputted_data(self.parameters, "")
        
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
                condition = True
                while condition:
                    try:
                        item = QLineEdit(self.parameters[array_key][array_index])
                        condition = False
                    except (IndexError):
                        self.parameters[array_key].append(self.parameters[array_key][0])
                hbox.addWidget(item)
                item.editingFinished.connect(lambda item=item: self.update_dictionary_array(array_key, array_index, item))
            elif key != "input_file_project_folder" and key != "input_file_raw_data_folder" and key != "output_file_additional_comment" and key != "output_file_sample_name" and key != "output_file_element":
                item = QLineEdit(self.parameters[key])
                hbox.addWidget(item)
                item.editingFinished.connect(lambda item=item, key=key: self.validate_input(item, key))
            else:
                item = QLineEdit(self.parameters[key])
                hbox.addWidget(item)
                item.textChanged.connect(lambda: self.update_dictionary(key, item.text()))
        elif item_type == "q_combo_box":
            hbox.addWidget(item_label)
            item = QComboBox()
            item.addItems(combo_box_options)
            if "array" in key:
                split_key_list = key.split('_')
                array_key = '_'.join(split_key_list[:-1])
                array_index = int(split_key_list[-1])
                condition = True
                while condition:
                    try:
                        item.setCurrentText(self.parameters[array_key][array_index])
                        condition = False
                    except (IndexError):
                        self.parameters[array_key].append(self.parameters[array_key][0])
                hbox.addWidget(item)
                item.currentTextChanged.connect(lambda item=item, key=key: self.update_dictionary_array(array_key, array_index, item))
            else:
                item.setCurrentText(self.parameters[key])
                hbox.addWidget(item)
                item.currentTextChanged.connect(lambda: self.update_dictionary(key, item.currentText()))
        elif item_type == "q_check_box":
            hbox.addWidget(item_label)
            item = QCheckBox()
            if "array" in key:
                split_key_list = key.split('_')
                array_key = '_'.join(split_key_list[:-1])
                array_index = int(split_key_list[-1])
                condition = True
                while condition:
                    try:
                        item.setChecked(self.parameters[array_key][array_index])
                        condition = False
                    except (IndexError):
                        self.parameters[array_key].append(self.parameters[array_key][0])
                hbox.addWidget(item)
                item.clicked.connect(lambda: self.create_mutliple_gui_items_from_checkbox_arrays(array_key, array_index, item, hbox))
            elif key == "plot_waterfall_instead_of_heat_map":
                self.hbox_plot_waterfall_instead_of_heat_map = QHBoxLayout()
                self.hbox_plot_waterfall_instead_of_heat_map.addWidget(item_label)
                self.item_plot_waterfall_instead_of_heat_map = QCheckBox()
                self.item_plot_waterfall_instead_of_heat_map.setChecked(self.parameters[key])
                self.hbox_plot_waterfall_instead_of_heat_map.addWidget(self.item_plot_waterfall_instead_of_heat_map)
                self.item_plot_waterfall_instead_of_heat_map.clicked.connect(lambda key=key: self.create_waterfall_gui_items(self.item_plot_waterfall_instead_of_heat_map, self.item_plot_waterfall_instead_of_heat_map.isChecked(), "plot_waterfall_instead_of_heat_map", self.hbox_plot_waterfall_instead_of_heat_map))
                return self.hbox_plot_waterfall_instead_of_heat_map
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

    def create_waterfall_gui_items(self, item, item_bool, key, hbox):
        self.update_dictionary_checkbox(key, item)
        if item_bool== True:
            self.vbox.insertLayout(self.vbox.indexOf(hbox)+1, self.create_gui_item("plot_y_distance_between_plots", "Input the y spacing between the spectra: ", "q_line_edit", [""]))
            self.vbox.insertLayout(self.vbox.indexOf(hbox)+2, self.create_gui_item("plot_display_incoming_energy_by_lines", "Would you like to display the incoming energy next to the spectra? ", "q_check_box", [""]))
            self.vbox.insertLayout(self.vbox.indexOf(hbox)+3, self.create_gui_item("plot_incoming_energy_x_offset", "Input value to adjust the x cooridnate of the incoming energy text: ", "q_line_edit", [""]))
            self.vbox.insertLayout(self.vbox.indexOf(hbox)+4, self.create_gui_item("plot_incoming_energy_y_offset", "Input value to adjust the y cooridnate of the incoming energy text: ", "q_line_edit", [""]))
            self.vbox.insertLayout(self.vbox.indexOf(hbox)+5, self.create_gui_item("plot_incoming_energy_text_size", "What text size of the incoming energy text would you like: ", "q_line_edit", [""]))
            self.vbox.insertLayout(self.vbox.indexOf(hbox)+6, self.create_gui_item("plot_incoming_energy_significant_numbers", "What many significant numbers of the incoming energy text would you like to display? ", "q_line_edit", [""]))
            self.vbox.insertLayout(self.vbox.indexOf(hbox)+7, self.create_gui_item("is_plot_grid", "Would you like to display grid lines in the y direction? ", "q_check_box", [""]))
        elif self.is_first_time_creating_waterfall_items== False:
            self.remove_item(self.vbox.indexOf(hbox)+1)
            self.remove_item(self.vbox.indexOf(hbox)+2)
            self.remove_item(self.vbox.indexOf(hbox)+3)
            self.remove_item(self.vbox.indexOf(hbox)+4)
            self.remove_item(self.vbox.indexOf(hbox)+5)
            self.remove_item(self.vbox.indexOf(hbox)+6)
            self.remove_item(self.vbox.indexOf(hbox)+7)
        self.is_first_time_creating_waterfall_items= False

    def update_dictionary(self, key, updated_value):
        self.parameters[key] = updated_value

    def update_dictionary_checkbox(self, key, item):
        if item.isChecked():
            self.parameters[key] = True
            if key== "is_view_roots_or_input_txt":
                self.vbox.insertLayout(self.vbox.count()-1,self.create_gui_item("input_complete_file_name", "Input example file name to view roots/txt ", "q_line_edit", [""]))                
        else:
            self.parameters[key] = False

    def update_dictionary_checkbox_array(self, key, array_index, item):
            #if self.validate_input_for_array(key, array_index, item):
            self.parameters[key][array_index] = item.isChecked()

    def update_dictionary_array(self, key, array_index, item):
        if key == "energy_per_channel_polynomial_coefficients_array":
            try:
                self.parameters[key][array_index] = item
            except (IndexError):
                self.parameters[key].append(item)
        elif self.validate_input_for_array(key, array_index, item) or key == "input_complete_file_name_array":
            try:
                self.parameters[key][array_index] = item.text()
            except AttributeError:
                self.parameters[key][array_index] = item




    def validate_input_for_array(self, key, array_index, item):
        # Determine if item is a widget (with a text() method) or already a string.
        if hasattr(item, 'text'):
            input_value = item.text()
            widget = item  # Keep a reference for actions like clear() or showing QMessageBox warnings.
        else:
            input_value = item
            widget = None

        # Proceed only if the input value differs from the corresponding parameter.
        if input_value != self.parameters[key][array_index]:
            if input_value == "":
                # If input is blank, warn (if it's a widget) and return False.
                if widget is not None:
                    QMessageBox.warning(self, "Invalid Input", "Do not leave blank")
                    widget.clear()
                return False
            else:
                try:
                    if input_value[0] == "0":
                        # Use your external conversion for numbers that start with "0"
                        float(iteratable_number_to_float_script.iteratable_number_to_float(input_value))
                        return True
                    else:
                        float(input_value)
                        return True
                except ValueError:
                    if widget is not None:
                        QMessageBox.warning(self, "Invalid Input", "Input must be an integer or float.")
                        widget.clear()
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


    def create_mutliple_gui_items_from_checkboxes(self, item, key, hbox):
        self.update_dictionary_checkbox(key, item)
        
        if key == "is_energy_window_used":
            if self.is_energy_window_used_displayed== False and self.parameters["is_energy_window_used"]:
                self.vbox.insertLayout(self.vbox.indexOf(hbox)+1, self.create_gui_item("plot_energy_loss_min", "Input the lower cut off on the x axis: ", "q_line_edit", [""]))
                self.vbox.insertLayout(self.vbox.indexOf(hbox)+2, self.create_gui_item("plot_energy_loss_max", "Input the upper cut off on the x axis: ", "q_line_edit", [""]))  
                self.vbox.insertLayout(self.vbox.indexOf(hbox)+3, self.create_gui_item("plot_incoming_energy_min", "Input the lower cut off on the y axis: ", "q_line_edit", [""]))
                self.vbox.insertLayout(self.vbox.indexOf(hbox)+4, self.create_gui_item("plot_incoming_energy_max", "Input the upper cut off on the y axis: ", "q_line_edit", [""]))                      
                self.is_energy_window_used_displayed =True
            elif self.is_energy_window_used_displayed == True and self.parameters["is_energy_window_used"] == False:
                self.remove_item(self.vbox.indexOf(hbox)+1)
                self.remove_item(self.vbox.indexOf(hbox)+2)
                self.remove_item(self.vbox.indexOf(hbox)+3)
                self.remove_item(self.vbox.indexOf(hbox)+4)
                self.is_energy_window_used_displayed =False
        elif key == "is_plot_intensity_limits_used":
            if self.is_plot_intensity_limits_used_displayed== False and self.parameters["is_plot_intensity_limits_used"]:
                self.vbox.insertLayout(self.vbox.indexOf(hbox)+1, self.create_gui_item("plot_intensity_min", "Input the lower cut off on the z axis: ", "q_line_edit", [""]))
                self.vbox.insertLayout(self.vbox.indexOf(hbox)+2, self.create_gui_item("plot_intensity_max", "Input the upper cut off on the z axis: ", "q_line_edit", [""]))
                self.is_plot_intensity_limits_used_displayed =True
            elif self.is_plot_intensity_limits_used_displayed == True and self.parameters["is_plot_intensity_limits_used"] == False:
                self.remove_item(self.vbox.indexOf(hbox)+1)
                self.remove_item(self.vbox.indexOf(hbox)+2)
                self.is_plot_intensity_limits_used_displayed =False


    def create_mutliple_gui_items_from_checkbox_arrays(self, array_key, array_index, item, hbox):
        self.update_dictionary_checkbox_array(array_key, array_index, item)
        if array_key == "is_approximate_energy_for_normalization_to_zero_array":
            if self.is_approximate_energy_for_normalization_to_zero_displayed== False and self.parameters["is_approximate_energy_for_normalization_to_zero_array"][array_index]:
                self.vbox.insertLayout(self.vbox.indexOf(hbox)+1,self.create_gui_item("approximate_energy_for_normalization_to_zero_array" + "_" + str(array_index), "Approximate incoming energy of lowest intenisty: ", "q_line_edit", [""]))
                self.is_approximate_energy_for_normalization_to_zero_displayed =True
            elif self.is_approximate_energy_for_normalization_to_zero_displayed == True and self.parameters["is_approximate_energy_for_normalization_to_zero_array"][array_index] == False:
                self.remove_item(self.vbox.indexOf(hbox)+1)
                self.is_approximate_energy_for_normalization_to_zero_displayed =False
        elif array_key == "is_subtract_fitted_background_array":
            if self.is_subtract_fitted_background_displayed== False and self.parameters["is_subtract_fitted_background_array"][array_index]:
                self.vbox.insertLayout(self.vbox.indexOf(hbox)+1,self.create_gui_item("background_fit_type_array" + "_" + str(array_index), "What type of graph would you like to fit? ", "q_combo_box", ["Linear", "ln(x)", "log(x)", "Gaussian", "x^(-2)"]))
                self.vbox.insertLayout(self.vbox.indexOf(hbox)+2,self.create_gui_item("background_fit_energy_start_array" + "_" + str(array_index), "From what energy should the graph be fitted? ", "q_line_edit", [""]))
                self.vbox.insertLayout(self.vbox.indexOf(hbox)+3,self.create_gui_item("background_fit_energy_end_array" + "_" + str(array_index), "To what energy should the graph be fitted? ", "q_line_edit", [""]))
                self.is_subtract_fitted_background_displayed =True
            elif self.is_subtract_fitted_background_displayed == True and self.parameters["is_subtract_fitted_background_array"][array_index] == False:
                self.remove_item(self.vbox.indexOf(hbox)+1)
                self.remove_item(self.vbox.indexOf(hbox)+2)
                self.remove_item(self.vbox.indexOf(hbox)+3)
                self.is_subtract_fitted_background_displayed =False
        elif array_key == "is_energy_window_used_array":
            if self.is_energy_window_used_displayed== False and self.parameters["is_energy_window_used_array"][array_index]:
                self.vbox.insertLayout(self.vbox.indexOf(hbox)+1, self.create_gui_item("plot_energy_loss_min_array" + "_" + str(array_index), "Input the lower cut off on the x axis: ", "q_line_edit", [""]))
                self.vbox.insertLayout(self.vbox.indexOf(hbox)+2, self.create_gui_item("plot_energy_loss_max_array" + "_" + str(array_index), "Input the upper cut off on the x axis: ", "q_line_edit", [""])) 
                self.vbox.insertLayout(self.vbox.indexOf(hbox)+3, self.create_gui_item("plot_incoming_energy_min_array" + "_" + str(array_index), "Input the lower cut off on the y axis: ", "q_line_edit", [""]))
                self.vbox.insertLayout(self.vbox.indexOf(hbox)+4, self.create_gui_item("plot_incoming_energy_max_array" + "_" + str(array_index), "Input the upper cut off on the y axis: ", "q_line_edit", [""]))                       
                self.is_energy_window_used_displayed =True
            elif self.is_energy_window_used_displayed == True and self.parameters["is_energy_window_used_array"][array_index] == False:
                self.remove_item(self.vbox.indexOf(hbox)+1)
                self.remove_item(self.vbox.indexOf(hbox)+2)
                self.remove_item(self.vbox.indexOf(hbox)+3)
                self.remove_item(self.vbox.indexOf(hbox)+4)
                self.is_energy_window_used_displayed =False
        elif array_key == "is_plot_intensity_limits_used_array":
            if self.is_plot_intensity_limits_used_displayed== False and self.parameters["is_plot_intensity_limits_used_array"][array_index]:
                self.vbox.insertLayout(self.vbox.indexOf(hbox)+1, self.create_gui_item("plot_intensity_min_array" + "_" + str(array_index), "Input the lower cut off for the intensity window: ", "q_line_edit", [""]))
                self.vbox.insertLayout(self.vbox.indexOf(hbox)+2, self.create_gui_item("plot_intensity_max_array" + "_" + str(array_index), "Input the upper cut off for the intensity window: ", "q_line_edit", [""]))
                self.is_plot_intensity_limits_used_displayed =True
            elif self.is_plot_intensity_limits_used_displayed == True and self.parameters["is_plot_intensity_limits_used_array"][array_index] == False:
                self.remove_item(self.vbox.indexOf(hbox)+1)
                self.remove_item(self.vbox.indexOf(hbox)+2)
                self.is_plot_intensity_limits_used_displayed =False

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
        figure_name= "RIXS_map"
        figure_name+= "_combined"
        if self.parameters["plot_waterfall_instead_of_heat_map"]:
            figure_name+= "_waterfall"
        figure_name+="_" + self.parameters["output_file_element"]
        figure_name+="_" + self.parameters["output_file_edge"]
        figure_name+="_" + self.parameters["output_file_sample_name"]
        figure_name+="_files_" + self.parameters["input_file_iteratable_file_number_start"] + "_" + self.parameters["input_file_iteratable_file_number_end"]
        if self.parameters["input_file_number_of_files_to_ignore"] != "0" and self.parameters["input_file_number_of_files_to_ignore"] != "":
            figure_name+="_some_ignored_files"
        if self.parameters["is_normalization_to_i0"]:
            figure_name+= "_i0normalized"
        if self.parameters["is_energy_window_used_array"][0]:
            figure_name+= "_energy_window"
        if self.parameters["is_plot_intensity_limits_used_array"][0]:
            figure_name+= "_intensity_window"
        if self.parameters["plot_outgoing_energy_instead_of_energy_loss"]:
            figure_name+= "_emission_energy"
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
        
        full_figure_path= os.path.join(figure_path, figure_name)
        self.figure_to_save.savefig(full_figure_path)
        #self.figure_to_save.savefig(full_figure_path, dpi = 600)

        full_parameters_path=os.path.join(figure_path, figure_parameters_name)
        formatted_parameters = json.dumps(self.parameters, indent=0)
        with open(full_parameters_path, "w") as parameters_file:
            parameters_file.write(formatted_parameters)

        full_data_path=os.path.join(figure_path, figure_data_name) 

        data_dictionary= {}
        if self.parameters["plot_outgoing_energy_instead_of_energy_loss"]:
            for array_index in range(len(self.array_of_intensity_arrays_to_save)):
                data_dictionary['Emission energy [eV]' + '_' + 'spectra_' + str(array_index) + '_' + str(self.incoming_energy_array_to_save[array_index])]= self.array_of_x_value_arrays_to_save[array_index]
                data_dictionary["Intensity [a.u]" + '_' + 'spectra_' + str(array_index) + '_' + str(self.incoming_energy_array_to_save[array_index])]= self.array_of_intensity_arrays_to_save[array_index]
        else:
            for array_index in range(len(self.array_of_intensity_arrays_to_save)):
                data_dictionary['Energy loss [eV]' + '_' + 'spectra_' + str(array_index) + '_' + str(self.incoming_energy_array_to_save[array_index])]= self.array_of_x_value_arrays_to_save[array_index]
                data_dictionary["Intensity [a.u]" + '_' + 'spectra_' + str(array_index) + '_' + str(self.incoming_energy_array_to_save[array_index])]= self.array_of_intensity_arrays_to_save[array_index]
        
        data_dataframe = pd.DataFrame.from_dict(data_dictionary, orient='index').transpose().fillna('')
        data_dataframe.to_csv(full_data_path, sep= '\t', index=False)


    def save_treated_data_old(self):
        figure_name= "RIXS_map"
        figure_name+= "_combined"
        if self.parameters["plot_waterfall_instead_of_heat_map"]:
            figure_name+= "_waterfall"
        figure_name+="_" + self.parameters["output_file_element"]
        figure_name+="_" + self.parameters["output_file_edge"]
        figure_name+="_" + self.parameters["output_file_sample_name"]
        figure_name+="_files_" + self.parameters["input_file_iteratable_file_number_start"] + "_" + self.parameters["input_file_iteratable_file_number_end"]
        if self.parameters["input_file_number_of_files_to_ignore"] != "0" and self.parameters["input_file_number_of_files_to_ignore"] != "":
            figure_name+="_some_ignored_files"
        if self.parameters["is_i0_available_in_file"] or self.parameters["is_i0_avialable_in_seperate_file"]:
            figure_name+= "_i0normalized"
        if self.parameters["is_plot_intensity_normalize_to_value_array"][0]:
            figure_name+= "_normalized_to_value"
        if self.parameters["is_energy_window_used_array"][0]:
            figure_name+= "_energy_window"
        if self.parameters["is_plot_intensity_limits_used_array"][0]:
            figure_name+= "_intensity_window"
        if self.parameters["plot_outgoing_energy_instead_of_energy_loss"]:
            figure_name+= "_emission_energy"
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
        
        full_figure_path= os.path.join(figure_path, figure_name)
        self.figure_to_save.savefig(full_figure_path)

        full_parameters_path=os.path.join(figure_path, figure_parameters_name)
        formatted_parameters = json.dumps(self.parameters, indent=0)
        with open(full_parameters_path, "w") as parameters_file:
            parameters_file.write(formatted_parameters)


        full_data_path=os.path.join(figure_path, figure_data_name) 
        if self.parameters["plot_outgoing_energy_instead_of_energy_loss"]:
            data_dictionary= {'Emission energy [eV]':self.treated_data_array[0], 'Excitation energy [eV]':self.treated_data_array[1]}
        else:
            data_dictionary= {'Energy loss [eV]':self.treated_data_array[0], 'Excitation energy [eV]':self.treated_data_array[1]}
        for spectra in range(len(self.treated_data_array[2])):
            data_dictionary['Spectra_'+ str(spectra)]= self.treated_data_array[2][spectra]
        
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
        
        for string_number in parameters["input_file_ignore_file_number_array"]:
            if string_number != "":
                ignored_numbers_array.append(iteratable_number_to_int_script.iteratable_number_to_int(string_number))

        first_iteratable_int= iteratable_number_to_int_script.iteratable_number_to_int(parameters["input_file_iteratable_file_number_start"])
        last_iteratable_int= iteratable_number_to_int_script.iteratable_number_to_int(parameters["input_file_iteratable_file_number_end"])
        
        for iteratable_int in range(first_iteratable_int, last_iteratable_int + 1):
            if iteratable_int not in ignored_numbers_array:
                iteratable_string= str(iteratable_int)
                while len(parameters["input_file_iteratable_file_number_start"]) > len(iteratable_string):
                    iteratable_string = "0" + iteratable_string
                iteratable_file_number_array.append(iteratable_string)

        return iteratable_file_number_array

    def get_incoming_energy_array(self, parameters, iteratable_file_number_array):
        #The different options in this function have not been tested thoroughly
        incoming_energy_array = []
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
            elif parameters["input_file_format"]== "dat":
                complete_file_location = os.path.join(parameters["complete_incoming_energy_file_location"], parameters["complete_incoming_energy_file_name"])
                if complete_file_location[-4:] != ".dat":
                    complete_file_location = complete_file_location + ".dat"
            elif parameters["input_file_format"]== "csv":
                complete_file_location = os.path.join(parameters["complete_incoming_energy_file_location"], parameters["complete_incoming_energy_file_name"])
                if complete_file_location[-4:] != ".csv":
                    complete_file_location = complete_file_location + ".csv"

                data_row = int(parameters["txt_incoming_energy_row_in_file"])
                data_column= int(parameters["txt_incoming_energy_column_in_file"])
                if parameters["txt_delimiter"] == "Tab":
                    dataframe = pd.read_csv(complete_file_location, sep='\t', skiprows=data_row, usecols=[data_column], header=None)
                elif parameters["txt_delimiter"] == "Space":
                    dataframe = pd.read_csv(complete_file_location, sep=' ', skiprows=data_row, usecols=[data_column], header=None)
                else:
                    dataframe = pd.read_csv(complete_file_location, sep=parameters["txt_delimiter"], skiprows=data_row, usecols=[data_column], header=None)
            # Access the values of the column
                incoming_energy_array = dataframe.iloc[:, 0].values

            if isinstance(incoming_energy_array[0], np.ndarray) or isinstance(incoming_energy_array[0], list):
                if len(incoming_energy_array[0]) >1: 
                    for iteratable_number in range(len(iteratable_file_number_array)):
                        incoming_energy_array[iteratable_number]= np.mean(incoming_energy_array[iteratable_number])
                else:
                    for iteratable_number in range(len(iteratable_file_number_array)):
                        incoming_energy_array[iteratable_number]= incoming_energy_array[iteratable_number][0]

        elif parameters["is_incoming_energy_available_in_file"]:
            if parameters["input_file_format"]== "h5":
                for iteratable_number in iteratable_file_number_array:
                    incoming_energy = get_single_spectrum_h5_or_txt_file_scripts.get_single_spectrum_h5_file(parameters, parameters["h5_root_location_incoming_energy"], True, iteratable_number)
                    incoming_energy_array.append(incoming_energy)
            elif parameters["input_file_format"]== "txt" or parameters["input_file_format"]== "dat" or parameters["input_file_format"]== "csv":
                for iteratable_number in iteratable_file_number_array:
                    incoming_energy = get_single_spectrum_h5_or_txt_file_scripts.get_single_spectrum_txt_file(parameters, parameters["is_txt_single_incoming_energy_value"], parameters["txt_incoming_energy_row_in_file"], parameters["txt_incoming_energy_column_in_file"], True, iteratable_number, False)
                    incoming_energy_array.append(incoming_energy)
            if isinstance(incoming_energy_array[0], np.ndarray) or isinstance(incoming_energy_array[0], list):
                if len(incoming_energy_array[0]) >1: 
                    for iteratable_number in range(len(iteratable_file_number_array)):
                        incoming_energy_array[iteratable_number]= np.mean(incoming_energy_array[iteratable_number])
                else:
                    for iteratable_number in range(len(iteratable_file_number_array)):
                        incoming_energy_array[iteratable_number]= incoming_energy_array[iteratable_number][0]

        elif parameters["is_equal_incoming_energy_difference"]:
            #Here it should be possible to just do a linspace like there is in the "plot_singel_spectra" script?
            energy_difference_per_spectra= (float(parameters["energy_of_last_line_spectra"])-float(parameters["energy_of_first_line_spectra"]))/(len(iteratable_file_number_array)-1)
            for iteratable_number in range(len(iteratable_file_number_array)):
                incoming_energy_array.append(float(parameters["energy_of_first_line_spectra"])+ iteratable_number*energy_difference_per_spectra)
        
        elif parameters["is_segments_of_equal_incoming_energy_difference"]:
            current_energy= 0
            current_energy=float(parameters["first_incoming_energy_of_segment_array"][0])
            incoming_energy_array.append(current_energy) 
            for segment in range(int(parameters["input_number_of_incoming_energy_segments"])):
                array_index_in_segment= 1
                if segment != int(parameters["input_number_of_incoming_energy_segments"]) -1:
                    while current_energy < float(parameters["first_incoming_energy_of_segment_array"][segment + 1]) - (float(parameters["incoming_energy_difference_in_segment_array"][segment])/2):
                        current_energy=float(parameters["first_incoming_energy_of_segment_array"][segment])+ array_index_in_segment*float(parameters["incoming_energy_difference_in_segment_array"][segment])
                        incoming_energy_array.append(current_energy)
                        array_index_in_segment+=1
                else:
                    while current_energy < float(parameters["incoming_energy_of_last_spectra"]) - (float(parameters["incoming_energy_difference_in_segment_array"][segment])/2):
                        current_energy= float(parameters["first_incoming_energy_of_segment_array"][segment])+ array_index_in_segment*float(parameters["incoming_energy_difference_in_segment_array"][segment])
                        incoming_energy_array.append(current_energy)
                        array_index_in_segment+=1

        elif parameters["is_segments_of_equal_incoming_energy_difference_with_gap"]:
            current_energy= 0
            #current_energy=float(parameters["first_incoming_energy_of_segment_array"][0])
            #incoming_energy_array.append(current_energy) 
            for segment in range(int(parameters["input_number_of_incoming_energy_segments_with_gap"])):
                array_index_in_segment= 0
                if segment != int(parameters["input_number_of_incoming_energy_segments_with_gap"]) -1:
                    if segment == 0:
                        while current_energy < float(parameters["last_incoming_energy_of_segment_array"][segment]) - (float(parameters["incoming_energy_difference_in_segment_array"][segment])/2):
                            current_energy=float(parameters["first_incoming_energy_of_segment_array"][segment])+ array_index_in_segment*float(parameters["incoming_energy_difference_in_segment_array"][segment])
                            incoming_energy_array.append(current_energy)
                            array_index_in_segment+=1
                    else:
                        while current_energy < float(parameters["last_incoming_energy_of_segment_array"][segment]) - (float(parameters["incoming_energy_difference_in_segment_array"][segment])/2):
                            if float(parameters["first_incoming_energy_of_segment_array"][segment])+ array_index_in_segment*float(parameters["incoming_energy_difference_in_segment_array"][segment]) != current_energy:
                                current_energy=float(parameters["first_incoming_energy_of_segment_array"][segment])+ array_index_in_segment*float(parameters["incoming_energy_difference_in_segment_array"][segment])
                                incoming_energy_array.append(current_energy)
                            array_index_in_segment+=1
                else:
                    while current_energy < float(parameters["last_incoming_energy_of_segment_array"][segment]) - (float(parameters["incoming_energy_difference_in_segment_array"][segment])/2):
                        current_energy= float(parameters["first_incoming_energy_of_segment_array"][segment])+ array_index_in_segment*float(parameters["incoming_energy_difference_in_segment_array"][segment])
                        incoming_energy_array.append(current_energy)
                        array_index_in_segment+=1

        elif parameters["is_input_every_incoming_energy"]:
            for iteratable_number in range(len(iteratable_file_number_array)):
                incoming_energy_array.append(float(parameters["incoming_energy_of_spectra_array"][iteratable_number]))
            
        return np.asarray(incoming_energy_array)

    def gaussian(self, x, A, mu, sigma, offset):
        return A * np.exp(-(x - mu)**2 / (2 * sigma**2)) + offset
    
    def get_elastic_peak_channel_center_array(self, parameters, approximate_channel_per_energy, iteratable_file_number_array, incoming_energy_array ):
        channels_above_and_below_elastic_to_fit = int(parameters["channels_above_and_below_elastic_to_fit"])
        array_index=0
        elastic_peak_center_array= []
        array_of_intensity_arrays= np.zeros(len(iteratable_file_number_array), dtype=object)
        intensity_weights_array= np.zeros(len(iteratable_file_number_array))
        intensity_array_index= 0
        for iteratable_number in iteratable_file_number_array:
            #iteratable_int= iteratable_number_to_int_script.iteratable_number_to_int(iteratable_number)
            if parameters["input_file_format"] =="h5":
                y_values = get_single_spectrum_h5_or_txt_file_scripts.get_single_spectrum_h5_file(parameters, parameters["h5_root_location_data"], True, iteratable_number)
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
                    y_values= y_values/i0_values[array_index]
                    
                elif parameters["is_i0_available_in_file"]:
                    i0_values = get_single_spectrum_h5_or_txt_file_scripts.get_single_spectrum_h5_file(parameters, parameters["i0_root_location_data"], True, iteratable_number)
                    i0_mean= np.mean(i0_values)
                    y_values= y_values/i0_mean
                array_of_intensity_arrays[intensity_array_index]= y_values
                intensity_array_index+= 1
            elif parameters["input_file_format"] =="txt" or parameters["input_file_format"] == "dat" or parameters["input_file_format"] == "csv":
                y_values = get_single_spectrum_h5_or_txt_file_scripts.get_single_spectrum_txt_file(parameters, False, parameters["txt_intensity_data_row"], parameters["txt_intensity_data_column"], True, iteratable_number, parameters["is_several_spectra_per_file"])
                if parameters["is_i0_avialable_in_seperate_file"]:
                    complete_file_location = os.path.join(parameters["complete_i0_file_location"], parameters["complete_i0_file_name"])
                    if complete_file_location[-3:] == ".h5":
                        complete_file_location=complete_file_location[:-3]
                    if parameters["input_file_format"] == "txt":
                        if complete_file_location[-4:] != ".txt":
                            complete_file_location = complete_file_location + ".txt"
                    if parameters["input_file_format"] == "dat":
                        if complete_file_location[-4:] != ".dat":
                            complete_file_location = complete_file_location + ".dat"
                    if parameters["input_file_format"] == "csv":
                        if complete_file_location[-4:] != ".csv":
                            complete_file_location = complete_file_location + ".csv"

                    data_row = int(parameters["txt_i0_row_in_file"])
                    data_column= int(parameters["txt_i0_column_in_file"])
                    if parameters["txt_delimiter"] == "Tab":
                        dataframe = pd.read_csv(complete_file_location, sep='\t', skiprows=data_row, usecols=[data_column], header=None)
                    elif parameters["txt_delimiter"] == "Space":
                        dataframe = pd.read_csv(complete_file_location, sep=' ', skiprows=data_row, usecols=[data_column], header=None)
                    else:
                        dataframe = pd.read_csv(complete_file_location, sep=parameters["txt_delimiter"], skiprows=data_row, usecols=[data_column], header=None)
                # Access the values of the column
                    i0_values = dataframe.iloc[:, 0].values

                    if isinstance(i0_values[0], np.ndarray) or isinstance(i0_values[0], list):
                        if len(i0_values[0]) >1: 
                            for iteratable_number in range(len(iteratable_file_number_array)):
                                i0_values[iteratable_number]= np.mean(i0_values[iteratable_number])
                        else:
                            for iteratable_number in range(len(iteratable_file_number_array)):
                                i0_values[iteratable_number]= i0_values[iteratable_number][0]

                    y_values= y_values/i0_values[array_index] #This assumes that the i0_values found in the other file contains values for all RIXS spectra and not a seperate file for each RIXS spectra.
                elif parameters["is_i0_available_in_file"]:
                    i0_values = get_single_spectrum_h5_or_txt_file_scripts.get_single_spectrum_txt_file(parameters, parameters["is_txt_single_i0_value"], parameters["txt_i0_row_in_file"], parameters["txt_i0_column_in_file"], True, iteratable_number)
                    i0_mean= np.mean(i0_values)
                    y_values= y_values/i0_mean
                array_of_intensity_arrays[intensity_array_index]= y_values
                intensity_array_index+= 1
            peak_channel_center=0
            sum_of_intensity_weight= 0
            highest_intensity, highest_intensity_channel = find_elastic_peak_maximum_script.find_elastic_peak_maximum(parameters, y_values, round(approximate_channel_per_energy*(incoming_energy_array[array_index] - incoming_energy_array[0]) + int(parameters["approximate_channel_of_first_elastic_peak"])))
            if parameters["is_weighted_elastic_peak_fit"]:
                #highest_intensity_channel= highest_intensity_channel +1
                for channel in range(highest_intensity_channel - channels_above_and_below_elastic_to_fit, highest_intensity_channel + channels_above_and_below_elastic_to_fit +1):
                    peak_channel_center+= y_values[channel]*channel
                    sum_of_intensity_weight+= y_values[channel]
                peak_channel_center = peak_channel_center/sum_of_intensity_weight
                intensity_weights_array[array_index]=sum_of_intensity_weight
            elif parameters["is_full_gaussian_elastic_peak_fit"]:
                x_values_gaussian= np.linspace(highest_intensity_channel - channels_above_and_below_elastic_to_fit, highest_intensity_channel + channels_above_and_below_elastic_to_fit, 2*channels_above_and_below_elastic_to_fit)
                y_values_gaussian= y_values[highest_intensity_channel - channels_above_and_below_elastic_to_fit : highest_intensity_channel + channels_above_and_below_elastic_to_fit]
                mu_guess = highest_intensity_channel
                sigma_guess = (x_values_gaussian[0] - x_values_gaussian[-1]) / 8
                A_guess = highest_intensity
                initial_guesses = [A_guess, mu_guess, sigma_guess]
                gaussian_parameters, covariance = curve_fit(self.gaussian, x_values_gaussian, y_values_gaussian, p0=initial_guesses)
                gaussian_fitted_y_values= self.gaussian(x_values_gaussian, *gaussian_parameters)
                peak_channel_center= highest_intensity_channel - channels_above_and_below_elastic_to_fit + np.argmax(gaussian_fitted_y_values)
                intensity_weights_array[array_index]=np.argmax(gaussian_fitted_y_values)
            elif parameters["is_half_gaussian_elastic_peak_fit"]:
                x_values_gaussian= np.linspace(highest_intensity_channel, highest_intensity_channel + channels_above_and_below_elastic_to_fit, channels_above_and_below_elastic_to_fit )
                y_values_gaussian= y_values[highest_intensity_channel:highest_intensity_channel + channels_above_and_below_elastic_to_fit]
                #mu_guess = highest_intensity_channel
                #sigma_guess = (x_values_gaussian[0] - x_values_gaussian[-1]) / 4
                #A_guess = highest_intensity / (np.sqrt(2 * np.pi) * sigma_guess)
                #initial_guesses = [A_guess, mu_guess, sigma_guess]
                gaussian_parameters, covariance = curve_fit(self.gaussian, x_values_gaussian, y_values_gaussian)
                x_values_full_gaussian=np.linspace(highest_intensity_channel - channels_above_and_below_elastic_to_fit, highest_intensity_channel + channels_above_and_below_elastic_to_fit, 2*channels_above_and_below_elastic_to_fit)
                gaussian_fitted_y_values= self.gaussian(x_values_full_gaussian, *gaussian_parameters)
                peak_channel_center= highest_intensity_channel - channels_above_and_below_elastic_to_fit + np.argmax(gaussian_fitted_y_values)
                intensity_weights_array[array_index]=np.argmax(gaussian_fitted_y_values)

            array_index+=1
            elastic_peak_center_array.append(round(peak_channel_center))

        return elastic_peak_center_array, array_of_intensity_arrays, intensity_weights_array

    def get_array_of_intensity_arrays(self, parameters, iteratable_file_number_array):
        array_index=0
        array_of_intensity_arrays= np.zeros(len(iteratable_file_number_array), dtype=object)
        intensity_array_index= 0
        for iteratable_number in iteratable_file_number_array:
            #iteratable_int= iteratable_number_to_int_script.iteratable_number_to_int(iteratable_number)
            if parameters["input_file_format"] =="h5":
                y_values = get_single_spectrum_h5_or_txt_file_scripts.get_single_spectrum_h5_file(parameters, parameters["h5_root_location_data"], True, iteratable_number)
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
                    y_values= y_values/i0_values[array_index]
                    
                elif parameters["is_i0_available_in_file"]:
                    i0_values = get_single_spectrum_h5_or_txt_file_scripts.get_single_spectrum_h5_file(parameters, parameters["i0_root_location_data"], True, iteratable_number)
                    i0_mean= np.mean(i0_values)
                    y_values= y_values/i0_mean
                array_of_intensity_arrays[intensity_array_index]= y_values
                intensity_array_index+= 1
            elif parameters["input_file_format"] =="txt" or parameters["input_file_format"] == "dat" or parameters["input_file_format"] == "csv":
                y_values = get_single_spectrum_h5_or_txt_file_scripts.get_single_spectrum_txt_file(parameters, False, parameters["txt_intensity_data_row"], parameters["txt_intensity_data_column"], True, iteratable_number, parameters["is_several_spectra_per_file"])
                if parameters["is_i0_avialable_in_seperate_file"]:
                    complete_file_location = os.path.join(parameters["complete_i0_file_location"], parameters["complete_i0_file_name"])
                    if complete_file_location[-3:] == ".h5":
                        complete_file_location=complete_file_location[:-3]
                    if parameters["input_file_format"] == "txt":
                        if complete_file_location[-4:] != ".txt":
                            complete_file_location = complete_file_location + ".txt"
                    if parameters["input_file_format"] == "dat":
                        if complete_file_location[-4:] != ".dat":
                            complete_file_location = complete_file_location + ".dat"
                    if parameters["input_file_format"] == "csv":
                        if complete_file_location[-4:] != ".csv":
                            complete_file_location = complete_file_location + ".csv"

                    data_row = int(parameters["txt_i0_row_in_file"])
                    data_column= int(parameters["txt_i0_column_in_file"])
                    if parameters["txt_delimiter"] == "Tab":
                        dataframe = pd.read_csv(complete_file_location, sep='\t', skiprows=data_row, usecols=[data_column], header=None)
                    elif parameters["txt_delimiter"] == "Space":
                        dataframe = pd.read_csv(complete_file_location, sep=' ', skiprows=data_row, usecols=[data_column], header=None)
                    else:
                        dataframe = pd.read_csv(complete_file_location, sep=parameters["txt_delimiter"], skiprows=data_row, usecols=[data_column], header=None)
                # Access the values of the column
                    i0_values = dataframe.iloc[:, 0].values

                    if isinstance(i0_values[0], np.ndarray) or isinstance(i0_values[0], list):
                        if len(i0_values[0]) >1: 
                            for iteratable_number in range(len(iteratable_file_number_array)):
                                i0_values[iteratable_number]= np.mean(i0_values[iteratable_number])
                        else:
                            for iteratable_number in range(len(iteratable_file_number_array)):
                                i0_values[iteratable_number]= i0_values[iteratable_number][0]

                    y_values= y_values/i0_values[array_index] #This assumes that the i0_values found in the other file contains values for all RIXS spectra and not a seperate file for each RIXS spectra.
                elif parameters["is_i0_available_in_file"]:
                    i0_values = get_single_spectrum_h5_or_txt_file_scripts.get_single_spectrum_txt_file(parameters, parameters["is_txt_single_i0_value"], parameters["txt_i0_row_in_file"], parameters["txt_i0_column_in_file"], True, iteratable_number)
                    i0_mean= np.mean(i0_values)
                    y_values= y_values/i0_mean
                array_of_intensity_arrays[intensity_array_index]= y_values
                intensity_array_index+= 1
        return np.array(array_of_intensity_arrays)

    def get_x_values_array_and_energy_per_channel(self, array_of_x_values_array, array_of_intensity_arrays, iteratable_file_number_array):
        #The for loop below adds 4 datapoints in between each datapoints and interpolates the data. This is to make finer adjustments when alinging the data
        new_temp_array=[None]* len(array_of_intensity_arrays)
        for spectra in range(len(array_of_intensity_arrays)):
            original_length = len(array_of_intensity_arrays[spectra])
            desired_length = original_length * 5 - 4

            new_indices = np.linspace(0, original_length - 1, desired_length)
            new_intensity_array = np.interp(new_indices, np.arange(original_length), array_of_intensity_arrays[spectra])

            new_temp_array[spectra]=  new_intensity_array

        array_of_intensity_arrays = np.asarray(new_temp_array)
        
        total_lowest_x_value=0
        total_highest_x_value=0
        array_of_lowest_x_values= []
        array_of_highest_x_values= []
        sum_of_average_energy_per_pixel= 0
        for spectrum in range(len(iteratable_file_number_array)):
            array_of_lowest_x_values.append(min(array_of_x_values_array[spectrum]))
            array_of_highest_x_values.append(max(array_of_x_values_array[spectrum]))
            average_energy_per_pixel= (array_of_highest_x_values[spectrum] - array_of_lowest_x_values[spectrum])/len(array_of_intensity_arrays[spectrum])
            sum_of_average_energy_per_pixel +=average_energy_per_pixel
            if array_of_lowest_x_values[spectrum] <= total_lowest_x_value:
                total_lowest_x_value= array_of_lowest_x_values[spectrum]      
            if array_of_highest_x_values[spectrum] >= total_highest_x_value:
                total_highest_x_value= array_of_highest_x_values[spectrum]
            elif spectrum == 0:
                total_lowest_x_value= array_of_lowest_x_values[spectrum]
                total_highest_x_value= array_of_highest_x_values[spectrum]

        exact_energy_per_channel_slope= sum_of_average_energy_per_pixel/len(iteratable_file_number_array)
        half_of_exact_energy_per_channel_slope= exact_energy_per_channel_slope/2
        array_of_intensity_arrays_list = array_of_intensity_arrays.tolist()
        for spectrum in range(len(iteratable_file_number_array)):
            condition= True
            while condition:
                if total_lowest_x_value <= array_of_x_values_array[spectrum][0] - half_of_exact_energy_per_channel_slope:
                    array_of_x_values_array[spectrum]= np.insert(array_of_x_values_array[spectrum], 0, (array_of_x_values_array[spectrum][0] - exact_energy_per_channel_slope))
                    array_of_intensity_arrays_list[spectrum].insert(0, 0)
                    #array_of_x_values_array[spectrum].insert(0, (array_of_lowest_x_values[spectrum] - exact_energy_per_channel_slope))
                    #array_of_intensity_arrays[spectrum].insert(0, 0)
                else:
                    condition=False
            
            condition= True
            while condition:
                if total_highest_x_value >= array_of_x_values_array[spectrum][-1] + half_of_exact_energy_per_channel_slope:
                    array_of_x_values_array[spectrum]= np.append(array_of_x_values_array[spectrum], array_of_x_values_array[spectrum][-1] + exact_energy_per_channel_slope)
                    array_of_intensity_arrays_list[spectrum].append(0)
                    #array_of_x_values_array[spectrum].append(array_of_highest_x_values[spectrum] + exact_energy_per_channel_slope)
                    #array_of_intensity_arrays[spectrum].append(0)
                else:
                    condition=False
        
        lenght_of_longest_x_values_array=0
        for spectrum in range(len(iteratable_file_number_array)):
            if len(array_of_x_values_array[spectrum]) > lenght_of_longest_x_values_array:
                lenght_of_longest_x_values_array= len(array_of_x_values_array[spectrum])
        for spectrum in range(len(iteratable_file_number_array)):
            if len(array_of_x_values_array[spectrum])< lenght_of_longest_x_values_array:
                array_of_x_values_array[spectrum]= np.append(array_of_x_values_array[spectrum], array_of_x_values_array[spectrum][-1] + exact_energy_per_channel_slope)
                array_of_intensity_arrays_list[spectrum].append(0)
            
        array_of_intensity_arrays = np.array(array_of_intensity_arrays_list)

        sum_of_lowest_x_values= 0
        sum_of_highest_x_values= 0
        for spectrum in range(len(iteratable_file_number_array)):
            sum_of_lowest_x_values+= array_of_lowest_x_values[spectrum]
            sum_of_highest_x_values+= array_of_highest_x_values[spectrum]
        average_lowest_x_value= sum_of_lowest_x_values/len(iteratable_file_number_array)
        average_highest_x_value= sum_of_highest_x_values/len(iteratable_file_number_array)

        final_x_values_array= np.linspace(total_lowest_x_value, total_highest_x_value, len(array_of_intensity_arrays[0]))
        
        return final_x_values_array, exact_energy_per_channel_slope, array_of_intensity_arrays

    def weighted_linear_fit(self, x, y, weights):
        popt, pcov = curve_fit(self.linear_function, x, y, sigma=(np.argmax(weights)/weights))
        return popt

    def linear_function(self, x, a, b):
        return a * x + b

    def try_to_plot(self, parameters, extra_plot_parameters):
        try:
            self.plot_inputted_data(parameters, extra_plot_parameters)
        except (IndexError, ValueError):
            print("Plot exception happened")
            self.plot_only_raw_data(parameters)


    def get_y_value_arrays_and_nested_arrays_of_intensity_and_x_arrays(self, parameters):
        nested_arrays_of_x_value_arrays=[]
        array_of_y_value_arrays=[]
        nested_arrays_of_intensity_arrays= []
        for map_index in range(int(parameters["input_number_of_complete_file_names"])):
            complete_file_location= create_complete_file_location_for_treated_data.create_complete_file_location_for_treated_data(parameters["input_file_project_folder"], self.parameters["input_complete_file_name_array"][map_index])
            array_of_x_value_arrays, y_values_array, array_of_intensity_arrays = get_treated_rixs_data_script.get_treated_rixs_data(complete_file_location)
            #array_of_x_value_arrays = array_of_x_value_arrays.tolist()
            nested_arrays_of_x_value_arrays.append(array_of_x_value_arrays)
            array_of_y_value_arrays.append(y_values_array)
            #array_of_intensity_arrays= array_of_intensity_arrays.tolist()
            nested_arrays_of_intensity_arrays.append(array_of_intensity_arrays)

        #Changed these three to dtype=object from dtype=float to handle different shapes of arrays (like if one map has more spectra than the other)
        nested_arrays_of_x_value_arrays = np.asarray(nested_arrays_of_x_value_arrays, dtype=object)
        nested_arrays_of_intensity_arrays = np.asarray(nested_arrays_of_intensity_arrays, dtype=object)
        array_of_y_value_arrays = np.asarray(array_of_y_value_arrays, dtype=object)

        return nested_arrays_of_x_value_arrays, array_of_y_value_arrays, nested_arrays_of_intensity_arrays

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
            #channels_above_and_below_elastic_to_fit = np.abs(previous_elastic_peak_channel_center - np.abs(array_of_x_value_arrays[spectra_index] - energy_above_and_below_elastic_peak_to_fit_elastic_peak).argmin() )
           
            #print(np.abs(array_of_x_value_arrays[spectra_index] - 0).argmin())

            condition = True
            while condition:
                peak_channel_center = 0
                peak_energy_center = 0
                sum_of_intensity_weight = 0
                
                channels_above_elastic_to_fit = np.abs(previous_elastic_peak_channel_center - np.abs(array_of_x_value_arrays[spectra_index] - energy_above_and_below_elastic_peak_to_fit_elastic_peak).argmin() )
                channels_below_elastic_to_fit = np.abs(previous_elastic_peak_channel_center - np.abs(array_of_x_value_arrays[spectra_index] + energy_above_and_below_elastic_peak_to_fit_elastic_peak).argmin() )
                n = len(array_of_intensity_arrays[spectra_index])
                for channel in range(max(0, previous_elastic_peak_channel_center - channels_below_elastic_to_fit), min(n, previous_elastic_peak_channel_center + channels_above_elastic_to_fit + 1)):
                    peak_energy_center+= ((array_of_intensity_arrays[spectra_index][channel]) ** 2 ) * array_of_x_value_arrays[spectra_index][channel]
                    sum_of_intensity_weight+= (array_of_intensity_arrays[spectra_index][channel]) ** 2
                
                peak_energy_center = peak_energy_center/sum_of_intensity_weight
                #intensity_weights_array[array_index]=sum_of_intensity_weight
                peak_channel_center = np.abs(array_of_x_value_arrays[spectra_index] - peak_energy_center).argmin()
                change_in_peak_channel_center = previous_elastic_peak_channel_center - peak_channel_center
                
                previous_elastic_peak_channel_center = round(peak_channel_center)
                #if abs(array_of_x_value_arrays[spectra_index][previous_elastic_peak_channel_center]) <= elastic_energy_mismatch_tolerance:
                #    array_of_x_value_arrays[spectra_index] = array_of_x_value_arrays[spectra_index] - peak_center_in_energy
                if abs(change_in_peak_channel_center) <= 0.5:
                    energy_shift = peak_energy_center
                    array_of_x_value_arrays[spectra_index] = array_of_x_value_arrays[spectra_index] - energy_shift
                    #array_of_x_value_arrays[spectra_index] = array_of_x_value_arrays[spectra_index] - array_of_x_value_arrays[spectra_index][previous_elastic_peak_channel_center]
                    condition = False
            
        if is_original_x_values_energy_loss == False:
            for spectra_index in range(len(array_of_intensity_arrays)):
                array_of_x_value_arrays[spectra_index] = array_of_x_value_arrays[spectra_index] + incoming_energy_array[spectra_index]
        

        #for spectra_index in range(len(array_of_intensity_arrays)):
        #    array_of_x_value_arrays[spectra_index] = array_of_x_value_arrays[spectra_index] + (incoming_energy_array[spectra_index] - array_of_x_value_arrays[spectra_index][elastic_peak_center_array[spectra_index]])
        
        return array_of_x_value_arrays

    def move_elastic_peak_center_to_correct_energy_with_gaussian(self, array_of_intensity_arrays, incoming_energy_array, array_of_x_value_arrays):
        #elastic_peak_center_array = np.asarray(elastic_peak_center_array)
        is_original_x_values_energy_loss = self.nested_array_contains_negative_floats(array_of_x_value_arrays)
        
        if is_original_x_values_energy_loss == False:
            for spectra_index in range(len(array_of_intensity_arrays)):
                array_of_x_value_arrays[spectra_index] = array_of_x_value_arrays[spectra_index] - incoming_energy_array[spectra_index]
        
        energy_above_and_below_elastic_peak_to_fit_elastic_peak = float(self.parameters["energy_above_and_below_to_calculate_elastic_peak_weights"])

        #This first alignment is not really necessary.
        for spectra_index in range(len(array_of_intensity_arrays)):
            previous_elastic_peak_channel_center = np.abs(array_of_x_value_arrays[spectra_index] - 0).argmin()
            #channels_above_and_below_elastic_to_fit = np.abs(previous_elastic_peak_channel_center - np.abs(array_of_x_value_arrays[spectra_index] - energy_above_and_below_elastic_peak_to_fit_elastic_peak).argmin() )
            #print(np.abs(array_of_x_value_arrays[spectra_index] - 0).argmin())

            condition = True
            while condition:
                peak_channel_center = 0
                peak_energy_center = 0
                sum_of_intensity_weight = 0
                
                channels_above_elastic_to_fit = np.abs(previous_elastic_peak_channel_center - np.abs(array_of_x_value_arrays[spectra_index] - energy_above_and_below_elastic_peak_to_fit_elastic_peak).argmin() )
                channels_below_elastic_to_fit = np.abs(previous_elastic_peak_channel_center - np.abs(array_of_x_value_arrays[spectra_index] + energy_above_and_below_elastic_peak_to_fit_elastic_peak).argmin() )
                n = len(array_of_intensity_arrays[spectra_index])
                for channel in range(max(0, previous_elastic_peak_channel_center - channels_below_elastic_to_fit), min(n, previous_elastic_peak_channel_center + channels_above_elastic_to_fit + 1)):
                    peak_energy_center+= ((array_of_intensity_arrays[spectra_index][channel]) ** 2 ) * array_of_x_value_arrays[spectra_index][channel]
                    sum_of_intensity_weight+= (array_of_intensity_arrays[spectra_index][channel]) ** 2
                
                peak_energy_center = peak_energy_center/sum_of_intensity_weight
                #intensity_weights_array[array_index]=sum_of_intensity_weight
                peak_channel_center = np.abs(array_of_x_value_arrays[spectra_index] - peak_energy_center).argmin()
                change_in_peak_channel_center = previous_elastic_peak_channel_center - peak_channel_center
                
                previous_elastic_peak_channel_center = round(peak_channel_center)
                #if abs(array_of_x_value_arrays[spectra_index][previous_elastic_peak_channel_center]) <= elastic_energy_mismatch_tolerance:
                #    array_of_x_value_arrays[spectra_index] = array_of_x_value_arrays[spectra_index] - peak_center_in_energy
                energy_shift = peak_energy_center
                array_of_x_value_arrays[spectra_index] = array_of_x_value_arrays[spectra_index] - energy_shift
                if abs(change_in_peak_channel_center) <= 0.5:
                    #energy_shift = peak_energy_center
                    #array_of_x_value_arrays[spectra_index] = array_of_x_value_arrays[spectra_index] - energy_shift
                    #array_of_x_value_arrays[spectra_index] = array_of_x_value_arrays[spectra_index] - array_of_x_value_arrays[spectra_index][previous_elastic_peak_channel_center]
                    condition = False
        
        #aligning the elastic peaks again with the weighted intenisty again but with a smaller channel range for finer adjustment:
        for spectra_index in range(len(array_of_intensity_arrays)):
            previous_elastic_peak_channel_center = np.abs(array_of_x_value_arrays[spectra_index] - 0).argmin()
            energy_above_and_below_elastic_peak_to_fit_elastic_peak = float(self.parameters["energy_above_and_below_to_calculate_elastic_peak_weights"])
            channels_above_elastic_to_fit = np.abs(previous_elastic_peak_channel_center - np.abs(array_of_x_value_arrays[spectra_index] - energy_above_and_below_elastic_peak_to_fit_elastic_peak).argmin())
            channels_below_elastic_to_fit = np.abs(previous_elastic_peak_channel_center - np.abs(array_of_x_value_arrays[spectra_index] + energy_above_and_below_elastic_peak_to_fit_elastic_peak).argmin())

            #Get half_channel_width_of_elastic_peak first from the maximum peak intenisty to avoid errors.
            previous_elastic_peak_channel_center = previous_elastic_peak_channel_center - channels_above_elastic_to_fit + np.abs(array_of_intensity_arrays[spectra_index][previous_elastic_peak_channel_center - channels_above_elastic_to_fit : previous_elastic_peak_channel_center + channels_above_elastic_to_fit + 1] - np.max(array_of_intensity_arrays[spectra_index][previous_elastic_peak_channel_center - channels_above_elastic_to_fit : previous_elastic_peak_channel_center + channels_above_elastic_to_fit + 1])).argmin()

            energy_above_and_below_elastic_peak_to_fit_elastic_peak = float(self.parameters["energy_above_and_below_to_calculate_elastic_peak_weights"])
            channels_above_elastic_to_fit = np.abs(previous_elastic_peak_channel_center - np.abs(array_of_x_value_arrays[spectra_index] - energy_above_and_below_elastic_peak_to_fit_elastic_peak).argmin())
            channels_below_elastic_to_fit = np.abs(previous_elastic_peak_channel_center - np.abs(array_of_x_value_arrays[spectra_index] + energy_above_and_below_elastic_peak_to_fit_elastic_peak).argmin())
            rough_half_elastic_peak_intenisty = (np.max(array_of_intensity_arrays[spectra_index][previous_elastic_peak_channel_center - channels_above_elastic_to_fit : previous_elastic_peak_channel_center + channels_above_elastic_to_fit + 1]) - np.nanmin(array_of_intensity_arrays[spectra_index][previous_elastic_peak_channel_center: previous_elastic_peak_channel_center + 10 * channels_above_elastic_to_fit + 1 ])) / 2
            
            half_channel_width_of_elastic_peak = np.abs(array_of_intensity_arrays[spectra_index][previous_elastic_peak_channel_center : ] - rough_half_elastic_peak_intenisty).argmin()
            if half_channel_width_of_elastic_peak <= 1:
                half_channel_width_of_elastic_peak = 2
            channel_of_half_elastic_peak_width_above_elastic = previous_elastic_peak_channel_center + half_channel_width_of_elastic_peak
            half_energy_width_of_elastic_peak = array_of_x_value_arrays[spectra_index][channel_of_half_elastic_peak_width_above_elastic] - array_of_x_value_arrays[spectra_index][previous_elastic_peak_channel_center]
            
            condition = True
            iteration_count = 0
            while condition:
                peak_channel_center = 0
                peak_energy_center = 0
                sum_of_intensity_weight = 0

                channels_above_elastic_to_fit = np.abs(previous_elastic_peak_channel_center - np.abs(array_of_x_value_arrays[spectra_index] - half_energy_width_of_elastic_peak).argmin())
                channels_below_elastic_to_fit = np.abs(previous_elastic_peak_channel_center - np.abs(array_of_x_value_arrays[spectra_index] + half_energy_width_of_elastic_peak).argmin())
                n = len(array_of_intensity_arrays[spectra_index])
                for channel in range(max(0, previous_elastic_peak_channel_center - channels_below_elastic_to_fit), min(n, previous_elastic_peak_channel_center + channels_above_elastic_to_fit + 1)):
                    peak_energy_center += ((array_of_intensity_arrays[spectra_index][channel]) ** 2) * array_of_x_value_arrays[spectra_index][channel]
                    sum_of_intensity_weight += (array_of_intensity_arrays[spectra_index][channel]) ** 2

                peak_energy_center = peak_energy_center / sum_of_intensity_weight
                peak_channel_center = np.abs(array_of_x_value_arrays[spectra_index] - peak_energy_center).argmin()
                change_in_peak_channel_center = previous_elastic_peak_channel_center - peak_channel_center

                previous_elastic_peak_channel_center = round(peak_channel_center)
                energy_shift = peak_energy_center
                array_of_x_value_arrays[spectra_index] = array_of_x_value_arrays[spectra_index] - energy_shift

                half_channel_width_of_elastic_peak = np.abs(array_of_intensity_arrays[spectra_index][previous_elastic_peak_channel_center:] - rough_half_elastic_peak_intenisty).argmin()
                if half_channel_width_of_elastic_peak <= 1:
                    half_channel_width_of_elastic_peak = 2
                channel_of_half_elastic_peak_width_above_elastic = previous_elastic_peak_channel_center + half_channel_width_of_elastic_peak
                half_energy_width_of_elastic_peak = array_of_x_value_arrays[spectra_index][channel_of_half_elastic_peak_width_above_elastic] - array_of_x_value_arrays[spectra_index][previous_elastic_peak_channel_center]

                iteration_count += 1
                if abs(change_in_peak_channel_center) <= 0.5 or iteration_count >= 100:
                    condition = False

        #Gaussian fit here now that the spectra are somewhat aligned:
        for spectra_index in range(len(array_of_intensity_arrays)):
            try:
                previous_elastic_peak_channel_center = np.abs(array_of_x_value_arrays[spectra_index] - 0).argmin()
                #channels_above_and_below_elastic_to_fit = np.abs(previous_elastic_peak_channel_center - np.abs(array_of_x_value_arrays[spectra_index] - energy_above_and_below_elastic_peak_to_fit_elastic_peak).argmin() )
            
                #print(np.abs(array_of_x_value_arrays[spectra_index] - 0).argmin())

                
                #channels_above_elastic_to_fit = np.abs(previous_elastic_peak_channel_center - np.abs(array_of_x_value_arrays[spectra_index] - energy_above_and_below_elastic_peak_to_fit_elastic_peak).argmin() )
                #channels_below_elastic_to_fit = np.abs(previous_elastic_peak_channel_center - np.abs(array_of_x_value_arrays[spectra_index] + energy_above_and_below_elastic_peak_to_fit_elastic_peak).argmin() )
                #channels_above_elastic_to_fit = np.abs(previous_elastic_peak_channel_center - np.abs(array_of_x_value_arrays[spectra_index] - 0.2).argmin() )
                #channels_below_elastic_to_fit = np.abs(previous_elastic_peak_channel_center - np.abs(array_of_x_value_arrays[spectra_index] + 0.01).argmin() )
                
                #x_values_gaussian= array_of_x_value_arrays[spectra_index][previous_elastic_peak_channel_center - channels_below_elastic_to_fit : previous_elastic_peak_channel_center + channels_above_elastic_to_fit + 1]
                #y_values_gaussian= array_of_intensity_arrays[spectra_index][previous_elastic_peak_channel_center - channels_below_elastic_to_fit : previous_elastic_peak_channel_center + channels_above_elastic_to_fit + 1]
                #mu_guess = x_values_gaussian[channels_below_elastic_to_fit]
                energy_above_and_below_elastic_peak_to_fit_elastic_peak = float(self.parameters["energy_above_and_below_to_calculate_elastic_peak_weights"])
                channels_above_elastic_to_fit = np.abs(previous_elastic_peak_channel_center - np.abs(array_of_x_value_arrays[spectra_index] - energy_above_and_below_elastic_peak_to_fit_elastic_peak).argmin() )
                channels_below_elastic_to_fit = np.abs(previous_elastic_peak_channel_center - np.abs(array_of_x_value_arrays[spectra_index] + energy_above_and_below_elastic_peak_to_fit_elastic_peak).argmin() )
                rough_half_elastic_peak_intenisty = (np.max(array_of_intensity_arrays[spectra_index][previous_elastic_peak_channel_center - channels_above_elastic_to_fit : previous_elastic_peak_channel_center + channels_above_elastic_to_fit + 1]) - np.nanmin(array_of_intensity_arrays[spectra_index][previous_elastic_peak_channel_center: previous_elastic_peak_channel_center + channels_above_elastic_to_fit + 1 ])) / 2
                #channel_of_elastic_peak_maximum = previous_elastic_peak_channel_center - channels_above_elastic_to_fit + np.abs(array_of_intensity_arrays[spectra_index][previous_elastic_peak_channel_center - channels_above_elastic_to_fit : previous_elastic_peak_channel_center + channels_above_elastic_to_fit + 1] - np.max(array_of_intensity_arrays[spectra_index][previous_elastic_peak_channel_center - channels_above_elastic_to_fit : previous_elastic_peak_channel_center + channels_above_elastic_to_fit + 1])).argmin()
                half_channel_width_of_elastic_peak = np.abs(array_of_intensity_arrays[spectra_index][previous_elastic_peak_channel_center : ] - rough_half_elastic_peak_intenisty).argmin()
                if half_channel_width_of_elastic_peak <= 0:
                    half_channel_width_of_elastic_peak = 1
                channel_of_half_elastic_peak_width_above_elastic = previous_elastic_peak_channel_center + half_channel_width_of_elastic_peak
                half_energy_width_of_elastic_peak = array_of_x_value_arrays[spectra_index][channel_of_half_elastic_peak_width_above_elastic] - array_of_x_value_arrays[spectra_index][previous_elastic_peak_channel_center]
                FWHM_energy = 2 * half_energy_width_of_elastic_peak
                quarter_energy_width_of_elastic_peak = half_energy_width_of_elastic_peak / 2

                gaussian_fit_channel_start = np.abs(array_of_x_value_arrays[spectra_index] + quarter_energy_width_of_elastic_peak * 1.05).argmin() #added factor 1.05 to make avoid it choosing the max value as the starting point if the elastic peak consists of 3 datapoints
                gaussian_fit_channel_end = 20 * half_channel_width_of_elastic_peak + previous_elastic_peak_channel_center
                x_values_gaussian = array_of_x_value_arrays[spectra_index][gaussian_fit_channel_start : gaussian_fit_channel_end + 1]
                y_values_gaussian = array_of_intensity_arrays[spectra_index][gaussian_fit_channel_start : gaussian_fit_channel_end + 1]
                sigma_guess = FWHM_energy / 2.35482 # Same as FWHM_energy / (2 * np.sqrt(2 * np.log(2)))
                mu_guess = array_of_x_value_arrays[spectra_index][previous_elastic_peak_channel_center]
                offset_guess = np.mean(array_of_intensity_arrays[spectra_index][15 * half_channel_width_of_elastic_peak + previous_elastic_peak_channel_center : gaussian_fit_channel_end + 1])
                #sigma_guess = (x_values_gaussian[0] - x_values_gaussian[-1]) / 8
                A_guess = array_of_intensity_arrays[spectra_index][previous_elastic_peak_channel_center]
                initial_guesses = [A_guess, mu_guess, sigma_guess, offset_guess]
                gaussian_parameters, covariance_matrix = curve_fit(self.gaussian, x_values_gaussian, y_values_gaussian, p0=initial_guesses)
                standard_deviation_of_fitted_parameters = np.sqrt(np.diag(covariance_matrix))
                #for name, val, err in zip(['Gaussain max intenisty','Gaussain mean value','Gaussian sigma','Gaussain offset'], gaussian_parameters, standard_deviation_of_fitted_parameters):
                #    print(f"{name} = {val:.8f} ± {err:.8f}")
                print("Spectra ", spectra_index, " Gaussian mean value:", gaussian_parameters[1], " ± ", standard_deviation_of_fitted_parameters[1])
                
                if False:
                    y_fit = self.gaussian(x_values_gaussian, *gaussian_parameters)
                    #plt.close('all')
                    plt.figure(figsize=(6,4))
                    plt.plot(x_values_gaussian, y_values_gaussian, 'k.', alpha=0.5, label='Raw spectrum')
                    plt.plot(x_values_gaussian, y_fit, 'r-', linewidth=2, label='Gaussian fit')

                    # Optional: show 1σ confidence band via linear error propagation
                    # For small errors, you can approximate the band by varying each parameter by ±perr
                    ys_pp = self.gaussian(x_values_gaussian, *(gaussian_parameters + standard_deviation_of_fitted_parameters))
                    ys_mm = self.gaussian(x_values_gaussian, *(gaussian_parameters - standard_deviation_of_fitted_parameters))
                    plt.fill_between(x_values_gaussian, ys_mm, ys_pp, color='r', alpha=0.2,
                                    label=r'±1σ parameter band')

                    # Labels & legend
                    plt.xlabel('Energy Loss (eV)')
                    plt.ylabel('Intensity (arb. units)')
                    plt.title('Gaussian Fit: '
                            f'A={gaussian_parameters[0]:.3f}±{standard_deviation_of_fitted_parameters[0]:.3f}, '
                            f'μ={gaussian_parameters[1]:.4f}±{standard_deviation_of_fitted_parameters[1]:.4f} eV, '
                            f'σ={gaussian_parameters[2]:.4f}±{standard_deviation_of_fitted_parameters[2]:.4f} eV')
                    plt.legend(loc='best', fontsize=8)
                    plt.tight_layout()
                    plt.ion()
                #fine_x_axis_energy_loss = np.linspace(array_of_x_value_arrays[spectra_index][previous_elastic_peak_channel_center - channels_below_elastic_to_fit], array_of_x_value_arrays[spectra_index][previous_elastic_peak_channel_center + channels_above_elastic_to_fit + 1], 10000)
                #gaussian_fitted_y_values= self.gaussian(fine_x_axis_energy_loss, *gaussian_parameters)
                #peak_channel_center= previous_elastic_peak_channel_center - channels_below_elastic_to_fit + np.argmax(gaussian_fitted_y_values)
                energy_shift = gaussian_parameters[1]
                array_of_x_value_arrays[spectra_index] = array_of_x_value_arrays[spectra_index] - energy_shift
                #print("energy_shift = ", energy_shift)
            except RuntimeError:
                print("Gaussian fit could not be made for spectra: ", spectra_index)

        if is_original_x_values_energy_loss == False:
            for spectra_index in range(len(array_of_intensity_arrays)):
                array_of_x_value_arrays[spectra_index] = array_of_x_value_arrays[spectra_index] + incoming_energy_array[spectra_index]
        

        #for spectra_index in range(len(array_of_intensity_arrays)):
        #    array_of_x_value_arrays[spectra_index] = array_of_x_value_arrays[spectra_index] + (incoming_energy_array[spectra_index] - array_of_x_value_arrays[spectra_index][elastic_peak_center_array[spectra_index]])
        
        return array_of_x_value_arrays

    def align_and_combine_maps(self, parameters, array_of_y_values_arrays, nested_arrays_of_x_values_arrays, nested_arrays_of_intensity_arrays):
        
        if self.parameters["is_automatically_adjust_peak_to_correct_energy"]:
            for map_index in range(len(nested_arrays_of_intensity_arrays)):
                nested_arrays_of_x_values_arrays[map_index] = self.move_elastic_peak_center_to_correct_energy_with_gaussian(nested_arrays_of_intensity_arrays[map_index], array_of_y_values_arrays[map_index], nested_arrays_of_x_values_arrays[map_index])


        #Flatten the nested arrays. So an array of 10 elements consisting of 15 lists, the flattened version will be all lists in a 10*15 long list. So it basically stacks all maps on top of each other in a long list.
        array_of_y_values_arrays = [inner for outer in array_of_y_values_arrays for inner in outer]
        array_of_x_value_arrays = [inner for outer in nested_arrays_of_x_values_arrays for inner in outer]
        array_of_intensity_arrays = [inner for outer in nested_arrays_of_intensity_arrays for inner in outer]

        energy_mismatch_tolerance = float(self.parameters["energy_mismatch_tolerance"])

        unique_excitation_energies_list = []
        temporary_incoming_energy = np.asarray(array_of_y_values_arrays, dtype=float)

        condition = True
        while condition:
            if len(temporary_incoming_energy) <= 1:
                condition = False

            excitation_energy = temporary_incoming_energy[0]
            unique_excitation_energies_list.append(excitation_energy)

            condition_2 = True
            while condition_2 and len(temporary_incoming_energy) > 0:
                index_of_same_energy = np.abs(
                    temporary_incoming_energy - excitation_energy
                ).argmin()

                if np.abs(temporary_incoming_energy[index_of_same_energy] - excitation_energy) < energy_mismatch_tolerance:
                    temporary_incoming_energy = np.delete(temporary_incoming_energy, index_of_same_energy)

                    if len(temporary_incoming_energy) == 0:
                        condition_2 = False
                        condition = False
                else:
                    condition_2 = False

        #This for loop is for adding the intensities
        array_of_combined_intensity_arrays = []
        final_array_of_x_values_arrays = []
        for energy_index, excitation_energy in enumerate(unique_excitation_energies_list):
            indices_of_same_energy_array = [i for i, y in enumerate(array_of_y_values_arrays) if np.abs(y - excitation_energy) < energy_mismatch_tolerance]
            #combined_intensity_array = np.zeros(len(array_of_x_value_arrays[energy_index]), dtype=object)
            array_of_x_value_arrays_to_combine = []
            for spectra_index in indices_of_same_energy_array:
                array_of_x_value_arrays_to_combine.append(array_of_x_value_arrays[spectra_index])

            combined_x_values_array = np.asarray(list(heapq.merge(*array_of_x_value_arrays_to_combine)))
            combined_intensity_array = np.zeros(len(combined_x_values_array), dtype=object)
            for spectra_index in indices_of_same_energy_array:
                interpolating_function = interp1d(array_of_x_value_arrays[spectra_index], array_of_intensity_arrays[spectra_index], kind='linear', fill_value="extrapolate")
                combined_intensity_array += interpolating_function(combined_x_values_array)
            
            combined_intensity_array = np.array(combined_intensity_array)
            combined_intensity_array = combined_intensity_array /len(indices_of_same_energy_array) #To normalize the spectra incase some spectra are the combination of 2 spectra while others are of 3 or more.
            final_array_of_x_values_arrays.append(combined_x_values_array)
            array_of_combined_intensity_arrays.append(combined_intensity_array)

        final_array_of_x_values_arrays = np.asarray(final_array_of_x_values_arrays, dtype=object)
        unique_excitation_energies_list = np.asarray(unique_excitation_energies_list, dtype=float)
        array_of_combined_intensity_arrays = np.asarray(array_of_combined_intensity_arrays, dtype=object)
        
        #intensity = np.zeros(len(array_of_intensity_arrays[0]))
        #for i in range(4):
        #    intensity += array_of_intensity_arrays[i + 4]
        #plt.plot(array_of_x_value_arrays[4], intensity, linestyle='-', label='Original data')
        #plt.plot(final_array_of_x_values_arrays[1], array_of_combined_intensity_arrays[1], linestyle='-', label='Interpolated data')
        #plt.legend()
        #plt.show()

        return final_array_of_x_values_arrays, unique_excitation_energies_list, array_of_combined_intensity_arrays


    def align_and_combine_maps_with_different_number_of_lines(self, parameters, array_of_y_values_arrays, array_of_x_values_arrays, nested_arrays_of_intensity_arrays):
        array_of_lowest_x_values= []
        array_of_highest_x_values= []
        array_of_lowest_y_values= []
        array_of_highest_y_values= []
        array_of_y_value_difference_at_start= []
        array_of_y_value_difference_at_end= []     
        sum_of_average_energy_per_pixel= 0

        for map_index in range(int(parameters["input_number_of_complete_file_names"])):
            array_of_lowest_x_values.append(min(array_of_x_values_arrays[map_index]))
            array_of_highest_x_values.append(max(array_of_x_values_arrays[map_index]))
            #array_of_lowest_y_values.append(min(array_of_y_values_arrays[map_index]))
            #array_of_highest_y_values.append(max(array_of_y_values_arrays[map_index]))
            
            average_energy_per_pixel= (array_of_highest_x_values[map_index] - array_of_lowest_x_values[map_index])/len(array_of_x_values_arrays[map_index])
            sum_of_average_energy_per_pixel +=average_energy_per_pixel
            
            #y_value_difference_at_start= array_of_y_values_arrays[map_index][0] - array_of_y_values_arrays[map_index][1]
            #array_of_y_value_difference_at_start += y_value_difference_at_start
            #y_value_difference_at_end= array_of_y_values_arrays[map_index][-1] - array_of_y_values_arrays[map_index][-2]
            #array_of_y_value_difference_at_end += y_value_difference_at_end

        total_lowest_x_value= min(array_of_lowest_x_values)
        total_highest_x_value= max(array_of_highest_x_values)

        #total_lowest_y_value= min(array_of_lowest_y_values)
        #map_index_of_lowest_y_value= array_of_lowest_y_values.index(total_lowest_y_value)
        #total_highest_y_value= max(array_of_highest_y_values)
        #map_index_of_highest_y_value= array_of_highest_y_values.index(total_highest_y_value)


        exact_energy_per_channel_slope= sum_of_average_energy_per_pixel/int(parameters["input_number_of_complete_file_names"])
        half_of_exact_energy_per_channel_slope= exact_energy_per_channel_slope/2
        for map_index in range(int(parameters["input_number_of_complete_file_names"])):
            condition= True
            while condition:
                if total_lowest_x_value <= array_of_x_values_arrays[map_index][0] - half_of_exact_energy_per_channel_slope:
                    array_of_x_values_arrays[map_index]= np.insert(array_of_x_values_arrays[map_index], 0, (array_of_x_values_arrays[map_index][0] - exact_energy_per_channel_slope))
                    for spectrum in range(len(array_of_y_values_arrays[map_index])):
                        #nested_arrays_of_intensity_arrays[map_index][spectrum].insert(0, 0)
                        nested_arrays_of_intensity_arrays[map_index][spectrum]= np.insert(nested_arrays_of_intensity_arrays[map_index][spectrum], 0, 0)
                    #array_of_x_values_array[spectrum].insert(0, (array_of_lowest_x_values[spectrum] - exact_energy_per_channel_slope))
                    #array_of_intensity_arrays[spectrum].insert(0, 0)
                else:
                    condition=False
            
            condition= True
            while condition:
                if total_highest_x_value >= array_of_x_values_arrays[map_index][-1] + half_of_exact_energy_per_channel_slope:
                    array_of_x_values_arrays[map_index]= np.append(array_of_x_values_arrays[map_index], array_of_x_values_arrays[map_index][-1] + exact_energy_per_channel_slope)
                    for spectrum in range(len(array_of_y_values_arrays[map_index])):
                        #nested_arrays_of_intensity_arrays[map_index][spectrum].append(0)
                        nested_arrays_of_intensity_arrays[map_index][spectrum]= np.append(nested_arrays_of_intensity_arrays[map_index][spectrum], 0)
                    #array_of_x_values_array[spectrum].append(array_of_highest_x_values[spectrum] + exact_energy_per_channel_slope)
                    #array_of_intensity_arrays[spectrum].append(0)
                else:
                    condition=False
            
            
        lenght_of_longest_x_values_array=0
        for map_index in range(int(parameters["input_number_of_complete_file_names"])):
            if len(array_of_x_values_arrays[map_index]) > lenght_of_longest_x_values_array:
                lenght_of_longest_x_values_array= len(array_of_x_values_arrays[map_index])
        for map_index in range(int(parameters["input_number_of_complete_file_names"])):
            if len(array_of_x_values_arrays[map_index])< lenght_of_longest_x_values_array:
                array_of_x_values_arrays[map_index]= np.append(array_of_x_values_arrays[map_index], array_of_x_values_arrays[map_index][-1] + exact_energy_per_channel_slope)
                for spectrum in range(len(array_of_y_values_arrays[map_index])):
                    nested_arrays_of_intensity_arrays[map_index][spectrum]= np.append(nested_arrays_of_intensity_arrays[map_index][spectrum], 0)
        
        #I am now checking the lenght of the maps, but not the extreme values of them... Maybe I need to see if there is a mismatch with like a 0.05 eV allowens for mismatch?

        if False: #Added this if statement since we know there is a mismatch in the number of lines per map and then in the number of incident energies.
            lenght_of_longest_y_values_array=0
            intensity_array_of_zeros_to_append= [0]*lenght_of_longest_x_values_array
            for map_index in range(int(parameters["input_number_of_complete_file_names"])):
                if len(array_of_y_values_arrays[map_index]) > lenght_of_longest_y_values_array:
                    lenght_of_longest_y_values_array= len(array_of_y_values_arrays[map_index])
            for map_index in range(int(parameters["input_number_of_complete_file_names"])):
                if len(array_of_y_values_arrays[map_index])< lenght_of_longest_y_values_array:
                    condition= True
                    while condition:
                        if total_lowest_y_value <= array_of_y_values_arrays[map_index][0] - array_of_y_value_difference_at_start[map_index_of_lowest_y_value]/2:
                            array_of_y_values_arrays[map_index]= np.insert(array_of_y_values_arrays[map_index], 0, (array_of_y_values_arrays[map_index][0] - array_of_y_value_difference_at_start[map_index_of_lowest_y_value]))
                            #nested_arrays_of_intensity_arrays[map_index].insert(0, intensity_array_of_zeros_to_append)
                            #nested_arrays_of_intensity_arrays[map_index][spectrum]= np.insert(nested_arrays_of_intensity_arrays[map_index][spectrum], 0, intensity_array_of_zeros_to_append)
                            nested_arrays_of_intensity_arrays[map_index]= np.insert(nested_arrays_of_intensity_arrays[map_index], 0, intensity_array_of_zeros_to_append)

                            #array_of_x_values_array[spectrum].insert(0, (array_of_lowest_x_values[spectrum] - exact_energy_per_channel_slope))
                            #array_of_intensity_arrays[spectrum].insert(0, 0)
                        else:
                            condition=False
                    
                    condition= True
                    while condition:
                        if total_highest_y_value >= array_of_y_values_arrays[map_index][-1] + array_of_y_value_difference_at_end[map_index_of_highest_y_value]/2:
                            array_of_y_values_arrays[map_index]= np.append(array_of_y_values_arrays[map_index], array_of_y_values_arrays[map_index][-1] + array_of_y_value_difference_at_end[map_index_of_highest_y_value])
                            #nested_arrays_of_intensity_arrays[map_index][spectrum].append(intensity_array_of_zeros_to_append)
                            nested_arrays_of_intensity_arrays[map_index]= np.append(nested_arrays_of_intensity_arrays[map_index], intensity_array_of_zeros_to_append)
                            #array_of_x_values_array[spectrum].append(array_of_highest_x_values[spectrum] + exact_energy_per_channel_slope)
                            #array_of_intensity_arrays[spectrum].append(0)
                        else:
                            condition=False
                
                
                #array_of_y_values_arrays[map_index]= np.append(array_of_y_values_arrays[map_index], array_of_y_values_arrays[map_index][-1] + exact_energy_per_channel_slope)
                #nested_arrays_of_intensity_arrays[map_index].append(0)
        
        #nested_arrays_of_intensity_arrays = np.array(nested_arrays_of_intensity_arrays)
        sum_of_lowest_x_values= 0
        sum_of_highest_x_values= 0
        for map_index in range(int(parameters["input_number_of_complete_file_names"])):
            sum_of_lowest_x_values+= array_of_x_values_arrays[map_index][0]
            sum_of_highest_x_values+= array_of_x_values_arrays[map_index][-1]
        total_lowest_x_value=sum_of_lowest_x_values/int(parameters["input_number_of_complete_file_names"])
        total_highest_x_value=sum_of_highest_x_values/int(parameters["input_number_of_complete_file_names"])

        array_of_x_values= np.linspace(total_lowest_x_value, total_highest_x_value, len(array_of_x_values_arrays[0]))
        
        if False:
            array_of_y_values=[]
            for incoming_energy_index in range(len(array_of_y_values_arrays[0])):
                sum_of_incoming_energy=0
                for map_index in range(int(parameters["input_number_of_complete_file_names"])):
                    sum_of_incoming_energy+= array_of_y_values_arrays[map_index][incoming_energy_index]
                average_incoming_energy= sum_of_incoming_energy/int(parameters["input_number_of_complete_file_names"])
                array_of_y_values.append(average_incoming_energy)
            array_of_y_values= np.array(array_of_y_values)

        unique_excitation_energies_list =[]
        tolerance_of_mismatch_in_excitation_energy_in_eV = 0.05
        for map_index in range(len(array_of_y_values_arrays)):
            for energy in array_of_y_values_arrays[map_index]:
                energy = float(energy)
                if not self.is_too_close(energy, unique_excitation_energies_list, tolerance_of_mismatch_in_excitation_energy_in_eV):
                    unique_excitation_energies_list.append(energy)
                #total_incoming_energy_list.append(float(energy))
        #used_excitation_energies = set()
        #untreated_unique_excitation_energies_list = [x for x in total_incoming_energy_list if x not in used_excitation_energies and (used_excitation_energies.add(x) or True)]


        array_of_intensity_arrays= []
        #array_of_y_values_arrays = np.array(array_of_y_values_arrays, dtype=object)
        for incoming_energy in unique_excitation_energies_list: 
            intensity_array= [0]*len(array_of_x_values)
            for map_index in range(int(parameters["input_number_of_complete_file_names"])):
                if min(np.abs(array_of_y_values_arrays[map_index] - incoming_energy)) <= tolerance_of_mismatch_in_excitation_energy_in_eV:
                    incoming_energy_index = np.abs(array_of_y_values_arrays[map_index] - incoming_energy).argmin()
                    intensity_array = np.add(intensity_array, nested_arrays_of_intensity_arrays[map_index][incoming_energy_index])
            array_of_intensity_arrays.append(intensity_array)
        array_of_intensity_arrays= np.array(array_of_intensity_arrays)
        
        array_of_y_values = unique_excitation_energies_list

        if False: #This is old
            array_of_intensity_arrays= []
            for incoming_energy_index in range(len(array_of_y_values_arrays[0])): #Maybe add so it is [map_index_of_highest_number_of_lines] instead of [0]. Or map_index_of_lowest_number_of_lines. And I cant go by energy_index, needs to be energy value... And maybe with a mismatch allowance of 0.05 eV
                intensity_array= [0]*len(array_of_x_values)
                for map_index in range(int(parameters["input_number_of_complete_file_names"])):
                    intensity_array = np.add(intensity_array, nested_arrays_of_intensity_arrays[map_index][incoming_energy_index])
                array_of_intensity_arrays.append(intensity_array)
            array_of_intensity_arrays= np.array(array_of_intensity_arrays)
        

        return array_of_x_values, array_of_y_values, array_of_intensity_arrays

    def is_too_close(self, new_energy, unique_excitation_energies_list, tolerance_of_mismatch_in_excitation_energy_in_eV):
        # Check if the new energy is within tolerance of any existing energy
        for energy in unique_excitation_energies_list:
            if abs(new_energy - energy) <= tolerance_of_mismatch_in_excitation_energy_in_eV:
                return True
        return False

    def weighted_polynomial_fit(self, x, y, weights):
        coefficients = np.polyfit(x, y, int(self.parameters["degree_of_energy_per_channel_polynomial"]), w=weights)
        return coefficients

    def polynomial_fit(self, x, y):
        coefficients = np.polyfit(x, y, int(self.parameters["degree_of_energy_per_channel_polynomial"]))
        return coefficients
    
    def weighted_polynomial_fit_for_x_axis(self, x, y):
        coefficients = np.polyfit(x, y, int(self.parameters["degree_of_energy_per_channel_polynomial"]), w= 1 / (1 + np.abs(y)))
        return coefficients

    def linear_function(self, x, a, b):
        return a * x + b

    def one_over_x_function(self, x, a, b, c):
        return a / (x + b) + c

    def nested_array_contains_negative_floats(self, nested_array):
        for array in nested_array:
            if np.any(array < 0):
                return True
        return False

    def plot_inputted_data(self, parameters, extra_plot_parameters):
        plt.close('all')
        plots= []
        
        nested_arrays_of_x_values_arrays, array_of_y_values_arrays, nested_arrays_of_intensity_arrays = self.get_y_value_arrays_and_nested_arrays_of_intensity_and_x_arrays(parameters)
        
        array_of_x_value_arrays, incoming_energy_array, array_of_intensity_arrays = self.align_and_combine_maps(parameters, array_of_y_values_arrays, nested_arrays_of_x_values_arrays, nested_arrays_of_intensity_arrays)

        #polynomial_coefficients = np.flip(np.polyfit(np.arange(0, len(x_values_array)), x_values_array, int(parameters["degree_of_energy_per_channel_polynomial"])))

        colormap = parameters["plot_colormap_choice"]

        if parameters["is_set_negative_intensities_to_zero"]:
            for spectra_index in range(len(array_of_intensity_arrays)):
                smallest_intensity_in_spectra = min(array_of_intensity_arrays[spectra_index])
                if smallest_intensity_in_spectra < 0:
                    array_of_intensity_arrays[spectra_index] = array_of_intensity_arrays[spectra_index] - smallest_intensity_in_spectra

        
        if parameters["is_automatically_adjust_peak_to_correct_energy"]:
            array_of_x_value_arrays = self.move_elastic_peak_center_to_correct_energy_with_gaussian(array_of_intensity_arrays, incoming_energy_array, array_of_x_value_arrays)
                #array_of_x_value_arrays = np.vstack(array_of_intensity_arrays).astype(float)

        if parameters["is_subtract_background_from_RIXS"]:
            for spectra_index in range(len(array_of_intensity_arrays)):
                if self.nested_array_contains_negative_floats(array_of_x_value_arrays[spectra_index]):
                    background_subtraction_first_channel = np.abs(array_of_x_value_arrays[spectra_index] - float(parameters["energy_above_elastic_peak_to_fit_background_start"])).argmin()
                    background_subtraction_last_channel = np.abs(array_of_x_value_arrays[spectra_index] - float(parameters["energy_above_elastic_peak_to_fit_background_end"])).argmin()
                else:
                    background_subtraction_first_channel = np.abs(array_of_x_value_arrays[spectra_index] - incoming_energy_array[spectra_index] - float(parameters["energy_above_elastic_peak_to_fit_background_start"])).argmin()
                    background_subtraction_last_channel = np.abs(array_of_x_value_arrays[spectra_index] - incoming_energy_array[spectra_index] - float(parameters["energy_above_elastic_peak_to_fit_background_end"])).argmin()
                
                average_background_intenisty = np.mean(array_of_intensity_arrays[spectra_index][int(background_subtraction_first_channel) : int(background_subtraction_last_channel)])
                array_of_intensity_arrays[spectra_index] = array_of_intensity_arrays[spectra_index] - average_background_intenisty


            #array_of_intensity_arrays = self.get_array_of_intensity_arrays(parameters, iteratable_file_number_array)
            #array_of_intensity_arrays = np.vstack(array_of_intensity_arrays).astype(float)

        #if parameters["is_data_x_values_energy_loss"]== True:
        #    energy_loss_array=x_values_array
        self.figure_to_save, ax = plt.subplots(1)
        self.figure_to_save.set_frameon(False)
        #self.figure_to_save = go.Figure()
        if parameters["plot_outgoing_energy_instead_of_energy_loss"]:
            if self.nested_array_contains_negative_floats(array_of_x_value_arrays):
                for spectra_index in range(len(array_of_x_value_arrays)):
                    array_of_x_value_arrays[spectra_index]= array_of_x_value_arrays[spectra_index] + incoming_energy_array[spectra_index]
            ax.set_xlabel("Emission energy [eV]", fontsize= parameters["plot_x_axis_text_size"])
        else:
            if self.nested_array_contains_negative_floats(array_of_x_value_arrays) == False:
                for spectra_index in range(len(array_of_x_value_arrays)):
                    array_of_x_value_arrays[spectra_index]= array_of_x_value_arrays[spectra_index] - incoming_energy_array[spectra_index]
            ax.set_xlabel("Energy loss [eV]", fontsize= parameters["plot_x_axis_text_size"])

        if parameters["plot_invert_x_axis"]:
            ax.invert_xaxis()

        if parameters["plot_invert_y_axis"]:
            if parameters["plot_waterfall_instead_of_heat_map"]== True:
                reversed_incoming_energy_array = np.flip(incoming_energy_array)
                reversed_array_of_intensity_arrays = np.flip(array_of_intensity_arrays, axis=0)
            else:
                ax.invert_yaxis()

        if parameters["is_plot_intensity_normalize_to_value_array"][0]:
            maximum_intensity = array_of_intensity_arrays.max()
            value_to_divide_intenisties_with = maximum_intensity/ float(parameters["plot_value_to_normalize_highest_intensity_array"][0])
            array_of_intensity_arrays = array_of_intensity_arrays/value_to_divide_intenisties_with

        if parameters["is_manual_shift_elastic_peak"]:
            for spectra_index in range(len(incoming_energy_array)):
                elastic_peak_shift_energy = float(parameters["manual_shift_elastic_peak_array"][spectra_index]) 
                array_of_x_value_arrays[spectra_index] = array_of_x_value_arrays[spectra_index] - elastic_peak_shift_energy
                
        if parameters["plot_waterfall_instead_of_heat_map"]== True:
            if parameters["plot_invert_y_axis"]== False:
                for spectra in range(len(incoming_energy_array)):
                    ax.plot(array_of_x_value_arrays[spectra], array_of_intensity_arrays[spectra] + float(parameters["plot_y_distance_between_plots"]) * spectra)
                    if parameters["plot_display_incoming_energy_by_lines"]:
                        formatted_incoming_energy = "{:.{}g}".format(incoming_energy_array[spectra], int(parameters["plot_incoming_energy_significant_numbers"]))
                        #text = f'y={exact_energy_per_channel_slope:.8f}x+{exact_energy_per_channel_intercept:.2f}\nR={exact_energy_per_channel_r_value:.8f} \nStandard error={exact_energy_per_channel_std_err:.8f}'
                        if parameters["plot_outgoing_energy_instead_of_energy_loss"]== True:
                            ax.text(float(parameters["plot_incoming_energy_x_offset"]) + incoming_energy_array[spectra], float(parameters["plot_y_distance_between_plots"]) * spectra + float(parameters["plot_incoming_energy_y_offset"]), formatted_incoming_energy, fontsize= float(parameters["plot_incoming_energy_text_size"]))
                        else:
                            ax.text(float(parameters["plot_incoming_energy_x_offset"]), float(parameters["plot_y_distance_between_plots"]) * spectra + float(parameters["plot_incoming_energy_y_offset"]), formatted_incoming_energy, fontsize= float(parameters["plot_incoming_energy_text_size"]))
            elif parameters["plot_invert_y_axis"]== True:
                for spectra in range(len(incoming_energy_array)):
                    ax.plot(array_of_x_value_arrays[spectra], reversed_array_of_intensity_arrays[spectra] + float(parameters["plot_y_distance_between_plots"]) * spectra)
                    if parameters["plot_display_incoming_energy_by_lines"]:
                        formatted_incoming_energy = "{:.{}g}".format(reversed_incoming_energy_array[spectra], int(parameters["plot_incoming_energy_significant_numbers"]))
                        #text = f'y={exact_energy_per_channel_slope:.8f}x+{exact_energy_per_channel_intercept:.2f}\nR={exact_energy_per_channel_r_value:.8f} \nStandard error={exact_energy_per_channel_std_err:.8f}'
                        if parameters["plot_outgoing_energy_instead_of_energy_loss"]== True:
                            ax.text(float(parameters["plot_incoming_energy_x_offset"]) + reversed_incoming_energy_array[spectra], float(parameters["plot_y_distance_between_plots"]) * spectra + float(parameters["plot_incoming_energy_y_offset"]), formatted_incoming_energy, fontsize= float(parameters["plot_incoming_energy_text_size"]))
                        else:
                            ax.text(float(parameters["plot_incoming_energy_x_offset"]), float(parameters["plot_y_distance_between_plots"]) * spectra + float(parameters["plot_incoming_energy_y_offset"]), formatted_incoming_energy, fontsize= float(parameters["plot_incoming_energy_text_size"]))
            ax.set_ylabel("Intensity [a.u]", fontsize= parameters["plot_y_axis_text_size"])
            if parameters["is_plot_grid"]:
                ax.grid(which='both', axis='x')
        else:

            incoming_energy_array_to_plot = adjust_excitation_energy_for_pcolormesh_plot_script.adjust_excitation_energy_for_pcolormesh_plot(incoming_energy_array)
            array_of_x_value_arrays_to_plot = []
            for spectra_index in range(len(array_of_intensity_arrays)):
                single_x_array_to_plot = adjust_excitation_energy_for_pcolormesh_plot_script.adjust_excitation_energy_for_pcolormesh_plot(array_of_x_value_arrays[spectra_index])
                array_of_x_value_arrays_to_plot.append(single_x_array_to_plot)
            combined_intensity_array = np.concatenate(array_of_intensity_arrays)
            max_intensity_value = np.max(combined_intensity_array)
            min_intensity_value = np.min(combined_intensity_array)
            #max_intensity_value = np.max(array_of_intensity_arrays)
            #min_intensity_value = np.min(array_of_intensity_arrays)
            #array_of_x_value_arrays = [np.asarray(x_list, dtype=float) for x_list in array_of_x_value_arrays]
            #array_of_intensity_arrays = [[np.array(x_list, dtype=float)] for x_list in array_of_intensity_arrays]
            #array_of_intensity_arrays= list(array_of_intensity_arrays)
            #for spectra_index in range(len(array_of_intensity_arrays)):
            #    array_of_intensity_arrays[spectra_index].append()
            array_index = 0


            # Decide on the intensity limits and log scale before plotting
            if parameters["is_plot_intensity_limits_used_array"][array_index]:
                vmin_val = float(parameters["plot_intensity_min_array"][array_index])
                vmax_val = float(parameters["plot_intensity_max_array"][array_index])
            else:
                vmin_val = min_intensity_value
                vmax_val = max_intensity_value

            # Decide on norm based on whether we want a log scale or linear scale
            if parameters["is_log_scale_color_bar"]:
                if vmin_val <= 0:
                    if vmax_val >= 100:
                        vmin_val =  1
                    else:
                        vmin_val = vmax_val * 0.01
                if vmax_val <= vmin_val:
                    # Ensure vmax > vmin
                    vmax_val = vmin_val * 10
                norm = LogNorm(vmin=vmin_val, vmax=vmax_val)
            else:
                # This results in a normal (linear) scale
                norm = Normalize(vmin=vmin_val, vmax=vmax_val)

            # Now we do the plotting using the chosen norm
            for spectra_index in range(len(array_of_intensity_arrays)):
                im = ax.pcolormesh(
                    array_of_x_value_arrays_to_plot[spectra_index],
                    incoming_energy_array_to_plot[spectra_index : spectra_index + 2],
                    [array_of_intensity_arrays[spectra_index]],
                    cmap=colormap,
                    shading='flat',
                    norm=norm  # Using the norm here
                )
                ax.set_facecolor(cm.turbo(0))

            ax.set_ylabel("Excitation energy [eV]", fontsize=parameters["plot_y_axis_text_size"])

            if parameters["plot_display_color_bar"]:
                cbar = self.figure_to_save.colorbar(im, ax=ax)
                cbar.ax.tick_params(labelsize=14)


        if parameters["plot_display_sample_name_title"]:
            ax.set_title(parameters["output_file_sample_name"], fontsize= parameters["plot_title_size"])
        
        array_index=0
        if parameters["is_energy_window_used_array"][array_index]:
            if parameters["plot_outgoing_energy_instead_of_energy_loss"]== True:
                if float(self.parameters["plot_energy_loss_min_array"][array_index]) < 0:
                    self.update_dictionary_array("plot_energy_loss_min_array", array_index, str(float(self.parameters["plot_energy_loss_min_array"][array_index]) + incoming_energy_array[-1]))
                    self.update_dictionary_array("plot_energy_loss_max_array", array_index, str(float(self.parameters["plot_energy_loss_max_array"][array_index]) + incoming_energy_array[-1]))
                
            else:
                if float(self.parameters["plot_energy_loss_min_array"][array_index]) > 0:
                    self.update_dictionary_array("plot_energy_loss_min_array", array_index, str(float(self.parameters["plot_energy_loss_min_array"][array_index]) - incoming_energy_array[-1]))
                    self.update_dictionary_array("plot_energy_loss_max_array", array_index, str(float(self.parameters["plot_energy_loss_max_array"][array_index]) - incoming_energy_array[-1]))

            if parameters["plot_waterfall_instead_of_heat_map"]== True:
                if float(self.parameters["plot_incoming_energy_min_array"][array_index]) > float(self.parameters["plot_y_distance_between_plots"]) * len(array_of_intensity_arrays) + max(array_of_intensity_arrays[-1]):
                    self.update_dictionary_array("plot_incoming_energy_min_array", array_index, str(0))
                    self.update_dictionary_array("plot_incoming_energy_max_array", array_index, str(float(self.parameters["plot_y_distance_between_plots"]) * len(array_of_intensity_arrays) + max(array_of_intensity_arrays[-1])))
                
            else:
                if float(self.parameters["plot_incoming_energy_max_array"][array_index]) < incoming_energy_array[0]:
                    if len(incoming_energy_array) > 1:
                        self.update_dictionary_array("plot_incoming_energy_min_array", array_index, str(incoming_energy_array[0] - (incoming_energy_array[1] - incoming_energy_array[0]) / 2))
                        self.update_dictionary_array("plot_incoming_energy_max_array", array_index, str(incoming_energy_array[-1] + (incoming_energy_array[-1] - incoming_energy_array[-2]) / 2))
                    else:
                        self.update_dictionary_array("plot_incoming_energy_min_array", array_index, str(incoming_energy_array[0] - 0.5))
                        self.update_dictionary_array("plot_incoming_energy_max_array", array_index, str(incoming_energy_array[-1] + 0.5))

            ax.set_xlim(float(self.parameters["plot_energy_loss_min_array"][array_index]), float(self.parameters["plot_energy_loss_max_array"][array_index]))
            ax.set_ylim(float(self.parameters["plot_incoming_energy_min_array"][array_index]), float(self.parameters["plot_incoming_energy_max_array"][array_index]))

        

        plots_manager = plt.get_current_fig_manager()
        screen_geometry = QDesktopWidget().screenGeometry()
        plots_manager.window.setGeometry(10,80,floor(screen_geometry.width()/2 -50), floor(screen_geometry.height()-200))
        #fig.tight_layout()
        self.figure_to_save.set_figwidth(float(parameters["plot_figure_size_x_array"][0]))
        self.figure_to_save.set_figheight(float(parameters["plot_figure_size_y_array"][0]))
        ax.minorticks_on()
        
        ax.xaxis.set_tick_params(labelsize= parameters["plot_x_axis_number_size"])
        ax.yaxis.set_tick_params(labelsize= parameters["plot_y_axis_number_size"])

        self.array_of_x_value_arrays_to_save = array_of_x_value_arrays
        self.incoming_energy_array_to_save = incoming_energy_array
        self.array_of_intensity_arrays_to_save = array_of_intensity_arrays

        #self.treated_data_array= np.array([array_of_x_value_arrays, incoming_energy_array, array_of_intensity_arrays], dtype=object)

        self.figure_to_save.show()


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
