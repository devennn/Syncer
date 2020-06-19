import os
from pathlib import Path
import logging

prevProcessfname = os.path.join(str(Path.home()), "syncercache.json")

try:
    from utils import load_previous_process, record_process, print_process
except Exception:
    from .utils import load_previous_process, record_process, print_process

class GUI_Process:
    def __init__(self, window, rc):
        self.window = window
        self.rc = rc
        self.chosenPath = ""
        self.backFlag = False
        self.drive_list = []

    def startup(self, password):
        '''
        Startup process. If password is true other tabs are enabled

            Parameters:
                password (str): password for RClone
            Returns:
                None
        '''
        self.rc.startProcess = True
        if len(password) != 0:
            logging.debug("main: Password entered")
            self.rc.password = str(password) + '\n'
        else:
            logging.debug("main: No password")
            self.rc.password = ""
        self.drive_list = self.rc.run_rclone("listremotes")
        if len(self.drive_list) != 0:
            self.window['-NEWTAB-'].update(disabled=False)
            self.window['-PREVTAB-'].update(disabled=False)
            self.window['-SETSRC-'].update(disabled=False)
            self.window['-SETDES-'].update(disabled=False)
            self.window['-DRIVE-'].update(self.drive_list)
            self.window['-PREVDRIVE-'].update(self.drive_list)
            self.rc.startProcess = False
            self.window['-STARTTAB-'].update(disabled=True)
        else:
            self.window['-STARTMES-'].update("Wrong Password...")
    
    def list_drive(self, drives):
        '''
        List all drives registered

            Parameters:
                drives (list): List of drives

            Returns:
                None
        '''
        self.rc.pathBuild = ""
        stdout = self.rc.run_rclone("lsf", [drives])
        self.window['-DIRS-'].update(stdout)

    def list_dirs(self, dirs):
        '''
        List all directory in a drive or folder

            Parameters:
                dirs (list): list of dir

            Returns:
                None
        '''
        if len(dirs) == 0: # Skip rclone if empty
            return
        stdout = self.rc.run_rclone("lsf", [dirs])
        self.window['-DIRS-'].update(stdout)

    def back_button(self):
        '''
        Process for back button. List all contentc from 1 level before and update view
        '''
        tempPathBuild = self.rc.pathBuild.rsplit(os.sep)
        self.rc.pathBuild = tempPathBuild[0]
        stdout = self.rc.run_rclone("lsf", backFlag=True)
        self.window['-DIRS-'].update(stdout) 

    def choose_file(self, dir):
        '''
        Process for choose file button

            Parameters:
                dir (str): file chosen
            
            Returns:
                None
        '''
        if len(self.rc.pathBuild) == 0:
            return

        if self.rc.pathBuild[-1] is ':': # For file in root directory
            self.chosenPath = self.rc.pathBuild + dir
        else:          
            self.chosenPath = os.path.join(self.rc.pathBuild, dir)

        logging.debug("main: Chosen File: {}".format(self.chosenPath))
        self.window['-DISP-'].update(self.chosenPath)

    def choose_folder(self):
        '''
        Process for choosing folder button
        '''
        self.chosenPath = self.rc.pathBuild
        logging.debug("main: Chosen Folder: {}".format(self.chosenPath))
        self.window['-DISP-'].update(self.chosenPath)      

    def set_source(self):
        '''
        Process for setting source path
        '''   
        self.window['-SRC-'].update(self.chosenPath)
        self.rc.srcPath = self.chosenPath        

    def set_destination(self):
        '''
        Process for setting destination folder
        '''
        if len(self.chosenPath) == 0: # Return if not path chosen
            return

        # Return if chosenPath is a file
        if self.chosenPath[-1] != '/' and self.chosenPath[-1] != ':': 
            print_process(self.window, "Destination cannot be a File")
            return

        self.window['-DES-'].update(self.chosenPath)
        self.rc.desPath = self.chosenPath # Store value

    def copy_process(self):
        '''
        Process for copy button
        '''
        if self.rc.srcPath == '' or self.rc.desPath == '':
            return
        record_process(self.rc.srcPath, self.rc.desPath, prevProcessfname)
        self.rc.run_rclone("copy", [self.rc.srcPath])

    def sync_process(self):
        '''
        Process for Sync button
        '''
        if self.rc.srcPath == '' or self.rc.desPath == '': # Check for invalid path
            return      
        record_process(self.rc.srcPath, self.rc.desPath, prevProcessfname)       
        self.rc.run_rclone("sync")
    
    def move_process(self):
        '''
        Process for Move process
        '''
        if self.rc.srcPath == '' or self.rc.desPath == '': # Check for invalid path
            return      
        record_process(self.rc.srcPath, self.rc.desPath, prevProcessfname)       
        self.rc.run_rclone("move")

    def choose_previous(self, drive):
        '''
        Process for choosing previous process button

            Parameters:
                drive (list): list of chosen process
            
            Returns:
                None
        '''
        logging.debug("main: PREVDIRS: {}".format(drive))
        if len(drive) == 0: # Check invalid input
            return
        srcPath, _, desPath = drive[0].split() # Split to remove '->'

        # Update window
        self.window['-SRC-'].update(srcPath)
        self.rc.srcPath = srcPath
        self.window['-DES-'].update(desPath)
        self.rc.desPath = desPath

    def drive_previous(self, drive):
        '''
        List previous process when a drive is clicked in Previous tab

            Parameters:
                drive (list): List of drive chosen
        '''
        if os.path.exists(prevProcessfname) is False: # Check if there is previous process
            print_process(self.window, "No previous process...")
            return
        hist_list = load_previous_process(prevProcessfname, driveName=drive[0])
        self.window['-PREVDIRS-'].update(hist_list)   
