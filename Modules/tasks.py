from tkinter import messagebox, simpledialog
from Modules.logger import init_logger
from datetime import datetime
from threading import Thread
from tkinter import *
import shutil
import socket
import os


class Tasks:
    def __init__(self, endpoint, app, path, log_path):
        self.endpoint = endpoint
        self.app = app
        self.path = path
        self.log_path = log_path
        self.logger = init_logger(self.log_path, __name__)

    def bytes_to_number(self, b: int) -> int:
        res = 0
        for i in range(4):
            res += b[i] << (i * 8)
        return res

    def display_text(self):
        self.logger.info(f"Running display_text...")
        self.logger.debug(f"Reading {self.filenameRecv}...")
        with open(self.filenameRecv, 'r') as file:
            data = file.read()
            self.tab = Frame(self.app.notebook, height=350)
            tab_scrollbar = Scrollbar(self.tab, orient=VERTICAL)
            tab_scrollbar.pack(side=LEFT, fill=Y)
            tab_textbox = Text(self.tab, yscrollcommand=tab_scrollbar.set)
            tab_textbox.pack(fill=BOTH)
            self.logger.debug(f"Adding tab: Tasks {self.endpoint.ident}...")
            self.app.notebook.add(self.tab, text=f"Tasks {self.endpoint.ident}")
            tab_scrollbar.configure(command=tab_textbox.yview)
            tab_textbox.config(state=NORMAL)
            tab_textbox.delete(1.0, END)
            tab_textbox.insert(END, data)
            tab_textbox.config(state=DISABLED)
            self.logger.debug(f"Displaying tasks tab...")
            self.app.notebook.select(self.tab)
            self.logger.debug(f"Updating tabs list...")
            self.app.tabs += 1
            self.logger.info(f"display_text completed.")

    def what_task(self) -> str:
        self.logger.info(f"Running what_task...")
        self.logger.debug(f"Waiting for task name...")
        taskkill = simpledialog.askstring(parent=self.app, title='Task To Kill', prompt="Task to kill\t\t\t\t")
        self.logger.debug(f"Task Name: {taskkill}")
        if taskkill is None:
            try:
                self.logger.debug(f"Sending 'n' to {self.endpoint.ip}...")
                self.endpoint.conn.send('n'.encode())
                self.logger.debug(f"Calling app.enable_buttons_thread...")
                self.app.enable_buttons_thread()
                self.logger.debug(f"Displaying warning popup window...")
                messagebox.showwarning(f"From {self.endpoint.ip} | {self.endpoint.ident}",
                                       "Task Kill canceled.\t\t\t\t\t\t\t\t")
                return False

            except (WindowsError, socket.error) as e:
                self.logger.debug(f"Error: {e}")
                self.logger.debug(f"Updating statusbar message...")
                self.app.update_statusbar_messages_thread(msg=f"{e}")
                self.logger.debug(f"Calling app.remove_lost_connection({self.endpoint})...")
                self.app.remove_lost_connection(self.endpoint)
                self.logger.debug(f"Calling app.enable_buttons_thread...")
                self.app.enable_buttons_thread()
                return False

        if not taskkill:
            try:
                self.logger.debug(f"Sending 'n' to {self.endpoint.ip}...")
                self.endpoint.conn.send('n'.encode())
                self.logger.debug(f"Calling app.enable_buttons_thread...")
                self.app.enable_buttons_thread()
                self.logger.debug(f"Displaying warning popup window...")
                messagebox.showwarning(f"From {self.endpoint.ip} | {self.endpoint.ident}", "Task Kill canceled.\t\t\t\t\t\t\t\t")
                return False

            except (WindowsError, socket.error) as e:
                self.logger.debug(f"Error: {e}")
                self.logger.debug(f"Updating statusbar message...")
                self.app.update_statusbar_messages_thread(msg=f"{e}")
                self.logger.debug(f"Calling app.remove_lost_connection({self.endpoint})...")
                self.app.remove_lost_connection(self.endpoint)
                self.logger.debug(f"Calling app.enable_buttons_thread...")
                self.app.enable_buttons_thread()
                return False

        if not str(taskkill).endswith('.exe'):
            try:
                self.logger.debug(f"Sending 'n' to {self.endpoint.ip}...")
                self.endpoint.conn.send('n'.encode())
                self.logger.debug(f"Calling app.enable_buttons_thread...")
                self.app.enable_buttons_thread()
                self.logger.debug(f"Displaying warning popup window...")
                self.logger.debug(f"Updating statusbar message...")
                messagebox.showwarning(f"From {self.endpoint.ip} | {self.endpoint.ident}",
                                       "Task Kill canceled.\t\t\t\t\t\t\t\t")
                return False

            except (WindowsError, socket.error) as e:
                self.logger.debug(f"Error: {e}")
                self.logger.debug(f"Updating statusbar message...")
                self.app.update_statusbar_messages_thread(msg=f"{e}")
                self.logger.debug(f"Calling app.remove_lost_connection({self.endpoint})...")
                self.app.remove_lost_connection(self.endpoint)
                self.logger.debug(f"Calling app.enable_buttons_thread...")
                self.app.enable_buttons_thread()
                return False

        self.logger.debug(f"Calling enable_buttons_thread...")
        self.app.enable_buttons_thread()
        return taskkill

    def kill_task(self):
        self.logger.debug(f"Running kill_task...")
        try:
            self.logger.debug(f"Sending kill command to {self.endpoint.ip}...")
            self.endpoint.conn.send('kill'.encode())

        except (WindowsError, socket.error) as e:
            self.logger.debug(f"Error: {e}")
            self.logger.debug(f"Updating statusbar message...")
            self.app.update_statusbar_messages_thread(msg=f"{e}")
            self.logger.debug(f"Calling app.remove_lost_connection({self.endpoint})...")
            self.app.remove_lost_connection(self.endpoint)
            self.logger.debug(f"Calling app.enable_buttons_thread...")
            self.app.enable_buttons_thread()
            return False

        try:
            self.logger.debug(f"Sending {self.task_to_kill} to {self.endpoint.ip}...")
            self.endpoint.conn.send(self.task_to_kill.encode())

        except (WindowsError, socket.error) as e:
            self.logger.debug(f"Error: {e}")
            self.logger.debug(f"Updating statusbar message...")
            self.app.update_statusbar_messages_thread(msg=f"{e}")
            self.logger.debug(f"Calling app.remove_lost_connection({self.endpoint})...")
            self.app.remove_lost_connection(self.endpoint)
            self.logger.debug(f"Calling app.enable_buttons_thread...")
            self.app.enable_buttons_thread()
            return False

        try:
            self.logger.debug(f"Waiting for confirmation from {self.endpoint.ip}...")
            msg = self.endpoint.conn.recv(1024).decode()
            self.logger.debug(f"{self.endpoint.ip}: {msg}")

        except (WindowsError, socket.error) as e:
            self.logger.debug(f"Error: {e}")
            self.logger.debug(f"Updating statusbar message...")
            self.app.update_statusbar_messages_thread(msg=f"{e}")
            self.logger.debug(f"Calling app.remove_lost_connection({self.endpoint})...")
            self.app.remove_lost_connection(self.endpoint)
            self.logger.debug(f"Calling app.enable_buttons_thread...")
            self.app.enable_buttons_thread()
            return False

        self.logger.debug(f"Displaying {msg} in popup window...")
        messagebox.showinfo(f"From {self.endpoint.ip} | {self.endpoint.ident}", f"{msg}.\t\t\t\t\t\t\t\t")
        self.logger.debug(f"Updating statusbar message...")
        self.app.update_statusbar_messages_thread(msg=f'killed task '
                                                  f'{self.task_to_kill} on {self.endpoint.ip} | {self.endpoint.ident}.')
        self.logger.debug(f"Calling app.enable_buttons_thread...")
        self.app.enable_buttons_thread()
        return True

    def post_run(self):
        self.logger.info(f"Running post_run...")
        self.logger.debug(f"Displaying kill task pop-up...")
        self.killTask = messagebox.askyesno(f"Tasks from {self.endpoint.ip} | {self.endpoint.ident}", "Kill Task?\t\t\t\t\t\t\t\t")
        self.logger.debug(f"Kill task: {self.killTask}")
        if self.killTask:
            self.logger.debug(f"Calling what_task({self.filepath})...")
            self.task_to_kill = self.what_task()
            if str(self.task_to_kill) == '' or str(self.task_to_kill).startswith(' '):
                self.logger.debug(f"task_to_kill: {self.task_to_kill}")
                self.logger.debug(f"Calling app.enable_buttons_thread...")
                self.app.enable_buttons_thread()
                return False

            if not self.task_to_kill:
                self.logger.debug(f"Calling app.enable_buttons_thread...")
                self.app.enable_buttons_thread()
                self.logger.info(f"post_run completed.")
                return False

            self.logger.debug(f"Displaying kill confirmation pop-up...")
            confirmKill = messagebox.askyesno(f'Kill task: {self.task_to_kill} on {self.endpoint.ident}',
                                              f'Are you sure you want to kill {self.task_to_kill}?')
            self.logger.debug(f"Kill confirmation: {confirmKill}")
            if confirmKill:
                self.logger.debug(f"Calling kill_task({self.task_to_kill})...")
                self.kill_task()

            else:
                try:
                    self.logger.debug(f"Sending pass command to {self.endpoint.ip}...")
                    self.endpoint.conn.send('pass'.encode())
                    return False

                except (WindowsError, socket.error) as e:
                    self.logger.debug(f"Error: {e}")
                    self.logger.debug(f"Updating statusbar message...")
                    self.app.update_statusbar_messages_thread(msg=f"{e}")
                    self.logger.debug(f"Calling app.remove_lost_connection({self.endpoint})...")
                    self.app.remove_lost_connection(self.endpoint)
                    self.logger.debug(f"Calling app.enable_buttons_thread...")
                    self.app.enable_buttons_thread()
                    return False

        else:
            try:
                self.logger.debug(f"Sending 'n' to {self.endpoint.ip}...")
                self.endpoint.conn.send('n'.encode())
                self.logger.debug(f"Updating statusbar message...")
                self.app.update_statusbar_messages_thread(msg=f'tasks file received from '
                                                              f'{self.endpoint.ip} | {self.endpoint.ident}.')
                self.logger.info(f"post_run completed.")
                return True

            except (WindowsError, socket.error) as e:
                self.logger.debug(f"Error: {e}")
                self.logger.debug(f"Updating statusbar message...")
                self.app.update_statusbar_messages_thread(msg=f"{e}")
                self.logger.debug(f"Calling app.remove_lost_connection({self.endpoint})...")
                self.app.remove_lost_connection(self.endpoint)
                self.logger.debug(f"Calling app.enable_buttons_thread...")
                self.app.enable_buttons_thread()
                return False

    def get_file_name(self):
        self.logger.info(f"Running get_file_name...")
        self.logger.debug(f"Waiting for filename from {self.endpoint.ip}...")
        self.endpoint.conn.settimeout(10)
        self.filenameRecv = self.endpoint.conn.recv(1024).decode()
        self.endpoint.conn.settimeout(None)
        self.logger.debug(f"Filename: {self.filenameRecv}")

    def get_file_size(self):
        self.logger.info(f"Running get_file_size...")
        self.logger.debug(f"Waiting for file size from {self.endpoint.ip}...")
        self.endpoint.conn.settimeout(10)
        self.size = self.endpoint.conn.recv(4)
        self.endpoint.conn.settimeout(None)
        self.size = self.bytes_to_number(self.size)
        self.logger.debug(f"Size: {self.size}")

    def get_file_content(self):
        self.logger.info(f"Running get_file_content...")

        current_size = 0
        buffer = b""

        self.logger.debug(f"Writing content to {self.filenameRecv}...")
        with open(self.filenameRecv, 'wb') as tsk_file:
            self.endpoint.conn.settimeout(60)
            while current_size < self.size:
                data = self.endpoint.conn.recv(1024)
                if not data:
                    break

                if len(data) + current_size > self.size:
                    data = data[:self.size - current_size]

                buffer += data
                current_size += len(data)
                tsk_file.write(data)
            self.endpoint.conn.settimeout(None)

    def confirm(self):
        self.logger.info(f"Running confirm...")
        self.logger.debug(f"Sending confirmation to {self.endpoint.ip}...")
        self.endpoint.conn.send(f"Received file: {self.filenameRecv}\n".encode())
        self.endpoint.conn.settimeout(10)
        msg = self.endpoint.conn.recv(1024).decode()
        self.endpoint.conn.settimeout(None)
        self.logger.debug(f"{self.endpoint.ip}: {msg}")

    def move(self):
        self.logger.info(f"Running move...")
        src = os.path.abspath(self.filenameRecv)
        dst = fr"{self.path}\{self.endpoint.ident}"

        self.logger.debug(f"Moving {src} to {dst}...")
        try:
            shutil.move(src, dst)

        except FileExistsError:
            pass

    def run(self):
        self.logger.info(f"Running run...")
        self.app.running = True
        self.app.disable_buttons_thread()
        self.filepath = os.path.join(self.path, self.endpoint.ident)
        try:
            os.makedirs(self.filepath)

        except FileExistsError:
            self.logger.debug(f"{self.filepath} exists.")
            pass

        try:
            self.logger.debug(f"Sending tasks command to {self.endpoint.ip}...")
            self.endpoint.conn.send('tasks'.encode())

        except (WindowsError, socket.error) as e:
            self.logger.debug(f"Error: {e}")
            self.logger.debug(f"Calling app.remove_lost_connection({self.endpoint})")
            self.app.remove_lost_connection(self.endpoint)
            return False

        self.logger.debug(f"Calling get_file_name...")
        self.get_file_name()
        self.logger.debug(f"Calling get_file_size...")
        self.get_file_size()
        self.logger.debug(f"Calling get_file_content...")
        self.get_file_content()
        self.logger.debug(f"Calling confirm...")
        self.confirm()
        self.logger.debug(f"Calling display_text...")
        self.display_text()
        self.logger.debug(f"Calling move...")
        self.move()
        self.logger.debug(f"Calling post_run...")
        self.post_run()
        self.logger.debug(f"Calling app.enable_buttons_thread...")
        self.app.enable_buttons_thread()
        self.logger.info(f"run completed.")
