import os
import logging
import PySimpleGUI as sg 

from rclone import RClone

logging.basicConfig(level=logging.DEBUG)

sg.ChangeLookAndFeel('BlueMono')      

def setup_window(rc):

    drive_list = rc.run_rclone("listremotes")
    
    row1 = [
        sg.Frame("Drives", layout=[[sg.Listbox(values=drive_list, size=(15, 7) ,  key='-DRIVE-', enable_events=True)], 
                    [sg.Button("Sync", key='-SYNC-'), sg.Button("Copy", key='-Copy-')]]), 
        sg.Frame("Directory", layout=[[sg.Listbox(values=[], size=(42, 7) ,  key='-DIRS-', enable_events=True)], 
                    [sg.Button("Back", key='-BACK-'), sg.Button("Choose File", key='-CHOOSE-'), 
                    sg.Button("Choose Folder", key='-CHOOSEFOLDER-')]])
    ]
    row2 = [sg.Text("Chosen: ", size=(10, 1)), sg.Text(size=(29, 1), key='-DISP-', background_color='#ffffff'), 
            sg.Button("Source", key='-SETSRC-'), sg.Button("Destination", key='-SETDES-')]
    row3 = [sg.Text("Source:", size=(10, 1)), sg.Text(size=(55, 1), key='-SRC-', background_color='#ffffff')]
    row4 = [sg.Text("Destination:", size=(10, 1)), sg.Text(size=(55, 1), key='-DES-', background_color='#ffffff')]
    row5 = [sg.Text(size=(65, 1), key='-VIEWPROCESS-')]

    return [row1, row2, row3, row4, row5] 


def main():
    rc = RClone()
    layout = setup_window(rc)
    window = sg.Window("Syncer", layout)
    backFlag = False
    startFlag = True

    while True:
        event, values = window.read()
        logging.debug("Event: {}".format(event))
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
                logging.debug("Back: {}".format(rc.pathBuild))
                stdout = rc.run_rclone("lsf", backFlag=True)
                window['-DIRS-'].update(stdout)  

            if event == '-CHOOSE-': # Choose File button
                if rc.pathBuild[len(rc.pathBuild) - 1] is ':':
                    chosenPath = rc.pathBuild + values['-DIRS-'][0] 
                else:          
                    chosenPath = os.path.join(rc.pathBuild, values['-DIRS-'][0])
                logging.debug("Chosen File: {}".format(chosenPath))
                window['-DISP-'].update(chosenPath)

            if event == '-CHOOSEFOLDER-': # Choose Folder button
                chosenPath = rc.pathBuild
                logging.debug("Chosen Folder: {}".format(chosenPath))
                window['-DISP-'].update(chosenPath)
            
            if event == '-SETSRC-': # Set Source button
                window['-SRC-'].update(chosenPath)
                rc.srcPath = chosenPath

            if event == '-SETDES-': # Set destination button
                if chosenPath[len(chosenPath) - 1] != '/':
                    window['-VIEWPROCESS-'].update("Destination cannot be a File")
                    continue
                window['-DES-'].update(chosenPath)
                rc.desPath = chosenPath

            if event == '-Copy-': # Copy button
                rc.run_rclone("copy", [rc.srcPath])
                window['-VIEWPROCESS-'].update("Done Copy...")
            
            if event == '-SYNC-': # Sync button               
                rc.run_rclone("sync")
                window['-VIEWPROCESS-'].update("Done Sync...") 

        else:
            logging.debug("Exit Program...")
            break

if __name__ == "__main__":
    main()