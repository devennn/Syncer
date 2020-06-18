import os
import time
import logging
import threading
import subprocess
import PySimpleGUI as sg 

try:
    from utils import print_process
except Exception:
    from .utils import print_process

process_list = ['copy', 'sync', 'move']
gradientColor = ['#0080ff', '#0000ff', '#8000ff']

class RClone:
    def __init__(self):
        self.password = ""
        self.pathBuild = ""
        self.srcPath = ""
        self.desPath = ""
        self.window = None
        self.startProcess = False
        self.process = None
        

    def run_rclone(self, command, args_list=[], backFlag=False):
        pipeOutput = False
        if command == "lsf":
            if backFlag == False and args_list[0][0][-1] != '/' and self.pathBuild is not "":
                logging.debug("run_rclone: File: {}".format(args_list[0][0]))
                return
            if backFlag == False:
                self.pathBuild = os.path.join(self.pathBuild, args_list[0][0])
            cmd = ["rclone", command]
            cmd += [self.pathBuild]
            pipeOutput = True
        elif command == "ls":
            cmd= ["rclone", command, args_list[0]]
            pipeOutput = True
        elif command == "listremotes":
            cmd = ["rclone", command]
            pipeOutput = True
        elif command == "copy":
            cmd= ["rclone", command, args_list[0], self.desPath, "--no-traverse", "--progress"]
        elif command == "sync":
            cmd= ["rclone", command, self.srcPath, self.desPath, "--progress"]
        elif command == "move":
            cmd= ["rclone", command, self.srcPath, self.desPath, "--no-traverse", "--progress"]
        
        return self.rclone_process(cmd, pipeOutput)


    def rclone_process(self, cmd, pipeOutput):

        logging.debug("rclone_process: Invoking: {}".format(cmd))
        self.process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, 
                                universal_newlines=True)
        self.process.stdin.write(self.password)
        self.process.stdin.close()

        stdout = ""
        start_time = time.monotonic()
        indx = 0
        print_process(self.window, "Processing...")
        for line in self.process.stdout: # Get Real time output from subprocess
            if self.window is not None and self.startProcess is False:
                if cmd[1] in process_list:
                    fmtTime = time.strftime("%H:%M:%S", time.gmtime(time.monotonic() - start_time))
                    print_process(self.window, "Processing... Elapsed Time: {}".format(fmtTime))
                    try:
                        self.window['-VIEWPROCESS-'].update(background_color=gradientColor[indx])
                        self.window.Refresh()
                    except Exception as e:
                        logging.debug("rclone_process: {}".format(e))
                        return
            stdout += line # Record process stdout
            indx += 1
            if indx > len(gradientColor) - 1:
                indx = 0
        self.window['-VIEWPROCESS-'].update(background_color="#000000")
        print_process(self.window, "Done...")
        return self.rclone_format(stdout)
        

    def rclone_format(self, stdout):
        temp, formatted_out = [], []
        for s in stdout:
            if s is '\n':
                formatted_out.append(''.join(temp))
                temp = []
            else:
                temp.append(s)

        return formatted_out