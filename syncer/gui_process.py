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
        self.rc.pathBuild = ""
        stdout = self.rc.run_rclone("lsf", [drives])
        self.window['-DIRS-'].update(stdout)

    def list_dirs(self, dirs):
        if len(dirs) == 0: # Skip rclone if empty
            return
        stdout = self.rc.run_rclone("lsf", [dirs])
        self.window['-DIRS-'].update(stdout)

    def back_button(self):
        tempPathBuild = self.rc.pathBuild.rsplit(os.sep)
        self.rc.pathBuild = tempPathBuild[0]
        stdout = self.rc.run_rclone("lsf", backFlag=True)
        self.window['-DIRS-'].update(stdout) 

    def choose_file(self, dir):
        if len(self.rc.pathBuild) == 0:
            return
        if self.rc.pathBuild[-1] is ':':
            self.chosenPath = self.rc.pathBuild + dir
        else:          
            self.chosenPath = os.path.join(self.rc.pathBuild, dir)
        logging.debug("main: Chosen File: {}".format(self.chosenPath))
        self.window['-DISP-'].update(self.chosenPath)

    def choose_folder(self):
        self.chosenPath = self.rc.pathBuild
        logging.debug("main: Chosen Folder: {}".format(self.chosenPath))
        self.window['-DISP-'].update(self.chosenPath)      

    def set_source(self):   
        self.window['-SRC-'].update(self.chosenPath)
        self.rc.srcPath = self.chosenPath        

    def set_destination(self):
        if len(self.chosenPath) == 0:
            return
        if self.chosenPath[-1] != '/' and self.chosenPath[-1] != ':':
            print_process(self.window, "Destination cannot be a File")
            return
        self.window['-DES-'].update(self.chosenPath)
        self.rc.desPath = self.chosenPath

    def copy_process(self, event):
        if self.rc.srcPath == '' or self.rc.desPath == '':
            return
        if event == '-COPY-':
            record_process(self.rc.srcPath, self.rc.desPath, prevProcessfname)
        self.rc.run_rclone("copy", [self.rc.srcPath])

    def sync_process(self, event):
        if self.rc.srcPath == '' or self.rc.desPath == '':
            return      
        if event == '-SYNC-':
            record_process(self.rc.srcPath, self.rc.desPath, prevProcessfname)       
        self.rc.run_rclone("sync")

    def choose_previous(self, drive):
        logging.debug("main: PREVDIRS: {}".format(drive))
        if len(drive) == 0:
            return
        srcPath, _, desPath = drive[0].split()
        self.window['-SRC-'].update(srcPath)
        self.rc.srcPath = srcPath
        self.window['-DES-'].update(desPath)
        self.rc.desPath = desPath

    def drive_previous(self, drive):
        if os.path.exists(prevProcessfname) is False:
            print_process(self.window, "No previous process...")
            return
        hist_list = load_previous_process(prevProcessfname, driveName=drive[0])
        self.window['-PREVDIRS-'].update(hist_list)                       