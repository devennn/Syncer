import os
import logging
import threading
import subprocess
import PySimpleGUI as sg 

class RClone:
    def __init__(self):
        self.password = ""
        self.pathBuild = ""
        self.srcPath = ""
        self.desPath = ""
        self.window = None
        

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
        
        return self.rclone_process(cmd, pipeOutput)


    def rclone_process(self, cmd, pipeOutput):
        if self.password == "":
            self.password = self.prompt_password()

        stdout = ""
        logging.debug("rclone_process: Invoking: {}".format(cmd))

        if pipeOutput is True:
            stdoutPipeVal = subprocess.PIPE
        else:
            stdoutPipeVal = None
        p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=stdoutPipeVal,
            stderr=subprocess.PIPE, universal_newlines=True)

        stdout, _ = p.communicate(self.password)
        
        if stdout is None:
            return

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


    def prompt_password(self):
        layout = [[sg.Text("Leave empty if no password")],      
                    [sg.InputText(size=(20, 1), password_char='*')], [sg.Submit()]]      

        window = sg.Window('Password', layout)    

        event, values = window.read()    
        window.close()

        return (str(values[0]) + '\n') # Make sure pw in correct format