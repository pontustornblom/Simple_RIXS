#add_treated_files_to_waterfall

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
import matplotlib.pyplot as plt
from matplotlib.pyplot import cm
import subprocess
from scipy.optimize import curve_fit
from scipy import stats
import json
import h5py
import parameter_scripts
import get_single_spectrum_h5_or_txt_file_scripts
import iteratable_number_to_int_script
import iteratable_number_to_float_script
import find_elastic_peak_maximum_script
import create_complete_file_location_view_roots_or_txt_script
import create_complete_file_location_for_treated_data

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
        self.vbox.addLayout(self.create_gui_item("output_file_sample_name", "Sample name: ", "q_line_edit", [""]))
        self.vbox.addLayout(self.create_gui_item("output_file_additional_comment", "Addional comment that will be saved with the file name: ", "q_line_edit", [""]))

        self.vbox.addLayout(self.create_gui_item("x_axis_title", "What is the title of the x-axis? ", "q_line_edit", [""]))
        self.vbox.addLayout(self.create_gui_item("y_axis_title", "What is the title of the y-axis? ", "q_line_edit", [""]))

        self.vbox.addLayout(self.create_gui_item("plot_display_sample_name_title", "Would you like to display the sample name as a title of the plot? ", "q_check_box", [""]))
        self.vbox.addLayout(self.create_gui_item("plot_title", "Input the title of the plot: ", "q_line_edit", [""]))
        self.vbox.addLayout(self.create_gui_item("is_display_legend", "Would you like to display the legend? ", "q_check_box", [""]))
        self.vbox.addLayout(self.create_gui_item("is_plot_grid", "Would you like to display vertical grid lines? ", "q_check_box", [""]))

        self.vbox.addLayout(self.create_gui_item("is_energy_window_used_array_0", "Would you like to zoom in on the plot in the x-direction? ", "q_check_box", [""]))
        if self.parameters["is_energy_window_used_array"][0]:
            self.vbox.addLayout(self.create_gui_item("plot_incoming_energy_min_array_0", "Input the lower cut off for the x-axis: ", "q_line_edit", [""]))
            self.vbox.addLayout(self.create_gui_item("plot_incoming_energy_max_array_0", "Input the upper cut off for the x-axis: ", "q_line_edit", [""]))
            #self.is_energy_window_used_displayed= True 

        self.vbox.addLayout(self.create_gui_item("is_plot_intensity_limits_used_array_0", "Would you like to zoom in on the plot in the y-direction? ", "q_check_box", [""]))
        if self.parameters["is_plot_intensity_limits_used_array"][0]:
            self.vbox.addLayout(self.create_gui_item("plot_intensity_min_array_0", "Input the lower cut off for the y-axis: ", "q_line_edit", [""]))
            self.vbox.addLayout(self.create_gui_item("plot_intensity_max_array_0", "Input the upper cut off for the y-axis: ", "q_line_edit", [""]))
            #self.is_plot_intensity_limits_used_displayed= True 

        
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

        self.setWindowTitle("Simple RIXS add treated files to waterfall")
        self.show()

        #if self.is_first_and_last_spectrum_displayed== False:
        
        #This line below has to b etoggleed manually (If this script actually needs to plot something)
        try:
            self.plot_inputted_data(self.parameters, "")
        except (IndexError, ValueError):
            print("Exception happened")
            self.plot_only_raw_data(self.parameters)
        
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
                self.vbox.insertLayout(self.vbox.indexOf(hbox)+1,self.create_gui_item("plot_incoming_energy_min_array_" + str(array_index), "Input the lower cut off for the incoming energy window: ", "q_line_edit", [""]))
                self.vbox.insertLayout(self.vbox.indexOf(hbox)+2,self.create_gui_item("plot_incoming_energy_max_array_" + str(array_index), "Input the upper cut off for the incoming energy window: ", "q_line_edit", [""]))
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
        elif key =="is_combine_datapoints_array":
            if self.parameters[key][array_index]:
                self.vbox.insertLayout(self.vbox.indexOf(hbox)+1, self.create_gui_item("number_of_points_to_combine_array_" + str(array_index), "How many datapoints would you like to bin together for region " +self.parameters["pfy_region_name_array"][array_index] +"? ", "q_line_edit", [""]))
            elif self.parameters[key][array_index]== False:
                self.remove_item(self.vbox.indexOf(hbox)+1)


    def create_dynamic_gui_item_for_waterfall_inputs(self):
        for file_name_index in range(int(self.parameters["input_number_of_complete_file_names"])):
            #self.vbox.insertLayout(self.vbox.indexOf(hbox)+2*pfy_region+1,self.create_gui_item("incoming_energy_segment_"+ str(pfy_region), "First incoming energy of segment "+ str(pfy_region)+":                     ", "q_line_edit", [""]))
            #self.vbox.insertLayout(self.vbox.indexOf(hbox)+2*pfy_region+2,self.create_gui_item("incoming_energy_difference_in_segment_"+ str(pfy_region), "Incoming energy difference of spectra in segment "+ str(pfy_region)+ ":", "q_line_edit", [""]))
            #self.vbox.insertLayout(self.vbox.indexOf(hbox)+2*int(item_text)+1,self.create_gui_item("incoming_energy_of_last_spectra", "Incoming energy of last spectra: ", "q_line_edit", [""]))
            

            self.vbox.addLayout(self.create_gui_item("", "-- Inputs for file " + self.parameters["input_complete_file_name_array"][file_name_index] + " --" , "q_text_label", [""]))

            self.vbox.addLayout(self.create_gui_item("plot_legend_names_array_" + str(file_name_index), "Name of this data: ", "q_line_edit", [""]))
            
            self.vbox.addLayout(self.create_gui_item("plot_waterfall_space_y_array_" + str(file_name_index), "How much should the plot be translated in the y-direction: ", "q_line_edit", [""]))           

            self.vbox.addLayout(self.create_gui_item("is_invert_the_plot_array_" + str(file_name_index), "Would you like to invert the plot? ", "q_check_box", [""]))

            self.vbox.addLayout(self.create_gui_item("is_normalize_to_zero_and_one_array_" + str(file_name_index), "Would you like to normalize the data by setting the lowest intensity \nto zero and the end intensity to one? \n(This normalization will happen if the plot is inverted)", "q_check_box", [""]))

            #self.vbox.addLayout(self.create_gui_item("incoming_energy_range_normalization_to_one_array_" + str(file_name_index), "How many incoming eV to average over at the end of the spectra \nto normalize the intensity to one: ", "q_line_edit", [""]))
            
            self.vbox.addLayout(self.create_gui_item("is_approximate_energy_for_normalization_to_zero_array_" + str(file_name_index), "Would you like to set an approximate energy of where to find the minimum intensity? ", "q_check_box", [""]))
            if self.parameters["is_approximate_energy_for_normalization_to_zero_array"][file_name_index]:
                self.vbox.addLayout(self.create_gui_item("approximate_energy_for_normalization_to_zero_array_" + str(file_name_index), "Approximate incoming energy of lowest intenisty: ", "q_line_edit", [""]))
                self.vbox.addLayout(self.create_gui_item("energy_above_and_below_finding_min_intensity_array_" + str(file_name_index), "How many eV above and below the approximate intensity should \nthe lowest intensity be searched over? ", "q_line_edit", [""]))

                #self.is_approximate_energy_for_normalization_to_zero_displayed= True

            self.vbox.addLayout(self.create_gui_item("energy_above_and_below_normalization_to_zero_array_" + str(file_name_index), "How many eV above and below the lowest intensity point should \nbe included to average over? ", "q_line_edit", [""]))

            self.vbox.addLayout(self.create_gui_item("is_subtract_fitted_background_array_" + str(file_name_index), "Would you like to fit a graph to the background to subtract from the spectra? ", "q_check_box", [""]))
            if self.parameters["is_subtract_fitted_background_array"][file_name_index]:
                self.vbox.addLayout(self.create_gui_item("background_fit_type_array_" + str(file_name_index), "What type of graph would you like to fit? ", "q_combo_box", ["Linear", "ln(x)", "log(x)", "Gaussian"]))
                self.vbox.addLayout(self.create_gui_item("background_fit_energy_start_array_" + str(file_name_index), "From what energy should the graph be fitted for region " +self.parameters["pfy_region_name_array"][file_name_index] +"? ", "q_line_edit", [""]))
                self.vbox.addLayout(self.create_gui_item("background_fit_energy_end_array_" + str(file_name_index), "To what energy should the graph be fitted? ", "q_line_edit", [""]))
                #self.is_subtract_fitted_background_displayed= True 
            
            self.vbox.addLayout(self.create_gui_item("is_combine_datapoints_array_" + str(file_name_index), "Would you like to bin datapoints together to smoothen the data? \n(Not implemented yet)", "q_check_box", [""]))
            if self.parameters["is_combine_datapoints_array"][file_name_index]:
                self.vbox.addLayout(self.create_gui_item("number_of_points_to_combine_array_" + str(file_name_index), "How many datapoints would you like to bin together? ", "q_line_edit", [""]))

                               
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
        figure_name= "Waterfall"
        figure_name+="_" + self.parameters["output_file_element"]
        figure_name+="_" + self.parameters["output_file_edge"]
        figure_name+="_" + self.parameters["output_file_sample_name"]
        figure_name+="_" + self.parameters["plot_title"]
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
        #plt.rcParams['figure.dpi'] = 300
        self.figure_to_save.savefig(full_figure_path, dpi=300)
        
        #extent = self.axs[pfy_region].get_window_extent().transformed(self.figure_to_save.dpi_scale_trans.inverted())
        #fig.savefig('ax2_figure.png', bbox_inches=extent)

        # Pad the saved area by 10% in the x-direction and 20% in the y-direction
        #self.figure_to_save.savefig(full_figure_path, bbox_inches=extent.expanded(1.1, 1.2))

        full_parameters_path=os.path.join(figure_path, figure_parameters_name)
        formatted_parameters = json.dumps(self.parameters, indent=0)
        with open(full_parameters_path, "w") as parameters_file:
            parameters_file.write(formatted_parameters)


        full_data_path=os.path.join(figure_path, figure_data_name)
        data_dictionary= {self.parameters["x_axis_title"]:self.array_of_x_values_arrays[0]}
        for file_name_index in range(int(self.parameters["input_number_of_complete_file_names"])):
            data_dictionary[self.parameters["plot_legend_names_array"][file_name_index]]= self.array_of_y_values_arrays[file_name_index]
        
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

    def get_arrays_of_x_and_y_values_arrays(self, parameters):
        #parameters, complete_file_location = create_complete_file_location_view_roots_or_txt_script.create_complete_file_location_view_roots_or_txt(parameters, False, "")
        data_row= 1
        #main_dataframe = pd.read_csv(complete_file_location, sep='\t', skiprows=data_row, header=None) 
        #x_values_array= main_dataframe.iloc[:, 0].values
        #incoming_energy_array= main_dataframe.iloc[:, 1].values  
       
        array_of_x_values_arrays = []
        array_of_y_values_arrays = []
        for file_name_index in range(int(self.parameters["input_number_of_complete_file_names"])):
            complete_file_location= create_complete_file_location_for_treated_data.create_complete_file_location_for_treated_data(parameters["input_file_project_folder"], self.parameters["input_complete_file_name_array"][file_name_index])
            main_dataframe = pd.read_csv(complete_file_location, sep='\t', skiprows=data_row, header=None) 
            x_values_array= main_dataframe.iloc[:, 0].values
            y_values_array= main_dataframe.iloc[:, 1].values
            
            array_of_x_values_arrays.append(x_values_array)
            array_of_y_values_arrays.append(y_values_array)
        return array_of_y_values_arrays, array_of_x_values_arrays

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

    def plot_inputted_data(self, parameters, extra_plot_parameters):
        plt.close()

        #complete_treated_file_location= create_complete_file_location_for_treated_data.create_complete_file_location_for_treated_data(self.parameters["input_file_project_folder"], self.parameters["input_complete_file_name_array"][array_index])

        self.array_of_y_values_arrays, self.array_of_x_values_arrays = self.get_arrays_of_x_and_y_values_arrays(parameters)

        self.array_of_y_values_arrays = self.treat_intensity_data(parameters, self.array_of_y_values_arrays, self.array_of_x_values_arrays)

        self.figure_to_save, ax = plt.subplots(1)
        #plot_color_array = list(cm.rainbow(np.linspace(0, 1, ceil(int(parameters["input_number_of_complete_file_names"])/2))))
        plot_color_array = list(cm.rainbow(np.linspace(0, 1, int(parameters["input_number_of_complete_file_names"]))))
        for file_name_index in range(int(parameters["input_number_of_complete_file_names"])):
            ax.plot(self.array_of_x_values_arrays[file_name_index], self.array_of_y_values_arrays[file_name_index] + float(parameters["plot_waterfall_space_y_array"][file_name_index]), label= parameters["plot_legend_names_array"][file_name_index], color=plot_color_array[file_name_index])
        
        #for file_name_index in range(int(parameters["input_number_of_complete_file_names"])):
        #    if file_name_index < ceil(int(parameters["input_number_of_complete_file_names"])/2) -1:
        #        ax.plot(self.array_of_x_values_arrays[file_name_index], self.array_of_y_values_arrays[file_name_index] + float(parameters["plot_waterfall_space_y_array"][file_name_index]), label= parameters["plot_legend_names_array"][file_name_index], color=plot_color_array[file_name_index])
        #    elif file_name_index == int(parameters["input_number_of_complete_file_names"]) - 1:
        #        ax.plot(self.array_of_x_values_arrays[file_name_index], self.array_of_y_values_arrays[file_name_index] + float(parameters["plot_waterfall_space_y_array"][file_name_index]), label= parameters["plot_legend_names_array"][file_name_index], color=plot_color_array[0], linestyle="dashdot")   
        #    else:
        #        ax.plot(self.array_of_x_values_arrays[file_name_index], self.array_of_y_values_arrays[file_name_index] + float(parameters["plot_waterfall_space_y_array"][file_name_index]), label= parameters["plot_legend_names_array"][file_name_index], color=plot_color_array[file_name_index - ceil(int(parameters["input_number_of_complete_file_names"])/2) + 1], linestyle="dashed")



        if parameters["is_energy_window_used_array"][0]:
            ax.set_xlim(float(parameters["plot_incoming_energy_min_array"][0]), float(parameters["plot_incoming_energy_max_array"][0]))

        if parameters["is_plot_intensity_limits_used_array"][0]:
            ax.set_ylim(float(parameters["plot_intensity_min_array"][0]), float(parameters["plot_intensity_max_array"][0]))
            
        if parameters["plot_display_sample_name_title"]:
            ax.set_title(parameters["plot_title"])
        
        if parameters["is_plot_grid"]:
            ax.grid(which='both', axis='x')

        if parameters["is_display_legend"]:
            plt.legend(loc='best')
        ax.set_xlabel(parameters["x_axis_title"])
        ax.set_ylabel(parameters["y_axis_title"])

        #intensity_array = np.vstack(intensity_array).astype(float)
 
        plots_manager = plt.get_current_fig_manager()
        screen_geometry = QDesktopWidget().screenGeometry()
        plots_manager.window.setGeometry(50,80,floor(screen_geometry.width()/2 -50), floor(screen_geometry.height()-200))


        self.figure_to_save.tight_layout()

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
        ax.set_xlabel('Incoming energy [eV]')
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
