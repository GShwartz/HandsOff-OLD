from Modules.logger import init_logger
from datetime import datetime
from threading import Thread
import subprocess
import socket
import sys
import os


class Tasks:
    def __init__(self, client, log_path, app_path):
        self.log_path = log_path
        self.app_path = app_path
        self.client = client
        self.dt = self.get_date()
        self.taskfile = rf"tasks {self.client.hostname} {str(self.client.localIP)} {self.dt}.txt"
        self.task_path = os.path.join(app_path, self.taskfile)
        self.logger = init_logger(self.log_path, __name__)

    def get_date(self) -> str:
        d = datetime.now().replace(microsecond=0)
        dt = str(d.strftime("%d-%b-%y %I.%M.%S %p"))
        return dt

    def convert_to_bytes(self, no):
        result = bytearray()
        result.append(no & 255)
        for i in range(3):
            no = no >> 8
            result.append(no & 255)
        return result

    def command_to_file(self):
        self.logger.info(f"Running command_to_file()...")
        try:
            self.logger.debug(f"Writing heading on {self.task_path}...")
            with open(self.task_path, 'w') as task_file:
                task_file.write(f"{'=' * 80}\n")
                task_file.write(f"IP: {self.client.localIP} | NAME: {self.client.hostname} | "
                                f"LOGGED USER: {os.getlogin()} | {self.dt}\n")
                task_file.write(f"{'=' * 80}\n")

            with open(self.task_path, 'a') as task_file:
                self.logger.debug(f"Adding tasks list to {self.task_path}...")
                subprocess.run(['tasklist'], stdout=task_file)
                task_file.write('\n')

            return True

        except (FileNotFoundError, FileExistsError) as e:
            self.logger.debug(f"File error: {e}")
            return False

    def send_file_name(self):
        self.logger.info(f"Running send_file_name()...")
        try:
            self.logger.debug(f"Sending file name...")
            self.client.soc.send(f"{self.taskfile}".encode())
            return True

        except (WindowsError, socket.error) as e:
            self.logger.debug(f"Connection Error: {e}")
            return False

    def send_file_size(self):
        self.logger.info(f"Running send_file_size()...")
        self.logger.debug(f"Defining file size...")
        length = os.path.getsize(self.task_path)
        self.logger.debug(f"File Size: {length}")

        try:
            self.logger.debug(f"Sending file size...")
            self.client.soc.send(self.convert_to_bytes(length))
            return True

        except (WindowsError, socket.error) as e:
            self.logger.debug(f"Connection Error: {e}")
            return False

    def send_file_content(self):
        self.logger.info(f"Running send_file_content()...")
        self.logger.debug(f"Opening {self.task_path}...")
        with open(self.task_path, 'rb') as tsk_file:
            self.logger.debug(f"Reading content...")
            tsk_data = tsk_file.read(1024)
            try:
                self.logger.debug(f"Sending file content...")
                while tsk_data:
                    self.client.soc.send(tsk_data)
                    if not tsk_data:
                        break

                    tsk_data = tsk_file.read(1024)

                self.logger.debug(f"Send completed.")

            except (WindowsError, socket.error) as e:
                self.logger.debug(f"Connection Error: {e}")
                return False

    def confirm(self) -> bool:
        self.logger.info(f"Running confirm()...")
        try:
            self.logger.debug(f"Waiting for confirmation...")
            self.client.soc.settimeout(10)
            msg = self.client.soc.recv(1024).decode()
            self.client.soc.settimeout(None)
            self.logger.debug(f"Server: {msg}")

        except (WindowsError, socket.error) as e:
            self.logger.debug(f"Connection Error: {e}")
            return False

        try:
            self.logger.debug(f"Sending confirmation...")
            self.client.soc.send(f"{self.client.hostname} | {self.client.localIP}: Task List Sent.\n".encode())
            self.logger.info(f"confirm completed.")
            return True

        except (WindowsError, socket.error) as e:
            self.logger.debug(f"Connection Error: {e}")
            return False

    def kill(self) -> bool:
        self.logger.info(f"Running kill()...")
        self.logger.debug(f"Waiting for task name...")
        try:
            self.client.soc.settimeout(10)
            task2kill = self.client.soc.recv(1024).decode()
            self.client.soc.settimeout(None)
            self.logger.debug(f"Task name: {task2kill}")

        except (WindowsError, socket.error) as e:
            self.logger.debug(f"Connection Error: {e}")
            return False

        if str(task2kill).lower()[:1] == 'q':
            return True

        self.logger.debug(f"Killing {task2kill}...")
        os.system(f'taskkill /IM {task2kill} /F')
        self.logger.debug(f"{task2kill} killed.")
        self.logger.debug(f"Sending killed confirmation to server...")
        try:
            self.client.soc.send(f"Task: {task2kill} Killed.".encode())
            self.logger.debug(f"Send completed.")

        except (WindowsError, socket.error) as e:
            self.logger.debug(f"Connection Error: {e}")
            return False

        return True

    def run(self) -> bool:
        self.logger.debug(f"Calling command_to_file()...")
        self.command_to_file()
        self.logger.debug(f"Calling send_file_name()...")
        self.send_file_name()
        self.logger.debug(f"Calling send_file_size()...")
        self.send_file_size()
        self.logger.debug(f"Calling send_file_content()...")
        self.send_file_content()
        self.logger.debug(f"Calling Calling confirm()...")
        self.confirm()
        self.logger.debug(f"Removing {self.task_path}...")
        os.remove(self.task_path)
        self.logger.debug(f"Flushing stdout...")
        sys.stdout.flush()

        try:
            self.client.soc.settimeout(10)
            self.logger.debug(f"Waiting for confirmation...")
            kil = self.client.soc.recv(1024).decode()
            self.client.soc.settimeout(None)
            self.logger.debug(f"Server: {kil}")

        except (WindowsError, socket.error) as e:
            self.logger.debug(f"Connection Error: {e}")
            return False

        if str(kil)[:4].lower() == "kill":
            self.logger.debug(f"Calling kill()...")
            self.kill()
            return True
