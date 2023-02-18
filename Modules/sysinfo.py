import sys
from datetime import datetime
from threading import Thread
from tkinter import *
import socket
import os


class Sysinfo:
    def __init__(self, endpoint, app, path, log_path):
        self.app = app
        self.endpoint = endpoint
        self.app_path = path
        self.log_path = log_path
        self.path = os.path.join(self.app_path, self.endpoint.ident)

    def make_dir(self):
        try:
            os.makedirs(self.path)

        except FileExistsError:
            logIt_thread(self.log_path, debug=False, msg=f'Passing FileExistsError...')
            pass

    def get_file_name(self):
        try:
            logIt_thread(self.log_path, msg=f'Sending si command to {self.endpoint.conn}...')
            self.endpoint.conn.send('si'.encode())
            logIt_thread(self.log_path, msg=f'Send complete.')
            self.filename = self.endpoint.conn.recv(1024).decode()
            self.file_path = os.path.join(self.path, self.filename)

        except (WindowsError, socket.error) as e:
            logIt_thread(log_path, msg=f'Connection error: {e}')
            return False

    def get_file_size(self):
        try:
            self.size = self.endpoint.conn.recv(4)
            self.endpoint.conn.send("OK".encode())
            self.size = bytes_to_number(self.size)

        except (WindowsError, socket.error) as e:
            logIt_thread(self.log_path, msg=f'Connection error: {e}')
            return False

    def get_file_content(self):
        current_size = 0
        buffer = b""
        try:
            with open(self.file_path, 'wb') as tsk_file:
                while current_size < self.size:
                    logIt_thread(self.log_path, msg=f'Receiving file content from {self.endpoint.ip}...')
                    data = self.endpoint.conn.recv(1024)
                    if not data:
                        break

                    if len(data) + current_size > self.size:
                        data = data[:self.size - current_size]

                    buffer += data
                    current_size += len(data)
                    tsk_file.write(data)

        except ValueError:
            print("something is wrong in get_file_content.")
            sys.exit(1)

    def confirm(self):
        try:
            self.endpoint.conn.settimeout(10)
            self.endpoint.conn.send(f"Received file: {self.filename}\n".encode())
            logIt_thread(self.log_path, msg=f'Waiting for msg from {self.endpoint.ip}...')
            msg = self.endpoint.conn.recv(1024).decode()
            self.endpoint.conn.settimeout(None)

        except (WindowsError, socket.error) as e:
            logIt_thread(self.log_path, msg=f'Connection error: {e}')
            return False

    def file_validation(self):
        try:
            with open(self.file_path, 'r') as file:
                data = file.read()
                # print(data)   # for debugging

        except Exception as e:
            logIt_thread(self.log_path, msg=f'File validation Error: {e}')
            return False

    def display_text(self):
        try:
            with open(self.file_path, 'r') as file:
                data = file.read()
                self.tab = Frame(self.app.notebook, height=350)
                tab_scrollbar = Scrollbar(self.tab, orient=VERTICAL)
                tab_scrollbar.pack(side=LEFT, fill=Y)
                tab_textbox = Text(self.tab, yscrollcommand=tab_scrollbar.set)
                tab_textbox.pack(fill=BOTH)
                self.app.notebook.add(self.tab, text=f"SysInfo {self.endpoint.ident}")
                tab_scrollbar.configure(command=tab_textbox.yview)
                tab_textbox.config(state=NORMAL)
                tab_textbox.delete(1.0, END)
                tab_textbox.insert(END, data)
                tab_textbox.config(state=DISABLED)
                self.app.notebook.select(self.tab)
                self.app.tabs += 1

        except ValueError:
            print("something is wrong in display_text")
            sys.exit(1)

    def run(self):
        self.app.refresh_btn.config(state=DISABLED)
        self.app.connected_table.unbind("<Button-1>")
        self.app.connected_table.configure(selectmode='none')
        self.app.disable_buttons_thread()
        self.app.running = True

        self.app.update_statusbar_messages_thread(msg=f'waiting for system information from '
                                                  f'{self.endpoint.ip} | {self.endpoint.ident}...')

        self.make_dir()
        self.get_file_name()
        self.get_file_size()
        self.get_file_content()
        self.confirm()
        self.file_validation()
        self.display_text()

        self.app.enable_buttons_thread()
        self.app.update_statusbar_messages_thread(msg=f'system information file received from '
                                                  f'{self.endpoint.ip} | {self.endpoint.ident}.')

        self.app.refresh_btn.configure(state=NORMAL)
        self.app.connected_table.bind("<Button-1>", self.app.select_item)
        self.app.connected_table.configure(selectmode='browse')


def logIt_thread(log_path=None, debug=False, msg='') -> None:
    logit_thread = Thread(target=logIt,
                          args=(log_path, debug, msg),
                          daemon=True,
                          name="Log Thread")
    logit_thread.start()


def bytes_to_number(b: int) -> int:
    dt = get_date()
    res = 0
    for i in range(4):
        res += b[i] << (i * 8)
    return res


def get_date() -> str:
    d = datetime.now().replace(microsecond=0)
    dt = str(d.strftime("%d/%b/%y %H:%M:%S"))

    return dt


def logIt(logfile=None, debug=None, msg='') -> bool:
    dt = get_date()
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
