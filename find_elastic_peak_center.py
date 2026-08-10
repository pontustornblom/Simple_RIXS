#find_elastic_peak_center_2
import sys
import os
import platform
import subprocess
from PyQt5.QtWidgets import QLabel, QMainWindow, QCheckBox, QComboBox, QLineEdit, QPushButton, QLayout, QApplication, QVBoxLayout, QHBoxLayout, QWidget, QDesktopWidget, QLabel, QTextEdit, QMessageBox
#from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QEventLoop
from PyQt5.QtCore import pyqtSignal
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from math import floor
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import subprocess
from scipy.optimize import curve_fit
from scipy import stats
import h5py
import parameter_scripts
import get_single_spectrum_h5_or_txt_file_scripts
import iteratable_number_to_int_script
import find_elastic_peak_maximum_script
import iteratable_number_to_float_script

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
        #self.setMinimumWidth(self.width())
        #self.adjustSize()
        self.move(floor(screen_geometry.width()/2 +10), 10)

        self.is_energy_window_used_displayed = False
        self.is_plot_intensity_limits_used_displayed= False

        self.vbox = QVBoxLayout()

        self.vbox.addLayout(self.create_gui_item("input_file_project_folder", "Folder of the current project: ", "q_line_edit", [""]))
        self.vbox.addLayout(self.create_gui_item("input_file_raw_data_folder", "Subfolder where the raw data is stored: ", "q_line_edit", [""]))
        self.vbox.addLayout(self.create_gui_item("open file location", "Open raw data file location", "q_push_button",  [""]))   
        #if self.parameters["is_incoming_energy_available_in_file"] == False:
        #    self.vbox.addLayout(self.create_gui_item("energy_of_first_line_spectra", "Excitation energy of first spectra [eV]: ", "q_line_edit", [""]))
        #    self.vbox.addLayout(self.create_gui_item("energy_of_last_line_spectra", "Excitation energy of last spectra [eV]: ", "q_line_edit", [""]))
                
        self.vbox.addLayout(self.create_gui_item("is_plot_intensity_limits_used_array_0", "Would you like to set an intensity window for the plot? ", "q_check_box", [""]))
        if self.parameters["is_plot_intensity_limits_used_array"][0]:
            self.vbox.addLayout(self.create_gui_item("plot_intensity_min_array_0", "Input the lower cut off for the incoming energy window: ", "q_line_edit", [""]))
            self.vbox.addLayout(self.create_gui_item("plot_intensity_max_array_0", "Input the upper cut off for the incoming energy window: ", "q_line_edit", [""]))
            self.is_plot_intensity_limits_used_displayed= True 

        self.vbox.addLayout(self.create_gui_item("approximate_channel_of_first_elastic_peak", "Approximate channel number of the first elastic peak: ", "q_line_edit", [""]))
        self.vbox.addLayout(self.create_gui_item("approximate_channel_of_last_elastic_peak", "Approximate channel number of the last elastic peak: ", "q_line_edit", [""]))
        self.vbox.addLayout(self.create_gui_item("channels_above_and_below_for_finding_elastic", "Approximate channel number above and below elastic peak to find the maximum intensity: ", "q_line_edit", [""]))
        self.vbox.addLayout(self.create_gui_item("channels_above_and_below_elastic_to_fit", "Approximate channel number above and below the max intensity to calculate elastic peak center: ", "q_line_edit", [""]))
        self.vbox.addLayout(self.create_gui_item("degree_of_energy_per_channel_polynomial", "What degree polynomial do you want to fit the elastic peaks to? (Set to 1 for linear) \n(Note that the current plot will only show a linear fit, but later it will be the polynomial you want)\n(Make sure the channels above and below is large enough if you are not doing a linear fit) ", "q_line_edit", [""]))        
        self.vbox.addLayout(self.create_gui_item("is_input_energy_per_channel_and_intercept_manually", "Would you like to manually input the energy per channel polynomial coefficients? \n(You will input this in a later window) ", "q_check_box", [""]))
        self.vbox.addLayout(self.create_gui_item("is_use_converging_weighted_squared_peak_center_finder", "Find center of elastic peak by squared weighted intensities and by converging the solution: \n(15 points above and below maximum is recommended for very low resolution spectras) ", "q_check_box", [""]))
        self.vbox.addLayout(self.create_gui_item("is_use_converging_weighted_peak_center_finder", "Find center of elastic peak by weighted intensities and by converging the solution: \n(Use more than 10 points above and below maximum! 15 is recommended for very low resolution spectras) ", "q_check_box", [""]))
        self.vbox.addLayout(self.create_gui_item("is_weighted_elastic_peak_fit", "Find center of elastic peak by weighted intensities: ", "q_check_box", [""]))
        self.vbox.addLayout(self.create_gui_item("is_full_gaussian_elastic_peak_fit", "Find center of elastic peak by fitting a full gaussian: ", "q_check_box", [""]))
        self.vbox.addLayout(self.create_gui_item("is_half_gaussian_elastic_peak_fit", "Find center of elastic peak by fitting a half gaussian: \n (To the high energy side of the peak) ", "q_check_box", [""]))
        self.vbox.addLayout(self.create_gui_item("is_intensity_weight_for_linear_fit", "Would you like the polynomial fit to the elastic peak centers to be weighted by the intensity of the elastic peak? ", "q_check_box", [""]))


        self.vbox.addLayout(self.create_gui_item("Zoom in on elastic peak", "Zoom in on elastic peak", "q_push_button",  [""]))
        self.vbox.addLayout(self.create_gui_item("Update the plot", "Update the plot", "q_push_button",  [""]))

        self.vbox.addLayout(self.create_bottom_buttons())

        self.central_widget = QWidget()
        self.central_widget.setLayout(self.vbox)
        self.setCentralWidget(self.central_widget)
        self.setWindowTitle("Simple RIXS Find Elastic Peak")
        self.show()

        #x= [1,2,3,4,5]
        #y=[1,3,6,8,20]
        #plt.plot(x,y)
        #plt.show()
        #plt.show(block=False)
        #plt.pause(0.001)
        #plt.close()
        #if self.is_first_and_last_spectrum_displayed== False:
        
        #THE LINE BELOW HAS TO BE TOGGLED ON AND OFF MANUALLY
        #self.plot_inputted_data(self.parameters, "")
        
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
            elif key != "input_file_project_folder" and key != "input_file_raw_data_folder":
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
                        self.vbox.insertLayout(self.vbox.count()-1,self.create_gui_item("input_complete_file_name", "Input example file name to view roots/txt ", "q_line_edit", [""]))                
                else:
                    self.parameters[key] = False

    def update_dictionary_checkbox_array(self, key, array_index, item):
            #if self.validate_input_for_array(key, array_index, item):
            self.parameters[key][array_index] = item.isChecked()

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
        if item.text() != self.parameters[key]:
            self.update_dictionary(key, item.text())
            if item.text()== "":
                try:
                    int(item.text())
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
                        int(iteratable_number_to_int_script.iteratable_number_to_int(item.text()))
                        return True
                    else:
                        int(item.text())
                        return True
                except ValueError:
                    QMessageBox.warning(
                        self, "Invalid Input", "Input must be an integer."
                    )
                    item.clear()
                    return False

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

    def get_approximate_channel_per_energy_and_incoming_energy_array(self, parameters, iteratable_file_number_array, y_values):
        #The different options in this function have not been tested thoroughly
        condition = True
        while condition:
            first_spectra_approximate_channel= iteratable_number_to_int_script.iteratable_number_to_int(self.parameters["approximate_channel_of_first_elastic_peak"])
            last_spectra_approximate_channel= iteratable_number_to_int_script.iteratable_number_to_int(self.parameters["approximate_channel_of_last_elastic_peak"])
            if last_spectra_approximate_channel > len(y_values):
                self.update_dictionary("approximate_channel_of_first_elastic_peak", str(int((int(parameters["approximate_channel_of_first_elastic_peak"]) + 9 ) / 10)))
                self.update_dictionary("approximate_channel_of_last_elastic_peak", str(int((int(parameters["approximate_channel_of_last_elastic_peak"]) + 9 ) / 10)))
            elif last_spectra_approximate_channel <= 20:
                print("Warning. you might have an empty intensity array, or a very short one")
                condition = False
            else:
                condition = False
            

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
                    dataframe = pd.read_csv(complete_file_location, sep='\t', skiprows=data_row, usecols=[data_column], header=None, low_memory=False)
                elif parameters["txt_delimiter"] == " ":
                    dataframe = pd.read_csv(complete_file_location, sep=' ', skiprows=data_row, usecols=[data_column], header=None, low_memory=False)
                else:
                    dataframe = pd.read_csv(complete_file_location, sep=parameters["txt_delimiter"], skiprows=data_row, usecols=[data_column], header=None, low_memory=False)
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
        intensity_weights_array= np.zeros(len(iteratable_file_number_array))
        intensity_array_index= 0
        for iteratable_number in iteratable_file_number_array:
            #iteratable_int= iteratable_number_to_int_script.iteratable_number_to_int(iteratable_number)
            if parameters["input_file_format"] =="h5":
                y_values = get_single_spectrum_h5_or_txt_file_scripts.get_single_spectrum_h5_file(parameters, parameters["h5_root_location_data"], True, iteratable_number)
                if parameters["is_i0_avialable_in_seperate_file"]:
                    #A lot of code here since the "Get singel spectrum script" is aimed at getting data from the datafile.
                    if parameters["is_use_same_file_for_i0_as_for_incoming_energy"]:
                        complete_file_location = os.path.join(parameters["complete_incoming_energy_file_location"], parameters["complete_incoming_energy_file_name"])
                    else:
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

                if False:
                    #The four rows below adds 9 datapoints in between each datapoints and interpolates the data. This is to make finer adjustments when alinging the data
                    original_length = len(y_values)
                    desired_length = original_length * 10 - 9
                    x_values = np.linspace(0, original_length - 1, desired_length)
                    y_values = np.interp(x_values, np.arange(original_length), y_values)
                    x_values = np.arange(0, len(y_values))

                array_of_intensity_arrays[intensity_array_index]= y_values
                intensity_array_index+= 1
            elif parameters["input_file_format"] =="txt":
                y_values = get_single_spectrum_h5_or_txt_file_scripts.get_single_spectrum_txt_file(parameters, False, parameters["txt_intensity_data_row"], parameters["txt_intensity_data_column"], True, iteratable_number, parameters["is_several_spectra_per_file"])
                if parameters["is_i0_avialable_in_seperate_file"]:
                    if parameters["is_use_same_file_for_i0_as_for_incoming_energy"]:
                        complete_file_location = os.path.join(parameters["complete_incoming_energy_file_location"], parameters["complete_incoming_energy_file_name"])
                    else:
                        complete_file_location = os.path.join(parameters["complete_i0_file_location"], parameters["complete_i0_file_name"])
                    if complete_file_location[-3:] == ".h5":
                        complete_file_location=complete_file_location[:-3]
                    if complete_file_location[-4:] != ".txt":
                        complete_file_location = complete_file_location + ".txt"

                    data_row = int(parameters["txt_i0_row_in_file"])
                    data_column= int(parameters["txt_i0_column_in_file"])
                    if parameters["txt_delimiter"] == "Tab":
                        dataframe = pd.read_csv(complete_file_location, sep='\t', skiprows=data_row, usecols=[data_column], header=None, low_memory=False)
                    elif parameters["txt_delimiter"] == "Space":
                        dataframe = pd.read_csv(complete_file_location, sep=' ', skiprows=data_row, usecols=[data_column], header=None, low_memory=False)
                    else:
                        dataframe = pd.read_csv(complete_file_location, sep=parameters["txt_delimiter"], skiprows=data_row, usecols=[data_column], header=None, low_memory=False)
                    # Access the values of the column
                    i0_values = dataframe.iloc[:, 0].values

                    if isinstance(i0_values[0], np.ndarray) or isinstance(i0_values[0], list):
                        if len(i0_values[0]) >1: 
                            for iteratable_number in range(len(iteratable_file_number_array)):
                                i0_values[iteratable_number]= np.mean(i0_values[iteratable_number])
                        else:
                            for iteratable_number in range(len(iteratable_file_number_array)):
                                i0_values[iteratable_number]= i0_values[iteratable_number][0]

                    y_values= y_values/i0_values[array_index]
                elif parameters["is_i0_available_in_file"]:
                    i0_values = get_single_spectrum_h5_or_txt_file_scripts.get_single_spectrum_txt_file(parameters, parameters["is_txt_single_i0_value"], parameters["txt_i0_row_in_file"], parameters["txt_i0_column_in_file"], True, iteratable_number)
                    i0_mean= np.mean(i0_values)
                    y_values= y_values/i0_mean
                if False:
                    #The four rows below adds 9 datapoints in between each datapoints and interpolates the data. This is to make finer adjustments when alinging the data
                    original_length = len(y_values)
                    desired_length = original_length * 10 - 9
                    x_values = np.linspace(0, original_length - 1, desired_length)
                    y_values = np.interp(x_values, np.arange(original_length), y_values)
                    x_values = np.arange(0, len(y_values))

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
        x_values = np.arange(0, len(y_values))

        return elastic_peak_center_array, x_values, array_of_intensity_arrays, intensity_weights_array


    def plot_inputted_data(self, parameters, extra_plot_parameters):
        plt.close()
        plots= []
        
        if parameters["input_file_format"] =="h5":
            y_values = get_single_spectrum_h5_or_txt_file_scripts.get_single_spectrum_h5_file(parameters, parameters["h5_root_location_data"], True, parameters["input_file_iteratable_file_number_start"])
            x_values = [x for x in range(len(y_values))]
            plots.append([x_values, y_values, "Channel", "Counts" ])
            y_values = get_single_spectrum_h5_or_txt_file_scripts.get_single_spectrum_h5_file(parameters, parameters["h5_root_location_data"], True, parameters["input_file_iteratable_file_number_end"])
            x_values = [x for x in range(len(y_values))]
            plots.append([x_values, y_values, "Channel", "Counts" ])

            condition = True
            while condition:
                first_spectra_approximate_channel= iteratable_number_to_int_script.iteratable_number_to_int(self.parameters["approximate_channel_of_first_elastic_peak"])
                last_spectra_approximate_channel= iteratable_number_to_int_script.iteratable_number_to_int(self.parameters["approximate_channel_of_last_elastic_peak"])

                if last_spectra_approximate_channel > len(y_values):
                    self.update_dictionary("approximate_channel_of_first_elastic_peak", str(int((int(parameters["approximate_channel_of_first_elastic_peak"]) + 9 ) / 10)))
                    self.update_dictionary("approximate_channel_of_last_elastic_peak", str(int((int(parameters["approximate_channel_of_last_elastic_peak"]) + 9 ) / 10)))
                elif last_spectra_approximate_channel <= 20:
                    print("Warning. you might have an empty intensity array, or a very short one")
                    condition = False
                else:
                    condition = False

            #The for loop below adds 9 datapoints in between each datapoints and interpolates the data. This is to make finer adjustments when alinging the data
            if False:
                for spectra in range(2):
                    original_length = len(plots[spectra][1])
                    desired_length = original_length * 10 - 9

                    x_values = np.linspace(0, original_length - 1, desired_length)
                    new_intensity_array = np.interp(x_values, np.arange(original_length), plots[spectra][1])
                    x_values = np.arange(0, len(y_values))

                    plots[spectra][0]=  x_values
                    plots[spectra][1]=  new_intensity_array

            self.fig, axs = plt.subplots(3)
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
                        axs[plot_number].scatter(highest_intensity_channel_first_graph, highest_intensity_first_graph, color="red")
                        axs[plot_number].axvline(int(parameters["approximate_channel_of_first_elastic_peak"])- int(parameters["channels_above_and_below_for_finding_elastic"]), color="red")
                        axs[plot_number].axvline(int(parameters["approximate_channel_of_first_elastic_peak"])+ int(parameters["channels_above_and_below_for_finding_elastic"]), color="red")
                        axs[plot_number].set_ylim(ymax=highest_intensity_first_graph + highest_intensity_first_graph*0.1, ymin=0)
                    elif plot_number == 1:
                        y_values = get_single_spectrum_h5_or_txt_file_scripts.get_single_spectrum_h5_file(parameters, parameters["h5_root_location_data"], True, parameters["input_file_iteratable_file_number_end"])
                        highest_intensity_last_graph, highest_intensity_channel_last_graph = find_elastic_peak_maximum_script.find_elastic_peak_maximum(parameters, y_values, int(parameters["approximate_channel_of_last_elastic_peak"]))
                        for channel in range(highest_intensity_channel_last_graph- int(parameters["channels_above_and_below_elastic_to_fit"]), highest_intensity_channel_last_graph+ int(parameters["channels_above_and_below_elastic_to_fit"])+ 1):
                            axs[plot_number].scatter(channel,y_values[channel], color="green")
                        axs[plot_number].scatter(highest_intensity_channel_last_graph,highest_intensity_last_graph, color="red")
                        axs[plot_number].axvline(int(parameters["approximate_channel_of_last_elastic_peak"])- int(parameters["channels_above_and_below_for_finding_elastic"]), color="red")
                        axs[plot_number].axvline(int(parameters["approximate_channel_of_last_elastic_peak"])+ int(parameters["channels_above_and_below_for_finding_elastic"]), color="red")
                        axs[plot_number].set_ylim(ymax=highest_intensity_last_graph + highest_intensity_last_graph*0.1, ymin=0)

        elif parameters["input_file_format"] =="txt":
            y_values = get_single_spectrum_h5_or_txt_file_scripts.get_single_spectrum_txt_file(parameters, False, parameters["txt_intensity_data_row"], parameters["txt_intensity_data_column"], True, parameters["input_file_iteratable_file_number_start"], parameters["is_several_spectra_per_file"])
            x_values = [x for x in range(len(y_values))]
            plots.append([x_values, y_values, "Channel", "Counts" ])
            y_values = get_single_spectrum_h5_or_txt_file_scripts.get_single_spectrum_txt_file(parameters, False, parameters["txt_intensity_data_row"], parameters["txt_intensity_data_column"], True, parameters["input_file_iteratable_file_number_end"], parameters["is_several_spectra_per_file"])
            x_values = [x for x in range(len(y_values))]
            plots.append([x_values, y_values, "Channel", "Counts" ])

            condition = True
            while condition:
                first_spectra_approximate_channel= iteratable_number_to_int_script.iteratable_number_to_int(self.parameters["approximate_channel_of_first_elastic_peak"])
                last_spectra_approximate_channel= iteratable_number_to_int_script.iteratable_number_to_int(self.parameters["approximate_channel_of_last_elastic_peak"])

                if last_spectra_approximate_channel > len(y_values):
                    self.update_dictionary("approximate_channel_of_first_elastic_peak", str(int((int(parameters["approximate_channel_of_first_elastic_peak"]) + 9 ) / 10)))
                    self.update_dictionary("approximate_channel_of_last_elastic_peak", str(int((int(parameters["approximate_channel_of_last_elastic_peak"]) + 9 ) / 10)))
                elif last_spectra_approximate_channel <= 20:
                    print("Warning. you might have an empty intensity array, or a very short one")
                    condition = False
                else:
                    condition = False
            if False:
            #The for loop below adds 9 datapoints in between each datapoints and interpolates the data. This is to make finer adjustments when alinging the data
                for spectra in range(2):
                    original_length = len(plots[spectra][1])
                    desired_length = original_length * 10 - 9

                    x_values = np.linspace(0, original_length - 1, desired_length)
                    new_intensity_array = np.interp(x_values, np.arange(original_length), plots[spectra][1])
                    x_values = np.arange(0, len(new_intensity_array))

                    plots[spectra][0]=  x_values
                    plots[spectra][1]=  new_intensity_array

            self.fig, axs = plt.subplots(3)
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
                        y_values = plots[plot_number][1]
                        #y_values = get_single_spectrum_h5_or_txt_file_scripts.get_single_spectrum_txt_file(parameters, False, parameters["txt_intensity_data_row"], parameters["txt_intensity_data_column"], True, parameters["input_file_iteratable_file_number_start"], parameters["is_several_spectra_per_file"])
                        highest_intensity_first_graph, highest_intensity_channel_first_graph = find_elastic_peak_maximum_script.find_elastic_peak_maximum(parameters, y_values, int(parameters["approximate_channel_of_first_elastic_peak"]))
                        for channel in range(highest_intensity_channel_first_graph- int(parameters["channels_above_and_below_elastic_to_fit"]), highest_intensity_channel_first_graph+ int(parameters["channels_above_and_below_elastic_to_fit"])+ 1):
                            axs[plot_number].scatter(channel,y_values[channel], color="green")
                        axs[plot_number].scatter(highest_intensity_channel_first_graph,highest_intensity_first_graph, color="red")
                        axs[plot_number].axvline(highest_intensity_channel_first_graph- int(parameters["channels_above_and_below_for_finding_elastic"]), color="red")
                        axs[plot_number].axvline(highest_intensity_channel_first_graph+ int(parameters["channels_above_and_below_for_finding_elastic"]), color="red")
                        axs[plot_number].set_ylim(ymax=highest_intensity_first_graph + highest_intensity_first_graph*0.1, ymin=0)
                    elif plot_number == 1:
                        y_values = plots[plot_number][1]
                        #y_values = get_single_spectrum_h5_or_txt_file_scripts.get_single_spectrum_txt_file(parameters, False, parameters["txt_intensity_data_row"], parameters["txt_intensity_data_column"], True, parameters["input_file_iteratable_file_number_end"], parameters["is_several_spectra_per_file"])
                        highest_intensity_last_graph, highest_intensity_channel_last_graph = find_elastic_peak_maximum_script.find_elastic_peak_maximum(parameters, y_values, int(parameters["approximate_channel_of_last_elastic_peak"]))
                        for channel in range(highest_intensity_channel_last_graph- int(parameters["channels_above_and_below_elastic_to_fit"]), highest_intensity_channel_last_graph+ int(parameters["channels_above_and_below_elastic_to_fit"])+ 1):
                            axs[plot_number].scatter(channel,y_values[channel], color="green")
                        axs[plot_number].scatter(highest_intensity_channel_last_graph,highest_intensity_last_graph, color="red")
                        axs[plot_number].axvline(highest_intensity_channel_last_graph- int(parameters["channels_above_and_below_for_finding_elastic"]), color="red")
                        axs[plot_number].axvline(highest_intensity_channel_last_graph+ int(parameters["channels_above_and_below_for_finding_elastic"]), color="red")
                        axs[plot_number].set_ylim(ymax=highest_intensity_last_graph + highest_intensity_last_graph*0.1, ymin=0)
        
        iteratable_file_number_array= self.get_iteratable_file_number_array(parameters)

        approximate_channel_per_energy, incoming_energy_array = self.get_approximate_channel_per_energy_and_incoming_energy_array(parameters, iteratable_file_number_array, y_values)
        
        #approximate_channel_per_energy= approximate_channel_per_energy * 5
        #apporximate_energy_per_channel = 1/approximate_channel_per_energy
        
        #self.is_first_and_last_spectrum_displayed= True
        elastic_peak_center_array, x_values, array_of_intensity_arrays, intensity_weights_array= self.get_elastic_peak_channel_center_array(parameters, approximate_channel_per_energy, iteratable_file_number_array, incoming_energy_array)

        linregress_result = stats.linregress(np.array([highest_intensity_channel_first_graph,highest_intensity_channel_last_graph]), np.array([incoming_energy_array[0],incoming_energy_array[-1]]))
        very_apporximate_energy_per_channel_slope = linregress_result[0]
        very_apporximate_energy_per_channel_intercept = linregress_result[1]

        array_of_intensity_arrays = np.vstack(array_of_intensity_arrays).astype(float)

        colormap = "turbo"
        #im = axs[0].imshow(array_of_intensity_arrays, cmap='viridis', origin='lower', extent=[x_values[0], x_values[-1], incoming_energy_array[0] - ((incoming_energy_array[1]-incoming_energy_array[0])/2), incoming_energy_array[-1] + ((incoming_energy_array[-1]-incoming_energy_array[-2])/2)] , aspect='auto')
        im = axs[2].pcolormesh(x_values, incoming_energy_array, array_of_intensity_arrays, cmap=colormap)

        #array_of_energy_loss_arrays= np.zeros(len())
        self.fig = axs[2].figure
        cbar = axs[2].figure.colorbar(im, ax=axs)

        axs[2].plot(x_values, very_apporximate_energy_per_channel_slope*x_values + very_apporximate_energy_per_channel_intercept, color='red')
       
        text = f'Elastic line based on the two points:\ny={very_apporximate_energy_per_channel_slope:.8f}x+{very_apporximate_energy_per_channel_intercept:.2f}'
        axs[2].text(0.05, 0.95, text, transform=axs[2].transAxes, fontsize=12, verticalalignment='top', bbox=dict(facecolor='white', alpha=0.5))

        axs[2].set_ylim(incoming_energy_array[0]- ((incoming_energy_array[1]-incoming_energy_array[0])/2), incoming_energy_array[-1] + ((incoming_energy_array[-1]-incoming_energy_array[-2])/2))
        axs[2].set_xlabel('Channel')
        axs[2].set_ylabel('Excitation energy [eV]')

        plots_manager = plt.get_current_fig_manager()
        screen_geometry = QDesktopWidget().screenGeometry()
        plots_manager.window.setGeometry(50,80,floor(screen_geometry.width()/2 -50), floor(screen_geometry.height()-200))
        #plt.tight_layout()

        if parameters["is_plot_intensity_limits_used_array"][0]:
            im.set_clim(vmin=float(parameters["plot_intensity_min_array"][0]), vmax=float(parameters["plot_intensity_max_array"][0]))
            im.set_clim(vmin=float(parameters["plot_intensity_min_array"][0]), vmax=float(parameters["plot_intensity_max_array"][0]))

        self.fig.show()


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
