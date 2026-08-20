#input_energy_per_channel_script
import sys
import os
from PyQt5.QtCore import QEventLoop
from PyQt5.QtCore import pyqtSignal
import platform
import subprocess
from PyQt5.QtWidgets import QLabel, QMainWindow, QCheckBox, QComboBox, QLineEdit, QPushButton, QLayout, QApplication, QVBoxLayout, QHBoxLayout, QWidget, QDesktopWidget, QLabel, QMessageBox, QScrollArea
#from PyQt5.QtCore import Qt, QSize
#from PyQt5.QtGui import QPixmap
#from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
#from matplotlib.figure import Figure
from math import floor
#import numpy as np
import matplotlib.pyplot as plt
#import subprocess
import parameter_scripts
import get_single_spectrum_h5_or_txt_file_scripts
import iteratable_number_to_int_script
import iteratable_number_to_float_script
import find_elastic_peak_maximum_script



class DropLineEdit(QLineEdit):
    """QLineEdit that accepts a dropped file and inserts its base name (with extension)."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            super().dragEnterEvent(event)

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            super().dragMoveEvent(event)

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        if not urls:
            return
        self.setText(os.path.basename(urls[0].toLocalFile()))
        event.acceptProposedAction()
        self.editingFinished.emit()

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
        #self.setMaximumHeight(floor(screen_geometry.height()))
        self.move(floor(screen_geometry.width()/2 +10), 10)

        self.is_first_time_creating_dynamic_items= True

        self.vbox = QVBoxLayout()

        self.vbox.addLayout(self.create_gui_item("input_file_project_folder", "Folder of the current project: ", "q_line_edit", [""]))
        self.vbox.addLayout(self.create_gui_item("input_file_raw_data_folder", "Subfolder where the raw data is stored: ", "q_line_edit", [""]))
        self.vbox.addLayout(self.create_gui_item("open file location", "Open raw data file location", "q_push_button",  [""]))   

        self.vbox.addLayout(self.create_gui_item("", " You previously prompted that you wanted to manually input the energy per channel slope and intercept.\n You therefore have to input that information below. ", "q_text_label", [""]))
        self.vbox.addLayout(self.create_gui_item("degree_of_energy_per_channel_polynomial", "What degree polynomial do you want to fit the elastic peaks to? (Set to 1 for linear) ", "q_line_edit", [""]))        
        self.create_dynamic_gui_item_for_polynomial_coefficients(self.item_polynomial_degree, self.item_polynomial_degree.text(), "degree_of_energy_per_channel_polynomial", self.hbox_polynomial_degree, "input_first_and_last_incoming_energy", "Input the incoming energy of the first and last spectra: ")
        for coefficients_index in range(int(self.parameters["degree_of_energy_per_channel_polynomial"]) + 1):
            self.vbox.addLayout(self.create_gui_item("energy_per_channel_polynomial_coefficients_array_" + str(coefficients_index), "What coefficient do you want for coefficient " + str(coefficients_index) + "? \nNote: The first coefficient is for the lowest rank term and the last is for the highest.", "q_line_edit", [""]))

        #self.vbox.addLayout(self.create_gui_item("energy_per_channel_slope_of_elastic_peak", "Input the energy per channel: \n(The slope of a line going through the elastic peaks)", "q_line_edit", [""]))
        #self.vbox.addLayout(self.create_gui_item("energy_per_channel_intercept_of_elastic_peak", "Input the intercept of the line going through the elastic peaks: ", "q_line_edit", [""]))

               
        #if self.parameters["is_incoming_energy_available_in_file"] == False:
        #    self.vbox.addLayout(self.create_gui_item("energy_of_first_line_spectra", "Incoming energy of first spectra [eV]: ", "q_line_edit", [""]))
        #    self.vbox.addLayout(self.create_gui_item("energy_of_last_line_spectra", "Incoming energy of last spectra [eV]: ", "q_line_edit", [""]))

        self.is_first_time_creating_dynamic_items= False

        self.vbox.addLayout(self.create_bottom_buttons())

        self.central_widget = QWidget()
        #self.central_widget.setWidgetResizable(True)

        self.central_widget.setLayout(self.vbox)
        
        self.setCentralWidget(self.central_widget)
        #Scrollstuff:
        self.scroll = QScrollArea()
        self.scroll.setWidget(self.central_widget)
        self.scroll.setWidgetResizable(True)
        self.setCentralWidget(self.scroll)

        #self.scroll.setMaximumHeight(screen_geometry.height())
        #self.adjustSize()

        self.setWindowTitle("Simple RIXS Input energy per channel")
        self.show()

    def create_gui_item(self, key, item_label_text, item_type, combo_box_options):
        hbox = QHBoxLayout()
        item_label = QLabel(item_label_text)
        if item_type =="q_line_edit":
            if "array" in key:
                hbox.addWidget(item_label)
                split_key_list = key.split('_')
                array_key = '_'.join(split_key_list[:-1])
                array_index = int(split_key_list[-1])
                condition = True
                while condition:
                    try:
                        if array_key == "input_complete_file_name_array":
                            item = DropLineEdit(self.parameters[array_key][array_index])
                        else:
                            item = QLineEdit(self.parameters[array_key][array_index])
                        condition = False
                    except (IndexError):
                        self.parameters[array_key].append(self.parameters[array_key][0])
                hbox.addWidget(item)
                item.editingFinished.connect(lambda item=item: self.update_dictionary_array(array_key, array_index, item))
            elif key== "input_number_of_incoming_energy_segments":
                self.hbox_number_of_segments = QHBoxLayout()
                self.hbox_number_of_segments.addWidget(item_label)
                self.item_number_of_segments= QLineEdit(self.parameters[key])
                self.hbox_number_of_segments.addWidget(self.item_number_of_segments)
                self.item_number_of_segments.editingFinished.connect(lambda: self.create_dynamic_gui_item_for_segments(self.item_number_of_segments, self.item_number_of_segments.text(), key, self.hbox_number_of_segments, "input_number_of_incoming_energy_segments", "How many segments of equal incoming energy difference are there? \n(Maximum 10 segments)"))
                return self.hbox_number_of_segments
            elif key== "input_number_of_incoming_energy_segments_with_gap":
                self.hbox_number_of_segments_with_gap = QHBoxLayout()
                self.hbox_number_of_segments_with_gap.addWidget(item_label)
                self.item_number_of_segments_with_gap= QLineEdit(self.parameters[key])
                self.hbox_number_of_segments_with_gap.addWidget(self.item_number_of_segments_with_gap)
                self.item_number_of_segments_with_gap.editingFinished.connect(lambda: self.create_dynamic_gui_item_for_segments_with_gap(self.item_number_of_segments_with_gap, self.item_number_of_segments_with_gap.text(), key, self.hbox_number_of_segments_with_gap, "input_number_of_incoming_energy_segments_with_gap", "How many segments of equal incoming energy difference are there? \n(Maximum 10 segments)"))
                return self.hbox_number_of_segments_with_gap
            elif key== "input_number_of_incoming_energies":
                self.hbox_number_of_incoming_energies = QHBoxLayout()
                self.hbox_number_of_incoming_energies.addWidget(item_label)
                self.item_number_of_incoming_energies= QLineEdit(self.parameters[key])
                self.hbox_number_of_incoming_energies.addWidget(self.item_number_of_incoming_energies)
                self.item_number_of_incoming_energies.editingFinished.connect(lambda: self.create_dynamic_gui_item_for_incoming_energies(self.item_number_of_incoming_energies, self.item_number_of_incoming_energies.text(), key, self.hbox_number_of_incoming_energies, "input_number_of_incoming_energies", "How many spectra would you like to give the incoming energy for? \n (Maximum 50 energies)"))
                return self.hbox_number_of_incoming_energies
            elif key == "degree_of_energy_per_channel_polynomial":
                self.hbox_polynomial_degree = QHBoxLayout()
                self.hbox_polynomial_degree.addWidget(item_label)
                self.item_polynomial_degree= QLineEdit(self.parameters[key])
                self.hbox_polynomial_degree.addWidget(self.item_polynomial_degree)
                self.item_polynomial_degree.editingFinished.connect(lambda: self.create_dynamic_gui_item_for_polynomial_coefficients(self.item_polynomial_degree, self.item_polynomial_degree.text(), "degree_of_energy_per_channel_polynomial", self.hbox_polynomial_degree, "input_first_and_last_incoming_energy", "Input the incoming energy of the first and last spectra: "))
                return self.hbox_polynomial_degree
            elif key[:39]== "first_incoming_energy_segment_with_gap_":
                hbox.addWidget(item_label)
                item = QLineEdit(self.parameters["first_incoming_energy_of_segment_array"][int(key[39:])])
                hbox.addWidget(item)
                item.editingFinished.connect(lambda item=item, key=key: self.update_dictionary_array("first_incoming_energy_of_segment_array", int(key[39:]), item))
            elif key[:38]== "last_incoming_energy_segment_with_gap_":
                hbox.addWidget(item_label)
                item = QLineEdit(self.parameters["last_incoming_energy_of_segment_array"][int(key[38:])])
                hbox.addWidget(item)
                item.editingFinished.connect(lambda item=item, key=key: self.update_dictionary_array("last_incoming_energy_of_segment_array", int(key[38:]), item))
            elif key[:30]== "first_incoming_energy_segment_":
                hbox.addWidget(item_label)
                item = QLineEdit(self.parameters["first_incoming_energy_of_segment_array"][int(key[30:])])
                hbox.addWidget(item)
                item.editingFinished.connect(lambda item=item, key=key: self.update_dictionary_array("first_incoming_energy_of_segment_array", int(key[30:]), item))
            elif key[:29]== "last_incoming_energy_segment_":
                hbox.addWidget(item_label)
                item = QLineEdit(self.parameters["last_incoming_energy_of_segment_array"][int(key[29:])])
                hbox.addWidget(item)
                item.editingFinished.connect(lambda item=item, key=key: self.update_dictionary_array("last_incoming_energy_of_segment_array", int(key[29:]), item))

            elif key[:47]== "incoming_energy_difference_in_segment_with_gap_":
                hbox.addWidget(item_label)
                item = QLineEdit(self.parameters["incoming_energy_difference_in_segment_array"][int(key[47:])])
                hbox.addWidget(item)
                item.editingFinished.connect(lambda item=item, key=key: self.update_dictionary_array("incoming_energy_difference_in_segment_array", int(key[47:]), item))

            elif key[:38]== "incoming_energy_difference_in_segment_":
                hbox.addWidget(item_label)
                item = QLineEdit(self.parameters["incoming_energy_difference_in_segment_array"][int(key[38:])])
                hbox.addWidget(item)
                item.editingFinished.connect(lambda item=item, key=key: self.update_dictionary_array("incoming_energy_difference_in_segment_array", int(key[38:]), item))

            elif key[:24]== "incoming_energy_segment_" and key!="incoming_energy_of_last_spectra" and key!="incoming_energy_of_last_spectra_with_gap":
                hbox.addWidget(item_label)
                item = QLineEdit(self.parameters["incoming_energy_of_spectra_array"][int(key[24:])])
                hbox.addWidget(item)
                item.editingFinished.connect(lambda item=item, key=key: self.update_dictionary_array("incoming_energy_of_spectra_array", int(key[24:]), item))

            elif key == "incoming_energy_of_last_spectra_with_gap":
                hbox.addWidget(item_label)
                item = QLineEdit(self.parameters["incoming_energy_of_last_spectra"])
                hbox.addWidget(item)
                item.editingFinished.connect(lambda item=item, key=key: self.validate_input(item, key))
         
            elif key != "input_file_project_folder" or key != "input_file_raw_data_folder":
                hbox.addWidget(item_label)
                item = QLineEdit(self.parameters[key])
                hbox.addWidget(item)
                item.editingFinished.connect(lambda item=item, key=key: self.validate_input(item, key))
            else:
                hbox.addWidget(item_label)
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
            if key== "is_equal_incoming_energy_difference":
                self.hbox_is_equal = QHBoxLayout()
                self.hbox_is_equal.addWidget(item_label)
                self.item_is_equal = QCheckBox()
                self.item_is_equal.setChecked(self.parameters[key])
                self.hbox_is_equal.addWidget(self.item_is_equal)
                self.item_is_equal.clicked.connect(lambda: self.create_dynamic_gui_item_from_checkboxes(self.item_is_equal, self.item_is_equal.text(), key, self.hbox_is_equal, "input_first_and_last_incoming_energy", "Input the incoming energy of the first and last spectra: "))
                return self.hbox_is_equal
                #self.create_dynamic_gui_item_from_checkboxes(self.item_is_equal, self.item_is_equal.text(), key, hbox, "input_first_and_last_incoming_energy", "Input the incoming energy of the first and last spectra: ")
            elif key== "is_segments_of_equal_incoming_energy_difference":
                self.hbox_is_segments = QHBoxLayout()
                self.hbox_is_segments.addWidget(item_label)
                self.item_is_segments = QCheckBox()
                self.item_is_segments.setChecked(self.parameters[key])
                self.hbox_is_segments.addWidget(self.item_is_segments)
                self.item_is_segments.clicked.connect(lambda: self.create_dynamic_gui_item_from_checkboxes(self.item_is_segments, self.item_is_segments.text(), key, self.hbox_is_segments, "input_number_of_incoming_energy_segments", "How many segments of equal incoming energy difference are there? \n (15 max) "))
                return self.hbox_is_segments
            elif key== "is_segments_of_equal_incoming_energy_difference_with_gap":
                self.hbox_is_segments_with_gap = QHBoxLayout()
                self.hbox_is_segments_with_gap.addWidget(item_label)
                self.item_is_segments_with_gap = QCheckBox()
                self.item_is_segments_with_gap.setChecked(self.parameters[key])
                self.hbox_is_segments_with_gap.addWidget(self.item_is_segments_with_gap)
                self.item_is_segments_with_gap.clicked.connect(lambda: self.create_dynamic_gui_item_from_checkboxes(self.item_is_segments_with_gap, self.item_is_segments_with_gap.text(), key, self.hbox_is_segments_with_gap, "input_number_of_incoming_energy_segments_with_gap", "How many segments of equal incoming energy difference are there? \n (15 max) "))
                return self.hbox_is_segments_with_gap
            elif key== "is_input_every_incoming_energy":
                self.hbox_input_every_energy = QHBoxLayout()
                self.hbox_input_every_energy.addWidget(item_label)
                self.item_input_every_energy = QCheckBox()
                self.item_input_every_energy.setChecked(self.parameters[key])
                self.hbox_input_every_energy.addWidget(self.item_input_every_energy)
                self.item_input_every_energy.clicked.connect(lambda: self.create_dynamic_gui_item_from_checkboxes(self.item_input_every_energy, self.item_input_every_energy.text(), key, self.hbox_input_every_energy, "input_number_of_incoming_energies", "How many spectra would you like to give the incoming energy for? \n (Maximum 50 energies) "))   
                return self.hbox_input_every_energy
            else:
                hbox.addWidget(item_label)
                item = QCheckBox()
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
        elif item_type== "q_array_inputs":
            hbox.addWidget(item_label)
            item_list=[]
            if key== "input_file_ignore_file_number":
                for input_square in range(int(self.parameters["input_file_number_of_files_to_ignore"])):
                    item = QLineEdit(self.parameters[key][input_square])
                    item.textChanged.connect(lambda text, index=input_square: self.update_dictionary_array(key, index, text))
                    item_list.append(item)
                    hbox.addWidget(item_list[input_square])
        else:
            print("Error: Item was not added to the GUI")
        return hbox

    def create_dynamic_gui_item_from_checkboxes(self, item, item_text, key, hbox, new_key, new_label_text):
        item_box_was_set_to_true= item.isChecked()
        if self.is_first_time_creating_checkboxes== False:
            if self.parameters["is_equal_incoming_energy_difference"]:
                self.remove_item(self.vbox.indexOf(self.hbox_is_equal)+1)
                self.remove_item(self.vbox.indexOf(self.hbox_is_equal)+2)
            elif self.parameters["is_segments_of_equal_incoming_energy_difference"]:
                if self.parameters["input_number_of_incoming_energy_segments"]== "0" or self.parameters["input_number_of_incoming_energy_segments"]== "":
                    self.remove_item(self.vbox.indexOf(self.hbox_is_segments)+1)
                else:
                    self.remove_item(self.vbox.indexOf(self.hbox_is_segments)+1)
                    for item in range(2*int(self.parameters["input_number_of_incoming_energy_segments"])):
                        self.remove_item(self.vbox.indexOf(self.hbox_is_segments)+ item +1) 
                    self.remove_item(self.vbox.indexOf(self.hbox_is_segments)+2*int(self.parameters["input_number_of_incoming_energy_segments"])+1)
                    self.remove_item(self.vbox.indexOf(self.hbox_is_segments)+2*int(self.parameters["input_number_of_incoming_energy_segments"])+2)
                    self.parameters["input_number_of_incoming_energy_segments"]="0"

            elif self.parameters["is_segments_of_equal_incoming_energy_difference_with_gap"]:
                if self.parameters["input_number_of_incoming_energy_segments_with_gap"]== "0" or self.parameters["input_number_of_incoming_energy_segments_with_gap"]== "":
                    self.remove_item(self.vbox.indexOf(self.hbox_is_segments_with_gap)+1)
                else:
                    self.remove_item(self.vbox.indexOf(self.hbox_is_segments_with_gap)+1)
                    for item in range(3*int(self.parameters["input_number_of_incoming_energy_segments_with_gap"])):
                        self.remove_item(self.vbox.indexOf(self.hbox_is_segments_with_gap)+ item +1)
                    #self.remove_item(self.vbox.indexOf(self.hbox_is_segments_with_gap)+2*int(self.parameters["input_number_of_incoming_energy_segments_with_gap"])+1)
                    #self.remove_item(self.vbox.indexOf(self.hbox_is_segments_with_gap)+2*int(self.parameters["input_number_of_incoming_energy_segments_with_gap"])+2)
                    self.remove_item(self.vbox.indexOf(self.hbox_is_segments_with_gap)+3*int(self.parameters["input_number_of_incoming_energy_segments_with_gap"])+1)
                    self.parameters["input_number_of_incoming_energy_segments_with_gap"]="0"

            elif self.parameters["is_input_every_incoming_energy"]:
                if self.parameters["input_number_of_incoming_energies"]== "0" or self.parameters["input_number_of_incoming_energies"]== "":
                    self.remove_item(self.vbox.indexOf(self.hbox_input_every_energy)+1)
                else:
                    self.remove_item(self.vbox.indexOf(self.hbox_input_every_energy)+1)
                    for item in range(int(self.parameters["input_number_of_incoming_energies"])):
                        self.remove_item(self.vbox.indexOf(self.hbox_input_every_energy) + item+1)
                    self.remove_item(self.vbox.indexOf(self.hbox_input_every_energy) + int(self.parameters["input_number_of_incoming_energies"])+1)
                    self.parameters["input_number_of_incoming_energies"]="0"
            self.set_checkboxes_to_false()
        
        if item_box_was_set_to_true:
            self.parameters[key] = True
            #self.update_dictionary_checkbox(key, True)
            if key== "is_equal_incoming_energy_difference":
                self.item_is_equal.setChecked(True)
                self.vbox.insertLayout(self.vbox.indexOf(hbox)+1,self.create_gui_item("energy_of_last_line_spectra", "Input the incoming energy of the last spectra: ", "q_line_edit", [""]))
                self.vbox.insertLayout(self.vbox.indexOf(hbox)+1,self.create_gui_item("energy_of_first_line_spectra", "Input the incoming energy of the first spectra: ", "q_line_edit", [""]))
            elif key== "is_segments_of_equal_incoming_energy_difference":
                self.item_is_segments.setChecked(True)
                self.vbox.insertLayout(self.vbox.indexOf(hbox)+1,self.create_gui_item("input_number_of_incoming_energy_segments", "How many segments of equal incoming energy difference are there? \n (Maximum 10 segments)", "q_line_edit", [""]))
            elif key== "is_segments_of_equal_incoming_energy_difference_with_gap":
                self.item_is_segments_with_gap.setChecked(True)
                self.vbox.insertLayout(self.vbox.indexOf(hbox)+1,self.create_gui_item("input_number_of_incoming_energy_segments_with_gap", "How many segments of equal incoming energy difference are there? \n (Maximum 10 segments)", "q_line_edit", [""]))
            elif key== "is_input_every_incoming_energy":
                self.item_input_every_energy.setChecked(True)
                self.vbox.insertLayout(self.vbox.indexOf(hbox)+1,self.create_gui_item("input_number_of_incoming_energies", "How many spectra would you like to give the incoming energy for? \n (Maximum 30 energies)", "q_line_edit", [""]))

            elif self.validate_input(item, key):
                if int(item_text) == 0:
                    for array_index in range(len(self.parameters[new_key])):
                        self.update_dictionary_array(new_key, array_index, "")
                    if self.is_ignore_file_number_array_displayed:
                        self.remove_item(self.vbox.indexOf(hbox)+1)
                        self.is_ignore_file_number_array_displayed =False
                else: 
                    if self.is_ignore_file_number_array_displayed:
                        self.remove_item(self.vbox.indexOf(hbox)+1)
                    self.vbox.insertLayout(self.vbox.indexOf(hbox)+1,self.create_gui_item(new_key, new_label_text, "q_array_inputs", [""]))
                    self.is_ignore_file_number_array_displayed =True            

    def create_dynamic_gui_item_for_segments(self, item, item_text, key, hbox, new_key, new_label_text):
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
                    self.vbox.insertLayout(self.vbox.indexOf(hbox)+2*segment+2,self.create_gui_item("incoming_energy_difference_in_segment_"+ str(segment), "Incoming energy difference of spectra in segment "+ str(segment)+ ":", "q_line_edit", [""]))
                self.vbox.insertLayout(self.vbox.indexOf(hbox)+2*int(item_text)+1,self.create_gui_item("incoming_energy_of_last_spectra", "Incoming energy of last spectra: ", "q_line_edit", [""]))

    def create_dynamic_gui_item_for_segments_with_gap(self, item, item_text, key, hbox, new_key, new_label_text):
        if self.validate_input(item, key):
            if self.is_first_time_creating_checkboxes== False:
                if self.parameters[key]!= "":
                    old_number_of_segments= int(self.parameters[key])
                else:
                    old_number_of_segments=0
                self.update_dictionary(key, item.text())
                if old_number_of_segments>0:
                    for segment in range(3*old_number_of_segments):
                        self.remove_item(self.vbox.indexOf(hbox)+segment+1)
                    #self.remove_item(self.vbox.indexOf(hbox)+2*old_number_of_segments+1)
            if int(item_text) != 0:
                for segment in range(int(item_text)):
                    self.vbox.insertLayout(self.vbox.indexOf(hbox)+3*segment+1,self.create_gui_item("first_incoming_energy_segment_with_gap_"+ str(segment), "First incoming energy of segment "+ str(segment)+":                     ", "q_line_edit", [""]))
                    self.vbox.insertLayout(self.vbox.indexOf(hbox)+3*segment+2,self.create_gui_item("incoming_energy_difference_in_segment_with_gap_"+ str(segment), "Incoming energy difference of spectra in segment "+ str(segment)+ ":", "q_line_edit", [""]))
                    self.vbox.insertLayout(self.vbox.indexOf(hbox)+3*segment+3,self.create_gui_item("last_incoming_energy_segment_with_gap_"+ str(segment), "Last incoming energy of segment "+ str(segment)+":                     ", "q_line_edit", [""]))

                #self.vbox.insertLayout(self.vbox.indexOf(hbox)+2*int(item_text)+1,self.create_gui_item("incoming_energy_of_last_spectra_with_gap", "Incoming energy of last spectra: ", "q_line_edit", [""]))
    
    def create_dynamic_gui_item_for_incoming_energies(self, item, item_text, key, hbox, new_key, new_label_text):
        if self.validate_input(item, key):
            if self.is_first_time_creating_checkboxes== False:
                if self.parameters[key]!= "":
                    old_number_of_energies= int(self.parameters[key])
                else:
                    old_number_of_energies=0
                self.update_dictionary(key, item.text())
                if old_number_of_energies>0:
                    for incoming_energy in range(old_number_of_energies):
                        self.remove_item(self.vbox.indexOf(hbox)+incoming_energy+1)
            if int(item_text) != 0:
                for incoming_energy in range(int(item_text)):
                    self.vbox.insertLayout(self.vbox.indexOf(hbox)+incoming_energy+1,self.create_gui_item("incoming_energy_of_spectra_array_"+ str(incoming_energy), "Incoming energy of spectra "+ str(incoming_energy)+":                     ", "q_line_edit", [""]))

    def create_dynamic_gui_item_for_polynomial_coefficients(self, item, item_text, key, hbox, new_key, new_label_text):
        if self.validate_input(item, key):
            if self.is_first_time_creating_dynamic_items== False:
                if self.parameters[key]!= "":
                    old_degree_of_fit = int(self.parameters[key])
                else:
                    old_degree_of_fit=0
                self.update_dictionary(key, item.text())
                if old_degree_of_fit>0:
                    for coefficient in range(old_degree_of_fit + 1):
                        self.remove_item(self.vbox.indexOf(hbox) + coefficient + 1)
            if int(item_text) != 0:
                for coefficient in range(int(item_text) + 1):
                    self.vbox.insertLayout(self.vbox.indexOf(hbox) + coefficient + 1, self.create_gui_item("energy_per_channel_polynomial_coefficients_array_"+ str(coefficient), "Value of polynomial coefficient "+ str(coefficient)+":                     ", "q_line_edit", [""]))

            
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
                    
    def update_dictionary(self, key, updated_value):
        self.parameters[key] = updated_value

    def update_dictionary_checkbox(self, key, item):
                if item.isChecked():
                    self.parameters[key] = True
                else:
                    self.parameters[key] = False

    def set_checkboxes_to_false(self):
        self.item_is_equal.setChecked(False)
        self.parameters["is_equal_incoming_energy_difference"] = False
        self.item_is_segments.setChecked(False)
        self.parameters["is_segments_of_equal_incoming_energy_difference"] = False
        self.item_is_segments_with_gap.setChecked(False)
        self.parameters["is_segments_of_equal_incoming_energy_difference_with_gap"] = False
        self.item_input_every_energy.setChecked(False)
        self.parameters["is_input_every_incoming_energy"] = False

    def update_dictionary_array(self, key, array_index, item):

            if self.validate_input_for_array(key, array_index, item):
                self.parameters[key][array_index] = item.text()

    def validate_input_for_array(self, key, array_index, item):
        if item.text() != self.parameters[key][array_index]:
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
        if item.text() != self.parameters[key] or key== "input_number_of_incoming_energy_segments" or key== "input_number_of_incoming_energy_segments_with_gap" or key=="input_number_of_incoming_energies":
            if key !="input_number_of_incoming_energy_segments" and key!= "input_number_of_incoming_energies" and key !="input_number_of_incoming_energy_segments_with_gap" and key!= "input_number_of_incoming_energies_with_gap":
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

    def plot_inputted_data(self, parameters, extra_plot_parameters):
        plt.close()
        plots= []
        #self.is_first_and_last_spectrum_displayed= True
        if parameters["input_file_format"] =="h5":
            y_values = get_single_spectrum_h5_or_txt_file_scripts.get_single_spectrum_h5_file(parameters, parameters["h5_root_location_data"], True, parameters["input_file_iteratable_file_number_start"])
            x_values = [x for x in range(len(y_values))]
            plots.append([x_values, y_values, "Channel", "Counts" ])
            y_values = get_single_spectrum_h5_or_txt_file_scripts.get_single_spectrum_h5_file(parameters, parameters["h5_root_location_data"], True, parameters["input_file_iteratable_file_number_end"])
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


        elif parameters["input_file_format"] =="txt":
            y_values = get_single_spectrum_h5_or_txt_file_scripts.get_single_spectrum_txt_file(parameters, False, parameters["txt_intensity_data_row"], parameters["txt_intensity_data_column"], True, parameters["input_file_iteratable_file_number_start"], parameters["is_several_spectra_per_file"])
            x_values = [x for x in range(len(y_values))]
            plots.append([x_values, y_values, "Channel", "Counts" ])
            y_values = get_single_spectrum_h5_or_txt_file_scripts.get_single_spectrum_txt_file(parameters, False, parameters["txt_intensity_data_row"], parameters["txt_intensity_data_column"], True, parameters["input_file_iteratable_file_number_end"], parameters["is_several_spectra_per_file"])
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

    def get_inputted_parameters_from_gui(self):
        return self.parameters

if __name__ == '__main__':
    input_file_location= "C:\\Users\\ponto479\\Documents\\02 Beamtime Data\\SLS Adress 03-2022\\RIXS"
    parameters= parameter_scripts.get_parameters(input_file_location)
    #parameters={"input_file_location": "C:\\Users\\ponto479\\Documents\\02 Beamtime Data\\SLS Adress 03-2022\\RIXS",
                #"is_program_running":True, "input_file_iteratable_file_number_start":"0100", "input_file_iteratable_file_number_end": "0120" }
    #parameters["is_view_roots_or_input_txt"]
    parameters = run_main_gui(parameters)
    #print(parameters)
