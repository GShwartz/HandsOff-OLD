from datetime import datetime
from threading import Thread
from PIL import Image
import subprocess
import socket
import shutil
import time
import os


class Screenshot:
    def __init__(self, con, root, tmp_availables, clients, log_path, targets):
        self.targets = targets
        self.con = con
        self.root = root
        self.tmp_availables = tmp_availables
        self.clients = clients
        self.log_path = log_path

    def get_date(self):
        d = datetime.now().replace(microsecond=0)
        dt = str(d.strftime("%m/%d/%Y %H:%M:%S"))

        return dt

    def logIt_thread(self, log_path=None, debug=False, msg=''):
        self.logit_thread = Thread(target=self.logIt, args=(log_path, debug, msg), name="Log Thread")
        self.logit_thread.start()
        return

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

    def bytes_to_number(self, b):
        res = 0
        for i in range(4):
            res += b[i] << (i * 8)
        return res

    def recv_file(self, ip):
        def make_dir():
            self.logIt_thread(self.log_path, debug=False, msg=f'Running make_dir()...')
            self.logIt_thread(self.log_path, debug=False, msg=f'Creating Directory...')
            for conKey, ipValue in self.clients.items():
                for macKey, ipVal in ipValue.items():
                    for ipKey, userValue in ipVal.items():
                        if ipKey == ip:
                            for item in self.tmp_availables:
                                if item[2] == ip:
                                    for identKey, timeValue in userValue.items():
                                        name = item[3]
                                        loggedUser = item[4]
                                        clientVersion = item[5]
                                        path = os.path.join(self.root, name)

                                        try:
                                            os.makedirs(path)

                                        except FileExistsError:
                                            self.logIt_thread(self.log_path, debug=False, msg=f'Passing FileExistsError...')
                                            pass

                                    return path

        def file_name():
            self.logIt_thread(self.log_path, debug=False, msg=f'Running file_name()...')
            try:
                self.logIt_thread(self.log_path, debug=False, msg=f'Waiting for filename from client...')
                filename = self.con.recv(1024)
                self.logIt_thread(self.log_path, debug=False, msg=f'File name: {filename}')

                self.logIt_thread(self.log_path, debug=False, msg=f'Sending confirmation to client...')
                self.con.send("Filename OK".encode())
                self.logIt_thread(self.log_path, debug=False, msg=f'Send completed.')

                return filename

            except (WindowsError, socket.error) as e:
                self.logIt_thread(self.log_path, debug=True, msg=f'Error: {e}')
                return False

        def fetch(filename):
            self.logIt_thread(self.log_path, debug=False, msg=f'Running fetch()...')
            try:
                self.logIt_thread(self.log_path, debug=False, msg=f'Waiting for file size...')
                size = self.con.recv(4)
                self.logIt_thread(self.log_path, debug=False, msg=f'File size: {size}')

                self.logIt_thread(self.log_path, debug=False, msg=f'Converting size bytes to numbers...')
                size = self.bytes_to_number(size)
                self.logIt_thread(self.log_path, debug=False, msg=f'Converting completed.')

                current_size = 0
                buffer = b""
                try:
                    self.logIt_thread(self.log_path, debug=False, msg=f'Opening file: {filename} for writing...')
                    with open(filename, 'wb') as file:
                        self.logIt_thread(self.log_path, debug=False, msg=f'Fetching file content...')
                        while current_size < size:
                            data = self.con.recv(1024)
                            if not data:
                                break

                            if len(data) + current_size > size:
                                data = data[:size - current_size]

                            buffer += data
                            current_size += len(data)
                            file.write(data)

                    self.logIt_thread(self.log_path, debug=False, msg=f'Fetch completed.')

                except FileExistsError:
                    self.logIt_thread(self.log_path, debug=False, msg=f'File Exists error.')
                    self.logIt_thread(self.log_path, debug=False, msg=f'Opening {filename} for appends...')
                    with open(filename, 'ab') as file:
                        while current_size < size:
                            self.logIt_thread(self.log_path, debug=False, msg=f'Fetching file content...')
                            data = self.con.recv(1024)
                            if not data:
                                break

                            if len(data) + current_size > size:
                                data = data[:size - current_size]

                            buffer += data
                            current_size += len(data)
                            file.write(data)

                    self.logIt_thread(self.log_path, debug=False, msg=f'Fetch completed.')

                # Show Image
                with Image.open(filename) as img:
                    img.show()

                return

            except (WindowsError, socket.error) as e:
                self.logIt_thread(self.log_path, debug=True, msg=f'Error: {e}')
                return False

        def confirm():
            self.logIt_thread(self.log_path, debug=False, msg=f'Running confirm()...')
            try:
                self.logIt_thread(self.log_path, debug=False, msg=f'Waiting for answer from client...')
                ans = self.con.recv(1024).decode()
                self.logIt_thread(self.log_path, debug=False, msg=f'Client answer: {ans}')

            except (WindowsError, socket.error) as e:
                self.logIt_thread(self.log_path, debug=False, msg=f'Error: {e}')
                return False

        def move(filename, path):
            self.logIt_thread(self.log_path, debug=False, msg=f'Running move({filename}, {path})...')
            # Move screenshot file to directory
            self.logIt_thread(self.log_path, debug=False, msg=f'Renaming {filename}...')
            filename = str(filename).strip("b'")
            self.logIt_thread(self.log_path, debug=False, msg=f'New filename: {filename}')

            self.logIt_thread(self.log_path, debug=False, msg=f'Capturing {filename} absolute path...')
            src = os.path.abspath(filename)
            self.logIt_thread(self.log_path, debug=False, msg=f'Abs path: {src}')

            self.logIt_thread(self.log_path, debug=False, msg=f'Defining destination...')
            dst = fr"{path}"
            self.logIt_thread(self.log_path, debug=False, msg=f'Destination: {dst}.')

            self.logIt_thread(self.log_path, debug=False, msg=f'Moving file...')
            shutil.move(src, dst)
            self.logIt_thread(self.log_path, debug=False, msg=f'File {filename} moved to {dst}.')

        self.logIt_thread(self.log_path, debug=False, msg=f'Running recv_file()...')
        self.logIt_thread(self.log_path, debug=False, msg=f'Calling make_dir()...')
        path = make_dir()

        self.logIt_thread(self.log_path, debug=False, msg=f'Defining filename...')
        filename = file_name()
        self.logIt_thread(self.log_path, debug=False, msg=f'File name: {filename}.')

        self.logIt_thread(self.log_path, debug=False, msg=f'Calling fetch({filename})...')
        fetch(filename)

        confirm()

        self.logIt_thread(self.log_path, debug=False, msg=f'Calling move({filename}, {path})')
        move(filename, path)

        self.logIt_thread(self.log_path, debug=False, msg=f'=== End of self.recv() ===')
