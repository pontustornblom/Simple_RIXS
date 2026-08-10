#select_PFY_region
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
import matplotlib.pyplot as plt
from matplotlib.pyplot import cm
import subprocess
from scipy.optimize import curve_fit
from scipy import stats
import json
import h5py
from matplotlib.patches import Rectangle
import parameter_scripts
import get_single_spectrum_h5_or_txt_file_scripts
import iteratable_number_to_int_script
import iteratable_number_to_float_script
import find_elastic_peak_maximum_script
#import create_complete_file_location_view_roots_or_txt_script
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
        #self.is_energy_window_used_displayed= False
        self.is_plot_intensity_limits_used_displayed= False
        self.is_first_time_creating_pfy_regions= True
        #self.is_first_and_last_spectrum_displayed= False
        
        self.vbox = QVBoxLayout()

        self.vbox.addLayout(self.create_gui_item("input_file_project_folder", "Folder of the current project: ", "q_line_edit", [""]))
        self.vbox.addLayout(self.create_gui_item("input_file_raw_data_folder", "Subfolder where the raw data is stored: ", "q_line_edit", [""]))
        self.vbox.addLayout(self.create_gui_item("open file location", "Open raw data file location", "q_push_button",  [""]))   

        self.vbox.addLayout(self.create_gui_item("Update the plot", "Update the plot", "q_push_button",  [""]))

        self.vbox.addLayout(self.create_bottom_buttons())

        self.vbox.addLayout(self.create_gui_item("plot_colormap_choice", "Which colormap would you like to have? \n (turbo is recommended) ", "q_combo_box", ["turbo", "viridis", "gist_earth", "gist_stern", "inferno", "plasma", "gray", "gnuplot", "gist_rainbow"]))
        
        self.vbox.addLayout(self.create_gui_item("is_plot_intensity_limits_used_array_0", "Would you like to set an intensity window for the plot? ", "q_check_box", [""]))
        if self.parameters["is_plot_intensity_limits_used_array"][0]:
            self.vbox.addLayout(self.create_gui_item("plot_intensity_min_array_0", "Input the lower cut off for the incoming energy window: ", "q_line_edit", [""]))
            self.vbox.addLayout(self.create_gui_item("plot_intensity_max_array_0", "Input the upper cut off for the incoming energy window: ", "q_line_edit", [""]))
            self.is_plot_intensity_limits_used_displayed= True 

        #self.vbox.addLayout(self.create_gui_item("is_energy_window_used_array_0", "Would you like to set an energy window for the plot? ", "q_check_box", [""]))
        #if self.parameters["is_energy_window_used_array"][0]:
        #    self.vbox.addLayout(self.create_gui_item("plot_incoming_energy_min_array_0", "Input the lower cut off for the incoming energy window: ", "q_line_edit", [""]))
        #    self.vbox.addLayout(self.create_gui_item("plot_incoming_energy_max_array_0", "Input the upper cut off for the incoming energy window: ", "q_line_edit", [""]))
        #    self.vbox.addLayout(self.create_gui_item("plot_energy_loss_min_array_0", "Input the lower cut off for the emission energy window: ", "q_line_edit", [""]))
        #    self.vbox.addLayout(self.create_gui_item("plot_energy_loss_max_array_0", "Input the upper cut off for the emission energy window: ", "q_line_edit", [""]))
        #    self.is_energy_window_used_displayed= True 

        self.vbox.addLayout(self.create_gui_item("number_of_pfy_regions", "How many PFY areas would you like to select? ", "q_line_edit", [""]))
        if self.parameters["number_of_pfy_regions"] != "" and self.parameters["number_of_pfy_regions"] != "0":
            self.create_dynamic_pfy_gui_items(self.item_number_of_pfy_regions, self.item_number_of_pfy_regions.text(), "number_of_pfy_regions", self.hbox_number_of_pfy_regions)
        
        self.vbox.addLayout(self.create_gui_item("plot_outgoing_energy_instead_of_energy_loss", "Would you like to have the maps as emission energy insead of energy loss? ", "q_check_box", [""]))

        self.vbox.addLayout(self.create_gui_item("Update the plot", "Update the plot", "q_push_button",  [""]))

        self.vbox.addLayout(self.create_gui_item("", "The following inputs does not effect the calculation, it affects the saved file name", "q_text_label", [""]))
        self.vbox.addLayout(self.create_gui_item("output_file_element", "Element that is being studied: ", "q_line_edit", [""]))
        self.vbox.addLayout(self.create_gui_item("output_file_edge", "Edge that is being studied: ", "q_combo_box", ["K-edge", "L-edge", "L1-edge", "L2-edge", "L3-edge", "M-edge", "M1-edge", "M5-edge"]))
        self.vbox.addLayout(self.create_gui_item("output_file_sample_name", "Sample series name: ", "q_line_edit", [""]))
        self.vbox.addLayout(self.create_gui_item("output_file_additional_comment", "Addional comment that will be saved with the file name: ", "q_line_edit", [""]))
        
        self.vbox.addLayout(self.create_gui_item("", "If everything looks good then a figure will be saved when you hit Save and continue", "q_text_label", [""]))

        self.is_first_time_creating_pfy_regions= False



        self.vbox.addLayout(self.create_bottom_buttons())

        self.central_widget = QWidget()
        self.central_widget.setLayout(self.vbox)
        self.setCentralWidget(self.central_widget)

        #Scrollstuff:
        self.scroll = QScrollArea()
        self.scroll.setWidget(self.central_widget)
        self.scroll.setWidgetResizable(True)
        self.setCentralWidget(self.scroll)

        self.setWindowTitle("Simple RIXS select PFY region")
        self.show()

        #if self.is_first_and_last_spectrum_displayed== False:
        #self.try_to_plot(self.parameters, "")
        self.plot_inputted_data(self.parameters, "")
        #This line below has to be toggleed manually (If this script actually needs to plot something)
        
        
        #parameters, complete_file_location = create_complete_file_location_view_roots_or_txt_script.create_complete_file_location_view_roots_or_txt(self.parameters)

    def create_gui_item(self, key, item_label_text, item_type, combo_box_options):
        hbox = QHBoxLayout()
        item_label = QLabel(item_label_text)
        if item_type =="q_line_edit":
            hbox.addWidget(item_label)
            if key == "number_of_pfy_regions":
                self.hbox_number_of_pfy_regions = QHBoxLayout()
                self.hbox_number_of_pfy_regions.addWidget(item_label)
                self.item_number_of_pfy_regions = QLineEdit(self.parameters[key])
                self.hbox_number_of_pfy_regions.addWidget(self.item_number_of_pfy_regions)
                self.item_number_of_pfy_regions.editingFinished.connect(lambda item=self.item_number_of_pfy_regions, key=key: self.create_dynamic_pfy_gui_items(item, item.text(), key, self.hbox_number_of_pfy_regions))
                return self.hbox_number_of_pfy_regions
            elif "array" in key:
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
            elif key != "input_file_project_folder" and key != "input_file_raw_data_folder" and key != "output_file_element" and key != "output_file_sample_name" and key != "output_file_additional_comment":
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
                item.clicked.connect(lambda: self.try_to_plot(self.parameters, "update_plot"))
        elif item_type=="q_text_label":
            hbox.addWidget(item_label)
        else:
            print("Error: Item was not added to the GUI")
        return hbox          

    def create_dynamic_pfy_gui_items(self, item, item_text, key, hbox):
        if self.validate_input(item, key):
            if self.is_first_time_creating_pfy_regions== False:
                if self.parameters[key]!= "":
                    old_number_of_pfy_regions= int(self.parameters[key])
                else:
                    old_number_of_pfy_regions=0
                self.update_dictionary(key, item.text())
                if old_number_of_pfy_regions>0:
                    for pfy_region in range(old_number_of_pfy_regions):
                        self.remove_item(self.vbox.indexOf(hbox)+3*pfy_region+1)
                        self.remove_item(self.vbox.indexOf(hbox)+3*pfy_region+2)
                        self.remove_item(self.vbox.indexOf(hbox)+3*pfy_region+3)
            if int(item_text) != 0:
                for pfy_region in range(int(item_text)):
                    self.vbox.insertLayout(self.vbox.indexOf(hbox)+3*pfy_region+1,self.create_gui_item("pfy_region_name_array_"+ str(pfy_region), "Name of PFY region "+ str(pfy_region)+":                     ", "q_line_edit", [""]))
                    self.vbox.insertLayout(self.vbox.indexOf(hbox)+3*pfy_region+2,self.create_gui_item("pfy_energy_loss_start_array_"+ str(pfy_region), "Lowest emission energy of PFY region "+ str(pfy_region)+":                     ", "q_line_edit", [""]))
                    self.vbox.insertLayout(self.vbox.indexOf(hbox)+3*pfy_region+3,self.create_gui_item("pfy_energy_loss_end_array_"+ str(pfy_region), "Highest emission energy of PFY region "+ str(pfy_region)+ ":                     ", "q_line_edit", [""]))


    def update_dictionary(self, key, updated_value):
        self.parameters[key] = updated_value

    def update_dictionary_checkbox(self, key, item):
                if item.isChecked():
                    self.parameters[key] = True
                    if key== "is_view_roots_or_input_txt":
                        self.vbox.insertLayout(self.vbox.count()-1,self.create_gui_item("input_complete_file_name_array_0", "Input example file name to view roots/txt ", "q_line_edit", [""]))                
                else:
                    self.parameters[key] = False

    def update_dictionary_checkbox_array(self, key, array_index, item):
            #if self.validate_input_for_array(key, array_index, item):
            self.parameters[key][array_index] = item.isChecked()


    def update_dictionary_array(self, key, array_index, item):
            if self.validate_input_for_array(key, array_index, item) or key[:16] == "pfy_region_name_":
                self.parameters[key][array_index] = item.text()

    def validate_input_for_array(self, key, array_index, item):
        if item.text() != self.parameters[key][array_index] and key[:16] != "pfy_region_name_":
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
        if item.text() != self.parameters[key] or key == "number_of_pfy_regions":
            if key != "number_of_pfy_regions":
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
        #This function is not used. It has been replaced by create_multiple_gui_items_from_checkbox_arrays for all cases I think
        if key == "is_energy_window_used":
            if self.is_energy_window_used_displayed== False and self.parameters["is_energy_window_used"]:
                self.vbox.insertLayout(self.vbox.indexOf(hbox)+1, self.create_gui_item("plot_incoming_energy_min", "Input the lower cut off for the incoming energy window: ", "q_line_edit", [""]))
                self.vbox.insertLayout(self.vbox.indexOf(hbox)+2, self.create_gui_item("plot_incoming_energy_max", "Input the upper cut off for the incoming energy window: ", "q_line_edit", [""]))            
                self.vbox.insertLayout(self.vbox.indexOf(hbox)+1, self.create_gui_item("plot_energy_loss_min", "Input the lower cut off for the emission energy window: ", "q_line_edit", [""]))
                self.vbox.insertLayout(self.vbox.indexOf(hbox)+2, self.create_gui_item("plot_energy_loss_max", "Input the upper cut off for the emission energy window: ", "q_line_edit", [""]))            
                self.is_energy_window_used_displayed =True
            elif self.is_energy_window_used_displayed == True and self.parameters["is_energy_window_used"] == False:
                self.remove_item(self.vbox.indexOf(hbox)+1)
                self.remove_item(self.vbox.indexOf(hbox)+2)
                self.remove_item(self.vbox.indexOf(hbox)+3)
                self.remove_item(self.vbox.indexOf(hbox)+4)
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
    
        if key == "is_energy_window_used_array":
            if self.is_energy_window_used_displayed== False and self.parameters["is_energy_window_used_array"][array_index]:
                self.vbox.insertLayout(self.vbox.indexOf(hbox)+1,self.create_gui_item("plot_incoming_energy_min_array_" + str(array_index), "Input the lower cut off for the incoming energy window: ", "q_line_edit", [""]))
                self.vbox.insertLayout(self.vbox.indexOf(hbox)+2,self.create_gui_item("plot_incoming_energy_max_array_" + str(array_index), "Input the upper cut off for the incoming energy window: ", "q_line_edit", [""]))
                self.vbox.insertLayout(self.vbox.indexOf(hbox)+3,self.create_gui_item("plot_energy_loss_min_array_" + str(array_index), "Input the lower cut off for the incoming energy window: ", "q_line_edit", [""]))
                self.vbox.insertLayout(self.vbox.indexOf(hbox)+4,self.create_gui_item("plot_energy_loss_max_array_" + str(array_index), "Input the upper cut off for the incoming energy window: ", "q_line_edit", [""]))
                self.is_energy_window_used_displayed =True
            elif self.is_energy_window_used_displayed== True and self.parameters["is_energy_window_used_array"][array_index] == False:
                self.remove_item(self.vbox.indexOf(hbox)+1)
                self.remove_item(self.vbox.indexOf(hbox)+2)
                self.remove_item(self.vbox.indexOf(hbox)+3)
                self.remove_item(self.vbox.indexOf(hbox)+4)
                self.is_energy_window_used_displayed =False
        elif key == "is_plot_intensity_limits_used_array":
            if self.is_plot_intensity_limits_used_displayed== False and self.parameters["is_plot_intensity_limits_used_array"][array_index]:
                self.vbox.insertLayout(self.vbox.indexOf(hbox)+1, self.create_gui_item("plot_intensity_min_array_" + str(array_index), "Input the lower cut off for the intensity window: ", "q_line_edit", [""]))
                self.vbox.insertLayout(self.vbox.indexOf(hbox)+2, self.create_gui_item("plot_intensity_max_array_" + str(array_index), "Input the upper cut off for the intensity window: ", "q_line_edit", [""]))
                self.is_plot_intensity_limits_used_displayed =True
            elif self.is_plot_intensity_limits_used_displayed == True and self.parameters["is_plot_intensity_limits_used_array"][array_index] == False:
                self.remove_item(self.vbox.indexOf(hbox)+1)
                self.remove_item(self.vbox.indexOf(hbox)+2)
                self.is_plot_intensity_limits_used_displayed =False

    def create_dynamic_gui_item(self, item, item_text, key, hbox, new_key, new_label_text):
        if self.validate_input(item, key):
            if self.is_first_time_creating_checkboxes== False:
                if self.parameters[key]!= "":
                    old_number_of_segments= int(self.parameters[key])
                else:
                    old_number_of_segments=0
                self.update_dictionary(key, item.text())
                if old_number_of_segments>0:
                    for segment in range(2*old_number_of_segments):
                        self.remove_item(self.vbox.indexOf(hbox)+segment+1)
                    self.remove_item(self.vbox.indexOf(hbox)+2*old_number_of_segments+1)
            if int(item_text) != 0:
                for segment in range(int(item_text)):
                    self.vbox.insertLayout(self.vbox.indexOf(hbox)+2*segment+1,self.create_gui_item("incoming_energy_segment_"+ str(segment), "First incoming energy of segment "+ str(segment)+":                     ", "q_line_edit", [""]))
                    self.vbox.insertLayout(self.vbox.indexOf(hbox)+2*segment+2,self.create_gui_item("incoming_energy_difference_in_segment_"+ str(segment), "Excitation energy difference of spectra in segment "+ str(segment)+ ":", "q_line_edit", [""]))
                self.vbox.insertLayout(self.vbox.indexOf(hbox)+2*int(item_text)+1,self.create_gui_item("incoming_energy_of_last_spectra", "Excitation energy of last spectra: ", "q_line_edit", [""]))


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
        figure_name= "PFY_regions_on_map"
        figure_name+="_" + self.parameters["output_file_element"]
        figure_name+="_" + self.parameters["output_file_edge"]
        figure_name+="_" + self.parameters["output_file_sample_name"]
        if self.parameters["plot_display_sample_name_title"]:
            figure_name+="_" + self.parameters["plot_title"]
        figure_name+="_" + self.parameters["input_number_of_complete_file_names"] + "_files"
        for spectra_index in range(int(self.parameters["number_of_pfy_regions"])):
            figure_name+="_" + self.parameters["pfy_energy_loss_start_array"][spectra_index]
            figure_name+="_" + self.parameters["pfy_energy_loss_end_array"][spectra_index]
        if self.parameters["output_file_additional_comment"] != "":
            figure_name+="_" + self.parameters["output_file_additional_comment"]
        figure_parameters_name= figure_name
        figure_data_name= figure_name
        figure_name+="_figure.png"
        figure_parameters_name+="_parameters.txt"
        figure_data_name+= "_data.txt"
        figure_path= os.path.join(self.parameters["input_file_project_folder"], "Simple RIXS Figures")
        if not os.path.exists(figure_path):
            os.makedirs(figure_path)
        
        #full_figure_path= os.path.join(figure_path, figure_name)
        #self.figure_to_save.savefig(full_figure_path)

        #full_parameters_path=os.path.join(figure_path, figure_parameters_name)
        #with open(full_parameters_path, "w") as parameters_file:
        #    json.dump(self.parameters, parameters_file)


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
        
        for iteratable_int in range(first_iteratable_int, last_iteratable_int + 1):
            if iteratable_int not in ignored_numbers_array:
                iteratable_string= str(iteratable_int)
                while len(parameters["input_file_iteratable_file_number_start"]) > len(iteratable_string):
                    iteratable_string = "0" + iteratable_string
                iteratable_file_number_array.append(iteratable_string)

        return iteratable_file_number_array

    def get_approximate_channel_per_energy_and_incoming_energy_array(self, parameters, iteratable_file_number_array):
        #The different options in this function have not been tested thoroughly
        first_spectra_approximate_channel= iteratable_number_to_int_script.iteratable_number_to_int(parameters["approximate_channel_of_first_elastic_peak"])
        last_spectra_approximate_channel= iteratable_number_to_int_script.iteratable_number_to_int(parameters["approximate_channel_of_last_elastic_peak"])

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
            elif parameters["input_file_format"]== "txt":
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
            
        approximate_channel_per_energy= (first_spectra_approximate_channel - last_spectra_approximate_channel)/(incoming_energy_array[0] - incoming_energy_array[-1])

        return approximate_channel_per_energy, np.asarray(incoming_energy_array)

    def gaussian(self, x, A, mu, sigma):
        return A * np.exp(-(x - mu)**2 / (2 * sigma**2))
    
    def get_elastic_peak_channel_center_array(self, parameters, approximate_channel_per_energy, iteratable_file_number_array, incoming_energy_array ):
        channels_above_and_below_elastic_to_fit = int(parameters["channels_above_and_below_elastic_to_fit"])

        array_index=0
        elastic_peak_center_array= []
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
                    i0_mean= np.mean(i0_values)
                    y_values= y_values/i0_mean
                    
                elif parameters["is_i0_available_in_file"]:
                    i0_values = get_single_spectrum_h5_or_txt_file_scripts.get_single_spectrum_h5_file(parameters, parameters["i0_root_location_data"], True, iteratable_number)
                    i0_mean= np.mean(i0_values)
                    y_values= y_values/i0_mean
                array_of_intensity_arrays[intensity_array_index]= y_values
                intensity_array_index+= 1
            elif parameters["input_file_format"] =="txt":
                y_values = get_single_spectrum_h5_or_txt_file_scripts.get_single_spectrum_txt_file(parameters, False, parameters["txt_intensity_data_row"], parameters["txt_intensity_data_column"], True, iteratable_number, parameters["is_several_spectra_per_file"])
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
                        for iteratable_number in range(len(iteratable_file_number_array)):
                            i0_values[iteratable_number]= np.mean(i0_values[iteratable_number])
                    else:
                        for iteratable_number in range(len(iteratable_file_number_array)):
                            i0_values[iteratable_number]= i0_values[iteratable_number][0]

                    i0_mean= np.mean(i0_values)
                    y_values= y_values/i0_mean
                elif parameters["is_i0_available_in_file"]:
                    i0_values = get_single_spectrum_h5_or_txt_file_scripts.get_single_spectrum_h5_file(parameters, parameters["is_txt_single_i0_value"], parameters["txt_i0_row_in_file"], parameters["txt_i0_column_in_file"], True, iteratable_number)
                    i0_mean= np.mean(i0_values)
                    y_values= y_values/i0_mean
                array_of_intensity_arrays[intensity_array_index]= y_values
                intensity_array_index+= 1
            peak_channel_center=0
            sum_of_intensity_weight= 0
            highest_intensity, highest_intensity_channel = find_elastic_peak_maximum_script.find_elastic_peak_maximum(parameters, y_values, round(approximate_channel_per_energy*(incoming_energy_array[array_index] - incoming_energy_array[0]) + int(parameters["approximate_channel_of_first_elastic_peak"])))
            if parameters["is_weighted_elastic_peak_fit"]:
                for channel in range(highest_intensity_channel - channels_above_and_below_elastic_to_fit, highest_intensity_channel + channels_above_and_below_elastic_to_fit +1):
                    peak_channel_center+= y_values[channel]*channel
                    sum_of_intensity_weight+= y_values[channel]
                peak_channel_center = peak_channel_center/sum_of_intensity_weight
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

            array_index+=1
            elastic_peak_center_array.append(round(peak_channel_center))
        x_values = np.arange(1, len(y_values) + 1)

        return elastic_peak_center_array, x_values, array_of_intensity_arrays
    
    def nested_array_contains_negative_floats(self, nested_array):
        for array in nested_array:
            if np.any(array < 0):
                return True
        return False

    def try_to_plot(self, parameters, extra_plot_parameters):
        try:
            self.plot_inputted_data(parameters, extra_plot_parameters)
        except (IndexError, ValueError):
            print("Exception happened")
            self.plot_only_raw_data(parameters)
            

    def plot_inputted_data(self, parameters, extra_plot_parameters):
        plt.close()
        plots= []
        
        #parameters, complete_file_location = create_complete_file_location_view_roots_or_txt_script.create_complete_file_location_view_roots_or_txt(parameters, False, "")
        complete_file_location = create_complete_file_location_for_treated_data.create_complete_file_location_for_treated_data(parameters["input_file_project_folder"], parameters["input_complete_file_name_array"][0])
        
        array_of_x_value_arrays, incoming_energy_array, array_of_intensity_arrays = get_treated_rixs_data_script.get_treated_rixs_data(complete_file_location)
        
        self.figure_to_save, ax = plt.subplots(1)

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

        header_row= 0
        x_values_header_dataframe = pd.read_csv(complete_file_location, sep='\t', skiprows=header_row, usecols=[0], header=None)
        x_values_header= x_values_header_dataframe.iloc[0, 0]

        
        #intensity_max=100
        #intensity_min=0
        #vmax=intensity_max, vmin=intensity_min,
        array_of_intensity_arrays = np.vstack(array_of_intensity_arrays).astype(float)

        colormap = parameters["plot_colormap_choice"]
        #im = axs[0].imshow(array_of_intensity_arrays, cmap='viridis', origin='lower', extent=[x_values[0], x_values[-1], incoming_energy_array[0] - ((incoming_energy_array[1]-incoming_energy_array[0])/2), incoming_energy_array[-1] + ((incoming_energy_array[-1]-incoming_energy_array[-2])/2)] , aspect='auto')
        #im = axs.pcolormesh(x_values_array, y_values_array, array_of_intensity_arrays, cmap=colormap)

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
        if parameters["is_plot_intensity_limits_used_array"][array_index] and parameters["plot_waterfall_instead_of_heat_map"]== False:
            #im.set_clim(vmin=float(parameters["plot_intensity_min_array"][array_index]), vmax=float(parameters["plot_intensity_max_array"][array_index]))
            for spectra_index in range(len(array_of_intensity_arrays)):
                #incoming_energy = incoming_energy_array_to_plot[spectra_index : spectra_index + 2]
                im = ax.pcolormesh(array_of_x_value_arrays_to_plot[spectra_index], incoming_energy_array_to_plot[spectra_index : spectra_index + 2], [array_of_intensity_arrays[spectra_index]], cmap=colormap, shading = 'flat', vmin = float(parameters["plot_intensity_min_array"][array_index]), vmax = float(parameters["plot_intensity_max_array"][array_index]))
                ax.set_facecolor(cm.turbo(0))
        else:
            for spectra_index in range(len(array_of_intensity_arrays)):
                #incoming_energy = incoming_energy_array_to_plot[spectra_index : spectra_index + 2]
                im = ax.pcolormesh(array_of_x_value_arrays_to_plot[spectra_index], incoming_energy_array_to_plot[spectra_index : spectra_index + 2], [array_of_intensity_arrays[spectra_index]], cmap=colormap, shading = 'flat', vmin = min_intensity_value, vmax = max_intensity_value)
                ax.set_facecolor(cm.turbo(0))
        #ax.set_ylabel("Excitation energy [eV]", fontsize= parameters["plot_y_axis_text_size"])
            
        #array_of_energy_loss_arrays= np.zeros(len())
        fig = ax.figure
        cbar = ax.figure.colorbar(im, ax=ax)
        cbar.ax.tick_params(labelsize=14)
        
        ax.set_xlabel(x_values_header, fontsize = 16)
        ax.set_ylabel("Excitation energy [eV]", fontsize = 16)
        ax.tick_params(axis='y', labelsize=16)
        ax.tick_params(axis='x', labelsize=16)

        rectangle_colors_array= ['r','m','g','y','b','r--','m--','g--','y--','b--']
        for pfy_region in range(int(parameters["number_of_pfy_regions"])):
            try:
                energy_loss_start = float(parameters["pfy_energy_loss_start_array"][pfy_region])
                incoming_energy_start = float(incoming_energy_array[0] - 0.5 * (incoming_energy_array[1] - incoming_energy_array[0]))
                energy_loss_end = float(parameters["pfy_energy_loss_end_array"][pfy_region])
                incoming_energy_end = float(incoming_energy_array[-1] + 0.5 * (incoming_energy_array[-1] - incoming_energy_array[-2]))
                rect = Rectangle((energy_loss_start, incoming_energy_start), energy_loss_end - energy_loss_start, incoming_energy_end - incoming_energy_start, facecolor='none', edgecolor=rectangle_colors_array[pfy_region], linewidth= 3)
                plt.gca().add_patch(rect)
            except:
                print("Rectangle exception happened")
            #rect.set_alpha(0.0)
            

        
        plots_manager = plt.get_current_fig_manager()
        screen_geometry = QDesktopWidget().screenGeometry()
        plots_manager.window.setGeometry(50,80,floor(screen_geometry.width()/2 -50), floor(screen_geometry.height()-200))
        #fig.tight_layout()
