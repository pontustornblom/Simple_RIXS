#subtract_treated_files_script_2

import sys
import os
import platform
import subprocess
from PyQt5.QtWidgets import QLabel, QMainWindow, QCheckBox, QComboBox, QLineEdit, QPushButton, QLayout, QApplication, QVBoxLayout, QHBoxLayout, QWidget, QDesktopWidget, QLabel, QTextEdit, QMessageBox, QScrollArea
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from math import floor, ceil
import numpy as np
from PyQt5.QtCore import QEventLoop
from PyQt5.QtCore import pyqtSignal
import pandas as pd
import heapq
import matplotlib.pyplot as plt
from matplotlib.pyplot import cm
from scipy.optimize import curve_fit
from scipy import stats
from scipy.interpolate import interp1d
from scipy.ndimage import gaussian_filter1d
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
        self.setMinimumWidth(floor(screen_geometry.width()/2 -20))
        self.setFixedHeight(floor(screen_geometry.height() - floor(screen_geometry.height()/9)))
        self.move(floor(screen_geometry.width()/2 +10), 10)

        self.vbox = QVBoxLayout()

        self.vbox.addLayout(self.create_gui_item("input_file_project_folder", "Folder of the current project: ", "q_line_edit", [""]))
        self.vbox.addLayout(self.create_gui_item("input_file_raw_data_folder", "Subfolder where the raw data is stored: ", "q_line_edit", [""]))
        self.vbox.addLayout(self.create_gui_item("open file location", "Open raw data file location", "q_push_button",  [""]))   

        self.vbox.addLayout(self.create_gui_item("Update the plot", "Update the plot", "q_push_button",  [""]))

        self.vbox.addLayout(self.create_bottom_buttons())

        self.vbox.addLayout(self.create_gui_item("", "The following four inputs does not effect the calculation, it affects the saved file name", "q_text_label", [""]))
        self.vbox.addLayout(self.create_gui_item("output_file_element", "Element that is being studied: ", "q_line_edit", [""]))
        self.vbox.addLayout(self.create_gui_item("output_file_edge", "Edge that is being studied: ", "q_combo_box", ["K-edge", "L-edge", "L1-edge", "L2-edge", "L3-edge", "M-edge", "M1-edge", "M5-edge"]))
        self.vbox.addLayout(self.create_gui_item("output_file_additional_comment", "Additional comment that will be saved with the file name: ", "q_line_edit", [""]))

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
        
        self.vbox.addLayout(self.create_gui_item("subtract_spectra_on_emission_energy_axis_instead_of_energy_loss", "Would you like the x-axis to be emission energy instead of energy loss before subtracting the spectra? ", "q_check_box", [""]))                
        self.vbox.addLayout(self.create_gui_item("plot_outgoing_energy_instead_of_energy_loss", "Would you like the x-axis to be emission energy instead of energy loss in the final spectra? ", "q_check_box", [""]))                

        self.vbox.addLayout(self.create_gui_item("is_energy_window_used_array_0", "Would you like to zoom in on the plot in the x-direction? ", "q_check_box", [""]))
        if self.parameters["is_energy_window_used_array"][0]:
            self.vbox.addLayout(self.create_gui_item("plot_energy_loss_min_array_0", "Input the lower cut off for the x-axis: ", "q_line_edit", [""]))
            self.vbox.addLayout(self.create_gui_item("plot_energy_loss_max_array_0", "Input the upper cut off for the x-axis: ", "q_line_edit", [""]))

        self.vbox.addLayout(self.create_gui_item("is_plot_intensity_limits_used_array_0", "Would you like to zoom in on the plot in the y-direction? ", "q_check_box", [""]))
        if self.parameters["is_plot_intensity_limits_used_array"][0]:
            self.vbox.addLayout(self.create_gui_item("plot_intensity_min_array_0", "Input the lower cut off for the y-axis: ", "q_line_edit", [""]))
            self.vbox.addLayout(self.create_gui_item("plot_intensity_max_array_0", "Input the upper cut off for the y-axis: ", "q_line_edit", [""]))

        self.vbox.addLayout(self.create_gui_item("plot_display_incoming_energy_by_lines", "Would you like to display the incoming energy next to the spectra? ", "q_check_box", [""]))
        self.vbox.addLayout(self.create_gui_item("plot_incoming_energy_x_offset", "Input value to adjust the x coordinate of the incoming energy text: ", "q_line_edit", [""]))
        self.vbox.addLayout(self.create_gui_item("plot_incoming_energy_y_offset", "Input value to adjust the y coordinate of the incoming energy text: ", "q_line_edit", [""]))
        self.vbox.addLayout(self.create_gui_item("plot_incoming_energy_text_size", "What text size of the incoming energy text would you like: ", "q_line_edit", [""]))
        self.vbox.addLayout(self.create_gui_item("plot_incoming_energy_significant_numbers", "What many significant numbers of the incoming energy text would you like to display? ", "q_line_edit", [""]))
        
        self.vbox.addLayout(self.create_gui_item("is_binning_smooth_data_for_all_spectra", "Would you like to do bin data points together to smooth the data for all spectra? \n(This will override any selection of smoothening of an individual spectra below) ", "q_check_box", [""]))
        if self.parameters["is_binning_smooth_data_for_all_spectra"]:
            self.vbox.addLayout(self.create_gui_item("number_of_bins_for_smoothing_array_0", "How many datapoints would you like to bin together? ", "q_line_edit", [""]))
   
        self.vbox.addLayout(self.create_gui_item("is_gaussian_smooth_data_for_all_spectra", "Would you like to do gaussian smoothening for all spectra? \n(This will override any selection of smoothening of an individual spectra below) ", "q_check_box", [""]))
        if self.parameters["is_gaussian_smooth_data_for_all_spectra"]:
            self.vbox.addLayout(self.create_gui_item("sigma_for_gaussian_smoothing_array_0", "What value of sigma would you like for the gaussian smoothing? ", "q_line_edit", [""]))

        self.vbox.addLayout(self.create_gui_item("is_normalize_intensity_at_certain_emission_energy", "Would you like to do normalize the intensity at a certain emission energy for all spectra? ", "q_check_box", [""]))
        if self.parameters["is_normalize_intensity_at_certain_emission_energy"]:
            self.vbox.addLayout(self.create_gui_item("emission_energy_for_intenisty_normalization", "What emission energy would you like to normalize to? ", "q_line_edit", [""]))
            self.vbox.addLayout(self.create_gui_item("emission_energy_above_and_below_for_normalization", "What energy above and below the selected emission energy would like you average over? ", "q_line_edit", [""]))

        self.vbox.addLayout(self.create_gui_item("how_data_points_will_be_subtracted", "How would you like the data points to be subtracted? ", "q_combo_box", ["Create a new x-axis that includes the emission energy of both x-axes and linearly interpolate to get intensities at each point", "Create a new x-axis with equal spacing between data points that is twice as dense as the x-axis with the most points", "Subtract to closest datapoint in energy (the x-axis will be assumed to have the same distance between points that they are on a on a linear energy scale)"]))

        self.create_dynamic_gui_item_for_waterfall_inputs()

        self.vbox.addLayout(self.create_gui_item("Update the plot", "Update the plot", "q_push_button",  [""]))

        self.vbox.addLayout(self.create_gui_item("", "If everything looks good then a figure will be saved when you hit Save and continue", "q_text_label", [""]))

        self.vbox.addLayout(self.create_bottom_buttons())

        self.central_widget = QWidget()
        self.central_widget.setLayout(self.vbox)
        self.setCentralWidget(self.central_widget)

        # Scroll stuff:
        self.scroll = QScrollArea()
        self.scroll.setWidget(self.central_widget)
        self.scroll.setWidgetResizable(True)
        self.setCentralWidget(self.scroll)

        self.setWindowTitle("Simple RIXS add multiple spectra to waterfall")
        self.show()

        self.plot_inputted_data(self.parameters, "")


    def create_gui_item(self, key, item_label_text, item_type, combo_box_options):
        hbox = QHBoxLayout()
        item_label = QLabel(item_label_text)
        if item_type == "q_line_edit":
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
                # FIX: capture array_key and array_index by value via default args
                item.editingFinished.connect(lambda ak=array_key, ai=array_index, it=item: self.update_dictionary_array(ak, ai, it))
            elif key != "input_file_project_folder" and key != "input_file_raw_data_folder" and key[:22] != "pfy_region_name_array_" and key != "y_axis_title" and key != "x_axis_title" and key != "output_file_element" and key != "output_file_sample_name" and key != "output_file_additional_comment" and key != "plot_title":
                item = QLineEdit(self.parameters[key])
                hbox.addWidget(item)
                # FIX: capture item and key by value
                item.editingFinished.connect(lambda it=item, k=key: self.validate_input(it, k))
            else:
                item = QLineEdit(self.parameters[key])
                hbox.addWidget(item)
                # FIX: capture key by value
                item.textChanged.connect(lambda text, k=key: self.update_dictionary(k, text))
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
                item.currentTextChanged.connect(lambda text, ak=array_key, ai=array_index, it=item: self.update_dictionary_combobox_array(ak, ai, it))
            else:
                item = QComboBox()
                item.addItems(combo_box_options)
                item.setCurrentText(self.parameters[key])
                hbox.addWidget(item)
                item.currentTextChanged.connect(lambda text, k=key, it=item: self.update_dictionary(k, it.currentText()))
        elif item_type == "q_check_box":
            hbox.addWidget(item_label)
            item = QCheckBox()
            if key in ("is_binning_smooth_data_for_all_spectra",
                       "is_gaussian_smooth_data_for_all_spectra",
                       "is_normalize_intensity_at_certain_emission_energy"):
                item.setChecked(self.parameters[key])
                hbox.addWidget(item)
                item.clicked.connect(lambda checked, k=key, h=hbox, it=item: self.create_multiple_gui_items_from_checkboxes(it, k, h))
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
                item.clicked.connect(lambda checked, ak=array_key, ai=array_index, it=item, h=hbox: self.create_multiple_gui_items_from_checkbox_arrays(ak, ai, it, h))
            else:
                item.setChecked(self.parameters[key])
                hbox.addWidget(item)
                item.clicked.connect(lambda checked, k=key, it=item: self.update_dictionary_checkbox(k, it))
        elif item_type == "q_push_button":
            item_label = QLabel("")
            hbox.addWidget(item_label)
            item = QPushButton(item_label_text)
            hbox.addWidget(item)
            if key == "open file location":
                item.clicked.connect(lambda: self.open_folder(self.parameters["input_file_project_folder"], self.parameters["input_file_raw_data_folder"]))
            elif key == "Zoom in on elastic peak":
                item.clicked.connect(lambda: self.plot_inputted_data(self.parameters, "zoom_in_on_plot"))
            elif key == "Update the plot":
                item.clicked.connect(lambda: self.plot_inputted_data(self.parameters, "update_plot"))
        elif item_type == "q_text_label":
            hbox.addWidget(item_label)
        else:
            print("Error: Item was not added to the GUI")
        return hbox

    def update_dictionary(self, key, updated_value):
        self.parameters[key] = updated_value

    def update_dictionary_checkbox(self, key, item):
        self.parameters[key] = item.isChecked()
    
    def update_dictionary_combobox_array(self, key, array_index, item):
        self.parameters[key][array_index] = item.currentText()

    def update_dictionary_checkbox_array(self, key, array_index, item):
        self.parameters[key][array_index] = item.isChecked()

    def update_dictionary_array(self, key, array_index, item):
        if self.validate_input_for_array(key, array_index, item):
            self.parameters[key][array_index] = item.text()

    def validate_input_for_array(self, key, array_index, item):
        if item.text() != self.parameters[key][array_index]:
            if key == "plot_legend_names_array" or key == "input_complete_file_name_array":
                return True
            if item.text() == "":
                QMessageBox.warning(self, "Invalid Input", "Do not leave blank")
                item.clear()
                return False
            else:
                try:
                    if item.text()[0] == "0":
                        float(iteratable_number_to_float_script.iteratable_number_to_float(item.text()))
                        return True
                    else:
                        float(item.text())
                        return True
                except ValueError:
                    QMessageBox.warning(self, "Invalid Input", "Input must be an integer or float.")
                    item.clear()
                    return False
        return True  # No change, treat as valid

    def validate_input(self, item, key):
        if item.text() != self.parameters[key]:
            self.update_dictionary(key, item.text())
            if item.text() == "":
                QMessageBox.warning(self, "Invalid Input", "Do not leave blank")
                item.clear()
                return False
            else:
                try:
                    if item.text()[0] == "0":
                        float(iteratable_number_to_float_script.iteratable_number_to_float(item.text()))
                        return True
                    else:
                        float(item.text())
                        return True
                except ValueError:
                    QMessageBox.warning(self, "Invalid Input", "Input must be an integer or float.")
                    item.clear()
                    return False
        return True  # No change


    def create_multiple_gui_items_from_checkboxes(self, item, key, hbox):
        self.update_dictionary_checkbox(key, item)
        
        if key == "is_binning_smooth_data_for_all_spectra":
            if self.parameters["is_binning_smooth_data_for_all_spectra"]:
                self.vbox.insertLayout(self.vbox.indexOf(hbox)+1, self.create_gui_item("number_of_bins_for_smoothing_array_0", "How many datapoints would you like to bin together? ", "q_line_edit", [""]))
            else:
                self.remove_item(self.vbox.indexOf(hbox)+1)
        elif key == "is_gaussian_smooth_data_for_all_spectra":
            if self.parameters["is_gaussian_smooth_data_for_all_spectra"]:
                self.vbox.insertLayout(self.vbox.indexOf(hbox)+1, self.create_gui_item("sigma_for_gaussian_smoothing_array_0", "What value of sigma would you like for the gaussian smoothing? ", "q_line_edit", [""]))
            else:
                self.remove_item(self.vbox.indexOf(hbox)+1)
        elif key == "is_normalize_intensity_at_certain_emission_energy":
            if self.parameters["is_normalize_intensity_at_certain_emission_energy"]:
                self.vbox.insertLayout(self.vbox.indexOf(hbox)+1, self.create_gui_item("emission_energy_for_intenisty_normalization", "What emission energy would you like to normalize to? ", "q_line_edit", [""]))
                self.vbox.insertLayout(self.vbox.indexOf(hbox)+2, self.create_gui_item("emission_energy_above_and_below_for_normalization", "What energy above and below the selected emission energy would like you average over? ", "q_line_edit", [""]))
            else:
                self.remove_item(self.vbox.indexOf(hbox)+1)
                self.remove_item(self.vbox.indexOf(hbox)+1)  # index shifts after first removal


    def create_multiple_gui_items_from_checkbox_arrays(self, key, array_index, item, hbox):
        self.update_dictionary_checkbox_array(key, array_index, item)

        if key == "is_energy_window_used_array":
            if self.parameters["is_energy_window_used_array"][array_index]:
                self.vbox.insertLayout(self.vbox.indexOf(hbox)+1, self.create_gui_item("plot_energy_loss_min_array_" + str(array_index), "Input the lower cut off for the x-axis: ", "q_line_edit", [""]))
                self.vbox.insertLayout(self.vbox.indexOf(hbox)+2, self.create_gui_item("plot_energy_loss_max_array_" + str(array_index), "Input the upper cut off for the x-axis: ", "q_line_edit", [""]))
            else:
                self.remove_item(self.vbox.indexOf(hbox)+1)
                self.remove_item(self.vbox.indexOf(hbox)+1)
        elif key == "is_plot_intensity_limits_used_array":
            if self.parameters["is_plot_intensity_limits_used_array"][array_index]:
                self.vbox.insertLayout(self.vbox.indexOf(hbox)+1, self.create_gui_item("plot_intensity_min_array_" + str(array_index), "Input the lower cut off for the intensity window: ", "q_line_edit", [""]))
                self.vbox.insertLayout(self.vbox.indexOf(hbox)+2, self.create_gui_item("plot_intensity_max_array_" + str(array_index), "Input the upper cut off for the intensity window: ", "q_line_edit", [""]))
            else:
                self.remove_item(self.vbox.indexOf(hbox)+1)
                self.remove_item(self.vbox.indexOf(hbox)+1)
        elif key == "is_binning_smooth_data_array":
            if self.parameters[key][array_index]:
                self.vbox.insertLayout(self.vbox.indexOf(hbox)+1, self.create_gui_item("number_of_bins_for_smoothing_array_" + str(array_index), "How many datapoints would you like to bin together? ", "q_line_edit", [""]))
            else:
                self.remove_item(self.vbox.indexOf(hbox)+1)
        elif key == "is_gaussian_smooth_data_array":
            if self.parameters[key][array_index]:
                self.vbox.insertLayout(self.vbox.indexOf(hbox)+1, self.create_gui_item("sigma_for_gaussian_smoothing_array_" + str(array_index), "What value of sigma would you like for the gaussian smoothing? ", "q_line_edit", [""]))
            else:
                self.remove_item(self.vbox.indexOf(hbox)+1)

    def create_dynamic_gui_item_for_waterfall_inputs(self):
        """Create per-spectrum GUI controls for the two spectra to be subtracted."""
        array_index = 0
        for file_name_index in range(2):
            # FIX: removed the extra indentation level that had no enclosing block
            self.vbox.addLayout(self.create_gui_item("", "------------ Inputs for file " + self.parameters["plot_legend_names_array"][file_name_index] + " ------------", "q_text_label", [""]))

            self.vbox.addLayout(self.create_gui_item("plot_intensity_offset_array_" + str(array_index), "Input value that you want to offset the intensity by: ", "q_line_edit", [""]))

            self.vbox.addLayout(self.create_gui_item("plot_is_scale_intensity_of_spectra_array_" + str(array_index), "Would you like to scale the intensity of this spectra? ", "q_check_box", [""]))
            self.vbox.addLayout(self.create_gui_item("plot_scaling_array_" + str(array_index), "Input value that you want to multiply the intensity by: ", "q_line_edit", [""]))
            self.vbox.addLayout(self.create_gui_item("plot_scaling_text_x_offset_array_" + str(array_index), "How much do you want to offset the scaling text in the x direction? ", "q_line_edit", [""]))
            self.vbox.addLayout(self.create_gui_item("plot_scaling_text_y_offset_array_" + str(array_index), "How much do you want to offset the scaling text in the y direction? ", "q_line_edit", [""]))

            self.vbox.addLayout(self.create_gui_item("is_binning_smooth_data_array_" + str(array_index), "Would you like to bin together the data points in this spectra? ", "q_check_box", [""]))
            if self.parameters["is_binning_smooth_data_array"][array_index]:
                self.vbox.addLayout(self.create_gui_item("number_of_bins_for_smoothing_array_" + str(array_index), "How many data points would you like to bin together for this spectra? ", "q_line_edit", [""]))

            self.vbox.addLayout(self.create_gui_item("is_gaussian_smooth_data_array_" + str(array_index), "Would you like to do a gaussian smoothening for this spectra? ", "q_check_box", [""]))
            if self.parameters["is_gaussian_smooth_data_array"][array_index]:
                self.vbox.addLayout(self.create_gui_item("sigma_for_gaussian_smoothing_array_" + str(array_index), "What value of sigma would you like for the gaussian smoothing? ", "q_line_edit", [""]))

            self.vbox.addLayout(self.create_gui_item("is_hide_certain_spectra_array_" + str(array_index), "Would you like to hide this spectra? ", "q_check_box", [""]))

            array_index += 1
                               
    def remove_item(self, hbox_index):
        next_hbox = self.vbox.itemAt(hbox_index).layout()
        if next_hbox is not None:
            self.deleteItemsOfLayout(next_hbox)

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
        self.parameters["is_program_running"] = False
        plt.close()
        self.finished.emit()
        self.close()

    def close_program(self): 
        self.parameters["is_program_running"] = False
        plt.close()
        self.finished.emit()
        self.close()

    def save_treated_data(self):
        figure_name = "RIXS_subtracted_spectra"
        figure_name += "_" + self.parameters["output_file_element"]
        figure_name += "_" + self.parameters["output_file_edge"]
        figure_name += "_" + self.parameters["plot_legend_names_array"][0] + "_" + self.parameters["incoming_energy_of_spectra_array"][0]
        figure_name += "_minus_" + self.parameters["plot_legend_names_array"][1] + "_" + self.parameters["incoming_energy_of_spectra_array"][1]
        if self.parameters["output_file_additional_comment"] != "":
            figure_name += "_" + self.parameters["output_file_additional_comment"]
        figure_parameters_name = figure_name
        figure_data_name = figure_name
        figure_name += "_figure.png"
        figure_parameters_name += "_parameters.txt"
        figure_data_name += "_data.txt"
        figure_path = os.path.join(self.parameters["input_file_project_folder"], 'Simple RIXS Figures')
        if not os.path.exists(figure_path):
            os.makedirs(figure_path)
        
        full_figure_path = os.path.join(figure_path, figure_name)
        self.figure_to_save.savefig(full_figure_path, dpi=600)

        full_parameters_path = os.path.join(figure_path, figure_parameters_name)
        formatted_parameters = json.dumps(self.parameters, indent=0)
        with open(full_parameters_path, "w") as parameters_file:
            parameters_file.write(formatted_parameters)

        y_axis_title = "Intensity [a.u]"
        if self.parameters["plot_outgoing_energy_instead_of_energy_loss"]:
            x_axis_title = "Emission energy [eV]"
        else:
            x_axis_title = "Energy loss [eV]"

        full_data_path = os.path.join(figure_path, figure_data_name)
        data_dictionary = {}
        
        data_dictionary[x_axis_title + '_Difference_' + self.parameters["plot_legend_names_array"][0] + '_' + self.parameters["incoming_energy_of_spectra_array"][0]] = self.subtracted_x_value_array_to_save
        data_dictionary[y_axis_title + "_Difference_" + self.parameters["plot_legend_names_array"][0] + "_" + self.parameters["incoming_energy_of_spectra_array"][0]] = self.subtracted_intensity_array_to_save

        if self.parameters["subtract_spectra_on_emission_energy_axis_instead_of_energy_loss"]:
            x_axis_title_orig = "Emission energy [eV]"
        else:
            x_axis_title_orig = "Energy loss [eV]"
        
        data_dictionary[x_axis_title_orig + '_Minuend_' + self.parameters["plot_legend_names_array"][0] + '_' + self.parameters["incoming_energy_of_spectra_array"][0]] = self.original_array_of_x_values_arrays_to_save[0]
        data_dictionary[y_axis_title + "_Minuend_" + self.parameters["plot_legend_names_array"][0] + "_" + self.parameters["incoming_energy_of_spectra_array"][0]] = self.original_array_of_intensity_arrays_to_plot[0]
        
        data_dictionary[x_axis_title_orig + '_Subtrahend_' + self.parameters["plot_legend_names_array"][1] + '_' + self.parameters["incoming_energy_of_spectra_array"][1]] = self.original_array_of_x_values_arrays_to_save[1]
        data_dictionary[y_axis_title + "_Subtrahend_" + self.parameters["plot_legend_names_array"][1] + "_" + self.parameters["incoming_energy_of_spectra_array"][1]] = self.original_array_of_intensity_arrays_to_plot[1]

        data_dataframe = pd.DataFrame.from_dict(data_dictionary, orient='index').transpose().fillna('')
        data_dataframe.to_csv(full_data_path, sep='\t', index=False)

    def open_folder(self, project_folder, raw_data_folder):
        folder_path = os.path.join(project_folder, raw_data_folder)
        if platform.system() == "Darwin":
            subprocess.call(["open", folder_path])
        else:
            subprocess.call(["explorer", folder_path])

    def gaussian(self, x, A, mu, sigma):
        return A * np.exp(-(x - mu)**2 / (2 * sigma**2))

    def get_arrays_of_x_values_and_intenisty_arrays(self, parameters):
        """Load treated RIXS data for the two spectra to be subtracted."""
        array_of_x_values_arrays = []
        array_of_intensity_arrays = []

        for spectrum_index in range(2):
            complete_file_location = create_complete_file_location_for_treated_data.create_complete_file_location_for_treated_data(
                parameters["input_file_project_folder"],
                self.parameters["input_complete_file_name_array"][spectrum_index]
            )
            array_of_x_values_arrays_from_one_file, incoming_energy_array, array_of_intensity_arrays_from_one_file = get_treated_rixs_data_script.get_treated_rixs_data(complete_file_location)
            
            incoming_energy_index_of_spectra = np.nanargmin(np.abs(incoming_energy_array - float(parameters["incoming_energy_of_spectra_array"][spectrum_index])))
            intensity_array = array_of_intensity_arrays_from_one_file[incoming_energy_index_of_spectra]
            x_values_array = array_of_x_values_arrays_from_one_file[incoming_energy_index_of_spectra]
            array_of_x_values_arrays.append(x_values_array)
            array_of_intensity_arrays.append(intensity_array)

        return array_of_intensity_arrays, array_of_x_values_arrays

    def get_plot_color_and_linestyle_array(self, parameters):
        """Return color and linestyle arrays for the two spectra."""
        # FIX: simplified for the 2-spectrum subtraction case
        plot_color_array = list(cm.rainbow(np.linspace(0, 1, 2)))
        linestyles_array = ["solid", "dashed"]
        return plot_color_array, linestyles_array
    
    def subtract_spectra(self, parameters, array_of_x_value_arrays, array_of_intensity_arrays):
        """Subtract spectrum 1 from spectrum 0 using the selected method."""

        if parameters["how_data_points_will_be_subtracted"] == "Create a new x-axis that includes the emission energy of both x-axes and linearly interpolate to get intensities at each point":
            # Merge both x-axes and interpolate intensities onto the combined grid
            combined_x_values_array = np.asarray(list(heapq.merge(*array_of_x_value_arrays)))
            # Remove duplicates and sort
            combined_x_values_array = np.unique(combined_x_values_array)

            interpolating_function_0 = interp1d(array_of_x_value_arrays[0], array_of_intensity_arrays[0], kind='linear', fill_value="extrapolate")
            interpolating_function_1 = interp1d(array_of_x_value_arrays[1], array_of_intensity_arrays[1], kind='linear', fill_value="extrapolate")

            subtracted_intensity_array = interpolating_function_0(combined_x_values_array) - interpolating_function_1(combined_x_values_array)
            subtracted_intensity_array = np.array(subtracted_intensity_array, dtype=float)

        elif parameters["how_data_points_will_be_subtracted"] == "Create a new x-axis with equal spacing between data points that is twice as dense as the x-axis with the most points":
            # FIX: actually implemented this method
            # Determine the range covered by both spectra
            x_min = max(np.min(array_of_x_value_arrays[0]), np.min(array_of_x_value_arrays[1]))
            x_max = min(np.max(array_of_x_value_arrays[0]), np.max(array_of_x_value_arrays[1]))
            # Twice as many points as the denser axis
            n_points = 2 * max(len(array_of_x_value_arrays[0]), len(array_of_x_value_arrays[1]))
            combined_x_values_array = np.linspace(x_min, x_max, n_points)

            interpolating_function_0 = interp1d(array_of_x_value_arrays[0], array_of_intensity_arrays[0], kind='linear', fill_value="extrapolate")
            interpolating_function_1 = interp1d(array_of_x_value_arrays[1], array_of_intensity_arrays[1], kind='linear', fill_value="extrapolate")

            subtracted_intensity_array = interpolating_function_0(combined_x_values_array) - interpolating_function_1(combined_x_values_array)
            subtracted_intensity_array = np.array(subtracted_intensity_array, dtype=float)

        elif parameters["how_data_points_will_be_subtracted"] == "Subtract to closest datapoint in energy (the x-axis will be assumed to have the same distance between points that they are on a on a linear energy scale)":
            # FIX: actually implemented this method
            # Use the x-axis of spectrum 0 as reference; for each point find closest in spectrum 1
            combined_x_values_array = np.copy(array_of_x_value_arrays[0])
            subtracted_intensity_array = np.zeros(len(combined_x_values_array))

            for i, x_val in enumerate(combined_x_values_array):
                closest_index = np.argmin(np.abs(array_of_x_value_arrays[1] - x_val))
                subtracted_intensity_array[i] = array_of_intensity_arrays[0][i] - array_of_intensity_arrays[1][closest_index]

            subtracted_intensity_array = np.array(subtracted_intensity_array, dtype=float)

        # Convert x-axis for the difference plot if needed
        if parameters["plot_outgoing_energy_instead_of_energy_loss"] and not parameters["subtract_spectra_on_emission_energy_axis_instead_of_energy_loss"]:
            combined_x_values_array = combined_x_values_array + float(parameters["incoming_energy_of_spectra_array"][0])
        elif not parameters["plot_outgoing_energy_instead_of_energy_loss"] and parameters["subtract_spectra_on_emission_energy_axis_instead_of_energy_loss"]:
            combined_x_values_array = combined_x_values_array - float(parameters["incoming_energy_of_spectra_array"][0])

        return combined_x_values_array, subtracted_intensity_array


    def plot_inputted_data(self, parameters, extra_plot_parameters):
        plt.close()

        self.array_of_intensity_arrays, self.array_of_x_values_arrays = self.get_arrays_of_x_values_and_intenisty_arrays(parameters)

        # FIX: figsize expects inches, not pixels
        fig_width = float(parameters["plot_figure_size_x_array"][0])
        fig_height = float(parameters["plot_figure_size_y_array"][0])
        self.figure_to_save = plt.figure(figsize=(fig_width, fig_height), dpi=100)
        self.figure_to_save.set_frameon(False)

        ax1 = self.figure_to_save.add_subplot(2, 1, 1)  # Top: original spectra
        ax2 = self.figure_to_save.add_subplot(2, 1, 2)  # Bottom: difference
        
        plot_color_array, linestyles_array = self.get_plot_color_and_linestyle_array(parameters)

        # Work on copies so scaling/smoothing doesn't accumulate on repeated updates
        array_of_intensity_arrays_to_plot = [np.copy(arr) for arr in self.array_of_intensity_arrays]
        array_of_x_values_arrays_to_plot = [np.copy(arr) for arr in self.array_of_x_values_arrays]

        # Convert x-axis to emission energy or energy loss as configured
        if parameters["subtract_spectra_on_emission_energy_axis_instead_of_energy_loss"]:
            for idx in range(2):
                if np.any(array_of_x_values_arrays_to_plot[idx] < 0):
                    array_of_x_values_arrays_to_plot[idx] = array_of_x_values_arrays_to_plot[idx] + float(parameters["incoming_energy_of_spectra_array"][idx])
        else:
            for idx in range(2):
                if not np.any(array_of_x_values_arrays_to_plot[idx] < 0):
                    array_of_x_values_arrays_to_plot[idx] = array_of_x_values_arrays_to_plot[idx] - float(parameters["incoming_energy_of_spectra_array"][idx])

        legend_array = []
        for array_index in range(2):
            if parameters["is_hide_certain_spectra_array"][array_index]:
                legend_array.append(parameters["plot_legend_names_array"][array_index])
                continue

            # Normalize at a certain emission energy if requested
            if parameters["is_normalize_intensity_at_certain_emission_energy"]:
                e_norm = float(parameters["emission_energy_for_intenisty_normalization"])
                e_range = float(parameters["emission_energy_above_and_below_for_normalization"])
                idx_start = np.nanargmin(np.abs(array_of_x_values_arrays_to_plot[array_index] - (e_norm - e_range)))
                idx_end = np.nanargmin(np.abs(array_of_x_values_arrays_to_plot[array_index] - (e_norm + e_range)))
                if idx_start != idx_end:
                    lo, hi = min(idx_start, idx_end), max(idx_start, idx_end)
                    avg = np.average(array_of_intensity_arrays_to_plot[array_index][lo:hi])
                else:
                    avg = array_of_intensity_arrays_to_plot[array_index][idx_start]
                if avg != 0:
                    array_of_intensity_arrays_to_plot[array_index] /= avg

            # Scale intensity
            if parameters["plot_is_scale_intensity_of_spectra_array"][array_index]:
                scale_factor = float(parameters["plot_scaling_array"][array_index])
                array_of_intensity_arrays_to_plot[array_index] *= scale_factor
                formatted_scaling_text = "{:.{}g}".format(scale_factor, 8)
                ax1.text(float(parameters["plot_scaling_text_x_offset_array"][array_index]),
                         float(parameters["plot_scaling_text_y_offset_array"][array_index]),
                         "x" + formatted_scaling_text,
                         fontsize=float(parameters["plot_incoming_energy_text_size"]),
                         color=plot_color_array[array_index])

            # Intensity offset
            if float(parameters["plot_intensity_offset_array"][array_index]) != 0:
                array_of_intensity_arrays_to_plot[array_index] += float(parameters["plot_intensity_offset_array"][array_index])

            # Smoothing: binning (global overrides per-spectrum)
            if parameters["is_binning_smooth_data_for_all_spectra"]:
                n_bins = int(parameters["number_of_bins_for_smoothing_array"][0])
                array_of_intensity_arrays_to_plot[array_index] = smoothing_scripts.bin_intensity_array(array_of_intensity_arrays_to_plot[array_index], n_bins)
                array_of_x_values_arrays_to_plot[array_index] = smoothing_scripts.bin_energy_array(array_of_x_values_arrays_to_plot[array_index], n_bins)
            elif parameters["is_binning_smooth_data_array"][array_index]:
                n_bins = int(parameters["number_of_bins_for_smoothing_array"][array_index])
                array_of_intensity_arrays_to_plot[array_index] = smoothing_scripts.bin_intensity_array(array_of_intensity_arrays_to_plot[array_index], n_bins)
                array_of_x_values_arrays_to_plot[array_index] = smoothing_scripts.bin_energy_array(array_of_x_values_arrays_to_plot[array_index], n_bins)
            # Smoothing: gaussian (global overrides per-spectrum)
            elif parameters["is_gaussian_smooth_data_for_all_spectra"]:
                sigma = float(parameters["sigma_for_gaussian_smoothing_array"][0])
                array_of_intensity_arrays_to_plot[array_index] = gaussian_filter1d(array_of_intensity_arrays_to_plot[array_index], sigma)
            elif parameters["is_gaussian_smooth_data_array"][array_index]:
                sigma = float(parameters["sigma_for_gaussian_smoothing_array"][array_index])
                array_of_intensity_arrays_to_plot[array_index] = gaussian_filter1d(array_of_intensity_arrays_to_plot[array_index], sigma)

            array_of_intensity_arrays_to_plot[array_index] = np.asarray(array_of_intensity_arrays_to_plot[array_index])

            ax1.plot(array_of_x_values_arrays_to_plot[array_index],
                     array_of_intensity_arrays_to_plot[array_index],
                     label=parameters["plot_legend_names_array"][array_index],
                     color=plot_color_array[array_index],
                     linestyle=linestyles_array[array_index])

            legend_array.append(parameters["plot_legend_names_array"][array_index])

        # Store for saving
        self.original_array_of_x_values_arrays_to_save = [np.copy(a) for a in array_of_x_values_arrays_to_plot]
        self.original_array_of_intensity_arrays_to_plot = [np.copy(a) for a in array_of_intensity_arrays_to_plot]

        # --- Axis limits ---
        if parameters["is_energy_window_used_array"][0]:
            ax1.set_xlim(float(parameters["plot_energy_loss_min_array"][0]), float(parameters["plot_energy_loss_max_array"][0]))
            ax2.set_xlim(float(parameters["plot_energy_loss_min_array"][0]), float(parameters["plot_energy_loss_max_array"][0]))

        if parameters["is_plot_intensity_limits_used_array"][0]:
            ax1.set_ylim(float(parameters["plot_intensity_min_array"][0]), float(parameters["plot_intensity_max_array"][0]))

        if parameters["plot_display_sample_name_title"]:
            ax1.set_title(parameters["plot_title"], fontsize=parameters["plot_title_size"])
        
        if parameters["is_plot_grid"]:
            ax1.grid(which='both', axis='x')
            ax2.grid(which='both', axis='x')

        if parameters["is_display_legend"]:
            ax1.legend(legend_array, fontsize=parameters["plot_legend_text_size"], loc="best")

        # Axis labels for top subplot
        if parameters["subtract_spectra_on_emission_energy_axis_instead_of_energy_loss"]:
            ax1.set_xlabel("Emission energy [eV]", fontsize=parameters["plot_x_axis_text_size"])
        else:
            ax1.set_xlabel("Energy loss [eV]", fontsize=parameters["plot_x_axis_text_size"])
        ax1.set_ylabel("Intensity [a.u]", fontsize=parameters["plot_y_axis_text_size"])

        # Axis labels for bottom subplot
        if parameters["plot_outgoing_energy_instead_of_energy_loss"]:
            ax2.set_xlabel("Emission energy [eV]", fontsize=parameters["plot_x_axis_text_size"])
        else:
            ax2.set_xlabel("Energy loss [eV]", fontsize=parameters["plot_x_axis_text_size"])
        ax2.set_ylabel("Intensity [a.u]", fontsize=parameters["plot_y_axis_text_size"])

        ax1.minorticks_on()
        ax2.minorticks_on()
        ax1.xaxis.set_tick_params(labelsize=parameters["plot_x_axis_number_size"])
        ax1.yaxis.set_tick_params(labelsize=parameters["plot_y_axis_number_size"])
        ax2.xaxis.set_tick_params(labelsize=parameters["plot_x_axis_number_size"])
        ax2.yaxis.set_tick_params(labelsize=parameters["plot_y_axis_number_size"])

        # --- Subtraction ---
        subtracted_x_value_array, subtracted_intensity_array = self.subtract_spectra(
            parameters, array_of_x_values_arrays_to_plot, array_of_intensity_arrays_to_plot
        )

        self.subtracted_x_value_array_to_save = subtracted_x_value_array
        self.subtracted_intensity_array_to_save = subtracted_intensity_array

        ax2.plot(subtracted_x_value_array, subtracted_intensity_array, color='black')
        ax2.axhline(y=0, color='gray', linestyle='--', linewidth=0.5)

        # --- Window layout ---
        plots_manager = plt.get_current_fig_manager()
        screen_geometry = QDesktopWidget().screenGeometry()
        self.figure_to_save.set_size_inches(fig_width, fig_height, forward=True)
        self.figure_to_save.tight_layout()
        self.figure_to_save.show()


    def plot_only_raw_data(self, parameters):
        plt.close()

        incoming_energy_array = self.get_incoming_energy_array(parameters)
        
        if parameters["input_file_format"] == "h5":
            raw_intensity_array = get_single_spectrum_h5_or_txt_file_scripts.get_single_spectrum_h5_file(parameters, parameters["h5_root_location_data"], False, "")
        elif parameters["input_file_format"] == "txt":
            raw_intensity_array = get_single_spectrum_h5_or_txt_file_scripts.get_single_spectrum_txt_file(parameters, False, parameters["txt_intensity_data_row"], parameters["txt_intensity_data_column"], False, "", parameters["is_several_spectra_per_file"])
        
        # FIX: was using ax1 but variable was named ax
        fig, ax = plt.subplots(1)
        ax.plot(incoming_energy_array, raw_intensity_array)
        ax.set_xlabel('Excitation energy [eV]')
        ax.set_ylabel('Intensity [a.u]')
        
        plots_manager = plt.get_current_fig_manager()
        screen_geometry = QDesktopWidget().screenGeometry()
        plots_manager.window.setGeometry(50, 80, floor(screen_geometry.width()/2 - 50), floor(screen_geometry.height() - 200))
        fig.show()


    def get_inputted_parameters_from_gui(self):
        return self.parameters

if __name__ == '__main__':
    input_file_location = "C:\\Users\\ponto479\\Documents\\02 Beamtime Data\\SLS Adress 03-2022\\RIXS"
    parameters = parameter_scripts.get_parameters(input_file_location)
    parameters["is_view_roots_or_input_txt"]
    parameters = run_main_gui(parameters)