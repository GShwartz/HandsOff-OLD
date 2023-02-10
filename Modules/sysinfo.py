from datetime import datetime
from threading import Thread
from main import App
import socket
import shutil
import time
import os


class Sysinfo:
    def __init__(self, endpoint, path, log_path, app):
        self.app = app
        self.endpoint = endpoint
        self.root = path
        self.log_path = log_path
        self.path = os.path.join(self.root, self.endpoint.ident)

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

    def bytes_to_number(self, b):
        res = 0
        for i in range(4):
            res += b[i] << (i * 8)
        return res

    def run(self):

        self.logIt_thread(self.log_path, msg=f'Running recv_file()...')
        self.logIt_thread(self.log_path, msg=f'Calling make_dir()...')
        try:
            os.makedirs(self.path)

        except FileExistsError:
            self.logIt_thread(self.log_path, debug=False, msg=f'Passing FileExistsError...')
            pass

        self.logIt_thread(self.log_path, msg=f'Creating sysinfo file...')
        dt = self.get_date()
        self.sysinfo = rf'C:\HandsOff\{self.endpoint.ident}\sysinfo {dt}.txt'

        try:
            self.logIt_thread(self.log_path, msg=f'Sending si command to {self.endpoint.conn}...')
            self.endpoint.conn.send('si'.encode())
            self.logIt_thread(self.log_path, msg=f'Send complete.')
            filename = self.endpoint.conn.recv(1024).decode()
            file_path = os.path.join(self.path, filename)

        except (WindowsError, socket.error) as e:
            self.logIt_thread(self.log_path, msg=f'Connection error: {e}')
            return False

        try:
            size = self.endpoint.conn.recv(4)

        except (WindowsError, socket.error) as e:
            self.logIt_thread(self.log_path, msg=f'Connection error: {e}')
            return False

        size = self.bytes_to_number(size)

        current_size = 0
        buffer = b""
        with open(self.sysinfo, 'wb') as tsk_file:
            while current_size < size:
                self.logIt_thread(self.log_path, msg=f'Receiving file content from {self.endpoint.ip}...')
                data = self.endpoint.conn.recv(1024)
                if not data:
                    break

                if len(data) + current_size > size:
                    data = data[:size - current_size]

                buffer += data
                current_size += len(data)
                tsk_file.write(data)

        self.endpoint.conn.send(f"Received file: {filename}\n".encode())
        self.endpoint.conn.settimeout(10)
        self.logIt_thread(self.log_path, msg=f'Waiting for msg from {self.endpoint.ip}...')
        try:
            msg = self.endpoint.conn.recv(1024).decode()
            self.endpoint.conn.settimeout(None)

        except (WindowsError, socket.error) as e:
            self.logIt_thread(self.log_path, msg=f'Connection error: {e}')
            return False

        # Validate file received
        self.logIt_thread(self.log_path, msg=f'Validating file integrity...')
        with open(self.sysinfo, 'r') as file:
            data = file.read()
            # print(data)   # for debugging

        # Move screenshot file to directory
        self.logIt_thread(self.log_path, msg=f'Moving file to {self.sysinfo}...')
        try:
            shutil.move(file_path, self.sysinfo)

        except (FileNotFoundError, FileExistsError):
            pass

        return self.sysinfo
