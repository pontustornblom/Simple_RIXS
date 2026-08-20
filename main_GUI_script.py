#main_GUI_script
import sys
import os
import platform
import subprocess
from PyQt5.QtWidgets import QLabel, QMainWindow, QCheckBox, QComboBox, QLineEdit, QPushButton, QLayout, QApplication, QVBoxLayout, QHBoxLayout, QWidget, QDesktopWidget, QLabel, QMessageBox
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QEventLoop
from PyQt5.QtCore import pyqtSignal
from math import floor
import parameter_scripts
import iteratable_number_to_float_script



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
        #self.setMinimumWidth(self.width())
        self.adjustSize()
        self.move(floor(screen_geometry.width()/2 +10), 10)

        #self.open_folder(parameters["input_file_location"])
        self.is_complete_file_name_item_added =False

        self.vbox = QVBoxLayout()

        # Simple_RIXS_logo_layout = QHBoxLayout()
        # Simple_RIXS_logo_layout.addStretch(1)
        # Simple_RIXS_logo_label =QLabel()
        # logo_folder = 'Simple_RIXS_logo'
        # logo_file = 'Simple_RIXS_logo_final.png'
        # logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), logo_folder, logo_file)
        # Simple_RIXS_logo = QPixmap(logo_path)        
        # Simple_RIXS_logo_label.setPixmap(Simple_RIXS_logo)
        # Simple_RIXS_logo_layout.addWidget(Simple_RIXS_logo_label)
        # Simple_RIXS_logo_layout.addStretch(1)
        # self.vbox.addLayout(Simple_RIXS_logo_layout)
        #vbox.setSpacing(10)
        #vbox.setSizeConstraint(QLayout.SetFixedSize)

        self.vbox.addLayout(self.create_gui_item("input_file_project_folder", "Folder of the current project: ", "q_line_edit", [""]))
        self.vbox.addLayout(self.create_gui_item("input_file_raw_data_folder", "Subfolder where the raw data is stored: ", "q_line_edit", [""]))
        self.vbox.addLayout(self.create_gui_item("plot_type", "What would you like to do? ", "q_combo_box", [ "Replot treated spectra", "Make treated RIXS data", "Make treated RIXS data from Max IV Veritas", "Treat Veritas raw data using time information", "Make treated RIXS data from Max IV Species", "Make treated RIXS data from SPring-8 BL27SU", "Make treated RIXS data from NanoTerasu BL02U", "Make treated RIXS data from treated RIXS data", "Make treated RIXS data from Soleil Galaxies", "XAS", "Make treated XAS data from Max IV Veritas", "Make treated XAS data from Max IV Species", "Plot treated spectra", "Apply emission energy scale to RIXS map", "Make PFY from several treated RIXS files", "Add several RIXS spectra from different files to waterfall plot", "Integrate and add several RIXS spectra from different files to waterfall plot", "Add plots to waterfall plot", "Add multiple XAS to waterfall plot", "Add intensities from RIXS maps", "Add multiple treated intensity lines", "Combine raw spectral lines", "Convert heat map to waterfall", "Subtract treated line scans", "Subtract RIXS maps", "Integrate multiple RIXS maps to values", "Integrate multiple XAS to values"]))
        self.vbox.addLayout(self.create_gui_item("open file location", "Open raw data file location", "q_push_button",  [""]))
        self.vbox.addLayout(self.create_gui_item("input_file_format", "What is the format of the files that you want to use as input?", "q_combo_box", ["Previously treated data", "txt", "h5", "csv", "dat", "bin"]))
        self.vbox.addLayout(self.create_gui_item("is_view_roots_or_input_txt", "Do you want to display the h5 root structure or the txt file? \n (Will be set to False next time the program runs) ", "q_check_box",  [""]))

        #Save and close buttons
        self.vbox.addLayout(self.create_bottom_buttons())

        central_widget = QWidget()
        central_widget.setLayout(self.vbox)
        self.setCentralWidget(central_widget)
        self.setWindowTitle("Simple RIXS")
        self.show()

        #self.second_window = SecondWindow()

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
                #complete_treated_file_location= create_complete_file_location_for_treated_data.create_complete_file_location_for_treated_data(self.parameters["input_file_project_folder"], self.parameters["input_complete_file_name_array"][array_index])
                #complete_file_location= complete_file_location[:-8] + "parameters.txt"
                #self.treated_parameters = parameter_scripts.get_treated_parameters(complete_file_location)
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
                item.editingFinished.connect(lambda item=item: self.update_dictionary_array(array_key, array_index, item))
            else:
                item = DropLineEdit(self.parameters[key]) if key == "input_complete_file_name" else QLineEdit(self.parameters[key])
                item.textChanged.connect(lambda: self.update_dictionary(key, item.text()))
            hbox.addWidget(item)
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
        else:
            print("Error: Item was not added to the GUI")
        return hbox

    def update_dictionary(self, key, updated_value):
        self.parameters[key] = updated_value

    def update_dictionary_checkbox(self, key, item):
        if item.isChecked():
            self.parameters[key] = True
            if key== "is_view_roots_or_input_txt":
                if not self.is_complete_file_name_item_added:
                    self.vbox.insertLayout(self.vbox.count()-1,self.create_gui_item("input_complete_file_name_array_0", "Input example file name to view roots/txt \n(You can drop the file into the text box)", "q_line_edit", [""]))                
                    self.is_complete_file_name_item_added =True
        else:
            self.parameters[key] = False


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
        #self.second_window.close()
        self.finished.emit()
        self.close()

    def save_and_close(self):
        parameter_scripts.save_parameters(self.parameters)
        self.parameters["is_program_running"]=False
        self.finished.emit()
        #self.second_window.close()
        self.close()

    def close_program(self): 
        self.parameters["is_program_running"]=False
        #self.second_window.close()
        self.finished.emit()
        self.close()

    def get_inputted_parameters_from_gui(self):
        return self.parameters

    def open_folder(self, project_folder, raw_data_folder):
        folder_path = os.path.join(project_folder, raw_data_folder)
        if platform.system() == "Darwin":
            subprocess.call(["open", folder_path])
        else:
            subprocess.call(["explorer", folder_path])

    def update_end_of_file_name(self, item, key, hbox):
        if item.text() != self.parameters[key]:
            self.update_dictionary(key, item.text())
            self.remove_item(self.vbox.indexOf(hbox))
            if  key== "input_complete_file_name":
                self.vbox.insertLayout(self.vbox.indexOf(hbox),self.create_gui_item("input_complete_file_name", "Input complete file name of the raw data: \n(You can drop the file into the text box)", "q_line_edit", [""]))

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


class SecondWindow(QWidget):
    def __init__(self):
        super().__init__()
        #screen_geometry = QDesktopWidget().screenGeometry()
        #self.setFixedSize(floor(screen_geometry.width()/2 -5), screen_geometry.height()-160)
        self.adjustSize()
        self.move(10,10)

        layout = QVBoxLayout()
        self.label = QLabel("Second Window")
        Simple_RIXS_logo = QPixmap(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Simple_RIXS_logo', 'Simple_RIXS_logo_final.png'))
        self.label.setPixmap(Simple_RIXS_logo)
        layout.addWidget(self.label)
        self.setLayout(layout)
        self.show()

if __name__ == '__main__':
    input_file_location= "C:\\Users\\ponto479\\Documents\\02 Beamtime Data\\SLS Adress 03-2022\\RIXS"
    parameters= parameter_scripts.get_parameters(input_file_location)
    #parameters={"input_file_location": "C:\\Users\\ponto479\\Documents\\02 Beamtime Data\\SLS Adress 03-2022\\RIXS",
                #"is_program_running":True, "input_file_iteratable_file_number_start":"0100", "input_file_iteratable_file_number_end": "0120" }
    parameters = run_main_gui(parameters)
    #print(parameters)