from datetime import datetime
from threading import Thread
import ntpath
import socket
import shutil
import time
import os


class Tasks:
    def __init__(self, endpoint, log_path, path):
        self.endpoint = endpoint
        self.log_path = log_path
        self.path = path

    def get_date(self):
        d = datetime.now().replace(microsecond=0)
        dt = str(d.strftime("%m/%d/%Y %H:%M:%S"))

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

    def make_dir(self):
        self.logIt_thread(self.log_path, msg=f'Running make_dir()...')
        self.logIt_thread(self.log_path, msg=f'Creating Directory...')
        path = os.path.join(self.path, self.endpoint.ident)
        try:
            os.makedirs(path)

        except FileExistsError:
            self.logIt_thread(self.log_path, msg=f'Passing FileExistsError...')
            pass

    def tasks(self) -> str:
        self.logIt_thread(self.log_path, msg=f'Running tasks({self.endpoint.ip})...')
        try:
            self.logIt_thread(self.log_path, msg=f'Sending tasks command to {self.endpoint.ip}...')
            self.endpoint.conn.send('tasks'.encode())
            self.logIt_thread(self.log_path, msg=f'Send complete.')

            self.logIt_thread(self.log_path, msg=f'Waiting for filename from {self.endpoint.ip}...')
            self.endpoint.conn.settimeout(10)
            filenameRecv = self.endpoint.conn.recv(1024).decode()
            self.endpoint.conn.settimeout(None)
            self.logIt_thread(self.log_path, msg=f'Filename: {filenameRecv}.')

            self.logIt_thread(self.log_path, msg=f'Sleeping for {0.5} seconds...')
            time.sleep(1)

            self.logIt_thread(self.log_path, msg=f'Waiting for file size from {self.endpoint.ip}...')
            self.endpoint.conn.settimeout(10)
            size = self.endpoint.conn.recv(4)
            self.endpoint.conn.settimeout(None)
            self.logIt_thread(self.log_path, msg=f'Size: {size}.')

            self.logIt_thread(self.log_path, msg=f'Converting size bytes to numbers...')
            size = self.bytes_to_number(size)
            current_size = 0
            buffer = b""

            self.logIt_thread(self.log_path, msg=f'Renaming {filenameRecv}...')
            filenameRecv = str(filenameRecv).strip("b'")

            self.logIt_thread(self.log_path, msg=f'Calling self.make_dir({self.endpoint.ip})...')
            self.make_dir()

            self.logIt_thread(self.log_path, msg=f'Writing content to {filenameRecv}...')
            with open(filenameRecv, 'wb') as tsk_file:
                self.endpoint.conn.settimeout(60)
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
                self.endpoint.conn.settimeout(None)

            self.logIt_thread(self.log_path, msg=f'Printing file content to screen...')
            with open(filenameRecv, 'r') as file:
                data = file.read()

            self.logIt_thread(self.log_path, msg=f'Sending confirmation to {self.endpoint.ip}...')
            self.endpoint.conn.send(f"Received file: {filenameRecv}\n".encode())
            self.logIt_thread(self.log_path, msg=f'Send complete.')

            self.logIt_thread(self.log_path, msg=f'Waiting for closer from {self.endpoint.ip}...')
            self.endpoint.conn.settimeout(10)
            msg = self.endpoint.conn.recv(1024).decode()
            self.endpoint.conn.settimeout(None)
            self.logIt_thread(self.log_path, msg=f'{self.endpoint.ip}: {msg}')

            # Move screenshot file to directory
            src = os.path.abspath(filenameRecv)
            dst = fr"{self.path}\{self.endpoint.ident}"

            self.logIt_thread(self.log_path, msg=f'Moving {src} to {dst}...')
            try:
                shutil.move(src, dst)

            except FileExistsError:
                pass

            return dst + filenameRecv[11:]

        except (WindowsError, socket.error) as e:
            self.logIt_thread(self.log_path, msg=f'Error: {e}')
            return False
