from Modules.logger import init_logger
from datetime import datetime
from threading import Thread
import subprocess
import socket
import sys
import os


class SystemInformation:
    def __init__(self, client, log_path, app_path):
        self.log_path = log_path
        self.app_path = app_path
        self.client = client
        self.dt = self.get_date()
        self.sifile = rf"systeminfo {self.client.hostname} {self.dt}.txt"
        self.si_full_path = os.path.join(app_path, self.sifile)
        self.buffer_size = 1024
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
        with open(self.si_full_path, 'w') as sysinfo:
            self.logger.info(f"Running system information command...")
            sys_info = subprocess.run(['systeminfo'], stdout=subprocess.PIPE, text=True)
            sys_info_str = sys_info.stdout
            self.logger.debug(f"Adding header to {self.si_full_path}...")
            sysinfo.write(f"{'=' * 80}\n")
            sysinfo.write(
                f"IP: {self.client.localIP} | NAME: {self.client.hostname} | LOGGED USER: {os.getlogin()} | {self.dt}\n")
            sysinfo.write(f"{'=' * 80}\n")
            self.logger.debug(f"Adding system information to {self.si_full_path}...")
            sysinfo.write(f"{sys_info_str}\n\n")

    def send_filename(self):
        try:
            self.logger.info(f"Sending file name...")
            self.client.soc.send(f"{self.sifile}".encode())

        except (WindowsError, socket.error) as e:
            self.logger.debug(f"Connection Error: {e}")
            return False

    def send_file_size(self):
        self.logger.info(f"Running send_file_size...")
        try:
            self.logger.debug(f"Defining file size...")
            length = os.path.getsize(self.si_full_path)
            self.logger.debug(f"File Size: {length}")

            self.logger.debug(f"Sending file size...")
            self.client.soc.send(self.convert_to_bytes(length))

        except (WindowsError, socket.error) as e:
            self.logger.debug(f"Connection Error: {e}")
            return False

    def send_file_content(self):
        self.logger.info(f"Running send_file_content...")
        try:
            self.logger.debug(f"Opening {self.si_full_path}...")
            with open(self.si_full_path, 'rb') as sy_file:
                self.logger.debug(f"Sending file content...")
                sys_data = sy_file.read(self.buffer_size)
                while sys_data:
                    self.client.soc.send(sys_data)
                    if not sys_data:
                        break

                    sys_data = sy_file.read(self.buffer_size)

            self.logger.debug(f"Send completed.")

        except (WindowsError, socket.error, FileExistsError, FileNotFoundError) as e:
            self.logger.debug(f"Error: {e}")
            return False

    def confirm(self):
        self.logger.info(f"Running confirm...")
        try:
            self.logger.debug(f"Waiting for confirmation...")
            msg = self.client.soc.recv(self.buffer_size).decode()
            self.logger.debug(f"Server: {msg}")

        except (WindowsError, socket.error) as e:
            self.logger.debug(f"Connection Error: {e}")
            return False

    def run(self):
        self.logger.debug(f"Calling command_to_file...")
        self.command_to_file()
        self.logger.debug(f"Calling send_filename...")
        self.send_filename()
        self.logger.debug(f"Calling send_file_size...")
        self.send_file_size()
        self.logger.debug(f"Calling send_file_content...")
        self.send_file_content()
        self.logger.debug(f"Calling confirm...")
        self.confirm()
        self.logger.debug(f"Removing script file...")
        os.remove(self.si_full_path)
        self.logger.debug(f"Flushing stdout...")
        sys.stdout.flush()
