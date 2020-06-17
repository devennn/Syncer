#!/usr/bin/python3

import os
import json
import logging
import PySimpleGUI as sg 

from rclone import RClone
from gui_process import GUI_Process

logging.basicConfig(level=logging.DEBUG)

sg.ChangeLookAndFeel('BlueMono')  

def setup_window(drive_list):
    row1_tab1 = [
        [sg.Text("Enter password to start. Leave empty if not available")],     
        [sg.InputText(size=(40, 1), password_char='*', key='-PW-')], 
        [sg.Button("Start", key='-START-')],
        [sg.Text(size=(55, 1), key='-STARTMES-')]
    ]
    row1_tab2 = [[
        sg.Frame("Drives", layout=[[sg.Listbox(values=drive_list, size=(15, 7), key='-DRIVE-', enable_events=True)], 
                    [sg.Button("Sync", key='-SYNC-'), sg.Button("Copy", key='-COPY-')]]), 
        sg.Frame("Directory", layout=[[sg.Listbox(values=[], size=(42, 7) ,  key='-DIRS-', enable_events=True)], 
                    [sg.Button("Back", key='-BACK-'), sg.Button("Choose File", key='-CHOOSE-'), 
                    sg.Button("Choose Folder", key='-CHOOSEFOLDER-')]])
    ]]
    row1_tab3 = [[
        sg.Frame("Drives", layout=[[sg.Listbox(values=drive_list, size=(15, 7) ,  key='-PREVDRIVE-', enable_events=True)], 
                    [sg.Button("Sync", key='-SYNCPREV-'), sg.Button("Copy", key='-COPYPREV-')]]), 
        sg.Frame("Previous Process", layout=[[sg.Listbox(values=[], size=(42, 7) ,  key='-PREVDIRS-', enable_events=True)], 
                    [sg.Button("Choose Process", key='-CHOOSEPREV-')]])
    ]]
    row1_tabGroup = [sg.TabGroup([[sg.Tab("Start", row1_tab1, key='-STARTTAB-'), sg.Tab("New", row1_tab2, key='-NEWTAB-', disabled=True), 
                        sg.Tab("Previous", row1_tab3, key='-PREVTAB-', disabled=True)]])]
    row2 = [sg.Text("Chosen: ", size=(10, 1)), sg.Text(size=(29, 1), key='-DISP-', background_color='#ffffff'), 
            sg.Button("Source", key='-SETSRC-', disabled=True), sg.Button("Destination", key='-SETDES-', disabled=True)]
    row3 = [sg.Text("Source:", size=(10, 1)), sg.Text(size=(55, 1), key='-SRC-', background_color='#ffffff')]
    row4 = [sg.Text("Destination:", size=(10, 1)), sg.Text(size=(55, 1), key='-DES-', background_color='#ffffff')]
    row5 = [sg.Text("Status:", size=(10, 1)), sg.Text(size=(55, 1), key='-VIEWPROCESS-', text_color='#ffffff', background_color='#000000')]

    return [row1_tabGroup , row2, row3, row4, row5] 

def main():
    rc = RClone()
    drive_list = []
    layout = setup_window(drive_list)
    window = sg.Window("Syncer", layout)
    rc.window = window
    gp = GUI_Process(window, rc)

    while True:
        event, values = window.read()
        logging.debug("main: Event: {}".format(event))
        
        if event is not None:
            if event == '-START-':
                gp.startup(values['-PW-'])

            if event == '-DRIVE-':  
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

            if event == '-COPY-' or event == '-COPYPREV-': # Copy button
                gp.copy_process(event)
            
            if event == '-SYNC-' or event == '-SYNCPREV-': # Sync button  
                gp.sync_process()
            
            if event == '-CHOOSEPREV-':
                gp.choose_previous(values['-PREVDIRS-'])
            
            if event == '-PREVDRIVE-':
                gp.drive_previous(values['-PREVDRIVE-'])

        else:
            logging.debug("main: Exit Program...")
            break

if __name__ == "__main__":
    main()