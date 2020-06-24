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

process_list = ['copy', 'sync', 'move'] # Process that requires color progress bar
gradientColor = ['#0080ff', '#0000ff', '#8000ff'] # Color for progress bar

class RClone:
    def __init__(self):
        self.password = ""          # Password
        self.pathBuild = ""         # previous path chosen
        self.srcPath = ""           # Source path
        self.desPath = ""           # Destination path
        self.window = None          # Window instance
        self.startProcess = False   # Flag for start process 
        self.process = None         # subprocess instance
        

    def run_rclone(self, command, args_list=[], backFlag=False):
        '''
        Entry point to run RClone command. For process that require additional process, 
        refer to RClone official documentation for info

            Parameters:
                command (str): command name
                args_list (list): arguments of command if needed
                backFlag (bool): True if current process is for back button

            Returns:
                stdout (list): Stdout from command line process
        '''
        if command == "lsf":
            if backFlag == False and args_list[0][0][-1] != '/' and self.pathBuild is not "":
                logging.debug("run_rclone: File: {}".format(args_list[0][0]))
                return
            if backFlag == False:
                self.pathBuild = os.path.join(self.pathBuild, args_list[0][0])
            cmd = ["rclone", command]
            cmd += [self.pathBuild]
        elif command == "ls":
            cmd= ["rclone", command, args_list[0]]
        elif command == "listremotes":
            cmd = ["rclone", command]
        elif command == "copy":
            cmd= ["rclone", command, args_list[0], self.desPath, "--no-traverse", "--progress"]
        elif command == "sync":
            cmd= ["rclone", command, self.srcPath, self.desPath, "--progress"]
        elif command == "move":
            cmd= ["rclone", command, self.srcPath, self.desPath, "--no-traverse", "--progress"]
        
        return self.rclone_process(cmd)


    def rclone_process(self, cmd):
        '''
        Spawn subprocess to interact with command line

            Parameters:
                cmd (list): Command to passed to Popen

            Returns:
                stoud (list): formatted stdout from subprocess
        '''
        logging.debug("rclone_process: Invoking: {}".format(cmd))
        self.process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, 
                                universal_newlines=True)
        self.process.stdin.write(self.password) # Write password
        self.process.stdin.close() # close for safety

        stdout = ""
        start_time = time.monotonic() #Get start time of process
        indx = 0 # Color index
        print_process(self.window, "Processing...")
        for line in self.process.stdout: # Get Real time output from subprocess
            if self.window is not None and self.startProcess is False:
                if cmd[1] in process_list: # Only run color progress if command in list
                    # get process elapsed time and print
                    fmtTime = time.strftime("%H:%M:%S", time.gmtime(time.monotonic() - start_time)) 
                    print_process(self.window, "Processing... Elapsed Time: {}".format(fmtTime))

                    # update color progress 
                    try:
                        self.window['-VIEWPROCESS-'].update(background_color=gradientColor[indx])
                        self.window.Refresh()
                    except Exception as e:
                        logging.debug("rclone_process: {}".format(e))
                        self.process.kill() # Kill process if error happens
                        return
            stdout += line # Record process stdout
            indx += 1
            if indx > len(gradientColor) - 1: # Reset index to 0
                indx = 0
        self.window['-VIEWPROCESS-'].update(background_color="#000000") # Reset to black when done
        print_process(self.window, "Done...")
        return self.rclone_format(stdout)
        

    def rclone_format(self, stdout):
        '''
        Format stdout from subprocess

            Parameters:
                stdout (str): stdout from subprocess in string

            Returns:
                formatted_out (list): formatted string to list
        '''
        temp, formatted_out = [], []
        for s in stdout:
            if s is '\n':
                formatted_out.append(''.join(temp))
                temp = []
            else:
                temp.append(s)

        return formatted_out