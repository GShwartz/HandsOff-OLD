from tkinter import messagebox, simpledialog
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

    def display_text(self):
        with open(self.filenameRecv, 'r') as file:
            data = file.read()
            self.tab = Frame(self.app.notebook, height=350)
            tab_scrollbar = Scrollbar(self.tab, orient=VERTICAL)
            tab_scrollbar.pack(side=LEFT, fill=Y)
            tab_textbox = Text(self.tab, yscrollcommand=tab_scrollbar.set)
            tab_textbox.pack(fill=BOTH)
            self.app.notebook.add(self.tab, text=f"Tasks {self.endpoint.ident}")
            tab_scrollbar.configure(command=tab_textbox.yview)
            tab_textbox.config(state=NORMAL)
            tab_textbox.delete(1.0, END)
            tab_textbox.insert(END, data)
            tab_textbox.config(state=DISABLED)
            self.app.notebook.select(self.tab)
            self.app.tabs += 1

    def what_task(self) -> str:
        logIt_thread(self.log_path, msg=f'Waiting for task name...')
        taskkill = simpledialog.askstring(parent=self.app, title='Task To Kill', prompt="Task to kill\t\t\t\t")
        logIt_thread(self.log_path, msg=f'Task Name: {taskkill}.')
        if taskkill is None:
            try:
                logIt_thread(self.log_path, msg=f'Sending "n" to {self.endpoint.ip}...')
                self.endpoint.conn.send('n'.encode())
                logIt_thread(self.log_path, msg=f'Send completed.')
                logIt_thread(self.log_path, msg=f'Calling self.enable_buttons_thread()...')
                self.app.enable_buttons_thread()
                logIt_thread(self.log_path, msg=f'Displaying warning popup window..')
                messagebox.showwarning(f"From {self.endpoint.ip} | {self.endpoint.ident}",
                                       "Task Kill canceled.\t\t\t\t\t\t\t\t")
                logIt_thread(self.log_path, msg=f'Warning received.')
                return False

            except (WindowsError, socket.error) as e:
                logIt_thread(self.log_path, msg=f'Error: {e}.')
                self.app.update_statusbar_messages_thread(msg=f"{e}")
                logIt_thread(self.log_path, msg=f'Calling self.remove_lost_connection({self.endpoint})...')
                self.app.remove_lost_connection(self.endpoint)
                logIt_thread(self.log_path, msg=f'Calling self.enable_buttons_thread()...')
                self.app.enable_buttons_thread()
                return False

        if len(taskkill) == 0:
            try:
                logIt_thread(self.log_path, msg=f'Sending "n" to {self.endpoint.ip}...')
                self.endpoint.conn.send('n'.encode())
                logIt_thread(self.log_path, msg=f'Send completed.')
                logIt_thread(self.log_path, msg=f'Calling self.enable_buttons_thread()...')
                self.app.enable_buttons_thread()
                logIt_thread(self.log_path, msg=f'Displaying warning popup window...')
                messagebox.showwarning(f"From {self.endpoint.ip} | {self.endpoint.ident}", "Task Kill canceled.\t\t\t\t\t\t\t\t")
                return False

            except (WindowsError, socket.error) as e:
                logIt_thread(self.log_path, msg=f'Error: {e}.')
                self.app.update_statusbar_messages_thread(msg=f"{e}")
                logIt_thread(self.log_path, msg=f'Calling self.remove_lost_connection({self.endpoint.ip})...')
                self.app.remove_lost_connection(self.endpoint)
                logIt_thread(self.log_path, msg=f'Calling self.enable_buttons_thread()...')
                self.app.enable_buttons_thread()
                return False

        if not str(taskkill).endswith('.exe'):
            try:
                logIt_thread(self.log_path, msg=f'Calling sysinfo.run()...')
                self.endpoint.conn.send('n'.encode())
                logIt_thread(self.log_path, msg=f'Send completed.')
                logIt_thread(self.log_path, msg=f'Calling self.enable_buttons_thread()...')
                self.app.enable_buttons_thread()
                logIt_thread(self.log_path, msg=f'Displaying warning popup window...')
                messagebox.showwarning(f"From {self.endpoint.ip} | {self.endpoint.ident}",
                                       "Task Kill canceled.\t\t\t\t\t\t\t\t")
                return False

            except (WindowsError, socket.error) as e:
                logIt_thread(self.log_path, msg=f'Error: {e}.')
                self.app.update_statusbar_messages_thread(msg=f"{e}")
                logIt_thread(self.log_path, msg=f'Calling self.remove_lost_connection({self.endpoint})...')
                self.app.remove_lost_connection(self.endpoint)
                return False

        logIt_thread(self.log_path, msg=f'Calling self.enable_buttons_thread()...')
        self.app.enable_buttons_thread()
        return taskkill

    def kill_task(self):
        try:
            logIt_thread(self.log_path, msg=f'Sending kill command to {self.endpoint.ip}.')
            self.endpoint.conn.send('kill'.encode())
            logIt_thread(self.log_path, msg=f'Send complete.')

        except (WindowsError, socket.error) as e:
            logIt_thread(self.log_path, msg=f'Error: {e}.')
            self.app.update_statusbar_messages_thread(msg=f'{e}.')
            logIt_thread(self.log_path, msg=f'Calling self.remove_lost_connection({self.endpoint})')
            self.app.remove_lost_connection(self.endpoint)
            return False

        try:
            logIt_thread(self.log_path, msg=f'Sending {self.task_to_kill} to {self.endpoint.ip}...')
            self.endpoint.conn.send(self.task_to_kill.encode())
            logIt_thread(self.log_path, msg=f'Send complete.')

        except (WindowsError, socket.error) as e:
            logIt_thread(self.log_path, msg=f'Error: {e}.')
            self.app.update_statusbar_messages_thread(msg=f'{e}.')
            logIt_thread(self.log_path, msg=f'Calling self.remove_lost_connection({self.endpoint})')
            self.app.remove_lost_connection(self.endpoint)
            return False

        try:
            logIt_thread(self.log_path, msg=f'Waiting for confirmation from {self.endpoint.ip}...')
            msg = self.endpoint.conn.recv(1024).decode()
            logIt_thread(self.log_path, msg=f'{self.endpoint.ip}: {msg}')

        except (WindowsError, socket.error) as e:
            logIt_thread(self.log_path, msg=f'Error: {e}.')
            self.app.update_statusbar_messages_thread(msg=f'{e}.')
            logIt_thread(self.log_path, msg=f'Calling self.remove_lost_connection({self.endpoint})')
            self.app.remove_lost_connection(self.endpoint)
            return False

        logIt_thread(self.log_path, msg=f'Displaying {msg} in popup window...')
        messagebox.showinfo(f"From {self.endpoint.ip} | {self.endpoint.ident}", f"{msg}.\t\t\t\t\t\t\t\t")
        logIt_thread(self.log_path, msg=f'Message received.')
        self.app.update_statusbar_messages_thread(msg=f'killed task '
                                                  f'{self.task_to_kill} on {self.endpoint.ip} | {self.endpoint.ident}.')
        logIt_thread(self.log_path, msg=f'Calling self.enable_buttons_thread()...')
        self.app.enable_buttons_thread()
        return True

    def post_run(self):
        logIt_thread(self.log_path, msg=f'Displaying popup to kill a task...')
        self.killTask = messagebox.askyesno(f"Tasks from {self.endpoint.ip} | {self.endpoint.ident}", "Kill Task?\t\t\t\t\t\t\t\t")
        logIt_thread(self.log_path, msg=f'Kill task: {self.killTask}.')
        if self.killTask:
            logIt_thread(self.log_path, msg=f'Calling what_task({self.filepath})')
            self.task_to_kill = self.what_task()
            if str(self.task_to_kill) == '' or str(self.task_to_kill).startswith(' '):
                logIt_thread(self.log_path, msg=f'task_to_kill: {self.task_to_kill}')
                logIt_thread(self.log_path, msg=f'Calling self.enable_buttons_thread()...')
                self.app.enable_buttons_thread()
                return False

            if not self.task_to_kill:
                logIt_thread(self.log_path, msg=f'Calling self.enable_buttons_thread()...')
                self.app.enable_buttons_thread()
                return False

            logIt_thread(self.log_path, msg=f'Displaying popup for kill confirmation...')
            confirmKill = messagebox.askyesno(f'Kill task: {self.task_to_kill} on {self.endpoint.ident}',
                                              f'Are you sure you want to kill {self.task_to_kill}?')
            logIt_thread(self.log_path, msg=f'Kill confirmation: {confirmKill}.')
            if confirmKill:
                logIt_thread(self.log_path, msg=f'Calling kill_task({self.task_to_kill})...')
                self.kill_task()

            else:
                try:
                    logIt_thread(self.log_path, msg=f'Sending pass command to {self.endpoint.ip}.')
                    self.endpoint.conn.send('pass'.encode())
                    logIt_thread(self.log_path, msg=f'Send completed.')
                    return False

                except (WindowsError, socket.error) as e:
                    logIt_thread(self.log_path, msg=f'Error: {e}')
                    self.app.update_statusbar_messages_thread(msg=f'{e}.')
                    logIt_thread(self.log_path, msg=f'Calling self.remove_lost_connection({self.endpoint})...')
                    self.app.server.remove_lost_connection(self.endpoint)
                    return False

        else:
            try:
                logIt_thread(self.log_path, msg=f'Sending "n" to {self.endpoint.ip}.')
                self.endpoint.conn.send('n'.encode())
                logIt_thread(self.log_path, msg=f'Send completed.')
                self.app.update_statusbar_messages_thread(msg=f'tasks file received from '
                                                              f'{self.endpoint.ip} | {self.endpoint.ident}.')
                logIt_thread(self.log_path, msg=f'Calling self.enable_buttons_thread()...')
                return True

            except (WindowsError, socket.error) as e:
                logIt_thread(self.log_path, msg=f'Error: {e}.')
                self.app.update_statusbar_messages_thread(msg=f'{e}.')
                logIt_thread(self.log_path, msg=f'Calling self.remove_lost_connection({self.endpoint})...')
                self.app.remove_lost_connection(self.endpoint)
                return False

    def get_file_name(self):
        logIt_thread(self.log_path, msg=f'Waiting for filename from {self.endpoint.ip}...')
        self.endpoint.conn.settimeout(10)
        self.filenameRecv = self.endpoint.conn.recv(1024).decode()
        self.endpoint.conn.settimeout(None)
        logIt_thread(self.log_path, msg=f'Filename: {self.filenameRecv}.')

    def get_file_size(self):
        logIt_thread(self.log_path, msg=f'Waiting for file size from {self.endpoint.ip}...')
        self.endpoint.conn.settimeout(10)
        self.size = self.endpoint.conn.recv(4)
        self.endpoint.conn.settimeout(None)
        logIt_thread(self.log_path, msg=f'Size: {self.size}.')
        logIt_thread(self.log_path, msg=f'Converting size bytes to numbers...')
        self.size = bytes_to_number(self.size)

    def get_file_content(self):
        current_size = 0
        buffer = b""

        logIt_thread(self.log_path, msg=f'Writing content to {self.filenameRecv}...')
        with open(self.filenameRecv, 'wb') as tsk_file:
            self.endpoint.conn.settimeout(60)
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
            self.endpoint.conn.settimeout(None)

    def confirm(self):
        logIt_thread(self.log_path, msg=f'Sending confirmation to {self.endpoint.ip}...')
        self.endpoint.conn.send(f"Received file: {self.filenameRecv}\n".encode())
        logIt_thread(self.log_path, msg=f'Send complete.')

        logIt_thread(self.log_path, msg=f'Waiting for closer from {self.endpoint.ip}...')
        self.endpoint.conn.settimeout(10)
        msg = self.endpoint.conn.recv(1024).decode()
        self.endpoint.conn.settimeout(None)
        logIt_thread(self.log_path, msg=f'{self.endpoint.ip}: {msg}')

    def move(self):
        src = os.path.abspath(self.filenameRecv)
        dst = fr"{self.path}\{self.endpoint.ident}"

        logIt_thread(self.log_path, msg=f'Moving {src} to {dst}...')
        try:
            shutil.move(src, dst)

        except FileExistsError:
            pass

    def run(self):
        self.app.running = True
        self.app.disable_buttons_thread()
        self.filepath = os.path.join(self.path, self.endpoint.ident)
        try:
            os.makedirs(self.filepath)

        except FileExistsError:
            logIt_thread(self.log_path, msg=f'Passing FileExistsError...')
            pass

        try:
            logIt_thread(self.log_path, msg=f'Sending tasks command to {self.endpoint.ip}...')
            self.endpoint.conn.send('tasks'.encode())
            logIt_thread(self.log_path, msg=f'Send complete.')

        except (WindowsError, socket.error) as e:
            logIt_thread(self.log_path, msg=f'Error: {e}')
            self.app.remove_lost_connection(self.endpoint)
            return False

        self.get_file_name()
        self.get_file_size()
        self.get_file_content()
        self.confirm()
        self.display_text()
        self.move()
        self.post_run()
        self.app.running = False
        self.app.enable_buttons_thread()


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
    dt = str(d.strftime("%m/%d/%Y %H:%M:%S"))

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
