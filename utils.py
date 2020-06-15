import os
import json
import logging
from pathlib import Path

def load_previous_process(fname, drive_list=[], driveName=False):
    hist_list = []

    with open(fname, 'r') as f:
        hist = json.loads(f.read())
    
    if driveName is False:
        for d in drive_list:
            try:
                logging.debug("load_previous_process: Loading {}".format(d))
                for h in hist[d]:
                    prev_process = "{} -> {}".format(h[0], h[1])
                    hist_list.append(prev_process)
            except KeyError:
                logging.debug("load_previous_process: {} not exist".format(d))
    else:
        try:
            for h in hist[driveName]:
                prev_process = "{} -> {}".format(h[0], h[1])
                hist_list.append(prev_process)
        except KeyError:
            logging.debug("load_previous_process: {} no record".format(driveName))
    return hist_list

def record_process(srcPath, desPath, fname="prevprocess.json"):
    logging.debug("record_process: Start: {} -> {}".format(srcPath, desPath))
    driveName = srcPath.split(':')[0] + ':' # Correct drive format

    if os.path.exists(fname):
        f = open(fname, 'r')
        hist = json.loads(f.read())
        f.close()
    else:
        fname = Path(fname)
        fname.touch(exist_ok=True)
        hist = {}
    
    process_exist = False
    try:
        for path in hist[driveName]:
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