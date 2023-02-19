from Modules.logger import init_logger
from datetime import datetime
from threading import Thread
from tkinter import *
import socket
import sys
import os


class Sysinfo:
    def __init__(self, endpoint, app, path, log_path):
        self.app = app
        self.endpoint = endpoint
        self.app_path = path
        self.log_path = log_path
        self.path = os.path.join(self.app_path, self.endpoint.ident)
        self.logger = init_logger(self.log_path, __name__)

    def bytes_to_number(self, b: int) -> int:
        res = 0
        for i in range(4):
            res += b[i] << (i * 8)
        return res

    def make_dir(self):
        try:
            os.makedirs(self.path)

        except FileExistsError:
            self.logger.debug(f"{self.path} exists.")
            pass

    def get_file_name(self):
        try:
            self.logger.debug(f"Sending si command to {self.endpoint.conn}...")
            self.endpoint.conn.send('si'.encode())
            self.logger.debug(f"Waiting for filename from {self.endpoint.conn}...")
            self.filename = self.endpoint.conn.recv(1024).decode()
            self.logger.debug(f"Sending confirmation to {self.endpoint.conn}...")
            self.endpoint.conn.send("OK".encode())
            self.logger.debug(f"{self.endpoint.ip}: {self.filename}")
            self.file_path = os.path.join(self.path, self.filename)
            self.logger.debug(f"File path: {self.file_path}")

        except (WindowsError, socket.error) as e:
            self.logger.debug(f"Connection error: {e}")
            self.logger.debug(f"app.remove_lost_connection({self.endpoint})...")
            self.app.remove_lost_connection(self.endpoint)
            return False

    def get_file_size(self):
        try:
            self.logger.debug(f"Waiting for filesize from {self.endpoint.ip}...")
            self.size = self.endpoint.conn.recv(4)
            self.logger.debug(f"Sending confirmation to {self.endpoint.ip}...")
            self.endpoint.conn.send("OK".encode())
            self.size = self.bytes_to_number(self.size)
            self.logger.debug(f"File size: {self.size}")

        except (WindowsError, socket.error) as e:
            self.logger.debug(f"Connection error: {e}")
            self.logger.debug(f"app.remove_lost_connection({self.endpoint})...")
            self.app.remove_lost_connection(self.endpoint)
            return False

    def get_file_content(self):
        current_size = 0
        buffer = b""
        try:
            self.logger.debug(f"Receiving file content from {self.endpoint.ip}...")
            with open(self.file_path, 'wb') as tsk_file:
                while current_size < self.size:
                    data = self.endpoint.conn.recv(1024)
                    if not data:
                        break

                    if len(data) + current_size > self.size:
                        data = data[:self.size - current_size]

                    buffer += data
                    current_size += len(data)
                    tsk_file.write(data)

        except (WindowsError, socket.error) as e:
            self.logger.debug(f"Connection error: {e}")
            self.logger.debug(f"app.remove_lost_connection({self.endpoint})...")
            self.app.remove_lost_connection(self.endpoint)
            return False

    def confirm(self):
        try:
            self.logger.debug(f"Sending confirmation to {self.endpoint.ip}...")
            self.endpoint.conn.send(f"Received file: {self.filename}\n".encode())

        except (WindowsError, socket.error) as e:
            self.logger.debug(f"Connection error: {e}")
            self.logger.debug(f"app.remove_lost_connection({self.endpoint})...")
            self.app.remove_lost_connection(self.endpoint)
            return False

    def file_validation(self):
        try:
            self.logger.debug(f"Running validation on {self.file_path}...")
            with open(self.file_path, 'r') as file:
                data = file.read()

        except Exception as e:
            self.logger.debug(f"File validation Error: {e}")
            return False

    def display_text(self):
        self.logger.info(f"Running display_text...")
        try:
            self.logger.debug(f"Opening {self.file_path}...")
            with open(self.file_path, 'r') as file:
                data = file.read()
                self.tab = Frame(self.app.notebook, height=350)
                tab_scrollbar = Scrollbar(self.tab, orient=VERTICAL)
                tab_scrollbar.pack(side=LEFT, fill=Y)
                tab_textbox = Text(self.tab, yscrollcommand=tab_scrollbar.set)
                tab_textbox.pack(fill=BOTH)
                self.logger.debug(f"Defining notebook: SysInfo {self.endpoint.ident}...")
                self.app.notebook.add(self.tab, text=f"SysInfo {self.endpoint.ident}")
                tab_scrollbar.configure(command=tab_textbox.yview)
                tab_textbox.config(state=NORMAL)
                tab_textbox.delete(1.0, END)
                tab_textbox.insert(END, data)
                tab_textbox.config(state=DISABLED)
                self.logger.debug(f"Displaying tab in notebook...")
                self.app.notebook.select(self.tab)
                self.logger.debug(f"Updating tabs list...")
                self.app.tabs += 1
                self.logger.info(f"display_text completed.")

        except Exception as e:
            self.logger.debug(f"Display Error: {e}")
            return False

    def run(self):
        self.logger.info(f"Running Sysinfo...")
        self.logger.debug(f"Disabling the refresh button...")
        self.app.refresh_btn.config(state=DISABLED)
        self.logger.debug(f"Unbinding mouse clicks and selections from connected table...")
        self.app.connected_table.unbind("<Button-1>")
        self.app.connected_table.configure(selectmode='none')
        self.logger.debug(f"Calling app.disable_buttons_thread...")
        self.app.disable_buttons_thread()
        self.logger.debug(f"Updating statusbar message...")
        self.app.update_statusbar_messages_thread(msg=f'waiting for system information from '
                                                  f'{self.endpoint.ip} | {self.endpoint.ident}...')

        self.logger.debug(f"Calling make_dir...")
        self.make_dir()
        self.logger.debug(f"Calling get_file_name...")
        self.get_file_name()
        self.logger.debug(f"Calling get_file_size...")
        self.get_file_size()
        self.logger.debug(f"Calling get_file_content...")
        self.get_file_content()
        self.logger.debug(f"Calling confirm...")
        self.confirm()
        self.logger.debug(f"Calling file_validation...")
        self.file_validation()
        self.logger.debug(f"Calling display_text...")
        self.display_text()
        self.logger.debug(f"Calling app.enable_buttons_thread...")
        self.app.enable_buttons_thread()
        self.logger.debug(f"Updating statusbar message...")
        self.app.update_statusbar_messages_thread(msg=f'system information file received from '
                                                  f'{self.endpoint.ip} | {self.endpoint.ident}.')
        self.logger.debug(f"Enabling the refresh button...")
        self.app.refresh_btn.configure(state=NORMAL)
        self.logger.debug(f"Binding mouse click and selection to connected table...")
        self.app.connected_table.bind("<Button-1>", self.app.select_item)
        self.app.connected_table.configure(selectmode='browse')
        self.logger.info(f"Sysinfo completed.")
