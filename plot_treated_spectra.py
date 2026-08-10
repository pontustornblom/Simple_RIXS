#plot_treated_spectra
import sys
import os
import platform
import subprocess
from PyQt5.QtWidgets import QLabel, QMainWindow, QCheckBox, QComboBox, QLineEdit, QPushButton, QLayout, QApplication, QVBoxLayout, QHBoxLayout, QWidget, QDesktopWidget, QLabel, QTextEdit, QMessageBox
#from PyQt5.QtGui import QPixmap
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from math import floor
import numpy as np
from PyQt5.QtCore import QEventLoop
from PyQt5.QtCore import pyqtSignal
import pandas as pd
import matplotlib.pyplot as plt
import subprocess
from scipy.optimize import curve_fit
from scipy import stats
import json
import parameter_scripts
import get_single_spectrum_h5_or_txt_file_scripts
import iteratable_number_to_int_script
import find_elastic_peak_maximum_script
import create_complete_file_location_view_roots_or_txt_script

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

        #self.is_first_and_last_spectrum_displayed= False

        self.vbox = QVBoxLayout()

        self.vbox.addLayout(self.create_gui_item("input_file_project_folder", "Folder of the current project: ", "q_line_edit", [""]))
        self.vbox.addLayout(self.create_gui_item("input_file_raw_data_folder", "Subfolder where the raw data is stored: ", "q_line_edit", [""]))
        self.vbox.addLayout(self.create_gui_item("open file location", "Open raw data file location", "q_push_button",  [""]))   

        self.vbox.addLayout(self.create_gui_item("", " Does the peak fit look good? \nIf not you have to cancel and choose a different peak fit or look at the data.\nIf everything looks good then a figure will be saved when you hit Save and continue", "q_text_label", [""]))

        #self.vbox.addLayout(self.create_gui_item("approximate_channel_of_first_elastic_peak", "Approximate channel number of the first elastic peak: ", "q_line_edit", [""]))
        #self.vbox.addLayout(self.create_gui_item("approximate_channel_of_last_elastic_peak", "Approximate channel number of the last elastic peak: ", "q_line_edit", [""]))
        #self.vbox.addLayout(self.create_gui_item("channels_above_and_below_for_finding_elastic", "Approximate channel number above and below elastic peak to find the maximum intensity: ", "q_line_edit", [""]))
        #self.vbox.addLayout(self.create_gui_item("channels_above_and_below_elastic_to_fit", "Approximate channel number above and below the max intensity to calculate elastic peak center: ", "q_line_edit", [""]))
        #self.vbox.addLayout(self.create_gui_item("is_weighted_elastic_peak_fit", "Find center of elastic peak by weighted intensities: ", "q_check_box", [""]))
        #self.vbox.addLayout(self.create_gui_item("is_full_gaussian_elastic_peak_fit", "Find center of elastic peak by fitting a full gaussian: ", "q_check_box", [""]))
        #self.vbox.addLayout(self.create_gui_item("is_half_gaussian_elastic_peak_fit", "Find center of elastic peak by fitting a half gaussian: \n (To the high energy side of the peak) ", "q_check_box", [""]))

        #self.vbox.addLayout(self.create_gui_item("Zoom in on elastic peak", "Zoom in on elastic peak", "q_push_button",  [""]))
        #self.vbox.addLayout(self.create_gui_item("Update the plot", "Update the plot", "q_push_button",  [""]))

        self.vbox.addLayout(self.create_bottom_buttons())

        self.central_widget = QWidget()
        self.central_widget.setLayout(self.vbox)
        self.setCentralWidget(self.central_widget)
        self.setWindowTitle("Simple RIXS Plot treated spectra")
        self.show()

        #if self.is_first_and_last_spectrum_displayed== False:
        
        #This line below has to b etoggleed manually (If this script actually needs to plot something)
        self.plot_inputted_data(self.parameters, "")
        
        #parameters, complete_file_location = create_complete_file_location_view_roots_or_txt_script.create_complete_file_location_view_roots_or_txt(self.parameters)


    def create_gui_item(self, key, item_label_text, item_type, combo_box_options):
        hbox = QHBoxLayout()
        item_label = QLabel(item_label_text)
        if item_type =="q_line_edit":
            hbox.addWidget(item_label)
            item = QLineEdit(self.parameters[key])
            hbox.addWidget(item)
            if key != "input_file_project_folder" and key != "input_file_raw_data_folder":
                item.editingFinished.connect(lambda item=item, key=key: self.validate_input(item, key))
            else:
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
        figure_name= "treated_spectra_" + self.parameters["txt_intensity_data_column"] + "_" + str(self.incoming_energy) + "eV"
        figure_name+="_" + self.parameters["input_complete_file_name_array"][0][:-9]
        figure_parameters_name= figure_name
        figure_data_name= figure_name
        figure_name+="_figure.png"
        figure_parameters_name+="_parameters.txt"
        figure_data_name+= "_data.txt"
        figure_path= os.path.join(self.parameters["input_file_project_folder"], "Simple RIXS Figures")
        if not os.path.exists(figure_path):
            os.makedirs(figure_path)
        
        full_figure_path= os.path.join(figure_path, figure_name)
        self.figure_to_save.savefig(full_figure_path)

        full_parameters_path=os.path.join(figure_path, figure_parameters_name)
        formatted_parameters = json.dumps(self.parameters, indent=0)
        with open(full_parameters_path, "w") as parameters_file:
            parameters_file.write(formatted_parameters)

        full_data_path=os.path.join(figure_path, figure_data_name) 
        data_dictionary= {self.x_values_header:self.treated_data_array[0], 'Intensity [a.u]':self.treated_data_array[1]}
        
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

        if parameters["is_incoming_energy_available_in_file"]:
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
    
    def get_intensity_array(self, parameters):

        #iteratable_int= iteratable_number_to_int_script.iteratable_number_to_int(iteratable_number)
        if parameters["input_file_format"] =="h5":
            y_values = get_single_spectrum_h5_or_txt_file_scripts.get_single_spectrum_h5_file(parameters, parameters["h5_root_location_data"], False, "")
            if parameters["is_i0_available_in_file"]:
                i0_values = get_single_spectrum_h5_or_txt_file_scripts.get_single_spectrum_h5_file(parameters, parameters["i0_root_location_data"], False, "")
                i0_mean= np.mean(i0_values)
                y_values= y_values/i0_mean
        elif parameters["input_file_format"] =="txt":
            y_values = get_single_spectrum_h5_or_txt_file_scripts.get_single_spectrum_txt_file(parameters, False, parameters["txt_intensity_data_row"], parameters["txt_intensity_data_column"], False, "", parameters["is_several_spectra_per_file"])
            if parameters["is_i0_available_in_file"]:
                i0_values = get_single_spectrum_h5_or_txt_file_scripts.get_single_spectrum_txt_file(parameters, parameters["is_txt_single_i0_value"], parameters["txt_i0_row_in_file"], parameters["txt_i0_column_in_file"], False, "", False)
                i0_mean= np.mean(i0_values)
                y_values= y_values/i0_mean
        print("maybe it is better to select a mean around the minimum value")
        y_zero_intensity = np.min(y_values)
        print("I dont know how I should select the interval for the normalization of the 1 intensity.")
        y_one_intensity = np.mean(y_values[-round(len(y_values)/20):])

        intensity_normalized = (y_values - y_zero_intensity) / (y_one_intensity - y_zero_intensity)
        #x_values = np.arange(1, len(y_values) + 1)
        #intensity_normalized = y_values
        return intensity_normalized

    def plot_inputted_data(self, parameters, extra_plot_parameters):
        plt.close()
        plots= []
        
        #iteratable_file_number_array= self.get_iteratable_file_number_array(parameters)

        parameters, complete_file_location = create_complete_file_location_view_roots_or_txt_script.create_complete_file_location_view_roots_or_txt(parameters, False, "")
        header_row= 0
        data_row = 1
        second_column_header_dataframe= pd.read_csv(complete_file_location, sep='\t', skiprows=header_row, usecols=[1], header=None)
        second_column_header= second_column_header_dataframe.iloc[0, 0]
        if second_column_header[:9]== "Intensity":
            intensity_column= int(parameters["txt_intensity_data_column"])
        elif second_column_header[:15]== "Incoming energy":
            intensity_column= 2 + int(parameters["txt_intensity_data_column"])
            incoming_energy_dataframe= pd.read_csv(complete_file_location, sep='\t', skiprows=data_row, usecols=[1], header=None)
            self.incoming_energy= incoming_energy_dataframe.iloc[intensity_column, 0] #It should be intensity_column here even though it is the row.

        intensity_dataframe = pd.read_csv(complete_file_location, sep='\t', skiprows=data_row, usecols=[intensity_column], header=None)
        intensity_array=intensity_dataframe.iloc[:, 0].values
        
        x_values_dataframe= pd.read_csv(complete_file_location, sep='\t', skiprows=data_row, usecols=[0], header=None)
        x_values= x_values_dataframe.iloc[:, 0].values

        x_values_header_dataframe = pd.read_csv(complete_file_location, sep='\t', skiprows=header_row, usecols=[0], header=None)
        self.x_values_header= x_values_header_dataframe.iloc[0, 0]


        #incoming_energy_array = self.get_incoming_energy_array(parameters)
        #apporximate_energy_per_channel = 1/approximate_channel_per_energy
        #intensity_array= self.get_intensity_array(parameters)
       #self.is_first_and_last_spectrum_displayed= True
        #intensity_arrays= self.get_elastic_peak_channel_center_array(parameters, approximate_channel_per_energy, iteratable_file_number_array, incoming_energy_array)
        #exact_energy_per_channel_slope, exact_energy_per_channel_intercept, exact_energy_per_channel_r_value, exact_energy_per_channel_p_value, exact_energy_per_channel_std_err = stats.linregress(elastic_peak_center_array, incoming_energy_array)
        #Nej det här under borde bli fel, interceptet gäller väl bara för elastic peaken?
        #outgoing_energy= x_values*exact_energy_per_channel_slope + exact_energy_per_channel_intercept
        #array_of_intensity_arrays_energy_loss= np.zeros(len(iteratable_file_number_array), dtype=object)
        #energy_loss_array= exact_energy_per_channel_slope*(x_values - elastic_peak_center_array[-1])
        #for spectra_index in range(len(array_of_intensity_arrays)):
        #    first_part_of_array= array_of_intensity_arrays[spectra_index][:elastic_peak_center_array[spectra_index] - elastic_peak_center_array[-1]]
        #    second_part_of_array= array_of_intensity_arrays[spectra_index][elastic_peak_center_array[spectra_index] - elastic_peak_center_array[-1]:]
        #    array_of_intensity_arrays_energy_loss[spectra_index]=np.concatenate((second_part_of_array, first_part_of_array), axis=None)
        
        fig, ax = plt.subplots(1)
        #intensity_max=100
        #intensity_min=0
        #vmax=intensity_max, vmin=intensity_min,

        #intensity_array = np.vstack(intensity_array).astype(float)
        print("vmax,vmin,cmap och kanske annat i plotten här nere måste göra om till parameter inputs.")
        im = ax.plot(x_values, intensity_array)

        #cbar = axs.figure.colorbar(im, ax=axs)
        
        print("Use this to make a function to save the treated data")
        self.treated_data_array= np.array([x_values, intensity_array], dtype=object)
        self.figure_to_save = fig
        ax.set_xlabel(self.x_values_header)
        ax.set_ylabel('Intensity [a.u]')
        
        plots_manager = plt.get_current_fig_manager()
        screen_geometry = QDesktopWidget().screenGeometry()
        plots_manager.window.setGeometry(50,80,floor(screen_geometry.width()/2 -50), floor(screen_geometry.height()-200))
        #fig.tight_layout()
        
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
