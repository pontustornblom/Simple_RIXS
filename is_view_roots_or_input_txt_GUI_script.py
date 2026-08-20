#is_view_roots_or_input_txt_GUI_script
import sys
import os
import platform
from PyQt5.QtWidgets import QLabel, QMainWindow, QCheckBox, QComboBox, QLineEdit, QPushButton, QLayout, QApplication, QVBoxLayout, QHBoxLayout, QWidget, QDesktopWidget, QLabel, QTextEdit, QMessageBox, QScrollArea
from PyQt5.QtGui import QPixmap
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from math import floor
import matplotlib.pyplot as plt
import h5py
import numpy as np
from PyQt5.QtCore import QEventLoop
from PyQt5.QtCore import pyqtSignal
import subprocess
import parameter_scripts
import create_complete_file_location_view_roots_or_txt_script
import get_single_spectrum_h5_or_txt_file_scripts



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
        self.move(floor(screen_geometry.width()/2 +10), 10)

        self.is_first_time_creating_checkboxes= True
        self.is_incoming_energy_avialable_in_seperate_file_displayed= False
        self.is_i0_avialable_in_seperate_file_displayed= False
        #self.open_folder(parameters["input_file_location"])
        self.vbox = QVBoxLayout()

        #Simple_RIXS_logo_layout = QHBoxLayout()
        #Simple_RIXS_logo_layout.addStretch(1)
        #Simple_RIXS_logo_label =QLabel()
        #logo_folder = 'Simple_RIXS_logo'
        #logo_file = 'Simple_RIXS_logo_final.png'
        #logo_path = os.path.join('C:\\Users\\ponto479\\Documents\\13Pythonkod', logo_folder, logo_file)
        #Simple_RIXS_logo = QPixmap(logo_path)
        #Simple_RIXS_logo_label.setPixmap(Simple_RIXS_logo)
        #Simple_RIXS_logo_layout.addWidget(Simple_RIXS_logo_label)
        #Simple_RIXS_logo_layout.addStretch(1)
        #self.vbox.addLayout(Simple_RIXS_logo_layout)
        #vbox.setSpacing(10)
        #vbox.setSizeConstraint(QLayout.SetFixedSize)

        #self.vbox.addLayout(self.create_gui_item("input_file_location", "Raw data file location: ", "q_line_edit", [""]))
        self.vbox.addLayout(self.create_gui_item("input_file_project_folder", "Folder of the current project: ", "q_line_edit", [""]))
        self.vbox.addLayout(self.create_gui_item("input_file_raw_data_folder", "Subfolder where the raw data is stored: ", "q_line_edit", [""]))
        self.vbox.addLayout(self.create_gui_item("open file location", "Open raw data file location", "q_push_button",  [""]))
        if self.parameters["input_file_format"] == "h5":
            self.vbox.addLayout(self.create_gui_item("is_detector_count", "Are the counts given as counts in a 2D detector? (This is not available yet) ", "q_check_box",  [""]))
            self.vbox.addLayout(self.create_gui_item("is_several_spectra_per_file", "Are there several spectral lines per h5 file?(This is not available yet) ", "q_check_box",  [""]))
            self.vbox.addLayout(self.create_gui_item("h5_root_location_data", "Location of the spectrum: \n Example: entry/analysis/spectrum", "q_line_edit", [""]))
            self.vbox.addLayout(self.create_gui_item("h5_root_location_x_values", "Location of the x values (Energy Loss/Emission energy): \n Example: entry/analysis/spectrum", "q_line_edit", [""]))
            self.vbox.addLayout(self.create_gui_item("is_x_values_available_in_file", "Are x values given in the file? \n(Can be given as emission energy or energy loss. Uncheck if it is just channel number)", "q_check_box",  [""]))
            self.vbox.addLayout(self.create_gui_item("is_input_energy_per_channel_and_intercept_manually", "Would you like to manually input the energy per channel polynomial coefficients? \n(You will input this in a later window) ", "q_check_box", [""]))

            self.vbox.addLayout(self.create_gui_item("is_data_x_values_energy_loss", "Are the x values given as energy loss?", "q_check_box",  [""]))
            self.vbox.addLayout(self.create_gui_item("is_data_x_values_emission_energy", "Are the x values given as emission energy? ", "q_check_box",  [""]))            
            self.vbox.addLayout(self.create_gui_item("is_incoming_energy_available_in_file", "Is the incoming energy available in the file? ", "q_check_box",  [""]))

            self.vbox.addLayout(self.create_gui_item("is_incoming_energy_avialable_in_seperate_file", "Is the incoming energy available in another file? ", "q_check_box",  [""]))
            if self.parameters["is_incoming_energy_avialable_in_seperate_file"]:
                self.vbox.addLayout(self.create_gui_item("complete_incoming_energy_file_location", "Input the complete file location for the incoming energy file: ", "q_line_edit", [""]))
                self.vbox.addLayout(self.create_gui_item("complete_incoming_energy_file_name", "Input file name for the incoming energy file: ", "q_line_edit", [""]))
                self.is_incoming_energy_avialable_in_seperate_file_displayed= True
            self.vbox.addLayout(self.create_gui_item("h5_root_location_incoming_energy", "Location of the incoming energy: \n Example: entry/instruments/NDAttributes/PhotonEnergy", "q_line_edit", [""]))
            self.vbox.addLayout(self.create_gui_item("is_i0_available_in_file", "Is the I0 (I-zero) available in the file? ", "q_check_box",  [""]))           
            self.vbox.addLayout(self.create_gui_item("is_i0_avialable_in_seperate_file", "Is the I0 (I-zero) available in another file? ", "q_check_box",  [""]))
            if self.parameters["is_i0_avialable_in_seperate_file"]:
                self.vbox.addLayout(self.create_gui_item("complete_i0_file_location", "Input the complete file location for the I0 file: ", "q_line_edit", [""]))
                self.vbox.addLayout(self.create_gui_item("complete_i0_file_name", "Input file name for the I0 file: ", "q_line_edit", [""]))
                self.is_i0_avialable_in_seperate_file_displayed= True
            self.vbox.addLayout(self.create_gui_item("i0_root_location_data", "Location of the I0 values: \n Example: entry/analysis/spectrum", "q_line_edit", [""]))
            self.vbox.addLayout(self.create_gui_item("plot inputted root data", "Would you like to plot the data in these locations you just inputted? ", "q_push_button",  [""]))
        elif self.parameters["input_file_format"] == "txt" or self.parameters["input_file_format"] == "dat" or self.parameters["input_file_format"] == "csv":
            self.vbox.addLayout(self.create_gui_item("txt_delimiter", "What is the txt delimiter? ", "q_combo_box", ["Tab", ",", "Space", ";", ":", "|"]))
            self.vbox.addLayout(self.create_gui_item("txt_intensity_data_row", "Row of first intensity value: \n Note: The first row has index zero", "q_line_edit", [""]))
            self.vbox.addLayout(self.create_gui_item("txt_intensity_data_column", "Column of first intensity value: \n Note: The first column has index zero", "q_line_edit", [""]))
            self.vbox.addLayout(self.create_gui_item("is_several_spectra_per_file", "Are there several spectral lines per txt file? ", "q_check_box",  [""]))
            self.create_dynamic_gui_item_from_checkboxes(self.item_is_several_spectra, self.item_is_several_spectra.text(), "is_several_spectra_per_file", self.hbox_is_several_spectra, "txt_intensity_data_last_column", "Column of last spectrum value: \n Note: The first column has index zero")

            self.vbox.addLayout(self.create_gui_item("is_combine_several_spectra_per_file", "Are there several spectral lines per txt file that should be combined into one spectra? ", "q_check_box",  [""]))
            self.vbox.addLayout(self.create_gui_item("number_of_spectra_to_combine", "How many spectra do you want to combine in the file?", "q_line_edit", [""]))
            self.vbox.addLayout(self.create_gui_item("index_frequency_of_plots_to_combine", "How frequent does the columns you want to add up appear? \n(Choosing 1 means every column after the first specified column. Choosing 2 means every other)", "q_line_edit", [""]))

            self.vbox.addLayout(self.create_gui_item("is_x_values_available_in_file", "Are x values given in the file? \n(Can be given as emission energy or energy loss. Uncheck if it is just channel number)", "q_check_box",  [""]))
            self.vbox.addLayout(self.create_gui_item("is_input_energy_per_channel_and_intercept_manually", "Would you like to manually input the energy per channel polynomial coefficients? \n(You will input this in a later window) ", "q_check_box", [""]))

            self.vbox.addLayout(self.create_gui_item("is_data_x_values_energy_loss", "Are the x values given as energy loss? ", "q_check_box",  [""]))
            self.vbox.addLayout(self.create_gui_item("is_data_x_values_emission_energy", "Are the x values given as emission energy? ", "q_check_box",  [""]))
            self.vbox.addLayout(self.create_gui_item("degree_of_energy_per_channel_polynomial", "What degree polynomial do you want to fit the elastic peaks to? (Set to 1 for linear) ", "q_line_edit", [""]))        

            self.vbox.addLayout(self.create_gui_item("input_x_values_txt_row", "Row of first x value (Energy Loss/Emission energy): \n Note: The first row has index zero", "q_line_edit", [""]))
            self.vbox.addLayout(self.create_gui_item("input_x_values_txt_column", "Column of first x value (Energy Loss/Emission energy): \n Note: The first column has index zero", "q_line_edit", [""]))

            self.vbox.addLayout(self.create_gui_item("is_incoming_energy_available_in_file", "Is the incoming energy available in the file? ", "q_check_box",  [""]))
            self.vbox.addLayout(self.create_gui_item("is_incoming_energy_avialable_in_seperate_file", "Is the incoming energy available in another file? ", "q_check_box",  [""]))
            if self.parameters["is_incoming_energy_avialable_in_seperate_file"]:
                self.vbox.addLayout(self.create_gui_item("complete_incoming_energy_file_location", "Input the complete file location for the incoming energy file: ", "q_line_edit", [""]))
                self.vbox.addLayout(self.create_gui_item("complete_incoming_energy_file_name", "Input file name for the incoming energy file: ", "q_line_edit", [""]))
                self.is_incoming_energy_avialable_in_seperate_file_displayed= True
            self.vbox.addLayout(self.create_gui_item("is_txt_single_incoming_energy_value", "Is the incoming energy only given as a single value? ", "q_check_box",  [""]))
            self.vbox.addLayout(self.create_gui_item("txt_incoming_energy_row_in_file", "Row of first incoming energy value: \n Note: The first row has index zero", "q_line_edit", [""]))
            self.vbox.addLayout(self.create_gui_item("txt_incoming_energy_column_in_file", "Column of first incoming energy value: \n Note: The first column has index zero", "q_line_edit", [""]))
            self.vbox.addLayout(self.create_gui_item("is_i0_available_in_file", "Is the I0 (I-Zero) available in the file? ", "q_check_box",  [""]))
            self.vbox.addLayout(self.create_gui_item("is_i0_avialable_in_seperate_file", "Is the I0 (I-zero) available in another file? ", "q_check_box",  [""]))
            if self.parameters["is_i0_avialable_in_seperate_file"]:
                self.vbox.addLayout(self.create_gui_item("is_use_same_file_for_i0_as_for_incoming_energy", "Is it the same file as for the incoming energy? ", "q_check_box", [""]))
                self.vbox.addLayout(self.create_gui_item("complete_i0_file_location", "Input the complete file location for the I0 file: ", "q_line_edit", [""]))
                self.vbox.addLayout(self.create_gui_item("complete_i0_file_name", "Input file name for the I0 file: ", "q_line_edit", [""]))
                self.is_i0_avialable_in_seperate_file_displayed= True
            self.vbox.addLayout(self.create_gui_item("is_txt_single_i0_value", "Is the I0 (I-Zero) only given as a single value? ", "q_check_box",  [""]))
            self.vbox.addLayout(self.create_gui_item("txt_i0_row_in_file", "Row of first I0 value: \n Note: The first row has index zero", "q_line_edit", [""]))
            self.vbox.addLayout(self.create_gui_item("txt_i0_column_in_file", "Column of I0 spectrum value: \n Note: The first column has index zero", "q_line_edit", [""]))
            self.vbox.addLayout(self.create_gui_item("plot inputted root data", "Would you like to plot the data you just selected? ", "q_push_button",  [""]))
        else:
            print("This file format is not supported yet, sorry about that.")        

        self.is_first_time_creating_checkboxes= False

        self.vbox.addLayout(self.create_bottom_buttons())



        self.central_widget = QWidget()
        self.central_widget.setLayout(self.vbox)
        self.setCentralWidget(self.central_widget)
        #Scrollstuff:
        self.scroll = QScrollArea()
        self.scroll.setWidget(self.central_widget)
        self.scroll.setWidgetResizable(True)
        self.setCentralWidget(self.scroll)

        self.setWindowTitle("Simple RIXS View h5/txt file")
        self.show()

        #Display the h5 or txt file
        parameters, complete_file_location = create_complete_file_location_view_roots_or_txt_script.create_complete_file_location_view_roots_or_txt(self.parameters, False, self.parameters["input_complete_file_name_array"][0])
        if self.parameters["input_file_format"] == "h5":
            self.second_window = SecondWindow(parameters, complete_file_location)
        elif parameters["input_file_format"] == "txt" or parameters["input_file_format"] == "dat" or parameters["input_file_format"] == "csv":
            self.open_txt_file(complete_file_location)

    def create_gui_item(self, key, item_label_text, item_type, combo_box_options):
        hbox = QHBoxLayout()
        item_label = QLabel(item_label_text)
        if item_type =="q_line_edit":
            hbox.addWidget(item_label)
            item = DropLineEdit(self.parameters[key]) if key == "input_complete_file_name" else QLineEdit(self.parameters[key])
            hbox.addWidget(item)
            item.textChanged.connect(lambda: self.update_dictionary(key, item.text()))
            if self.parameters["input_file_format"] == "txt" and key != "input_file_project_folder" and key != "input_file_raw_data_folder" and key != "complete_incoming_energy_file_location" and key != "complete_incoming_energy_file_name" and key != "complete_i0_file_location" and key != "complete_i0_file_name":
                item.editingFinished.connect(lambda: self.validate_input(item))
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
            item.setChecked(self.parameters[key])
            hbox.addWidget(item)
            if key == "is_several_spectra_per_file":
                self.hbox_is_several_spectra = QHBoxLayout()
                self.hbox_is_several_spectra.addWidget(item_label)
                self.item_is_several_spectra = QCheckBox()
                self.item_is_several_spectra.setChecked(self.parameters[key])
                self.hbox_is_several_spectra.addWidget(self.item_is_several_spectra)
                self.item_is_several_spectra.clicked.connect(lambda: self.create_dynamic_gui_item_from_checkboxes(self.item_is_several_spectra, self.item_is_several_spectra.text(), key, self.hbox_is_several_spectra, "txt_intensity_data_last_column", "Column of last spectrum value: \n Note: The first column has index zero"))
                return self.hbox_is_several_spectra
            elif key == "is_incoming_energy_avialable_in_seperate_file":
                item.clicked.connect(lambda: self.create_mutliple_gui_items_from_checkboxes(item, key, hbox))
            elif key == "is_i0_avialable_in_seperate_file":
                item.clicked.connect(lambda: self.create_mutliple_gui_items_from_checkboxes(item, key, hbox))
            else:
                item.clicked.connect(lambda: self.update_dictionary_checkbox(key, item))
        elif item_type =="q_push_button":
            item_label = QLabel("")
            hbox.addWidget(item_label)
            item= QPushButton(item_label_text)
            hbox.addWidget(item)
            if key== "open file location":
                item.clicked.connect(lambda: self.open_folder(self.parameters["input_file_project_folder"], self.parameters["input_file_raw_data_folder"]))
            elif key== "plot inputted root data":
                item.clicked.connect(lambda: self.plot_inputted_data(self.parameters))

        else:
            print("Error: Item was not added to the GUI")
        return hbox

    def update_dictionary(self, key, updated_value):
        self.parameters[key] = updated_value

    def update_dictionary_checkbox(self, key, item):
                if item.isChecked():
                    self.parameters[key] = True
                    if key== "is_view_roots_or_input_txt":
                        self.vbox.insertLayout(self.vbox.count()-1,self.create_gui_item("input_complete_file_name", "Input example file name to view roots/txt \n(You can drop the file into the text box)", "q_line_edit", [""]))                
                else:
                    self.parameters[key] = False
    
    def validate_input(self, item):
        try:
            int(item.text())
        except ValueError:
            QMessageBox.warning(
                self, "Invalid Input", "Input must be an integer."
            )
            item.clear()

    def create_dynamic_gui_item_from_checkboxes(self, item, item_text, key, hbox, new_key, new_label_text):
        item_box_was_set_to_true= item.isChecked()
        if self.is_first_time_creating_checkboxes== False:
            if self.parameters["is_several_spectra_per_file"]:
                self.remove_item(self.vbox.indexOf(self.hbox_is_several_spectra)+1)
        
        if item_box_was_set_to_true:
            self.parameters[key] = True
            #self.update_dictionary_checkbox(key, True)
            if key== "is_several_spectra_per_file":
                self.item_is_several_spectra.setChecked(True)
                self.vbox.insertLayout(self.vbox.indexOf(hbox)+1,self.create_gui_item("txt_intensity_data_last_column", "Column of last spectrum value: \n Note: The first column has index zero", "q_line_edit", [""]))      
        else:
            self.parameters[key] = False
            #elif self.validate_input(item, key):
            #    if int(item_text) == 0:
            #        for array_index in range(len(self.parameters[new_key])):
            #            self.update_dictionary_array(new_key, array_index, "")
            #        if self.is_ignore_file_number_array_displayed:
            #            self.remove_item(self.vbox.indexOf(hbox)+1)
            #            self.is_ignore_file_number_array_displayed =False
            #    else: 
            #        if self.is_ignore_file_number_array_displayed:
            #           self.remove_item(self.vbox.indexOf(hbox)+1)
            #        self.vbox.insertLayout(self.vbox.indexOf(hbox)+1,self.create_gui_item(new_key, new_label_text, "q_array_inputs", [""]))
            #        self.is_ignore_file_number_array_displayed =True            


    def create_mutliple_gui_items_from_checkboxes(self, item, key, hbox):
        self.update_dictionary_checkbox(key, item)
        
        if key == "is_incoming_energy_avialable_in_seperate_file":
            if self.is_incoming_energy_avialable_in_seperate_file_displayed== False and self.parameters["is_incoming_energy_avialable_in_seperate_file"]:
                self.vbox.insertLayout(self.vbox.indexOf(hbox)+1,self.create_gui_item("complete_incoming_energy_file_location", "Input the complete file location for the incoming energy file: ", "q_line_edit", [""]))
                self.vbox.insertLayout(self.vbox.indexOf(hbox)+2,self.create_gui_item("complete_incoming_energy_file_name",  "Input file name for the incoming energy file: ", "q_line_edit", [""]))                
                self.is_incoming_energy_avialable_in_seperate_file_displayed =True
            elif self.is_incoming_energy_avialable_in_seperate_file_displayed == True and self.parameters["is_incoming_energy_avialable_in_seperate_file"] == False:
                self.remove_item(self.vbox.indexOf(hbox)+1)
                self.remove_item(self.vbox.indexOf(hbox)+2)
                self.is_incoming_energy_avialable_in_seperate_file_displayed =False
        elif key == "is_i0_avialable_in_seperate_file":
            if self.is_i0_avialable_in_seperate_file_displayed== False and self.parameters["is_i0_avialable_in_seperate_file"]:
                self.vbox.insertLayout(self.vbox.indexOf(hbox)+1, self.create_gui_item("is_use_same_file_for_i0_as_for_incoming_energy", "Is it the same file as for the incoming energy? ", "q_check_box", [""]))
                self.vbox.insertLayout(self.vbox.indexOf(hbox)+2, self.create_gui_item("complete_i0_file_location", "Input the complete file location for the I0 file: ", "q_line_edit", [""]))
                self.vbox.insertLayout(self.vbox.indexOf(hbox)+3, self.create_gui_item("complete_i0_file_name",  "Input file name for the I0 file: ", "q_line_edit", [""]))                
                self.is_i0_avialable_in_seperate_file_displayed =True
            elif self.is_i0_avialable_in_seperate_file_displayed == True and self.parameters["is_i0_avialable_in_seperate_file"] == False:
                self.remove_item(self.vbox.indexOf(hbox)+1)
                self.remove_item(self.vbox.indexOf(hbox)+2)
                self.remove_item(self.vbox.indexOf(hbox)+3)
                self.is_i0_avialable_in_seperate_file_displayed =False


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
        if self.parameters["input_file_format"] == "h5":
            self.second_window.close()
        plt.close()
        self.finished.emit()
        self.close()

    def save_and_close(self):
        parameter_scripts.save_parameters(self.parameters)
        self.parameters["is_program_running"]=False
        if self.parameters["input_file_format"] == "h5":
            self.second_window.close()
        plt.close()
        self.finished.emit()
        self.close()

    def close_program(self): 
        self.parameters["is_program_running"]=False
        if self.parameters["input_file_format"] == "h5":
            self.second_window.close()
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

    def plot_inputted_data(self, parameters):
        plt.close()
        plots= []
        if parameters["input_file_format"] =="h5":
            y_values = get_single_spectrum_h5_or_txt_file_scripts.get_single_spectrum_h5_file(parameters, parameters["h5_root_location_data"], False, parameters["input_complete_file_name_array"][0])
            x_values = [x for x in range(len(y_values))]
            plots.append([x_values, y_values, "Channel", "Counts" ])

            if parameters["is_incoming_energy_available_in_file"]:
                y_values = get_single_spectrum_h5_or_txt_file_scripts.get_single_spectrum_h5_file(parameters, parameters["h5_root_location_incoming_energy"], False, parameters["input_complete_file_name_array"][0])
                x_values = [x for x in range(len(y_values))]
                plots.append([x_values, y_values, "Time [Probably seconds]", "Incoming energy [Probably eV]"])

            if parameters["is_i0_available_in_file"]:
                y_values = get_single_spectrum_h5_or_txt_file_scripts.get_single_spectrum_h5_file(parameters, parameters["i0_root_location_data"], False, parameters["input_complete_file_name_array"][0])
                x_values = [x for x in range(len(y_values))]
                plots.append([x_values, y_values, "Time [Probably seconds]", "I0_value [Unit?]"])
            
            fig, axs = plt.subplots(len(plots))
            if parameters["is_incoming_energy_available_in_file"] or parameters["is_i0_available_in_file"]:
                for plot_number in range(len(plots)):
                    axs[plot_number].plot(plots[plot_number][0],plots[plot_number][1])
                    axs[plot_number].set(xlabel=plots[plot_number][2], ylabel= plots[plot_number][3])
            else:
                axs.plot(plots[0][0],plots[0][1])
                axs.set(xlabel=plots[0][2], ylabel= plots[0][3])
        elif parameters["input_file_format"] =="txt" or parameters["input_file_format"] =="dat" or parameters["input_file_format"] =="csv":
            y_values = get_single_spectrum_h5_or_txt_file_scripts.get_single_spectrum_txt_file(parameters, False, parameters["txt_intensity_data_row"], parameters["txt_intensity_data_column"], False, parameters["input_complete_file_name_array"][0], parameters["is_several_spectra_per_file"])
            x_values = [x for x in range(len(y_values))]
            plots.append([x_values, y_values, "Channel", "Counts" ])

            if parameters["is_incoming_energy_available_in_file"]:
                y_values = get_single_spectrum_h5_or_txt_file_scripts.get_single_spectrum_txt_file(parameters, parameters["is_txt_single_incoming_energy_value"], parameters["txt_incoming_energy_row_in_file"], parameters["txt_incoming_energy_column_in_file"], False, parameters["input_complete_file_name_array"][0], parameters["is_several_spectra_per_file"])
                if isinstance(y_values, np.ndarray):
                    x_values = [x for x in range(len(y_values))]
                else:
                    x_values=[0]
                plots.append([x_values, y_values, "Time [Probably seconds]", "Incoming energy [Probably eV]"])

            if parameters["is_i0_available_in_file"]:
                y_values = get_single_spectrum_h5_or_txt_file_scripts.get_single_spectrum_txt_file(parameters, parameters["is_txt_single_i0_value"], parameters["txt_i0_row_in_file"], parameters["txt_i0_column_in_file"], False, parameters["input_complete_file_name_array"][0], parameters["is_several_spectra_per_file"])
                if isinstance(y_values, np.ndarray):
                    x_values = [x for x in range(len(y_values))]
                else:
                    x_values=[0]
                plots.append([x_values, y_values, "Time [Probably seconds]", "I0_value [a.u]"])

            fig, axs = plt.subplots(len(plots))
            if parameters["is_incoming_energy_available_in_file"] or parameters["is_i0_available_in_file"]:
                for plot_number in range(len(plots)):
                    if isinstance(plots[plot_number][1], np.ndarray):
                        axs[plot_number].plot(plots[plot_number][0],plots[plot_number][1])
                    else: 
                        axs[plot_number].scatter(plots[plot_number][0],plots[plot_number][1])
                    axs[plot_number].set(xlabel=plots[plot_number][2], ylabel= plots[plot_number][3])
            else:
                if isinstance(plots[0][1], np.ndarray):
                    axs.plot(plots[0][0],plots[0][1])
                else: 
                    axs.scatter(plots[0][0],plots[0][1])
                    axs.set(xlabel=plots[0][2], ylabel= plots[0][3])
        
        
        plots_manager = plt.get_current_fig_manager()
        screen_geometry = QDesktopWidget().screenGeometry()
        plots_manager.window.setGeometry(50,80,floor(screen_geometry.width()/2 -50), floor(screen_geometry.height()-200))
        
        fig.tight_layout()
        fig.show()        

    def get_inputted_parameters_from_gui(self):
        return self.parameters


