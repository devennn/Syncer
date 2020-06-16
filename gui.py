import os
import json
import logging
import PySimpleGUI as sg 

from rclone import RClone
from utils import load_previous_process, record_process

logging.basicConfig(level=logging.DEBUG)

sg.ChangeLookAndFeel('BlueMono')  

def setup_window(drive_list):
    
    row1_tab1 = [
        sg.Frame("Drives", layout=[[sg.Listbox(values=drive_list, size=(15, 7), key='-DRIVE-', enable_events=True)], 
                    [sg.Button("Sync", key='-SYNC-'), sg.Button("Copy", key='-COPY-')]]), 
        sg.Frame("Directory", layout=[[sg.Listbox(values=[], size=(42, 7) ,  key='-DIRS-', enable_events=True)], 
                    [sg.Button("Back", key='-BACK-'), sg.Button("Choose File", key='-CHOOSE-'), 
                    sg.Button("Choose Folder", key='-CHOOSEFOLDER-')]])
    ]
    row1_tab2 = [
        sg.Frame("Drives", layout=[[sg.Listbox(values=drive_list, size=(15, 7) ,  key='-PREVDRIVE-', enable_events=True)], 
                    [sg.Button("Sync", key='-SYNCPREV-'), sg.Button("Copy", key='-COPYPREV-')]]), 
        sg.Frame("Previous Process", layout=[[sg.Listbox(values=[], size=(42, 7) ,  key='-PREVDIRS-', enable_events=True)], 
                    [sg.Button("Show", key='-GETPREV-'), sg.Button("Choose Process", key='-CHOOSEPREV-')]])
    ]
    row1_tabGroup = [sg.TabGroup([[sg.Tab("New", [row1_tab1]), sg.Tab("Previous", [row1_tab2])]])]
    row2 = [sg.Text("Chosen: ", size=(10, 1)), sg.Text(size=(29, 1), key='-DISP-', background_color='#ffffff'), 
            sg.Button("Source", key='-SETSRC-'), sg.Button("Destination", key='-SETDES-')]
    row3 = [sg.Text("Source:", size=(10, 1)), sg.Text(size=(55, 1), key='-SRC-', background_color='#ffffff')]
    row4 = [sg.Text("Destination:", size=(10, 1)), sg.Text(size=(55, 1), key='-DES-', background_color='#ffffff')]
    row5 = [sg.Text("Status:", size=(10, 1)), sg.Text(size=(55, 1), key='-VIEWPROCESS-', text_color='#ffffff', background_color='#000000')]

    return [row1_tabGroup , row2, row3, row4, row5] 


def print_process(window, message):
    window['-VIEWPROCESS-'].update(message)
    window.Refresh()


def main():
    rc = RClone()
    drive_list = rc.run_rclone("listremotes")
    layout = setup_window(drive_list)
    window = sg.Window("Syncer", layout)
    rc.window = window
    backFlag = False
    startFlag = True
    chosenPath = ''

    while True:
        event, values = window.read()
        logging.debug("main: Event: {}".format(event))
        temp = []
        srcValFlag = True
        
        if event is not None:
            if event == '-DRIVE-': # Start 
                rc.pathBuild = ""
                stdout = rc.run_rclone("lsf", [values['-DRIVE-']])
                window['-DIRS-'].update(stdout)
            
            if event == '-DIRS-': # List directory contents
                if len(values['-DIRS-']) == 0: # Skip rclone if empty
                    continue
                stdout = rc.run_rclone("lsf", [values['-DIRS-']])
                window['-DIRS-'].update(stdout)

            if event == '-BACK-': # Back button
                tempPathBuild = rc.pathBuild.rsplit(os.sep)
                rc.pathBuild = tempPathBuild[0]
                stdout = rc.run_rclone("lsf", backFlag=True)
                window['-DIRS-'].update(stdout)  

            if event == '-CHOOSE-': # Choose File button
                if len(rc.pathBuild) == 0:
                    continue
                if rc.pathBuild[-1] is ':':
                    chosenPath = rc.pathBuild + values['-DIRS-'][0] 
                else:          
                    chosenPath = os.path.join(rc.pathBuild, values['-DIRS-'][0])
                logging.debug("main: Chosen File: {}".format(chosenPath))
                window['-DISP-'].update(chosenPath)

            if event == '-CHOOSEFOLDER-': # Choose Folder button
                chosenPath = rc.pathBuild
                logging.debug("main: Chosen Folder: {}".format(chosenPath))
                window['-DISP-'].update(chosenPath)
            
            if event == '-SETSRC-': # Set Source button
                window['-SRC-'].update(chosenPath)
                rc.srcPath = chosenPath

            if event == '-SETDES-': # Set destination button
                if len(chosenPath) == 0:
                    continue
                if chosenPath[-1] != '/' and chosenPath[-1] != ':':
                    print_process(window, "Destination cannot be a File")
                    continue
                window['-DES-'].update(chosenPath)
                rc.desPath = chosenPath

            if event == '-COPY-' or event == '-COPYPREV-': # Copy button
                if rc.srcPath == '' or rc.desPath == '':
                    continue
                if event == '-COPY-':
                    record_process(rc.srcPath, rc.desPath)
                print_process(window, "Start Copy...")
                rc.run_rclone("copy", [rc.srcPath])
                print_process(window, "Done Copy...")
            
            if event == '-SYNC-' or event == '-SYNCPREV-': # Sync button  
                if rc.srcPath == '' or rc.desPath == '':
                    continue             
                print_process(window, "Start Sync...")
                rc.run_rclone("sync")
                print_process(window, "Done Sync...")

            if event == '-GETPREV-':
                fname = "prevprocess.json"
                if os.path.exists(fname) is False:
                    print_process(window, "No previous process...")
                else:
                    hist_list = load_previous_process(fname, drive_list)
                    print_process(window, "Choose Drive to Show...")
            
            if event == '-CHOOSEPREV-':
                logging.debug("main: PREVDIRS: {}".format(values['-PREVDIRS-']))
                if len(values['-PREVDIRS-']) == 0:
                    continue
                srcPath, _, desPath = values['-PREVDIRS-'][0].split()
                window['-SRC-'].update(srcPath)
                rc.srcPath = srcPath
                window['-DES-'].update(desPath)
                rc.desPath = desPath
            
            if event == '-PREVDRIVE-':
                fname = "prevprocess.json"
                hist_list = load_previous_process(fname, driveName=values['-PREVDRIVE-'][0])
                window['-PREVDIRS-'].update(hist_list)

        else:
            logging.debug("main: Exit Program...")
            break

if __name__ == "__main__":
    main()