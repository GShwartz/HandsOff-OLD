from datetime import datetime
from threading import Thread
import subprocess
import socket
import os
import sys
import os


class Tasks:
    def __init__(self, soc, path, hostname, localIP):
        self.soc = soc
        self.log_path = path
        self.hostname = hostname
        self.localIP = localIP
        self.task_list = []

    def get_date(self):
        d = datetime.now().replace(microsecond=0)
        dt = str(d.strftime("%b %d %Y %I.%M.%S %p"))

        return dt

    def logIt(self, logfile=None, debug=None, msg=''):
        dt = self.get_date()
        if debug:
            print(f"{dt}: {msg}")

        if logfile is not None:
            try:
                if not os.path.exists(logfile):
                    with open(logfile, 'w') as lf:
                        lf.write(f"{dt}: {msg}\n")
                        return True

                else:
                    with open(logfile, 'a') as lf:
                        lf.write(f"{dt}: {msg}\n")
                    return True

            except FileExistsError:
                pass

    def logIt_thread(self, log_path=None, debug=False, msg=''):
        self.logit_thread = Thread(target=self.logIt, args=(log_path, debug, msg), name="Log Thread")
        self.logit_thread.start()
        return

    def convert_to_bytes(self, no):
        result = bytearray()
        result.append(no & 255)
        for i in range(3):
            no = no >> 8
            result.append(no & 255)

        return result

    def command_to_file(self):
        self.logIt_thread(self.log_path, msg=f'Running command_to_file()...')
        try:
            dt = self.get_date()
            self.logIt_thread(self.log_path, msg=f'Opening file: {self.taskfile}...')
            with open(self.taskfile, 'w') as task_file:
                task_file.write(f"{'=' * 80}\n")
                task_file.write(f"IP: {self.localIP} | NAME: {self.hostname} | LOGGED USER: {os.getlogin()} | {dt}\n")
                task_file.write(f"{'=' * 80}\n")

            with open(self.taskfile, 'a') as task_file:
                subprocess.run(['tasklist'], stdout=task_file)
                task_file.write('\n')

            return True

        except (FileNotFoundError, FileExistsError) as e:
            self.logIt_thread(self.log_path, msg=f'File Error: {e}')
            return False

    def send_file_name(self):
        self.logIt_thread(self.log_path, msg=f'Running send_file_name()...')
        try:
            self.logIt_thread(self.log_path, msg=f'Sending file name: {self.taskfile}...')
            self.soc.send(f"{self.taskfile}".encode())
            self.logIt_thread(self.log_path, msg=f'Send Completed.')
            return True

        except (WindowsError, socket.error) as e:
            self.logIt_thread(self.log_path, msg=f'Connection Error: {e}')
            return False

    def print_file_content(self):
        self.logIt_thread(self.log_path, msg=f'Running print_file_content()...')
        self.logIt_thread(self.log_path, msg=f'Opening file: {self.taskfile}...')
        with open(self.taskfile, 'r') as file:
            self.logIt_thread(self.log_path, msg=f'Adding content to list...')
            for line in file.readlines():
                self.task_list.append(line)

        self.logIt_thread(self.log_path, msg=f'Printing content from list...')
        for t in self.task_list:
            print(t)

    def send_file_size(self):
        self.logIt_thread(self.log_path, msg=f'Running send_file_size()...')
        self.logIt_thread(self.log_path, msg=f'Defining file size...')
        length = os.path.getsize(self.taskfile)
        self.logIt_thread(self.log_path, msg=f'File Size: {length}')

        try:
            self.logIt_thread(self.log_path, msg=f'Sending file size...')
            self.soc.send(self.convert_to_bytes(length))
            self.logIt_thread(self.log_path, msg=f'Send Completed.')
            return True

        except (WindowsError, socket.error) as e:
            self.logIt_thread(self.log_path, msg=f'Connection Error: {e}')
            return False

    def send_file_content(self):
        self.logIt_thread(self.log_path, msg=f'Running send_file_content()...')
        self.logIt_thread(self.log_path, msg=f'Opening file: {self.taskfile}...')
        with open(self.taskfile, 'rb') as tsk_file:
            self.logIt_thread(self.log_path, msg=f'Reading content from {self.taskfile}...')
            tsk_data = tsk_file.read(1024)
            try:
                self.logIt_thread(self.log_path, msg=f'Sending file content...')
                while tsk_data:
                    self.soc.send(tsk_data)
                    if not tsk_data:
                        break

                    tsk_data = tsk_file.read(1024)

                self.logIt_thread(self.log_path, msg=f'Send Completed.')

            except (WindowsError, socket.error) as e:
                self.logIt_thread(self.log_path, msg=f'Connection Error: {e}')
                return False

    def confirm(self) -> bool:
        self.logIt_thread(self.log_path, msg=f'Running confirm()...')
        try:
            self.logIt_thread(self.log_path, msg=f'Waiting for confirmation from server...')
            self.soc.settimeout(10)
            msg = self.soc.recv(1024).decode()
            self.soc.settimeout(None)
            self.logIt_thread(self.log_path, msg=f'Server Confirmation: {msg}')

        except (WindowsError, socket.error) as e:
            self.logIt_thread(self.log_path, msg=f'Connection Error: {e}')
            return False

        try:
            self.logIt_thread(self.log_path, msg=f'Sending confirmation...')
            self.soc.send(f"{self.hostname} | {self.localIP}: Task List Sent.\n".encode())
            self.logIt_thread(self.log_path, msg=f'Send Completed.')
            return True

        except (WindowsError, socket.error) as e:
            self.logIt_thread(self.log_path, msg=f'Connection Error: {e}')
            return False

    def kill(self) -> bool:
        self.logIt_thread(self.log_path, msg=f'Waiting for task name...')
        try:
            self.soc.settimeout(10)
            task2kill = self.soc.recv(1024).decode()
            self.soc.settimeout(None)
            self.logIt_thread(self.log_path, msg=f'Task name: {task2kill}')

        except (WindowsError, socket.error) as e:
            self.logIt_thread(self.log_path, msg=f'Connection Error: {e}')
            return False

        if str(task2kill).lower()[:1] == 'q':
            return True

        self.logIt_thread(self.log_path, msg=f'Killing {task2kill}...')
        os.system(f'taskkill /IM {task2kill} /F')
        self.logIt_thread(self.log_path, msg=f'{task2kill} killed.')

        self.logIt_thread(self.log_path, msg=f'Sending killed confirmation to server...')
        try:
            self.soc.send(f"Task: {task2kill} Killed.".encode())
            self.logIt_thread(self.log_path, msg=f'Send Completed.')

        except (WindowsError, socket.error) as e:
            self.logIt_thread(self.log_path, msg=f'Connection Error: {e}')
            return False

        return True

    def run(self) -> bool:
        self.logIt_thread(self.log_path, msg=f'Defining tasks file name...')
        dt = self.get_date()
        self.taskfile = rf"C:\HandsOff\tasks {self.hostname} {str(self.localIP)} {dt}.txt"
        self.logIt_thread(self.log_path, msg=f'Tasks file name: {self.taskfile}')

        self.logIt_thread(self.log_path, msg=f'Calling command_to_file()...')
        self.command_to_file()
        self.logIt_thread(self.log_path, msg=f'Calling send_file_name()...')
        self.send_file_name()
        self.logIt_thread(self.log_path, msg=f'Calling print_file_content()...')
        self.print_file_content()
        self.logIt_thread(self.log_path, msg=f'Calling send_file_size()...')
        self.send_file_size()
        self.logIt_thread(self.log_path, msg=f'Calling send_file_content()...')
        self.send_file_content()
        self.logIt_thread(self.log_path, msg=f'Calling confirm()...')
        self.confirm()

        self.logIt_thread(self.log_path, msg=f'Removing file: {self.taskfile}...')
        os.remove(self.taskfile)

        try:
            self.soc.settimeout(10)
            kil = self.soc.recv(1024).decode()
            self.soc.settimeout(None)

        except (WindowsError, socket.error):
            return False

        if str(kil)[:4].lower() == "kill":
            self.logIt_thread(self.log_path, msg=f'Calling kill()...')
            self.kill()

        return True