class SecondWindow(QMainWindow):
    def __init__(self, parameters, complete_file_location):
        super().__init__()
        screen_geometry = QDesktopWidget().screenGeometry()
        self.setFixedSize(floor(screen_geometry.width()/2 -5), screen_geometry.height()-160)
        self.parameters = parameters
        self.move(10,10)
        text = QTextEdit()
        layout = QVBoxLayout()
        layout.addWidget(text)
        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        with h5py.File(complete_file_location, 'r') as file:
            self.print_h5_structure_helper(file, '/', text)
        self.show()
    
    def print_h5_structure_helper(self,file, indent, text):
        for key in file.keys():
            item = file[key]
            text.append(indent + key)
            if isinstance(item, h5py.Group):
                self.print_h5_structure_helper(item, indent + '      ', text)
        return text

if __name__ == '__main__':
    input_file_location= "C:\\Users\\ponto479\\Documents\\02 Beamtime Data\\SLS Adress 03-2022\\RIXS"
    parameters= parameter_scripts.get_parameters(input_file_location)
    #parameters={"input_file_location": "C:\\Users\\ponto479\\Documents\\02 Beamtime Data\\SLS Adress 03-2022\\RIXS",
                #"is_program_running":True, "input_file_iteratable_file_number_start":"0100", "input_file_iteratable_file_number_end": "0120" }
    parameters["is_view_roots_or_input_txt"]
    parameters = run_main_gui(parameters)
    #print(parameters)