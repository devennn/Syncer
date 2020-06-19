import os
import json
import logging
from pathlib import Path

def load_previous_process(fname, drive_list=[], driveName=False):
    '''
    Load recorded process. If driven name is given, will skip checking all

        Parameters:
            fname (str): File name of containing saved process
            drive_list (list): List of available drive from system
            driveName: default to False. Pass string for filename

        Returns:
            hist_list (list): List of stored process
    '''

    hist_list = []
    with open(fname, 'r') as f:
        hist = json.loads(f.read())
    
    if driveName is False: # load and check one by one
        for d in drive_list:
            try:
                logging.debug("load_previous_process: Loading {}".format(d))
                for h in hist[d]:
                    prev_process = "{} -> {}".format(h[0], h[1]) # format befor print
                    hist_list.append(prev_process)
            except KeyError:
                logging.debug("load_previous_process: {} not exist".format(d))
    else: # if driveName is passed
        try:
            for h in hist[driveName]:
                prev_process = "{} -> {}".format(h[0], h[1]) # Format before print
                hist_list.append(prev_process)
        except KeyError:
            logging.debug("load_previous_process: {} no record".format(driveName))
    return hist_list


def record_process(srcPath, desPath, fname):
    '''
    To record process

        Parameters:
            srcPath (str): source path
            desPath (str): Destination path
            fname (str): file name to store process

        Returns:
            None
    '''
    logging.debug("record_process: Start: {} -> {}".format(srcPath, desPath))
    driveName = srcPath.split(':')[0] + ':' # Correct drive format eg: Google:

    # Check if file exists. if not, create
    if os.path.exists(fname):
        f = open(fname, 'r')
        hist = json.loads(f.read())
        f.close()
    else:
        fname = Path(fname)
        fname.touch(exist_ok=True)
        hist = {}

    #if process has been recorded before, toggle this flag
    process_exist = False 

    try:
        for path in hist[driveName]:
            # Check if process exists by comparing string
            if srcPath == path[0] and desPath == path[1]:
                logging.debug("record_process: Process exists")
                process_exist = True
                break
        if process_exist is False:
            path = [srcPath, desPath]
            logging.debug("record_process: Save Path: {}".format(path))
            hist[driveName].append(path)
    except KeyError:
        logging.debug("record_process: Adding Drive: {}".format(driveName))
        path = [srcPath, desPath]
        hist[driveName] = [path]

    with open(fname, 'w') as f:
        f.write(json.dumps(hist))


def print_process(window, message):
    '''
    Printing process status

        Parameters:
            windows: windows instance from PySimpleGUI
            message (str): Message to print
    '''
    window['-VIEWPROCESS-'].update(message)
    window.Refresh()