from datetime import datetime
from threading import Thread
import ntpath
import socket
import shutil
import time
import os


class Tasks:
    def __init__(self, con, ip, clients, connections, targets, ips, tmp_availables, root, log_path, path, sname):
        self.con = con
        self.ip = ip
        self.clients = clients
        self.connections = connections
        self.targets = targets
        self.ips = ips
        self.tmp_availables = tmp_availables
        self.root = root
        self.log_path = log_path
        self.path = path
        self.sname = sname

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

    def make_dir(self, ip):
        self.logIt_thread(self.log_path, msg=f'Running make_dir()...')
        self.logIt_thread(self.log_path, msg=f'Creating Directory...')

        for conKey, macValue in self.clients.items():
            for macKey, ipVal in macValue.items():
                for ipKey, userValue in ipVal.items():
                    if ipKey == ip:
                        for item in self.tmp_availables:
                            if item[1] == ip:
                                for identKey, timeValue in userValue.items():
                                    name = item[2]
                                    loggedUser = item[3]
                                    clientVersion = item[4]
                                    path = os.path.join(self.root, name)

                                    try:
                                        os.makedirs(path)
                                        return path

                                    except FileExistsError:
                                        self.logIt_thread(self.log_path, msg=f'Passing FileExistsError...')
                                        pass

    def tasks(self, ip) -> str:
        self.logIt_thread(self.log_path, msg=f'Running tasks({ip})...')
        try:
            self.logIt_thread(self.log_path, msg=f'Sending tasks command to {ip}...')
            self.con.send('tasks'.encode())
            self.logIt_thread(self.log_path, msg=f'Send complete.')

            self.logIt_thread(self.log_path, msg=f'Waiting for filename from {ip}...')
            filenameRecv = self.con.recv(1024).decode()
            self.logIt_thread(self.log_path, msg=f'Filename: {filenameRecv}.')

            self.logIt_thread(self.log_path, msg=f'Sleeping for {0.5} seconds...')
            time.sleep(1)

            self.logIt_thread(self.log_path, msg=f'Waiting for file size from {ip}...')
            size = self.con.recv(4)
            self.logIt_thread(self.log_path, msg=f'Size: {size}.')

            self.logIt_thread(self.log_path, msg=f'Converting size bytes to numbers...')
            size = self.bytes_to_number(size)
            current_size = 0
            buffer = b""

            self.logIt_thread(self.log_path, msg=f'Renaming {filenameRecv}...')
            filenameRecv = str(filenameRecv).strip("b'")

            self.logIt_thread(self.log_path, msg=f'Calling self.make_dir({ip})...')
            path = self.make_dir(ip)

            self.logIt_thread(self.log_path, msg=f'Writing content to {filenameRecv}...')
            with open(filenameRecv, 'wb') as tsk_file:
                while current_size < size:
                    self.logIt_thread(self.log_path, msg=f'Receiving file content from {ip}...')
                    data = self.con.recv(1024)
                    if not data:
                        break

                    if len(data) + current_size > size:
                        data = data[:size - current_size]

                    buffer += data
                    current_size += len(data)
                    tsk_file.write(data)

            self.logIt_thread(self.log_path, msg=f'Printing file content to screen...')
            with open(filenameRecv, 'r') as file:
                data = file.read()

            self.logIt_thread(self.log_path, msg=f'Sending confirmation to {ip}...')
            self.con.send(f"Received file: {filenameRecv}\n".encode())
            self.logIt_thread(self.log_path, msg=f'Send complete.')

            self.logIt_thread(self.log_path, msg=f'Waiting for closer from {ip}...')
            msg = self.con.recv(1024).decode()
            self.logIt_thread(self.log_path, msg=f'{ip}: {msg}')

            # Move screenshot file to directory
            src = os.path.abspath(filenameRecv)
            dst = fr"{self.path}\{self.sname}"

            self.logIt_thread(self.log_path, msg=f'Moving {src} to {dst}...')
            try:
                shutil.move(src, dst)

            except FileExistsError:
                pass

            return dst + filenameRecv[11:]

        except (WindowsError, socket.error) as e:
            self.logIt_thread(self.log_path, msg=f'Error: {e}')
            print(f"[{colored('!', 'red')}]{e}")
            self.remove_lost_connection()

    def remove_lost_connection(self):
        self.logIt_thread(self.log_path, msg=f'Running self.remove_lost_connection()...')
        try:
            for conKey, ipValue in self.clients.items():
                if conKey == con:
                    for ipKey, identValue in ipValue.items():
                        if ipKey == ip:
                            for identKey, userValue in identValue.items():
                                self.targets.remove(con)
                                self.ips.remove(ip)

                                del self.connections[con]
                                del self.clients[con]
            return False

        except Exception as e:
            self.logIt_thread(self.log_path, msg=f'Error: {e}.')
            return False
