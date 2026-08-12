#RIXS Script
import sys
from PyQt5.QtWidgets import QApplication
import simple_RIXS_main_logic

if __name__ == '__main__':
    app = QApplication(sys.argv)

    #input_file_location has to be changed when new project folder is chosen.
    #It is recomended to save the "Simple_RIXS" script under a different name for each project. Example: "Simple_RIXS_ALS_2022_RIXS"
    #Example of folder path: input_file_project_folder= "C:\\Users\\ponto479\\Documents\\02 Beamtime Data\\ALS 11-2022\\RIXS"
    input_file_project_folder= "C:\\Users\\ponto479\\Documents\\02 Beamtime Data\\2024_02_Species"
    simple_RIXS_main_logic.main_logic(input_file_project_folder)

    sys.exit(0)

    