#        self.figure_to_save, ax = plt.subplots(1)
#        im3 = ax.pcolormesh(x_values, incoming_energy_array, array_of_intensity_arrays, cmap=colormap)
        #if parameters["plot_display_color_bar"]:
        #   cbar = fig.colorbar(im3, ax=ax)

#        if self.treated_parameters["is_energy_window_used_array"][0]:
#            axs.set_xlim(float(self.treated_parameters["plot_energy_loss_min_array"][0]), float(self.treated_parameters["plot_energy_loss_max_array"][0]))
#            axs.set_ylim(float(self.treated_parameters["plot_incoming_energy_min_array"][0]), float(self.treated_parameters["plot_incoming_energy_max_array"][0]))
#            ax.set_xlim(float(parameters["plot_energy_loss_min"]), float(parameters["plot_energy_loss_max"]))
#            ax.set_ylim(float(parameters["plot_incoming_energy_min"]), float(parameters["plot_incoming_energy_max"]))

        if parameters["is_plot_intensity_limits_used_array"][0]:
            im.set_clim(vmin=float(parameters["plot_intensity_min_array"][0]), vmax=float(parameters["plot_intensity_max_array"][0]))

        fig.show()

        # Show the plot
        #plt.show()
        
        #plt.plot(x_values,array_of_intensity_arrays)
        #plt.show()
        #plots_manager = plt.get_current_fig_manager()
        #screen_geometry = QDesktopWidget().screenGeometry()
        #plots_manager.window.setGeometry(50,80,floor(screen_geometry.width()/2 -50), floor(screen_geometry.height()-200))
        #self.fig.tight_layout()
        #self.fig.show()

        #plots.append([x_values, y_values, "Channel", "Counts" ])
        #y_values = get_single_spectrum_h5_or_txt_file_scripts.get_single_spectrum_h5_file(parameters, parameters["h5_root_location_data"], True, parameters["input_file_iteratable_file_number_end"])
        #x_values = [x for x in range(len(y_values))]
        #plots.append([x_values, y_values, "Channel", "Counts" ])
        
        '''
        self.fig, axs = plt.subplots(len(plots))
        for plot_number in range(len(plots)):
            axs[plot_number].plot(plots[plot_number][0],plots[plot_number][1])
            axs[plot_number].set(xlabel=plots[plot_number][2], ylabel= plots[plot_number][3])
            if extra_plot_parameters =="zoom_in_on_plot" or extra_plot_parameters == "update_plot":
                if plot_number == 0:
                    axs[plot_number].set_xlim([int(parameters["approximate_channel_of_first_elastic_peak"])-int(parameters["channels_above_and_below_for_finding_elastic"])*2, int(parameters["approximate_channel_of_first_elastic_peak"])+int(parameters["channels_above_and_below_for_finding_elastic"])*2])
                elif plot_number == 1:
                    axs[plot_number].set_xlim([int(parameters["approximate_channel_of_last_elastic_peak"])-int(parameters["channels_above_and_below_for_finding_elastic"])*2, int(parameters["approximate_channel_of_last_elastic_peak"])+int(parameters["channels_above_and_below_for_finding_elastic"])*2])
            if extra_plot_parameters == "update_plot":
                if plot_number == 0:
                    y_values = get_single_spectrum_h5_or_txt_file_scripts.get_single_spectrum_h5_file(parameters, parameters["h5_root_location_data"], True, parameters["input_file_iteratable_file_number_start"])
                    highest_intensity_first_graph, highest_intensity_channel_first_graph = find_elastic_peak_maximum_script.find_elastic_peak_maximum(parameters, y_values, int(parameters["approximate_channel_of_first_elastic_peak"]))
                    for channel in range(highest_intensity_channel_first_graph- int(parameters["channels_above_and_below_elastic_to_fit"]), highest_intensity_channel_first_graph+ int(parameters["channels_above_and_below_elastic_to_fit"])+ 1):
                        axs[plot_number].scatter(channel,y_values[channel], color="green")
                    axs[plot_number].scatter(highest_intensity_channel_first_graph,highest_intensity_first_graph, color="red")
                    axs[plot_number].axvline(int(parameters["approximate_channel_of_first_elastic_peak"])- int(parameters["channels_above_and_below_for_finding_elastic"]), color="red")
                    axs[plot_number].axvline(int(parameters["approximate_channel_of_first_elastic_peak"])+ int(parameters["channels_above_and_below_for_finding_elastic"]), color="red")
                elif plot_number == 1:
                    y_values = get_single_spectrum_h5_or_txt_file_scripts.get_single_spectrum_h5_file(parameters, parameters["h5_root_location_data"], True, parameters["input_file_iteratable_file_number_end"])
                    highest_intensity_last_graph, highest_intensity_channel_last_graph = find_elastic_peak_maximum_script.find_elastic_peak_maximum(parameters, y_values, int(parameters["approximate_channel_of_last_elastic_peak"]))
                    for channel in range(highest_intensity_channel_last_graph- int(parameters["channels_above_and_below_elastic_to_fit"]), highest_intensity_channel_last_graph+ int(parameters["channels_above_and_below_elastic_to_fit"])+ 1):
                        axs[plot_number].scatter(channel,y_values[channel], color="green")
                    axs[plot_number].scatter(highest_intensity_channel_last_graph,highest_intensity_last_graph, color="red")
                    axs[plot_number].axvline(int(parameters["approximate_channel_of_last_elastic_peak"])- int(parameters["channels_above_and_below_for_finding_elastic"]), color="red")
                    axs[plot_number].axvline(int(parameters["approximate_channel_of_last_elastic_peak"])+ int(parameters["channels_above_and_below_for_finding_elastic"]), color="red")

        if parameters["input_file_format"] =="txt":
            y_values = get_single_spectrum_h5_or_txt_file_scripts.get_single_spectrum_txt_file(parameters, False, parameters["txt_intensity_data_row"], parameters["txt_intensity_data_column"], True, parameters["input_file_iteratable_file_number_start"])
            x_values = [x for x in range(len(y_values))]
            plots.append([x_values, y_values, "Channel", "Counts" ])
            y_values = get_single_spectrum_h5_or_txt_file_scripts.get_single_spectrum_txt_file(parameters, False, parameters["txt_intensity_data_row"], parameters["txt_intensity_data_column"], True, parameters["input_file_iteratable_file_number_end"])
            x_values = [x for x in range(len(y_values))]
            plots.append([x_values, y_values, "Channel", "Counts" ])

            self.fig, axs = plt.subplots(len(plots))
            for plot_number in range(len(plots)):
                axs[plot_number].plot(plots[plot_number][0],plots[plot_number][1])
                axs[plot_number].set(xlabel=plots[plot_number][2], ylabel= plots[plot_number][3])
                if extra_plot_parameters =="zoom_in_on_plot" or extra_plot_parameters == "update_plot":
                    if plot_number == 0:
                        axs[plot_number].set_xlim([int(parameters["approximate_channel_of_first_elastic_peak"])-int(parameters["channels_above_and_below_for_finding_elastic"])*2, int(parameters["approximate_channel_of_first_elastic_peak"])+int(parameters["channels_above_and_below_for_finding_elastic"])*2])
                    elif plot_number == 1:
                        axs[plot_number].set_xlim([int(parameters["approximate_channel_of_last_elastic_peak"])-int(parameters["channels_above_and_below_for_finding_elastic"])*2, int(parameters["approximate_channel_of_last_elastic_peak"])+int(parameters["channels_above_and_below_for_finding_elastic"])*2])
                if extra_plot_parameters == "update_plot":
                    if plot_number == 0:
                        y_values = get_single_spectrum_h5_or_txt_file_scripts.get_single_spectrum_h5_file(parameters, parameters["h5_root_location_data"], True, parameters["input_file_iteratable_file_number_start"])
                        highest_intensity_first_graph, highest_intensity_channel_first_graph = find_elastic_peak_maximum_script.find_elastic_peak_maximum(parameters, y_values, int(parameters["approximate_channel_of_first_elastic_peak"]))
                        for channel in range(highest_intensity_channel_first_graph- int(parameters["channels_above_and_below_elastic_to_fit"]), highest_intensity_channel_first_graph+ int(parameters["channels_above_and_below_elastic_to_fit"])+ 1):
                            axs[plot_number].scatter(channel,y_values[channel], color="green")
                        axs[plot_number].scatter(highest_intensity_channel_first_graph,highest_intensity_first_graph, color="red")
                        axs[plot_number].axvline(highest_intensity_channel_first_graph- int(parameters["channels_above_and_below_for_finding_elastic"]), color="red")
                        axs[plot_number].axvline(highest_intensity_channel_first_graph+ int(parameters["channels_above_and_below_for_finding_elastic"]), color="red")
                    elif plot_number == 1:
                        y_values = get_single_spectrum_h5_or_txt_file_scripts.get_single_spectrum_h5_file(parameters, parameters["h5_root_location_data"], True, parameters["input_file_iteratable_file_number_end"])
                        highest_intensity_last_graph, highest_intensity_channel_last_graph = find_elastic_peak_maximum_script.find_elastic_peak_maximum(parameters, y_values, int(parameters["approximate_channel_of_last_elastic_peak"]))
                        for channel in range(highest_intensity_channel_last_graph- int(parameters["channels_above_and_below_elastic_to_fit"]), highest_intensity_channel_last_graph+ int(parameters["channels_above_and_below_elastic_to_fit"])+ 1):
                            axs[plot_number].scatter(channel,y_values[channel], color="green")
                        axs[plot_number].scatter(highest_intensity_channel_last_graph,highest_intensity_last_graph, color="red")
                        axs[plot_number].axvline(highest_intensity_channel_last_graph- int(parameters["channels_above_and_below_for_finding_elastic"]), color="red")
                        axs[plot_number].axvline(highest_intensity_channel_last_graph+ int(parameters["channels_above_and_below_for_finding_elastic"]), color="red")
        plots_manager = plt.get_current_fig_manager()
        screen_geometry = QDesktopWidget().screenGeometry()
        plots_manager.window.setGeometry(50,80,floor(screen_geometry.width()/2 -50), floor(screen_geometry.height()-200))
        self.fig.tight_layout()
        self.fig.show()
        '''

    def plot_only_raw_data(self, parameters):
        plt.close()

        parameters, complete_file_location = create_complete_file_location_view_roots_or_txt_script.create_complete_file_location_view_roots_or_txt(parameters, False, "")
        header_row= 0
        data_row = 1
        second_column_header_dataframe= pd.read_csv(complete_file_location, sep='\t', skiprows=header_row, usecols=[1], header=None)
        second_column_header= second_column_header_dataframe.iloc[0, 0]
        
        if second_column_header[:9]== "Intensity":
            intensity_column= int(parameters["txt_intensity_data_column"])
        elif second_column_header[:15]== "Excitation energy":
            incoming_energy_dataframe= pd.read_csv(complete_file_location, sep='\t', skiprows=data_row, usecols=[1], header=None, na_values=['NaN'])
            incoming_energy_array= incoming_energy_dataframe.iloc[:, 0].values #It should be intensity_column here even though it is the row.
        incoming_energy_array = incoming_energy_array[~np.isnan(incoming_energy_array)]

        intensity_dataframe = pd.read_csv(complete_file_location, sep='\t', skiprows=data_row, header=None)
        intensity_dataframe.drop(columns=[0, 1], inplace=True)
        array_of_intensity_arrays= np.zeros(len(incoming_energy_array), dtype=object)

        for spectra_number in range(len(incoming_energy_array)):
            array_of_intensity_arrays[spectra_number]= intensity_dataframe.iloc[:, spectra_number].values
        
        x_values_dataframe= pd.read_csv(complete_file_location, sep='\t', skiprows=data_row, usecols=[0], header=None)
        x_values= x_values_dataframe.iloc[:, 0].values

        x_values_header_dataframe = pd.read_csv(complete_file_location, sep='\t', skiprows=header_row, usecols=[0], header=None)
        self.x_values_header= x_values_header_dataframe.iloc[0, 0]

        
        fig, ax = plt.subplots(1)

        colormap = parameters["plot_colormap_choice"]
        array_of_intensity_arrays = np.vstack(array_of_intensity_arrays).astype(float)
        #im = axs[0].imshow(array_of_intensity_arrays, cmap='viridis', origin='lower', extent=[x_values[0], x_values[-1], incoming_energy_array[0] - ((incoming_energy_array[1]-incoming_energy_array[0])/2), incoming_energy_array[-1] + ((incoming_energy_array[-1]-incoming_energy_array[-2])/2)] , aspect='auto')
        im = ax.pcolormesh(x_values, incoming_energy_array, array_of_intensity_arrays, cmap=colormap)

        #array_of_energy_loss_arrays= np.zeros(len())
        fig = ax.figure
        
        ax.set_xlabel(self.x_values_header, fontsize = 16)
        ax.set_ylabel('Excitation energy [eV]', fontsize = 16)
        ax.yaxis(fontsize=20)
        ax.xaxis(fontsize=20)
        
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
