import os
import json
import time
import logging
import PySimpleGUI as sg 

try:
    from rclone import RClone
    from gui_process import GUI_Process
except Exception:
    from .rclone import RClone
    from .gui_process import GUI_Process

logging.basicConfig(level=logging.DEBUG)

sg.ChangeLookAndFeel('BlueMono')  

def setup_window():
    '''
    Return PySimpleGUI layout

        Parameter:
            None
        Return:
            PySimpleGUI list of layouts
    '''
    drive_list = []                             # Drive list empty at start
    process_list = ["", "Copy", "Sync", "Move"] # List of process for combo box
    drive_viewer_size = (15, 7)                 # Drive viewer window size
    dirs_viewer_size = (40, 7)                  # Directory viewer window size
    t2BtnSize = (5, 1)                          # tab 2 button size

    # Color
    whte = '#ffffff'
    blck = '#000000'

    # Tabs layout
    row1_tab1 = [
        [sg.Text("Enter password to start. Leave empty if not available")],     
        [sg.InputText(size=(40, 1), password_char='*', key='-PW-')], 
        [sg.Button("Start", key='-START-')],
        [sg.Text(size=(55, 1), key='-STARTMES-')]
    ]
    row1_tab2 = [[
        sg.Frame("Drives", layout=[
            [sg.Listbox(values=drive_list, size=drive_viewer_size, key='-DRIVE-', enable_events=True)], 
            [sg.Combo(process_list, size=(7, len(process_list)), key='-PROC-'), sg.Button("Run", key='-RUN-')]
        ]), 
        sg.Frame("Directory", layout=[
            [sg.Listbox(values=[], size=dirs_viewer_size,  key='-DIRS-', enable_events=True)], 
            [sg.Button("Back", key='-BACK-', size=t2BtnSize), sg.Button("File", key='-CHOOSE-', size=t2BtnSize), sg.Button("Folder", key='-CHOOSEFOLDER-', size=t2BtnSize)]
        ])
    ]]
    row1_tab3 = [[
        sg.Frame("Drives", layout=[
            [sg.Listbox(values=drive_list, size=drive_viewer_size,  key='-PREVDRIVE-', enable_events=True)], 
            [sg.Combo(process_list, size=(7, len(process_list)), key='-PROCPREV-'), sg.Button("Run", key='-RUNPREV-')]
        ]), 
        sg.Frame("Choose Drive to View", layout=[
            [sg.Listbox(values=[], size=dirs_viewer_size,  key='-PREVDIRS-', enable_events=True)], 
            [sg.Button("Choose Process", key='-CHOOSEPREV-')]
        ])
    ]]
    row1_tabGroup = [sg.TabGroup([
        [sg.Tab("Start", row1_tab1, key='-STARTTAB-'), 
        sg.Tab("New", row1_tab2, key='-NEWTAB-', disabled=True), 
        sg.Tab("Previous", row1_tab3, key='-PREVTAB-', disabled=True)]
    ])]

    row2 = [sg.Text("Chosen: ", size=(10, 1)), sg.Text(size=(29, 1), key='-DISP-', background_color=whte), sg.Button("Source", key='-SETSRC-', disabled=True), sg.Button("Destination", key='-SETDES-', disabled=True)]
    row3 = [sg.Text("Source:", size=(10, 1)), sg.Text(size=(55, 1), key='-SRC-', background_color=whte)]
    row4 = [sg.Text("Destination:", size=(10, 1)), sg.Text(size=(55, 1), key='-DES-', background_color=whte)]
    row5 = [sg.Text("Status:", size=(10, 1)), sg.Text(size=(55, 1), key='-VIEWPROCESS-', text_color=whte, background_color=blck)]

    return [row1_tabGroup , row2, row3, row4, row5] 

def main():
    rc = RClone()
    drive_list = []
    layout = setup_window()
    window = sg.Window("Syncer", layout)
    rc.window = window
    gp = GUI_Process(window, rc)

    while True:
        event, values = window.read()
        logging.debug("main: Event: {}".format(event))
        
        if event is not None:
            if event == '-START-': # For startup
                gp.startup(values['-PW-'])

            if event == '-DRIVE-': # List drives  
                gp.list_drive(values['-DRIVE-'])

            if event == '-DIRS-': # List directory contents
                gp.list_dirs(values['-DIRS-'])

            if event == '-BACK-': # Back button
                gp.back_button()

            if event == '-CHOOSE-': # Choose File button
                if len(values['-DIRS-']) != 0:
                    gp.choose_file(values['-DIRS-'][0])

            if event == '-CHOOSEFOLDER-': # Choose Folder button
                gp.choose_folder()
            
            if event == '-SETSRC-': # Set Source button
                gp.set_source()

            if event == '-SETDES-': # Set destination button
                gp.set_destination()
        
            if event == '-RUN-' or event == '-RUNPREV-': # Run button
                if values['-PROC-'] == 'Copy' or values['-PROCPREV-'] == 'Copy':
                    gp.copy_process()

                if values['-PROC-'] == 'Sync' or values['-PROCPREV-'] == 'Sync':
                    gp.sync_process()

                if values['-PROC-'] == 'Move' or values['-PROCPREV-'] == 'Move':
                    gp.move_process()
            
            if event == '-CHOOSEPREV-': # List directories on Previous tab
                gp.choose_previous(values['-PREVDIRS-'])
            
            if event == '-PREVDRIVE-': # List drives on Previous tab
                gp.drive_previous(values['-PREVDRIVE-'])

        else:
            logging.debug("main: Exit Program...")
            time.sleep(.25) # Buffer time to clean up everything
            break

if __name__ == "__main__":
    main()