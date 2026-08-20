#input_veritas_file_information_script
import sys
import os
from PyQt5.QtCore import QEventLoop
from PyQt5.QtCore import pyqtSignal
import platform
import subprocess
from PyQt5.QtWidgets import QLabel, QMainWindow, QCheckBox, QComboBox, QLineEdit, QPushButton, QLayout, QApplication, QVBoxLayout, QHBoxLayout, QWidget, QDesktopWidget, QLabel, QTextEdit, QMessageBox
#from PyQt5.QtGui import QPixmap
#from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
#from matplotlib.figure import Figure
from math import floor
import matplotlib.pyplot as plt
#import h5py
#import numpy as np
import subprocess
import parameter_scripts
import iteratable_number_to_int_script
import create_complete_file_location_view_roots_or_txt_script





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
        #self.setMinimumWidth(self.width())
        #self.adjustSize()
        self.move(floor(screen_geometry.width()/2 +10), 10)

        #self.open_folder(parameters["input_file_location"])
        self.is_multitiple_detectors_input_displayed= False 

        self.is_first_time_creating_ignore_file_number_array= True
        
        #Maybe have to do this: self.parameters["input_file_number_of_files_to_ignore"]="0"

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

        if self.parameters["plot_type"]== "Make treated RIXS data from Max IV Veritas" or self.parameters["plot_type"]== "Make treated RIXS data from Max IV Species":        
            self.vbox.addLayout(self.create_gui_item("is_input_file_names_manually", "Would you like to manually input the file names and numbers individually? \nThis is nessesary if your RIXS map is plit up over two different files. ", "q_check_box", [""]))

            self.vbox.addLayout(self.create_gui_item("input_complete_file_name_array_0", "Input complete file name of the RIXS data file: \n(You can drop the file into the text box)", "q_line_edit", [""]))
            self.vbox.addLayout(self.create_gui_item("input_file_iteratable_file_number_start", "First iteratable file number: ", "q_line_edit", [""]))
            self.vbox.addLayout(self.create_gui_item("input_file_iteratable_file_number_end", "Last iteratable file number: ", "q_line_edit", [""]))
            self.vbox.addLayout(self.create_gui_item("input_file_number_of_files_to_ignore", "How many files you want to ignore: ", "q_line_edit", [""]))
            self.vbox.addLayout(self.create_gui_item("degree_of_energy_per_channel_polynomial", "What degree polynomial do you want to calibrate the x-axis to? (1 for linear) ", "q_line_edit", [""]))


        elif self.parameters["plot_type"][:3]=="XAS":
            self.vbox.addLayout(self.create_gui_item("input_complete_file_name", "Input complete file name of the raw data: \n(You can drop the file into the text box)", "q_line_edit", [""]))

        self.vbox.addLayout(self.create_gui_item("complete_i0_file_name", "Input file name for the I0 file (where XAS data is stored): ", "q_line_edit", [""]))
        self.vbox.addLayout(self.create_gui_item("input_file_iteratable_file_number_start_2", "Entry where to find the first I0 (only the numbers): ", "q_line_edit", [""]))
        self.vbox.addLayout(self.create_gui_item("input_file_iteratable_file_number_end_2", "Entry where to find the last I0 (only the numbers): ", "q_line_edit", [""]))
            
        self.vbox.addLayout(self.create_gui_item("is_normalization_to_i0", "Do you want to normalize the data to i0? ", "q_check_box", [""]))

        self.vbox.addLayout(self.create_gui_item("", "The following inputs does not effect the calculation, it affects the saved file name", "q_text_label", [""]))
        self.vbox.addLayout(self.create_gui_item("output_file_element", "Element that is being studied: ", "q_line_edit", [""]))
        self.vbox.addLayout(self.create_gui_item("output_file_edge", "Edge that is being studied: ", "q_combo_box", ["K-edge", "L-edge", "L1-edge", "L2-edge", "L3-edge", "M-edge", "M1-edge", "M5-edge"]))
        self.vbox.addLayout(self.create_gui_item("output_file_sample_name", "Sample name: ", "q_line_edit", [""]))
        self.vbox.addLayout(self.create_gui_item("output_file_additional_comment", "Addional comment that will be saved with the file name: ", "q_line_edit", [""]))
        #else:
        #    print("This file format is not supported yet, sorry about that.")        
        self.vbox.addLayout(self.create_bottom_buttons())

        self.is_first_time_creating_ignore_file_number_array= False

        self.central_widget = QWidget()
        self.central_widget.setLayout(self.vbox)
        self.setCentralWidget(self.central_widget)
        self.setWindowTitle("Simple RIXS Input Veritas data information")
        self.show()


    def create_gui_item(self, key, item_label_text, item_type, combo_box_options):
        hbox = QHBoxLayout()
        item_label = QLabel(item_label_text)
        if item_type =="q_line_edit":
            hbox.addWidget(item_label)
            #hbox.addWidget(item)
            if "array" in key:
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
            elif key== "input_file_iteratable_file_number_start" or key== "input_file_iteratable_file_number_end" or key == "input_file_number_of_detectors" :
                item = QLineEdit(self.parameters[key])
                hbox.addWidget(item)
                item.editingFinished.connect(lambda item=item, key=key: self.validate_input(item, key))
            elif key== "input_file_number_of_files_to_ignore":
                item = QLineEdit(self.parameters[key])
                hbox.addWidget(item)
                item.editingFinished.connect(lambda: self.create_array_gui_item(item, item.text(), key, hbox, "input_file_ignore_file_number_array", "Input iteratable file numbers that should be ignored: \n (15 max) "))
                    #item.editingFinished.connect(lambda: self.vbox.insertLayout(self.vbox.indexOf(hbox)+1,self.create_gui_item("input_file_ignore_file_number_array", "Input iteratable file numbers that should be ignored: ", "q_array_inputs", [""])))
            elif key== "input_file_text_end_of_name":
                self.parameters, complete_file_location = create_complete_file_location_view_roots_or_txt_script.create_complete_file_location_view_roots_or_txt(self.parameters, True, self.parameters["input_file_iteratable_file_number_start"])      
                item = QLineEdit(self.parameters[key])
                hbox.addWidget(item)
                item.editingFinished.connect(lambda item=item, key=key, hbox=hbox: self.update_end_of_file_name(item, key, hbox))
            elif key== "input_complete_file_name":
                self.parameters, complete_file_location = create_complete_file_location_view_roots_or_txt_script.create_complete_file_location_view_roots_or_txt(self.parameters, False, "")
                item = DropLineEdit(self.parameters[key])
                hbox.addWidget(item)
                item.editingFinished.connect(lambda item=item, key=key, hbox=hbox: self.update_end_of_file_name(item, key, hbox))
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
            item.setChecked(self.parameters[key])
            hbox.addWidget(item)
            if key == "is_multiple_detectors":
                item.clicked.connect(lambda: self.create_mutliple_detector_gui_items(item, key, hbox))          
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
        elif item_type=="q_text_label":
            hbox.addWidget(item_label)
        elif item_type== "q_array_inputs":
            hbox.addWidget(item_label)
            item_list=[]
            if key== "input_file_ignore_file_number_array":
                for input_square in range(int(self.parameters["input_file_number_of_files_to_ignore"])):
                    item = QLineEdit(self.parameters[key][input_square])
                    item.textChanged.connect(lambda text, index=input_square: self.update_dictionary_array(key, index, text))
                    item_list.append(item)
                    hbox.addWidget(item_list[input_square])
                    #item_list[input_square].textChanged.connect(lambda: self.update_dictionary_array(key, input_square, item_list[input_square].text()))
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
    
    def update_dictionary_array(self, key, array_index, item):
        self.parameters[key][array_index] = item.text()

    def update_end_of_file_name(self, item, key, hbox):
        if item.text() != self.parameters[key]:
            self.update_dictionary(key, item.text())
            self.remove_item(self.vbox.indexOf(hbox))
            if key== "input_file_text_end_of_name":
                self.vbox.insertLayout(self.vbox.indexOf(hbox),self.create_gui_item("input_file_text_end_of_name", "Text at the end of the file: ", "q_line_edit", [""]))
            elif  key== "input_complete_file_name":
                self.vbox.insertLayout(self.vbox.indexOf(hbox),self.create_gui_item("input_complete_file_name", "Input complete file name of the raw data: \n(You can drop the file into the text box)", "q_line_edit", [""]))

        
    def validate_input(self, item, key):
        if item.text() != self.parameters[key]:
            if key != "input_file_number_of_files_to_ignore":
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

    def create_array_gui_item(self, item, item_text, key, hbox, array_key, array_label_text):
        if self.validate_input(item, key):
            if key == "input_file_number_of_files_to_ignore":
                    if self.is_first_time_creating_ignore_file_number_array== False:
                        if self.parameters[key]!= "":
                            old_number_of_file_names= int(self.parameters[key])
                        else:
                            old_number_of_file_names=0
                        self.update_dictionary(key, item_text)
                        if old_number_of_file_names>0:
                            for file_name_index in range(old_number_of_file_names):
                                self.remove_item(self.vbox.indexOf(hbox)+file_name_index+1)
                    if int(item_text) != 0:
                        for file_name_index in range(int(item_text)):
                            self.vbox.insertLayout(self.vbox.indexOf(hbox)+file_name_index+1, self.create_gui_item("input_file_ignore_file_number_array_" + str(file_name_index), "Input file number you want to ignore " + str(file_name_index) + ": ", "q_line_edit", [""]))

    def create_mutliple_detector_gui_items(self, item, key, hbox):
        self.update_dictionary_checkbox(key, item)
        if self.is_multitiple_detectors_input_displayed== False and self.parameters["is_multiple_detectors"]:
            self.vbox.insertLayout(self.vbox.indexOf(hbox)+1,self.create_gui_item("input_file_text_before_detector", "Text between iteratable file number and detector number: ", "q_line_edit", [""]))
            self.vbox.insertLayout(self.vbox.indexOf(hbox)+2,self.create_gui_item("input_file_number_of_detectors", "Input number of detectors: ", "q_line_edit", [""]))
            self.is_multitiple_detectors_input_displayed =True
        elif self.is_multitiple_detectors_input_displayed == True and self.parameters["is_multiple_detectors"] == False:
            self.remove_item(self.vbox.indexOf(hbox)+1)
            self.remove_item(self.vbox.indexOf(hbox)+2)
            self.is_multitiple_detectors_input_displayed =False


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