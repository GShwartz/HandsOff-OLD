from datetime import datetime
from threading import Thread
from typing import Optional
import PIL.ImageTk
import subprocess
import webbrowser
import threading
import PIL.Image
import argparse
import pystray
import os.path
import socket
import psutil
import shutil
import time
import glob
import sys
import csv
import cv2

# GUI
from tkinter import simpledialog
from tkinter import filedialog
from tkinter import messagebox
from tkinter import ttk
from tkinter import *
import tkinter as tk
import tkinter

# Local Modules
from Modules.server import Server
from Modules import vital_signs
from Modules import freestyle
from Modules import sysinfo


class About:
    def __init__(self):
        # Build GUI
        self.about_window = tk.Toplevel()
        self.about_window.title("HandsOff - About")
        self.about_window.iconbitmap('HandsOff.ico')

        # Update screen geometry variables
        app.update_idletasks()

        # Set Mid Screen Coordinates
        x = (app.WIDTH / 2) - (400 / 2)
        y = (app.HEIGHT / 2) - (200 / 2)

        # Set Window Size & Location & Center Window
        self.about_window.geometry(f'{400}x{200}+{int(x)}+{int(y)}')
        self.about_window.configure(background='slate gray', takefocus=True)
        self.about_window.grid_columnconfigure(2, weight=1)
        self.about_window.grid_rowconfigure(3, weight=1)
        self.about_window.maxsize(400, 200)
        self.about_window.minsize(400, 200)

        self.github_url = 'https://github.com/GShwartz/PeachGUI'
        self.youtube_url = 'https://www.youtube.com/channel/UC5jHVur21yVo7nu7nLnuyoQ'
        self.linkedIn_url = 'https://www.linkedin.com/in/gilshwartz/'

        self.github_black = PIL.ImageTk.PhotoImage(
            PIL.Image.open('images/github_black.png').resize((50, 50), PIL.Image.LANCZOS))
        self.github_purple = PIL.ImageTk.PhotoImage(
            PIL.Image.open('images/github_purple.png').resize((50, 50), PIL.Image.LANCZOS))
        self.linkedin_black = PIL.ImageTk.PhotoImage(
            PIL.Image.open('images/linkedin_black.png').resize((50, 50), PIL.Image.LANCZOS))
        self.linkedin_blue = PIL.ImageTk.PhotoImage(
            PIL.Image.open('images/linkedin_blue.png').resize((50, 50), PIL.Image.LANCZOS))
        self.youtube_red = PIL.ImageTk.PhotoImage(
            PIL.Image.open('images/youtube_red.png').resize((50, 50), PIL.Image.LANCZOS))
        self.youtube_black = PIL.ImageTk.PhotoImage(
            PIL.Image.open('images/youtube_black.png').resize((50, 50), PIL.Image.LANCZOS))
        app.social_buttons.append([self.github_black, self.github_purple,
                                   self.youtube_red, self.youtube_black,
                                   self.linkedin_blue, self.linkedin_black])

    def run(self):
        self.app_name_label = Label(self.about_window, relief='ridge', background='ghost white', width=45)
        self.app_name_label.configure(text='HandsOff\n\n'
                                           'Copyright 2022 Gil Shwartz. All rights reserved.\n'
                                           'handsoffapplication@gmail.com\n'
                                           '=====----=====\n')
        self.app_name_label.pack(ipady=10, ipadx=10, pady=5)

        self.github_label = Label(self.about_window, image=self.github_purple, background='slate gray')
        self.github_label.image = [self.github_purple, self.github_black]
        self.github_label.place(x=80, y=130)
        self.github_label.bind("<Button-1>", lambda x: self.on_github_click(self.github_url))
        self.github_label.bind("<Enter>", self.on_github_hover)
        self.github_label.bind("<Leave>", self.on_github_leave)

        self.youtube_label = Label(self.about_window, image=self.youtube_red, background='slate gray')
        self.youtube_label.image = [self.youtube_red, self.youtube_black]
        self.youtube_label.place(x=173, y=130)
        self.youtube_label.bind("<Button-1>", lambda x: self.on_youtube_click(self.youtube_url))
        self.youtube_label.bind("<Enter>", self.on_youtube_hover)
        self.youtube_label.bind("<Leave>", self.on_youtube_leave)

        self.linkedIn_label = Label(self.about_window, image=self.linkedin_blue, background='slate gray')
        self.linkedIn_label.image = [self.linkedin_black, self.linkedin_blue]
        self.linkedIn_label.place(x=264, y=130)
        self.linkedIn_label.bind("<Button-1>", lambda x: self.on_youtube_click(self.linkedIn_url))
        self.linkedIn_label.bind("<Enter>", self.on_linkedIn_hover)
        self.linkedIn_label.bind("<Leave>", self.on_linkedIn_leave)

    def on_github_hover(self, event):
        return self.github_label.config(image=self.github_black)

    def on_github_leave(self, event):
        return self.github_label.config(image=self.github_purple)

    def on_youtube_hover(self, event):
        return self.youtube_label.config(image=self.youtube_black)

    def on_youtube_leave(self, event):
        return self.youtube_label.config(image=self.youtube_red)

    def on_linkedIn_hover(self, event):
        return self.linkedIn_label.config(image=self.linkedin_black)

    def on_linkedIn_leave(self, event):
        return self.linkedIn_label.config(image=self.linkedin_blue)

    def on_github_click(self, url):
        return webbrowser.open_new_tab(url)

    def on_youtube_click(self, url):
        return webbrowser.open_new_tab(url)

    def on_linkedin_click(self, url):
        return webbrowser.open_new_tab(url)


class DisplayFileContent:
    # List to hold captured screenshot images
    displayed_screenshot_files = []
    frames = []
    tabs = 0
    notebooks = {}

    def __init__(self, notebook: Frame, filepath, tab: Optional[Frame], sname, txt=''):
        self.notebook = notebook
        self.filepath = filepath
        self.tab = tab
        self.sname = sname
        self.txt = txt

        logIt_thread(log_path,
                     msg=f'Running display_file_content({filepath}, {tab}, txt="{txt}")...')

    def display_text(self):
        with open(self.filepath, 'r') as file:
            data = file.read()
            self.tab = Frame(self.notebook, height=350)
            tab_scrollbar = Scrollbar(self.tab, orient=VERTICAL)
            tab_scrollbar.pack(side=LEFT, fill=Y)
            tab_textbox = Text(self.tab, yscrollcommand=tab_scrollbar.set)
            tab_textbox.pack(fill=BOTH)
            self.notebook.add(self.tab, text=f"{self.txt} {self.sname}")
            tab_scrollbar.configure(command=tab_textbox.yview)
            tab_textbox.config(state=NORMAL)
            tab_textbox.delete(1.0, END)
            tab_textbox.insert(END, data)
            tab_textbox.config(state=DISABLED)
            self.notebook.select(self.tab)
            self.tabs += 1

    def run(self):
        self.display_text()


class Tasks:
    # List to hold captured screenshot images
    displayed_screenshot_files = []
    frames = []
    tabs = 0
    notebooks = {}

    def __init__(self, endpoint, app, notebook):
        self.endpoint = endpoint
        self.app = app
        self.notebook = notebook

    def what_task(self, filepath) -> str:
        logIt_thread(log_path, msg=f'Waiting for task name...')
        task_to_kill = simpledialog.askstring(parent=self.app, title='Task To Kill', prompt="Task to kill\t\t\t\t")
        logIt_thread(log_path, msg=f'Task Name: {task_to_kill}.')
        if task_to_kill is None:
            try:
                logIt_thread(log_path, msg=f'Sending "n" to {self.endpoint.ip}...')
                self.endpoint.conn.send('n'.encode())
                logIt_thread(log_path, msg=f'Send completed.')
                logIt_thread(log_path, msg=f'Calling self.enable_buttons_thread()...')
                self.app.enable_buttons_thread()
                logIt_thread(log_path, msg=f'Displaying warning popup window..')
                messagebox.showwarning(f"From {self.endpoint.ip} | {self.endpoint.ident}",
                                       "Task Kill canceled.\t\t\t\t\t\t\t\t")
                logIt_thread(log_path, msg=f'Warning received.')
                return False

            except (WindowsError, socket.error) as e:
                logIt_thread(log_path, msg=f'Error: {e}.')
                self.app.update_statusbar_messages_thread(msg=f"{e}")
                logIt_thread(log_path, msg=f'Calling server.remove_lost_connection('
                                           f'{self.endpoint.conn}, {self.endpoint.ip})...')
                self.app.server.remove_lost_connection(self.endpoint)
                logIt_thread(log_path, msg=f'Calling self.enable_buttons_thread()...')
                self.app.enable_buttons_thread()
                return False

        if len(task_to_kill) == 0:
            try:
                logIt_thread(log_path, msg=f'Sending "n" to {self.endpoint.ip}...')
                self.endpoint.conn.send('n'.encode())
                logIt_thread(log_path, msg=f'Send completed.')
                logIt_thread(log_path, msg=f'Calling self.enable_buttons_thread()...')
                self.app.enable_buttons_thread()
                logIt_thread(log_path, msg=f'Displaying warning popup window...')
                messagebox.showwarning(f"From {self.endpoint.ip} | {self.endpoint.ident}",
                                       "Task Kill canceled.\t\t\t\t\t\t\t\t")
                return False

            except (WindowsError, socket.error) as e:
                logIt_thread(log_path, msg=f'Error: {e}.')
                self.app.update_statusbar_messages_thread(msg=f"{e}")
                logIt_thread(log_path,
                             msg=f'Calling server.remove_lost_connection('
                                 f'{self.endpoint.conn}, {self.endpoint.ip})...')
                self.app.server.remove_lost_connection(self.endpoint)
                logIt_thread(log_path, msg=f'Calling self.enable_buttons_thread()...')
                self.app.enable_buttons_thread()
                return False

        if not str(task_to_kill).endswith('.exe'):
            try:
                logIt_thread(log_path, msg=f'Calling sysinfo.run()...')
                self.endpoint.conn.send('n'.encode())
                logIt_thread(log_path, msg=f'Send completed.')
                logIt_thread(log_path, msg=f'Calling self.enable_buttons_thread()...')
                self.app.enable_buttons_thread()
                logIt_thread(log_path, msg=f'Displaying warning popup window...')
                messagebox.showwarning(f"From {self.endpoint.ip} | {self.endpoint.ident}",
                                       "Task Kill canceled.\t\t\t\t\t\t\t\t")
                return False

            except (WindowsError, socket.error) as e:
                logIt_thread(log_path, msg=f'Error: {e}.')
                self.app.update_statusbar_messages_thread(msg=f"{e}")
                logIt_thread(log_path, msg=f'Calling server.remove_lost_connection('
                                           f'{self.endpoint.conn}, {self.endpoint.ip})...')
                server.remove_lost_connection(self.endpoint)
                return False

        logIt_thread(log_path, msg=f'Calling self.enable_buttons_thread()...')
        self.app.enable_buttons_thread()
        return task_to_kill

    def kill_task(self, task_to_kill):
        try:
            logIt_thread(log_path, msg=f'Sending kill command to {self.endpoint.ip}.')
            self.endpoint.conn.send('kill'.encode())
            logIt_thread(log_path, msg=f'Send complete.')

        except (WindowsError, socket.error) as e:
            logIt_thread(log_path, msg=f'Error: {e}.')
            self.app.update_statusbar_messages_thread(msg=f'{e}.')
            logIt_thread(log_path, msg=f'Calling server.remove_lost_connection('
                                       f'{self.endpoint.conn}, {self.endpoint.ip})')
            self.app.server.remove_lost_connection(self.endpoint)
            return False

        try:
            logIt_thread(log_path, msg=f'Sending {task_to_kill} to {self.endpoint.ip}...')
            self.endpoint.conn.send(task_to_kill.encode())
            logIt_thread(log_path, msg=f'Send complete.')

        except (WindowsError, socket.error) as e:
            logIt_thread(log_path, msg=f'Error: {e}.')
            self.app.update_statusbar_messages_thread(msg=f'{e}.')
            logIt_thread(log_path, msg=f'Calling server.remove_lost_connection('
                                       f'{self.endpoint.conn}, {self.endpoint.ip})')
            self.app.server.remove_lost_connection(self.endpoint)
            return False

        try:
            logIt_thread(log_path, msg=f'Waiting for confirmation from {self.endpoint.ip}...')
            msg = self.endpoint.conn.recv(1024).decode()
            logIt_thread(log_path, msg=f'{self.endpoint.ip}: {msg}')

        except (WindowsError, socket.error) as e:
            logIt_thread(log_path, msg=f'Error: {e}.')
            self.app.update_statusbar_messages_thread(msg=f'{e}.')
            logIt_thread(log_path, msg=f'Calling server.remove_lost_connection('
                                       f'{self.endpoint.conn}, {self.endpoint.ip})')
            self.app.server.remove_lost_connection(self.endpoint)
            return False

        logIt_thread(log_path, msg=f'Displaying {msg} in popup window...')
        messagebox.showinfo(f"From {self.endpoint.ip} | {self.endpoint.ident}", f"{msg}.\t\t\t\t\t\t\t\t")
        logIt_thread(log_path, msg=f'Message received.')
        self.app.update_statusbar_messages_thread(msg=f'killed task {task_to_kill} on '
                                                      f'{self.endpoint.ip} | {self.endpoint.ident}.')
        logIt_thread(log_path, msg=f'Calling self.enable_buttons_thread()...')
        self.app.enable_buttons_thread()
        return True

    @staticmethod
    def display_text(filename):
        with open(filename, 'r') as file:
            data = file.read()
            self.tab = Frame(self.notebook, height=350)
            tab_scrollbar = Scrollbar(self.tab, orient=VERTICAL)
            tab_scrollbar.pack(side=LEFT, fill=Y)
            tab_textbox = Text(self.tab, yscrollcommand=tab_scrollbar.set)
            tab_textbox.pack(fill=BOTH)
            self.notebook.add(self.tab, text=f"{self.txt} {self.sname}")
            tab_scrollbar.configure(command=tab_textbox.yview)
            tab_textbox.config(state=NORMAL)
            tab_textbox.delete(1.0, END)
            tab_textbox.insert(END, data)
            tab_textbox.config(state=DISABLED)
            self.notebook.select(self.tab)
            self.tabs += 1

    def run(self):
        filepath = os.path.join(path, self.endpoint.ident)
        try:
            os.makedirs(filepath)

        except FileExistsError:
            logIt_thread(log_path, msg=f'Passing FileExistsError...')
            pass

        try:
            logIt_thread(log_path, msg=f'Sending tasks command to {self.endpoint.ip}...')
            self.endpoint.conn.send('tasks'.encode())
            logIt_thread(log_path, msg=f'Send complete.')

            logIt_thread(log_path, msg=f'Waiting for filename from {self.endpoint.ip}...')
            self.endpoint.conn.settimeout(10)
            self.filenameRecv = self.endpoint.conn.recv(1024).decode()
            print(self.filenameRecv)
            self.endpoint.conn.settimeout(None)
            logIt_thread(log_path, msg=f'Filename: {self.filenameRecv}.')

            logIt_thread(log_path, msg=f'Sleeping for {0.5} seconds...')
            time.sleep(1)

            logIt_thread(log_path, msg=f'Waiting for file size from {self.endpoint.ip}...')
            self.endpoint.conn.settimeout(10)
            size = self.endpoint.conn.recv(4)
            self.endpoint.conn.settimeout(None)
            logIt_thread(log_path, msg=f'Size: {size}.')

            logIt_thread(log_path, msg=f'Converting size bytes to numbers...')
            size = bytes_to_number(size)
            print(size)
            current_size = 0
            buffer = b""

            logIt_thread(log_path, msg=f'Renaming {self.filenameRecv}...')
            self.filenameRecv = str(self.filenameRecv).strip("b'")

            logIt_thread(log_path, msg=f'Writing content to {self.filenameRecv}...')
            with open(self.filenameRecv, 'wb') as tsk_file:
                self.endpoint.conn.settimeout(60)
                while current_size < size:
                    logIt_thread(log_path, msg=f'Receiving file content from {self.endpoint.ip}...')
                    data = self.endpoint.conn.recv(1024)
                    if not data:
                        break

                    if len(data) + current_size > size:
                        data = data[:size - current_size]

                    buffer += data
                    current_size += len(data)
                    tsk_file.write(data)
                self.endpoint.conn.settimeout(None)

            logIt_thread(log_path, msg=f'Printing file content to screen...')
            with open(self.filenameRecv, 'r') as file:
                data = file.read()

            logIt_thread(log_path, msg=f'Sending confirmation to {self.endpoint.ip}...')
            self.endpoint.conn.send(f"Received file: {self.filenameRecv}\n".encode())
            logIt_thread(log_path, msg=f'Send complete.')

            logIt_thread(log_path, msg=f'Waiting for closer from {self.endpoint.ip}...')
            self.endpoint.conn.settimeout(10)
            msg = self.endpoint.conn.recv(1024).decode()
            self.endpoint.conn.settimeout(None)
            logIt_thread(log_path, msg=f'{self.endpoint.ip}: {msg}')

            # Move screenshot file to directory
            src = os.path.abspath(self.filenameRecv)
            dst = fr"{path}\{self.endpoint.ident}"
            full_path = os.path.join(dst, self.filenameRecv[11:])

            logIt_thread(log_path, msg=f'Moving {src} to {dst}...')
            try:
                shutil.move(src, dst)

            except FileExistsError:
                pass

            self.tasks_tab = Frame(self.notebook, height=330)
            self.display_text(dst)
            display = DisplayFileContent(self.notebook, dst, self.app.tasks_tab,
                                         sname=self.endpoint.ident, txt='Tasks')
            display.run()

            return dst + self.filenameRecv[11:]

        except (WindowsError, socket.error) as e:
            logIt_thread(log_path, msg=f'Error: {e}')
            return False

        # # Disable controller buttons
        # logIt_thread(log_path, msg=f'Calling self.disable_buttons_thread()...')
        # self.app.disable_buttons_thread()
        # logIt_thread(log_path, debug=False, msg=f'Initializing Module: tasks...')
        # tsks = Tasks(self.endpoint, log_path, path)
        # self.app.update_statusbar_messages_thread(msg=f'running tasks command on '
        #                                               f'{self.endpoint.ip} | {self.endpoint.ident}.')
        #
        # logIt_thread(log_path, debug=False, msg=f'Calling tasks.tasks()...')
        # filepath = tsks.run()
        # logIt_thread(log_path, msg=f'filepath: {filepath}')
        #
        # logIt_thread(log_path,
        #              msg=f'Calling Display_file_content({self.notebook}, {None}, {filepath}, {self.app.tasks_tab},'
        #                  f'sname={self.endpoint.ident}, txt="Tasks")...')
        # display = DisplayFileContent(self.notebook, filepath, self.app.tasks_tab,
        #                              sname=self.endpoint.ident, txt='Tasks')
        # display.run()
        #
        # logIt_thread(log_path, msg=f'Displaying popup to kill a task...')
        # killTask = messagebox.askyesno(f"Tasks from {self.endpoint.ip} | {self.endpoint.ident}",
        #                                "Kill Task?\t\t\t\t\t\t\t\t")
        # logIt_thread(log_path, msg=f'Kill task: {killTask}.')
        #
        # if killTask:
        #     logIt_thread(log_path, msg=f'Calling what_task({filepath})')
        #     task_to_kill = self.what_task(filepath)
        #     if str(task_to_kill) == '' or str(task_to_kill).startswith(' '):
        #         logIt_thread(log_path, msg=f'task_to_kill: {task_to_kill}')
        #         logIt_thread(log_path, msg=f'Calling self.enable_buttons_thread()...')
        #         self.app.enable_buttons_thread()
        #         return False
        #
        #     if not task_to_kill:
        #         logIt_thread(log_path, msg=f'Calling self.enable_buttons_thread()...')
        #         self.app.enable_buttons_thread()
        #         return False
        #
        #     logIt_thread(log_path, msg=f'Displaying popup for kill confirmation...')
        #     confirmKill = messagebox.askyesno(f'Kill task: {task_to_kill} on {self.endpoint.ident}',
        #                                       f'Are you sure you want to kill {task_to_kill}?')
        #     logIt_thread(log_path, msg=f'Kill confirmation: {confirmKill}.')
        #     if confirmKill:
        #         logIt_thread(log_path, msg=f'Calling kill_task({task_to_kill})...')
        #         self.kill_task(task_to_kill)
        #
        #     else:
        #         try:
        #             logIt_thread(log_path, msg=f'Sending pass command to {self.endpoint.ip}.')
        #             self.endpoint.conn.send('pass'.encode())
        #             logIt_thread(log_path, msg=f'Send completed.')
        #             return False
        #
        #         except (WindowsError, socket.error) as e:
        #             logIt_thread(log_path, msg=f'Error: {e}')
        #             self.app.update_statusbar_messages_thread(msg=f'{e}.')
        #             logIt_thread(log_path,
        #                          msg=f'Calling server.remove_lost_connection({self.endpoint})...')
        #             self.app.server.remove_lost_connection(self.endpoint)
        #             return False
        #
        # else:
        #     try:
        #         logIt_thread(log_path, msg=f'Sending "n" to {self.endpoint.ip}.')
        #         self.endpoint.conn.send('n'.encode())
        #         logIt_thread(log_path, msg=f'Send completed.')
        #         self.app.update_statusbar_messages_thread(msg=f'tasks file received from '
        #                                                       f'{self.endpoint.ip} | {self.endpoint.ident}.')
        #         logIt_thread(log_path, msg=f'Calling self.enable_buttons_thread()...')
        #         self.app.enable_buttons_thread()
        #         return True
        #
        #     except (WindowsError, socket.error) as e:
        #         logIt_thread(log_path, msg=f'Error: {e}.')
        #         self.app.update_statusbar_messages_thread(msg=f'{e}.')
        #         logIt_thread(log_path, msg=f'Calling server.remove_lost_connection({self.endpoint})...')
        #         self.app.server.remove_lost_connection(self.endpoint)
        #         return False


class SystemInformation:
    def __init__(self, endpoint, app):
        self.app = app
        self.endpoint = endpoint
        self.path = os.path.join(path, self.endpoint.ident)

    def run(self):
        try:
            os.makedirs(self.path)

        except FileExistsError:
            self.logIt_thread(self.log_path, debug=False, msg=f'Passing FileExistsError...')
            pass

        self.logIt_thread(self.log_path, msg=f'Creating sysinfo file...')
        dt = self.get_date()
        self.sysinfo = rf'C:\HandsOff\{self.endpoint.ident}\sysinfo {self.endpoint.ident} {dt}.txt'

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


class App(tk.Tk):
    top_windows = []
    buttons = []
    social_buttons = []
    maintenance_buttons = []

    # List to hold captured screenshot images
    displayed_screenshot_files = []
    frames = []
    tabs = 0
    notebooks = {}

    # Temp dict to hold connected station's ID# & IP
    temp = {}

    # App Display sizes
    WIDTH = 1150
    HEIGHT = 870

    def __init__(self):
        super().__init__()
        self.style = ttk.Style()
        self.update_url = StringVar()
        self.new_url = ''
        self.server = Server(log_path, self, args.ip, args.port)
        self.running = False

        # ======== Server Config ==========
        # Start listener
        self.server.listener()

        # Create local app DIR
        if not os.path.exists(path):
            os.makedirs(path)

        # Run Listener Thread
        listenerThread = Thread(target=self.server.run,
                                daemon=True,
                                name="Listener Thread")
        listenerThread.start()

        # ======== GUI Config ===========
        # Set main window preferences
        self.title("HandsOff")
        self.iconbitmap('HandsOff.ico')

        # Update screen geometry variables
        self.update_idletasks()

        # Get current screen width & height
        self.width = self.winfo_screenwidth()
        self.height = self.winfo_screenheight()

        # Set Mid Screen Coordinates
        x = (self.width / 2) - (self.WIDTH / 2)
        y = (self.height / 2) - (self.HEIGHT / 2)

        # Set Window Size & Location & Center Window
        self.geometry(f'{self.WIDTH}x{self.HEIGHT}+{int(x)}+{int(y)}')
        self.maxsize(f'{self.WIDTH}', f'{self.HEIGHT}')
        self.minsize(f'{self.WIDTH}', f'{self.HEIGHT}')

        # Bind Keyboard Shortcut Keys
        self.bind("<F1>", self.about)
        self.bind("<F5>", self.refresh_command)
        self.bind("<F6>", self.clear_notebook_command)

        # Set Closing protocol
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Main Window Frames
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(5, weight=1)

        # Initiate app's styling
        self.make_style()

        # Build and display
        self.build_menubar()
        self.build_main_window_frames()
        self.build_connected_table()
        self.server_information()
        self.build_controller_buttons(None)
        self.create_notebook()
        self.show_available_connections()
        self.connection_history()

    # ==++==++==++== THREADED ==++==++==++== #
    # Update status bar messages Thread
    def update_statusbar_messages_thread(self, msg=''):
        statusbarThread = Thread(target=self.update_statusbar_messages,
                                 args=(msg,),
                                 name="Update Statusbar Thread")
        statusbarThread.start()

    # Display Server Information Thread
    def display_server_information_thread(self) -> None:
        # Display Server Information
        infoThread = Thread(target=self.server_information,
                            daemon=True,
                            name="ServerInfo")
        infoThread.start()

    # Vitals Thread
    def vital_signs_thread(self) -> None:
        vitalsThread = Thread(target=self.server.vital_signs,
                              daemon=True,
                              name="Vitals Thread")
        vitalsThread.start()

    # Update Client Thread
    def update_all_clients_thread(self, event=0):
        update = Thread(target=self.update_all_clients_command,
                        daemon=True,
                        name="Update All Clients Thread")
        update.start()

    # Update Selected Client Thread
    def update_selected_endpoint_thread(self, endpoint):
        updateThread = Thread(target=self.update_selected_endpoint,
                              args=(endpoint,),
                              daemon=True,
                              name="Update Selected Client Thread")
        updateThread.start()

    # Display Available Connections Thread
    def sac_thread(self) -> None:
        self.sacThread = Thread(target=self.show_available_connections,
                                daemon=True,
                                name="Show Available Connections Thread")
        # self.sacThread.daemon = True
        self.sacThread.start()

    # Connection History Thread
    def connection_history_thread(self) -> None:
        connhistThread = Thread(target=self.connection_history,
                                daemon=True,
                                name="Connection History Thread")
        connhistThread.start()

    # Disable Controller Buttons Thread
    def disable_buttons_thread(self) -> None:
        disable = Thread(target=self.disable_buttons,
                         daemon=True,
                         name="Disable Controller Buttons Thread")
        disable.start()

    # Enable Controller Buttons Thread
    def enable_buttons_thread(self) -> None:
        enable = Thread(target=self.enable_buttons,
                        daemon=True,
                        name="Enable Controller Buttons Thread")
        enable.start()

    # Save Connection History Thread
    def save_connection_history_thread(self, event=0):
        saveThread = Thread(target=self.save_connection_history,
                            daemon=True,
                            name="Save Connection History Thread")
        saveThread.start()

    # Restart All Clients Thread
    def restart_all_clients_thread(self, event=0):
        restartThread = Thread(target=self.restart_all_clients_command,
                               daemon=True,
                               name="Restart All Clients Thread")
        restartThread.start()

    # Show Help Thread
    def show_help_thread(self):
        helpThread = Thread(target=self.show_help,
                            daemon=True,
                            name="Show Help Thread")
        helpThread.start()

    # Client System Info Thread
    def client_system_information_thread(self, endpoint):
        clientSystemInformationThread = Thread(target=self.sysinfo_command,
                                               args=(endpoint,),
                                               daemon=True,
                                               name="Client System Information Thread")
        clientSystemInformationThread.start()

    # Grab Screenshot
    def screenshot_thread(self, endpoint):
        screenThread = Thread(target=self.screenshot_command,
                              args=(endpoint,),
                              daemon=True,
                              name='Screenshot Thread')
        screenThread.start()

    # Show Available Connections
    def show_available_connections_thread(self):
        historyThread = Thread(target=self.show_available_connections,
                               daemon=True,
                               name="Available Connections Thread")
        historyThread.start()

    def run_maintenance_thread(self, endpoint):
        maintenanceThread = Thread(target=self.run_maintenance_command,
                                   args=(endpoint,),
                                   daemon=True,
                                   name="Run Maintenance Thread")
        maintenanceThread.start()

    # ==++==++==++== END THREADED FUNCS ==++==++==++== #
    # ==++==++==++== GUI ==++==++==++==
    # Define GUI Styles
    def make_style(self):
        logIt_thread(log_path, msg=f'Styling App...')
        self.style.theme_create("HandsOff", parent='classic', settings={
            "TNotebook": {"configure": {"tabmargins": [2, 5, 2, 1], 'background': 'slate gray'}},
            "TNotebook.Tab": {"configure": {"padding": [7, 1], "background": 'SkyBlue3'},
                              "map": {"background": [("selected", 'green')],
                                      "expand": [("selected", [1, 1, 1, 0])]}},

            "Treeview.Heading": {
                "configure": {"padding": 1,
                              "background": 'slate grey',
                              'relief': 'ridge',
                              'foreground': 'ghost white'},
                "map": {"background": [("selected", 'green')]}},
        })

        self.style.theme_use("HandsOff")
        self.style.configure("Treeview.Heading", font=('Arial Bold', 8))
        self.style.map("Treeview", background=[('selected', 'sea green')])

    def update_tools_menu(self):
        if len(self.server.connHistory) > 0:
            self.tools.entryconfig(2, state=NORMAL)
            self.bind("<F10>", self.save_connection_history_thread)

        else:
            self.tools.entryconfig(2, state=DISABLED)
            self.unbind("<F10>")

        if len(self.server.endpoints) > 1:
            self.tools.entryconfig(3, state=NORMAL)
            self.tools.entryconfig(4, state=NORMAL)
            self.bind("<F11>", self.restart_all_clients_thread)
            self.bind("<F12>", self.update_all_clients_thread)

        else:
            self.tools.entryconfig(3, state=DISABLED)
            self.tools.entryconfig(4, state=DISABLED)
            self.unbind("<F11>")
            self.unbind("<F12>")

    # Create Menubar
    def build_menubar(self):
        logIt_thread(log_path, msg=f'Running build_menubar()...')
        menubar = Menu(self, tearoff=0)
        file = Menu(menubar, tearoff=0)
        self.tools = Menu(self, tearoff=0)
        helpbar = Menu(self, tearoff=0)

        file.add_command(label="Minimize", command=self.minimize)
        file.add_separator()
        file.add_command(label="Exit", command=self.on_closing)

        self.tools.add_command(label="Refresh <F5>", command=self.refresh_command)
        self.tools.add_command(label="Clear Details <F6>", command=self.clear_notebook_command)
        self.tools.add_command(label="Save Connection History <F10>", command=self.save_connection_history_thread,
                               state=DISABLED)
        self.tools.add_command(label="Restart All Clients <F11>", command=self.restart_all_clients_thread,
                               state=DISABLED)
        self.tools.add_command(label="Update All Clients <F12>", command=self.update_all_clients_thread,
                               state=DISABLED)

        helpbar.add_command(label="Help", command=self.show_help_thread)
        helpbar.add_command(label="About", command=self.about)

        menubar.add_cascade(label='File', menu=file)
        menubar.add_cascade(label='Tools', menu=self.tools)
        menubar.add_cascade(label="Help", menu=helpbar)

        logIt_thread(log_path, msg=f'Displaying Menubar...')
        self.config(menu=menubar)
        return

    # Build Main Frame GUI
    def build_main_window_frames(self) -> None:
        logIt_thread(log_path, msg=f'Running build_main_window_frames()...')
        logIt_thread(log_path, msg=f'Building main frame...')
        self.main_frame = Frame(self, relief="raised", bd=1)
        self.main_frame.configure(border=1)
        self.main_frame.grid(row=0, column=0, sticky="nswe", padx=1)
        self.main_frame.rowconfigure(5, weight=1)
        self.main_frame.columnconfigure(0, weight=1)

        logIt_thread(log_path, msg=f'Building main frame top bar...')
        self.main_frame_top = Frame(self.main_frame, relief='flat')
        self.main_frame_top.grid(row=0, column=0, sticky="nwes")

        logIt_thread(log_path, msg=f'Building main frame top bar labelFrame...')
        self.top_bar_label = LabelFrame(self.main_frame, text="Server Information", relief='solid',
                                        background='gainsboro')
        self.top_bar_label.grid(row=0, column=0, sticky='news')

        logIt_thread(log_path, msg=f'Building table frame in main frame...')
        self.main_frame_table = Frame(self.main_frame, relief='flat')
        self.main_frame_table.grid(row=1, column=0, sticky="news", pady=2)

        logIt_thread(log_path, msg=f'Building controller frame in main frame...')
        self.controller_frame = Frame(self.main_frame, relief='flat', background='gainsboro', height=60)
        self.controller_frame.grid(row=2, column=0, sticky='news', pady=2)

        logIt_thread(log_path,
                     msg=f'Building controller buttons label frame in main frame...')
        self.controller_btns = LabelFrame(self.controller_frame, text="Controller", relief='solid', height=60,
                                          background='gainsboro')
        self.controller_btns.pack(fill=BOTH)

        logIt_thread(log_path, msg=f'Building connected table in main frame...')
        self.table_frame = LabelFrame(self.main_frame_table, text="Connected Stations",
                                      relief='solid', background='gainsboro')
        self.table_frame.pack(fill=BOTH)

        logIt_thread(log_path, msg=f'Building details frame in main frame...')
        self.details_frame = Frame(self.main_frame, relief='flat', pady=2, height=310)
        self.details_frame.grid(row=3, column=0, sticky='news')

        logIt_thread(log_path, msg=f'Building statusbar frame in main frame...')
        self.statusbar_frame = Frame(self.main_frame, relief=SUNKEN, bd=1)
        self.statusbar_frame.grid(row=5, column=0, sticky='news')

        logIt_thread(log_path, msg=f'Building statusbar label frame in main frame...')
        self.status_label = Label(self.statusbar_frame, text='Status', relief=FLAT, anchor=W)
        self.status_label.pack(fill=BOTH)

    # Create Treeview Table for connected stations
    def build_connected_table(self) -> None:
        def highlight(event):
            self.connected_table = event.widget
            item = self.connected_table.identify_row(event.y)
            self.connected_table.tk.call(self.connected_table, "tag", "remove", "highlight")
            self.connected_table.tk.call(self.connected_table, "tag", "add", "highlight", item)

        logIt_thread(log_path, msg=f'Running build_connected_table()...')
        logIt_thread(log_path, msg=f'Displaying Scrollbar...')
        self.table_sb = Scrollbar(self.table_frame, orient=VERTICAL)
        self.table_sb.pack(side=LEFT, fill=Y)
        logIt_thread(log_path, msg=f'Displaying connected table...')
        self.connected_table = ttk.Treeview(self.table_frame,
                                            columns=("ID", "MAC Address",
                                                     "IP Address", "Station Name",
                                                     "Logged User", "Client Version"),
                                            show="headings", height=7,
                                            selectmode='browse', yscrollcommand=self.table_sb.set)
        self.connected_table.pack(fill=BOTH)
        self.table_sb.config(command=self.connected_table.yview)
        logIt_thread(log_path, msg=f'Defining highlight event for Connected Table...')
        self.connected_table.tag_configure('highlight', background='lightblue')

        # Columns & Headings config
        self.connected_table.column("#1", anchor=CENTER, width=100)
        self.connected_table.heading("#1", text="ID")
        self.connected_table.column("#2", anchor=CENTER)
        self.connected_table.heading("#2", text="MAC")
        self.connected_table.column("#3", anchor=CENTER)
        self.connected_table.heading("#3", text="IP")
        self.connected_table.column("#4", anchor=CENTER)
        self.connected_table.heading("#4", text="Station Name")
        self.connected_table.column("#5", anchor=CENTER)
        self.connected_table.heading("#5", text="Logged User")
        self.connected_table.column("#6", anchor=CENTER)
        self.connected_table.heading("#6", text="Client Version")
        self.connected_table.bind("<Button 1>", self.select_item)
        self.connected_table.bind("<Motion>", highlight)

        logIt_thread(log_path, msg=f'Stying table row colors...')
        self.connected_table.tag_configure('oddrow', background='snow')
        self.connected_table.tag_configure('evenrow', background='ghost white')

    # Create Controller Buttons
    def build_controller_buttons(self, endpoint):
        logIt_thread(log_path, msg=f'Building refresh button...')
        refresh_img = PIL.ImageTk.PhotoImage(
            PIL.Image.open('images/refresh_green.png').resize((17, 17), PIL.Image.LANCZOS))

        self.refresh_btn = Button(self.controller_btns, text=" Refresh", image=refresh_img,
                                  compound=LEFT, anchor=W,
                                  width=75, pady=5, command=self.refresh_command)
        self.refresh_btn.image = refresh_img
        self.refresh_btn.grid(row=0, column=0, pady=5, padx=2)

        logIt_thread(log_path, msg=f'Building screenshot button...')
        self.screenshot_btn = Button(self.controller_btns, text="Screenshot", width=10,
                                     pady=5, padx=10,
                                     command=lambda: self.screenshot_thread(endpoint))
        self.screenshot_btn.grid(row=0, column=1, sticky="w", pady=5, padx=2, ipadx=2)
        logIt_thread(log_path, msg=f'Updating controller buttons list...')
        self.buttons.append(self.screenshot_btn)
        logIt_thread(log_path, msg=f'Building anydesk button...')
        self.anydesk_btn = Button(self.controller_btns, text="Anydesk", width=14, pady=5,
                                  command=lambda: self.anydesk_command(endpoint))
        self.anydesk_btn.grid(row=0, column=2, sticky="w", pady=5, padx=2, ipadx=2)
        logIt_thread(log_path,
                     msg=f'Updating controller buttons list...')
        self.buttons.append(self.anydesk_btn)
        logIt_thread(log_path, msg=f'Building last restart button...')
        self.last_restart_btn = Button(self.controller_btns, text="Last Restart", width=14,
                                       pady=5,
                                       command=lambda: self.last_restart_command(endpoint))
        self.last_restart_btn.grid(row=0, column=3, sticky="w", pady=5, padx=2, ipadx=2)
        logIt_thread(log_path, msg=f'Updating controller buttons list...')
        self.buttons.append(self.last_restart_btn)
        logIt_thread(log_path,
                     msg=f'Building system information button...')
        self.sysinfo_btn = Button(self.controller_btns, text="SysInfo", width=14, pady=5,
                                  command=lambda: self.client_system_information_thread(endpoint))
        self.sysinfo_btn.grid(row=0, column=4, sticky="w", pady=5, padx=2, ipadx=2)
        logIt_thread(log_path, msg=f'Updating controller buttons list...')
        self.buttons.append(self.sysinfo_btn)
        logIt_thread(log_path, msg=f'Building tasks button...')
        self.tasks_btn = Button(self.controller_btns, text="Tasks", width=14, pady=5,
                                command=lambda: self.tasks(endpoint))
        self.tasks_btn.grid(row=0, column=5, sticky="w", pady=5, padx=2, ipadx=2)
        logIt_thread(log_path, msg=f'Updating controller buttons list...')
        self.buttons.append(self.tasks_btn)
        logIt_thread(log_path, msg=f'Building restart button...')
        self.restart_btn = Button(self.controller_btns, text="Restart", width=14, pady=5,
                                  command=lambda: self.restart_command(endpoint))
        self.restart_btn.grid(row=0, column=6, sticky="w", pady=5, padx=2, ipadx=2)
        logIt_thread(log_path, msg=f'Updating controller buttons list...')
        self.buttons.append(self.restart_btn)

        logIt_thread(log_path, msg=f'Building local files button...')
        self.browse_btn = Button(self.controller_btns, text="Local Files", width=14, pady=5,
                                 command=lambda: self.browse_local_files_command(endpoint))
        self.browse_btn.grid(row=0, column=7, sticky="w", pady=5, padx=2, ipadx=2)
        self.buttons.append(self.browse_btn)

        logIt_thread(log_path, msg=f'Building Update Client button...')
        self.update_client = Button(self.controller_btns, text="Update Client", width=14,
                                    pady=5, state=NORMAL,
                                    command=lambda: self.update_selected_endpoint_thread(endpoint))
        self.update_client.grid(row=0, column=8, sticky="w", pady=5, padx=2, ipadx=2)
        self.buttons.append(self.update_client)

        logIt_thread(log_path, msg=f'Building Maintenance button...')
        self.maintenance = Button(self.controller_btns, text="Maintenance", width=14,
                                  pady=5, state=DISABLED,
                                  command=lambda: self.run_maintenance_thread(endpoint))
        self.maintenance.grid(row=0, column=9, sticky="w", pady=5, padx=2, ipadx=2)
        # self.buttons.append(self.maintenance)

    # Build Table for Connection History
    def create_connection_history_table(self) -> None:
        logIt_thread(log_path, msg=f'Running create_connection_history_table()...')
        logIt_thread(log_path, msg=f'Displaying connection history labelFrame...')
        self.history_labelFrame = LabelFrame(self.main_frame, text="Connection History",
                                             relief='solid', background='gainsboro')
        self.history_labelFrame.grid(row=4, column=0, sticky='news')
        logIt_thread(log_path, msg=f'Displaying Scrollbar in history labelFrame...')
        self.history_table_scrollbar = Scrollbar(self.history_labelFrame, orient=VERTICAL)
        self.history_table_scrollbar.pack(side=LEFT, fill=Y)
        logIt_thread(log_path, msg=f'Displaying connection history table in labelFrame...')
        self.history_table = ttk.Treeview(self.history_labelFrame,
                                          columns=("ID", "MAC Address",
                                                   "IP Address", "Station Name",
                                                   "Logged User", "Time"),
                                          show="headings", selectmode='none',
                                          yscrollcommand=self.history_table_scrollbar.set)
        self.history_table.config(height=10)
        self.history_table.pack(fill=BOTH)
        self.history_table_scrollbar.config(command=self.history_table.yview)

        # Table Columns & Headings
        self.history_table.column("#1", anchor=CENTER, width=100)
        self.history_table.heading("#1", text="ID")
        self.history_table.column("#2", anchor=CENTER)
        self.history_table.heading("#2", text="MAC")
        self.history_table.column("#3", anchor=CENTER)
        self.history_table.heading("#3", text="IP")
        self.history_table.column("#4", anchor=CENTER)
        self.history_table.heading("#4", text="Station Name")
        self.history_table.column("#5", anchor=CENTER)
        self.history_table.heading("#5", text="Logged User")
        self.history_table.column("#6", anchor=CENTER)
        self.history_table.heading("#6", text="Time")

    # Build Notebook
    def create_notebook(self, event=0):
        def on_tab_change(event):
            t = event.widget.tab('current')['text']
            if self.tabs == 0:
                return

        logIt_thread(log_path, msg=f'Building details LabelFrame...')
        self.details_labelFrame = LabelFrame(self.main_frame, text="Details", relief='solid',
                                             foreground='white', height=400, background='slate gray')
        self.details_labelFrame.grid(row=3, sticky='news', columnspan=3)

        logIt_thread(log_path, msg=f'Clearing frames list...')
        self.frames.clear()

        logIt_thread(log_path, msg=f'Building notebook...')
        self.notebook = ttk.Notebook(self.details_labelFrame, height=250)
        self.notebook.pack(expand=True, pady=5, fill=X)
        self.notebook.bind("<<NotebookTabChanged>>", on_tab_change)

        logIt_thread(log_path, msg=f'Building tabs...')
        self.screenshot_tab = Frame(self.notebook, height=330)

        self.system_information_tab = Frame(self.notebook, height=330)
        self.tasks_tab = Frame(self.notebook, height=330)

        logIt_thread(log_path, msg=f'Building sysinfo scrollbar...')
        self.system_scrollbar = Scrollbar(self.system_information_tab, orient=VERTICAL)
        self.system_scrollbar.pack(side=LEFT, fill=Y)

        logIt_thread(log_path, msg=f'Building sysinfo textbox...')
        self.system_information_textbox = Text(self.system_information_tab,
                                               yscrollcommand=self.system_scrollbar.set)
        self.system_information_textbox.pack(fill=BOTH)
        logIt_thread(log_path, msg=f'Building tasks scrollbar...')
        self.tasks_scrollbar = Scrollbar(self.tasks_tab, orient=VERTICAL)
        self.tasks_scrollbar.pack(side=LEFT, fill=Y)

        logIt_thread(log_path, msg=f'Building tasks textbox...')
        self.tasks_tab_textbox = Text(self.tasks_tab, yscrollcommand=self.tasks_scrollbar.set)
        self.tasks_tab_textbox.pack(fill=X)

    # Update Status Bar Messages
    def update_statusbar_messages(self, msg=''):
        self.status_label.config(text=f"Status: {msg}")

    # Close App
    def on_closing(self, event=0) -> None:
        logIt_thread(log_path, msg=f'Displaying minimize popup window...')
        minimize = messagebox.askyesnocancel("Exit or Minimize", "Minimize to Tray?")
        logIt_thread(log_path, msg=f'Minimize: {minimize}')
        if minimize is None:
            return

        elif minimize:
            logIt_thread(log_path, msg=f'Hiding app window...')
            self.withdraw()

        else:
            if len(self.server.endpoints) > 0:
                for endpoint in self.server.endpoints:
                    try:
                        endpoint.conn.send('exit'.encode())

                    except socket.error:
                        pass

            mainThread = threading.current_thread()
            for thread in threading.enumerate():
                if thread is mainThread:
                    continue

                thread.join(timeout=0.5)

            logIt_thread(log_path, msg=f'Hiding app window...')
            self.withdraw()
            logIt_thread(log_path, msg=f'Destroying app window...')
            self.destroy()
            sys.exit(0)

    # Minimize Window
    def minimize(self):
        return self.withdraw()

    # Enable Controller Buttons
    def enable_buttons(self):
        logIt_thread(log_path, msg=f'Running enable_buttons()...')
        for button in list(self.buttons):
            logIt_thread(log_path, msg=f'Enabling {button.config("text")[-1]} button...')
            button.config(state=NORMAL)

    # Disable Controller Buttons
    def disable_buttons(self):
        logIt_thread(log_path, msg=f'Running disable_buttons()...')
        for button in list(self.buttons):
            logIt_thread(log_path, msg=f'Disabling {button.config("text")[-1]}...')
            button.config(state=DISABLED)

    # ==++==++==++== CONTROLLER BUTTONS COMMANDS==++==++==++==
    # Refresh server info & connected stations table with vital signs
    def refresh_command(self, event=0) -> None:
        logIt_thread(log_path, msg=f'Running refresh()...')
        logIt_thread(log_path, msg=f'Calling self_disable_buttons_thread(sidebar=False)...')
        self.disable_buttons_thread()
        logIt_thread(log_path, msg=f'Resetting tmp_availables list...')
        self.server.tmp_availables = []
        self.temp.clear()
        logIt_thread(log_path, msg=f'Calling vital_signs_thread()...')
        self.vital_signs_thread()
        logIt_thread(log_path, msg=f'Calling server_information()...')
        self.server_information()
        logIt_thread(log_path, msg=f'Calling update_tools_menu()...')
        self.update_tools_menu()
        logIt_thread(log_path, msg=f'Calling show_available_connections()...')
        self.show_available_connections()
        logIt_thread(log_path, msg=f'Calling connection_history()...')
        self.connection_history()
        self.update_statusbar_messages_thread(msg='refresh complete.')

    # Clear Notebook
    def clear_notebook_command(self, event=0):
        self.create_notebook()
        self.update_statusbar_messages_thread(msg='Details window cleared.')
        return

    def show_picture(self):
        self.sc.show()

    # Screenshot from Client
    def screenshot_command(self, endpoint) -> bool:
        logIt_thread(log_path, msg=f'Running screenshot({endpoint.conn}, {endpoint.ip}, {endpoint.ident})...')
        self.screenshot_path = fr"{path}\{endpoint.ident}"
        logIt_thread(log_path, msg=f'Calling self.disable_buttons_thread()...')
        self.disable_buttons_thread()
        self.running = True
        try:
            logIt_thread(log_path, msg=f'Sending screen command to client...')
            endpoint.conn.send('screen'.encode())

        except (ConnectionError, socket.error) as e:
            logIt_thread(log_path, msg=f'{e}')
            self.server.remove_lost_connection(endpoint)
            return False

        try:
            filename = endpoint.conn.recv(1024)
            endpoint.conn.send("Filename OK".encode())

        except (ConnectionError, socket.error) as e:
            logIt_thread(log_path, msg=f'{e}')
            self.server.remove_lost_connection(endpoint)
            return False

        try:
            size = endpoint.conn.recv(4)
            size = bytes_to_number(size)

        except (ConnectionError, socket.error) as e:
            logIt_thread(log_path, msg=f'{e}')
            self.server.remove_lost_connection(endpoint)
            return False

        current_size = 0
        buffer = b""
        try:
            logIt_thread(log_path, debug=False, msg=f'Opening file: {filename} for writing...')
            with open(filename, 'wb') as file:
                logIt_thread(log_path, debug=False, msg=f'Fetching file content...')
                while current_size < size:
                    data = endpoint.conn.recv(1024)
                    if not data:
                        break

                    if len(data) + current_size > size:
                        data = data[:size - current_size]

                    buffer += data
                    current_size += len(data)
                    file.write(data)

            logIt_thread(log_path, debug=False, msg=f'Fetch completed.')

        except FileExistsError:
            logIt_thread(log_path, debug=False, msg=f'File Exists error.')
            logIt_thread(log_path, debug=False, msg=f'Opening {filename} for appends...')
            with open(filename, 'ab') as file:
                while current_size < size:
                    logIt_thread(log_path, debug=False, msg=f'Fetching file content...')
                    data = endpoint.conn.recv(1024)
                    if not data:
                        break

                    if len(data) + current_size > size:
                        data = data[:size - current_size]

                    buffer += data
                    current_size += len(data)
                    file.write(data)

        try:
            logIt_thread(log_path, debug=False, msg=f'Waiting for answer from client...')
            ans = endpoint.conn.recv(1024).decode()
            logIt_thread(log_path, debug=False, msg=f'Client answer: {ans}')

        except (ConnectionError, socket.error) as e:
            logIt_thread(log_path, msg=f'{e}')
            self.server.remove_lost_connection(endpoint)
            return False

        logIt_thread(log_path, debug=False, msg=f'Running move({filename}, {path})...')
        logIt_thread(log_path, debug=False, msg=f'Renaming {filename}...')
        filename = str(filename).strip("b'")
        logIt_thread(log_path, debug=False, msg=f'New filename: {filename}')

        logIt_thread(log_path, debug=False, msg=f'Capturing {filename} absolute path...')
        src = os.path.abspath(filename)
        logIt_thread(log_path, debug=False, msg=f'Abs path: {src}')

        logIt_thread(log_path, debug=False, msg=f'Defining destination...')
        dst = fr"{self.screenshot_path}"
        logIt_thread(log_path, debug=False, msg=f'Destination: {dst}.')

        logIt_thread(log_path, debug=False, msg=f'Moving file...')
        shutil.move(src, dst)
        logIt_thread(log_path, debug=False, msg=f'File {filename} moved to {dst}.')

        try:
            logIt_thread(log_path, msg=f'Sorting jpg files by creation time...')
            self.images = glob.glob(fr"{self.screenshot_path}\*.jpg")
            self.images.sort(key=os.path.getmtime)
            logIt_thread(log_path, msg=f'Opening latest screenshot...')
            self.sc = PIL.Image.open(self.images[-1])

        except IndexError:
            pass

        logIt_thread(log_path, msg=f'Resizing to 650x350...')
        self.sc_resized = self.sc.resize((650, 350))
        self.last_screenshot = PIL.ImageTk.PhotoImage(self.sc_resized)
        self.displayed_screenshot_files.append(self.last_screenshot)

        logIt_thread(log_path, msg=f'Building working frame...')
        self.tab = Frame(self.notebook, height=350, background='slate gray')

        logIt_thread(log_path, msg=f'Building Preview Button...')
        button = Button(self.tab, image=self.last_screenshot, command=self.show_picture, border=5, bd=3)
        button.pack(padx=5, pady=10)

        logIt_thread(log_path, msg=f'Adding tab to notebook...')
        self.notebook.add(self.tab, text=f"Screenshot {endpoint.ident}")

        logIt_thread(log_path, msg=f'Displaying latest notebook tab...')
        self.notebook.select(self.tab)
        self.tabs += 1

        logIt_thread(log_path, msg=f'Calling self.enable_buttons_thread()...')
        self.enable_buttons_thread()
        self.running = False
        # return True

    # Run Anydesk on Client
    def anydesk_command(self, endpoint) -> bool:
        logIt_thread(log_path, msg=f'Running anydesk({endpoint.conn}, {endpoint.ip})...')
        self.update_statusbar_messages_thread(msg=f'running anydesk on {endpoint.ip} | {endpoint.ident}...')
        try:
            logIt_thread(log_path, msg=f'Sending anydesk command to {endpoint.conn}...')
            endpoint.conn.send('anydesk'.encode())
            logIt_thread(log_path, msg=f'Send Completed.')

            logIt_thread(log_path, msg=f'Waiting for response from client...')
            msg = endpoint.conn.recv(1024).decode()
            logIt_thread(log_path, msg=f'Client response: {msg}.')
            if "OK" not in msg:
                logIt_thread(log_path, msg=f'Printing msg from client...')
                self.update_statusbar_messages_thread(msg=f'{endpoint.ip} | {endpoint.ident}: Anydesk not installed.')
                logIt_thread(log_path, msg=f'Display popup confirmation for install anydesk...')
                install_anydesk = messagebox.askyesno("Install Anydesk",
                                                      "Anydesk isn't installed on the remote machine. "
                                                      "do you with to install?")
                logIt_thread(log_path, msg=f'Install anydesk: {install_anydesk}.')
                if install_anydesk:
                    self.update_statusbar_messages_thread(
                        msg=f'installing anydesk on {endpoint.ip} | {endpoint.ident}...')
                    logIt_thread(log_path, msg=f'Sending install command to {endpoint.conn}...')
                    endpoint.conn.send('y'.encode())
                    logIt_thread(log_path, msg=f'Send Completed.')
                    logIt_thread(log_path, msg=f'Initiating StringVar() for textVar...')
                    textVar = StringVar()
                    while True:
                        logIt_thread(log_path, msg=f'Waiting for response from client...')
                        msg = endpoint.conn.recv(1024).decode()
                        logIt_thread(log_path, msg=f'Client response: {msg}.')
                        textVar.set(msg)
                        logIt_thread(log_path, msg=f'textVar: {textVar}')
                        if "OK" not in str(msg):
                            self.update_statusbar_messages_thread(msg=f'{msg}')

                        else:
                            self.update_statusbar_messages_thread(msg=f'Status: {textVar}')
                            logIt_thread(log_path, msg=f'Display popup infobox')
                            messagebox.showinfo(f"From {endpoint.ip} | {endpoint.ident}", f"Anydesk Running.\t\t\t\t")
                            self.update_statusbar_messages_thread(msg=f'anydesk running on '
                                                                      f'{endpoint.ip} | {endpoint.ident}.')
                            return True

                else:
                    logIt_thread(log_path, msg=f'Sending cancel command to {endpoint.conn}...')
                    endpoint.conn.send('n'.encode())
                    logIt_thread(log_path, msg=f'Send Completed.')
                    return

            else:
                self.update_statusbar_messages_thread(msg=f'anydesk running on {endpoint.ip} | {endpoint.ident}.')
                logIt_thread(log_path, msg=f'Displaying popup window with "Anydesk Running"...')
                messagebox.showinfo(f"From {endpoint.ip} | {endpoint.ident}", f"Anydesk Running.\t\t\t\t")
                return True

        except (WindowsError, ConnectionError, socket.error, RuntimeError) as e:
            logIt_thread(log_path, debug=True, msg=f'Connection Error: {e}.')
            self.update_statusbar_messages_thread(msg=f'{e}.')
            logIt_thread(log_path, debug=True,
                         msg=f'Calling server.remove_lost_connection({endpoint.conn}, {endpoint.ip})...')
            server.remove_lost_connection(endpoint)
            return False

    # Display Clients Last Restart
    def last_restart_command(self, endpoint) -> bool:
        logIt_thread(log_path, msg=f'Running last_restart('
                                   f'{endpoint.conn}, {endpoint.ip}, {endpoint.ident})...')
        try:
            logIt_thread(log_path, msg=f'Sending lr command to client...')
            endpoint.conn.send('lr'.encode())
            logIt_thread(log_path, msg=f'Send Completed.')
            logIt_thread(log_path, msg=f'Waiting for response from client...')
            msg = endpoint.conn.recv(1024).decode()
            logIt_thread(log_path, msg=f'Client response: {msg}')
            self.update_statusbar_messages_thread(msg=f'restart for {endpoint.ident}: {msg.split("|")[1][15:]}')
            logIt_thread(log_path, msg=f'Display popup with last restart info...')
            messagebox.showinfo(f"Last Restart for: {endpoint.ip} | {endpoint.ident}",
                                f"\t{msg.split('|')[1][15:]}\t\t\t")
            return True

        except (WindowsError, socket.error, ConnectionResetError) as e:
            logIt_thread(log_path, msg=f'Connection Error: {e}.')
            self.update_statusbar_messages_thread(msg=f'{e}')
            logIt_thread(log_path, msg=f'Calling server.remove_lost_connection('
                                       f'{endpoint.conn}, {endpoint.ip})...')
            server.remove_lost_connection(endpoint)
            return False

    # Client System Information
    def sysinfo_command(self, endpoint):
        logIt_thread(log_path, msg=f'Running self.sysinfo('
                                   f'{endpoint.conn}, {endpoint.ip}, {endpoint.ident})...')
        logIt_thread(log_path, msg=f'Calling self.disable_buttons_thread(sidebar=True)...')
        self.disable_buttons_thread()
        self.running = True
        self.update()
        self.update_statusbar_messages_thread(msg=f'waiting for system information from '
                                                  f'{endpoint.ip} | {endpoint.ident}...')
        try:
            logIt_thread(log_path, msg=f'Initializing Module: sysinfo...')
            sinfo = sysinfo.Sysinfo(endpoint, path, log_path, self)
            logIt_thread(log_path, msg=f'Calling sysinfo.run()...')
            file_path = sinfo.run()
            self.update_statusbar_messages_thread(msg=f'system information file received from '
                                                      f'{endpoint.ip} | {endpoint.ident}.')
            display = DisplayFileContent(self.notebook, file_path, self.system_information_tab,
                                         sname=endpoint.ident, txt='System Information')
            display.run()
            self.running = False
            self.enable_buttons_thread()
            self.update()

        except (WindowsError, socket.error, ConnectionResetError) as e:
            logIt_thread(log_path, debug=True, msg=f'Connection Error: {e}.')
            self.update_statusbar_messages_thread(msg=f'{e}.')
            try:
                logIt_thread(log_path, msg=f'Calling server.remove_lost_connection('
                                           f'{endpoint.conn}, {endpoint.ip})...')
                self.server.remove_lost_connection(endpoint)
                logIt_thread(log_path, msg=f'Calling self.enable_buttons_thread...')
                self.enable_buttons_thread()
                return False

            except RuntimeError:
                logIt_thread(log_path, msg=f'Calling self.enable_buttons_thread...')
                self.enable_buttons_thread()
                return False

    # Display/Kill Tasks on Client
    def tasks(self, endpoint) -> bool:
        self.running = True
        tasks = Tasks(endpoint, self, self.notebook)
        tasks.run()
        self.running = False

    # Restart Client
    def restart_command(self, endpoint) -> bool:
        logIt_thread(log_path, msg=f'Running restart({endpoint.conn})')
        self.update_statusbar_messages_thread(msg=f' waiting for restart confirmation...')
        logIt_thread(log_path, msg=f'Displaying self.sure() popup window...')
        self.sure = messagebox.askyesno(f"Restart for: {endpoint.ip} | {endpoint.ident}",
                                        f"Are you sure you want to restart {endpoint.ident}?\t")
        logIt_thread(log_path, msg=f'self.sure = {self.sure}')

        if self.sure:
            try:
                logIt_thread(log_path, msg=f'Sending restart command to client...')
                endpoint.conn.send('restart'.encode())
                logIt_thread(log_path, msg=f'Send completed.')
                logIt_thread(log_path, msg=f'Calling server.remove_lost_connection('
                                           f'{endpoint})...')
                self.server.remove_lost_connection(endpoint)
                logIt_thread(log_path, msg=f'Restart command completed.')
                self.update_statusbar_messages_thread(msg=f'restart command sent to '
                                                          f'{endpoint.ip} | {endpoint.ident}.')
                logIt_thread(log_path, msg=f'Calling self.refresh()...')
                self.refresh_command()
                return True

            except (RuntimeError, WindowsError, socket.error) as e:
                logIt_thread(log_path, msg=f'Connection Error: {e}')
                self.update_statusbar_messages_thread(msg=f'{e}')
                logIt_thread(log_path, msg=f'Calling server.remove_lost_connection('
                                           f'{endpoint})...')
                self.server.remove_lost_connection(endpoint)
                return False

        else:
            self.update_statusbar_messages_thread(msg=f'restart canceled.')
            return False

    # Browse local files by Clients Station Names
    def browse_local_files_command(self, endpoint) -> subprocess:
        logIt_thread(log_path, msg=fr'Opening explorer window focused on "{path}\{endpoint.ident}"')
        return subprocess.Popen(rf"explorer {path}\{endpoint.ident}")

    # Update Selected Client
    def update_selected_endpoint(self, endpoint) -> bool:
        logIt_thread(log_path, msg=f'Running update_selected_client()...')
        logIt_thread(log_path, msg=f'Calling self.disable_buttons_thread()...')
        self.disable_buttons_thread()

        logIt_thread(log_path, msg=f'Displaying confirmation pop-up...')
        sure = messagebox.askyesno(f"Update client", "Are you sure?")
        if sure:
            logIt_thread(log_path, msg=f'Sending update command to {endpoint.ip} | {endpoint.ident}...')
            try:
                endpoint.conn.send('update'.encode())
                logIt_thread(log_path, msg=f'Send Completed.')
                logIt_thread(log_path, msg=f'Waiting for response from {endpoint.ip} | {endpoint.ident}...')
                msg = endpoint.conn.recv(1024).decode()
                logIt_thread(log_path, msg=f'{endpoint.ip}|{endpoint.ident}: {msg}')
                self.refresh_command()

            except (WindowsError, socket.error) as e:
                logIt_thread(log_path, msg=f'ERROR: {e}.')
                return False

            # self.server.remove_lost_connection(endpoint)
            logIt_thread(log_path, msg=f'Displaying update info popup window...')
            messagebox.showinfo(f"Update {endpoint.ident}", "Update command sent.")
            self.enable_buttons_thread()
            self.refresh_command(event=0)
            return True

        else:
            return False

    # Run Maintenance on Client
    def run_maintenance_command(self, endpoint) -> None:
        logIt_thread(log_path, msg=f"Sending maintenance command to {endpoint.ip} | {endpoint.ident}...")
        self.update_statusbar_messages_thread(
            msg=f"Waiting for maintenance confirmation on {endpoint.ip} | {endpoint.ident}...")
        sure = messagebox.askyesno(f"Maintenance for {endpoint.ip} | {endpoint.ident}", "Are you sure?")
        if sure:
            self.update_statusbar_messages_thread(
                msg=f"Sending maintenance command to {endpoint.ip} | {endpoint.ident}...")
            try:
                endpoint.conn.send('maintenance'.encode())
                logIt_thread(log_path, msg=f"Maintenance command sent.")
                logIt_thread(log_path,
                             msg=f"Calling server.remove_lost_connection({endpoint.conn}, {endpoint.ip})")
                self.update_statusbar_messages_thread(
                    msg=f"Maintenance command sent to {endpoint.ip} | {endpoint.ident}.")
                logIt_thread(msg=f"Calling server.remove_lost_connection({endpoint.conn}, {endpoint.ip})")
                server.remove_lost_connection(endpoint)
                time.sleep(0.5)
                logIt_thread(log_path, msg=f"Calling self.refresh_command()...")
                self.refresh_command()
                return True

            except (WindowsError, socket.error) as e:
                logIt_thread(log_path, msg=f"ERROR: {e}.")
                logIt_thread(log_path,
                             msg=f"Calling server.remove_lost_connection({endpoint.conn}, {endpoint.ip})")
                server.remove_lost_connection(endpoint)
                time.sleep(0.5)
                logIt_thread(log_path, msg=f"Calling self.refresh_command()...")
                self.refresh_command()
                return False

        else:
            return False

    # ==++==++==++== END Controller Buttons ==++==++==++==
    # Display Server Information
    def server_information(self) -> None:
        logIt_thread(log_path, msg=f'Running show server information...')
        last_reboot = psutil.boot_time()
        logIt_thread(log_path, msg=f'Displaying Label: '
                                   f'{self.server.serverIP} | {self.server.port} | '
                                   f'{datetime.fromtimestamp(last_reboot).replace(microsecond=0)}" | '
                                   f'{len(self.server.endpoints)}')
        label = Label(self.top_bar_label, background='ghost white',
                      text=f"\t\t\tServing on: handsoff.home.lab\tServer IP: {self.server.serverIP}\t  "
                           f"Server Port: {self.server.port}"
                           f"\tLast Boot: {datetime.fromtimestamp(last_reboot).replace(microsecond=0)}"
                           f"\tConnected Stations: {len(self.server.endpoints)}\t\t\t\t          ")
        label.grid(row=0, sticky='news')
        return

    # Display Available Stations
    def show_available_connections(self) -> None:
        # Clear previous entries in GUI table
        logIt_thread(log_path, msg=f'Cleaning connected table entries...')
        self.connected_table.delete(*self.connected_table.get_children())

        logIt_thread(log_path, msg=f'Running show_available_connections()...')
        if not self.server.endpoints:
            logIt_thread(log_path, msg='No connected Stations')
            return

        # Cleaning availables list
        logIt_thread(log_path, msg=f'Cleaning availables list...')
        self.server.tmp_availables = []

        logIt_thread(log_path, msg=f'Creating tmp_availables list...')
        for count, endpoint in enumerate(self.server.endpoints):
            self.server.tmp_availables.append((count, endpoint.client_mac, endpoint.ip,
                                               endpoint.ident, endpoint.user, endpoint.client_version))
        logIt_thread(log_path, msg=f'Available list created.')

        for item in self.server.tmp_availables:
            endpoint = next(endpoint for endpoint in self.server.endpoints if endpoint.client_mac == item[1])
            tag = 'evenrow' if item[0] % 2 == 0 else 'oddrow'

            logIt_thread(log_path, msg='Updating connected table...')
            self.connected_table.insert('', 'end', values=(item[0], endpoint.client_mac, endpoint.ip,
                                                           endpoint.ident, endpoint.user, endpoint.client_version),
                                        tags=(tag,))

    # Display Connection History
    def connection_history(self) -> bool:
        logIt_thread(log_path, msg=f'Running connection_history()...')
        logIt_thread(log_path, msg=f'Calling self.show_available_connections()...')
        self.show_available_connections()
        logIt_thread(log_path, msg=f'Calling self.disable_buttons_thread(sidebar=False)...')
        self.disable_buttons_thread()
        logIt_thread(log_path, msg=f'Calling self.create_connection_history_table()...')
        self.create_connection_history_table()

        self.update_statusbar_messages_thread(msg=f'Status: displaying connection history.')
        c = 0  # Initiate Counter for Connection Number
        try:
            for entry, t in self.server.connHistory.items():
                if c % 2 == 0:
                    self.history_table.insert('', 'end', values=(c, entry.client_mac, entry.ip,
                                                                 entry.ident, entry.user,
                                                                 t), tags=('evenrow',))
                else:
                    self.history_table.insert('', 'end', values=(c, entry.client_mac, entry.ip,
                                                                 entry.ident, entry.user,
                                                                 t), tags=('oddrow',))
                c += 1
                logIt_thread(log_path, msg=f'Stying table row colors...')
                self.history_table.tag_configure('oddrow', background='snow')
                self.history_table.tag_configure('evenrow', background='ghost white')

            return True

        except (KeyError, socket.error, ConnectionResetError) as e:
            logIt_thread(log_path, msg=f'ERROR: {e}')
            self.update_statusbar_messages_thread(msg=f'Status: {e}.')
            return False

    # Shell Connection to Client
    def shell(self, endpoint) -> None:
        logIt_thread(log_path, msg=f'Running shell({endpoint.conn}, {endpoint.ip})...')
        self.update_statusbar_messages_thread(msg=f'shell connected to {endpoint.ip} | {endpoint.ident}.')
        while True:
            # Wait for User Input & hide print
            logIt_thread(log_path, msg=f'Waiting for input...')
            cmd = input(f"")

            # Run Custom Command // FUTURE add-on for expert mode
            # if cmd == 100:
            #     logIt_thread(log_path, msg=f'Command: 100')
            #     try:
            #         logIt_thread(log_path, msg=f'Send freestyle command...')
            #         endpoint.conn.send("freestyle".encode())
            #         logIt_thread(log_path, msg=f'Send Completed.')
            #
            #     except (WindowsError, socket.error) as e:
            #         logIt_thread(log_path, msg=f'Connection Error: {e}')
            #         break
            #
            #     for item, connection in zip(server.tmp_availables, server.connections):
            #         for conKey, ipValue in server.clients.items():
            #             if conKey == connection:
            #                 for ipKey in ipValue.keys():
            #                     if item[1] == ipKey:
            #                         ipval = item[1]
            #                         host = item[2]
            #                         user = item[3]
            #
            #     logIt_thread(log_path, msg=f'Initializing Freestyle Module...')
            #     free = freestyle.Freestyle(con, path, server.tmp_availables, server.clients,
            #                                log_path, host, user)
            #     logIt_thread(log_path, msg=f'Calling freestyle module...')
            #     free.freestyle(ip)

    # ==++==++==++== MENUBAR ==++==++==++==
    # Restart All Clients
    def restart_all_clients_command(self):
        logIt_thread(log_path, msg=f'Running restart_all_clients()...')
        self.update_statusbar_messages_thread(msg=f'waiting for restart confirmation...')
        logIt_thread(log_path, msg=f'Displaying self.sure() popup window...')
        self.sure = messagebox.askyesno(f"Restart All Clients\t", "Are you sure?")
        logIt_thread(log_path, msg=f'self.sure = {self.sure}')

        if self.sure:
            for endpoint in self.server.endpoints:
                try:
                    endpoint.conn.send('restart'.encode())
                    msg = endpoint.conn.recv(1024).decode()
                    self.update_statusbar_messages_thread(msg=f"{msg}")
                    self.server.remove_lost_connection(endpoint)
                    refreshThread = Thread(target=self.refresh_command)
                    refreshThread.start()

                except (ConnectionResetError, socket.error):
                    continue

            refreshThread = Thread(target=self.refresh_command)
            refreshThread.start()
            time.sleep(0.5)

            messagebox.showinfo("Restart All Clients", "Done!\t\t\t\t")
            self.refresh_command()
            self.update_statusbar_messages_thread(msg='Restart command completed.')
            self.enable_buttons_thread()
            self.refresh_command()
            return True

        else:
            return False

    # Broadcast update command to all connected stations
    def update_all_clients_command(self) -> bool:
        logIt_thread(log_path, msg=f'Running update_all_clients()...')
        self.disable_buttons_thread()
        sure = messagebox.askyesno(f"Update All Clients", "Are you sure?")
        if sure:
            for endpoint in self.server.endpoints:
                try:
                    endpoint.conn.send('update'.encode())
                    logIt_thread(log_path, msg=f'Send Completed.')
                    logIt_thread(log_path,
                                 msg=f'Waiting for response from {endpoint.ip} | {endpoint.ident}...')
                    msg = endpoint.conn.recv(1024).decode()
                    logIt_thread(log_path, msg=f'{endpoint.ip}|{endpoint.ident}: {msg}')

                except (WindowsError, socket.error) as e:
                    logIt_thread(log_path, msg=f'ERROR: {e}.')
                    return False

            logIt_thread(log_path, msg=f'Displaying update info popup window...')
            messagebox.showinfo(f"Update {endpoint.ident}", "Update command sent.")
            self.refresh_command()
            self.enable_buttons_thread()
            return True

        else:
            return False

    # Show Help
    def show_help(self):
        github_url = 'https://github.com/GShwartz/HandsOff'
        return webbrowser.open_new_tab(github_url)

    # About Window
    def about(self, event=0) -> None:
        about = About()
        about.run()

    # Save History to file
    def save_connection_history(self, event=0) -> bool:
        logIt_thread(log_path, msg=f'Running self.save_connection_history()...')
        file_types = {'CSV Files': '.csv', 'TXT Files': '.txt'}

        # Create Saved Files Dir
        saves = fr"{path}\Saves"
        if not os.path.exists(saves):
            os.makedirs(saves)

        # Get Filename
        filename = filedialog.asksaveasfilename(initialdir=f"{saves}", defaultextension='.csv',
                                                filetypes=(('CSV files', '.csv'), ('TXT files', '.txt')))
        if len(filename) == 0 or str(filename) == '':
            logIt_thread(log_path, msg=f'Save canceled.')
            return False

        c = 0
        for name, ftype in file_types.items():
            if str(filename).endswith(ftype) and ftype == '.csv':
                header = ['MAC', 'IP', 'Station', 'User', 'Time']
                try:
                    with open(filename, 'w') as file:
                        writer = csv.writer(file)
                        writer.writerow(header)
                        for endpoint, dt in self.server.connHistory.items():
                            writer.writerow([endpoint.client_mac, endpoint.ip, endpoint.ident, endpoint.user, dt])
                        return True

                except Exception as e:
                    logIt_thread(log_path, msg=f'ERROR: {e}')
                    self.update_statusbar_messages_thread(msg=f'Status: {e}.')
                    return False

            else:
                try:
                    with open(filename, 'w') as file:
                        for endpoint, dt in self.server.connHistory.items():
                            file.write(f"#{c} | MAC: {endpoint.client_mac} | IP: {endpoint.ip} | "
                                       f"Station: {endpoint.ident} | User: {endpoint.user} | Time: {dt} \n")
                            c += 1
                        return True

                except Exception as e:
                    logIt_thread(log_path, msg=f'ERROR: {e}')
                    self.update_statusbar_messages_thread(msg=f'Status: {e}.')
                    return False

    # Manage Connected Table & Controller LabelFrame Buttons
    def select_item(self, event) -> bool:
        logIt_thread(log_path, msg=f'Running select_item()...')
        # Respond to mouse clicks on connected table
        rowid = self.connected_table.identify_row(event.y)
        row = self.connected_table.item(rowid)['values']
        if row:
            try:
                if row[2] not in self.temp.values():
                    logIt_thread(log_path, msg=f'Updating self.temp dictionary...')
                    self.temp[row[0]] = row[2]

            # Error can raise when clicking on empty space so the row is None or empty.
            except IndexError:
                pass

            logIt_thread(log_path, msg=f'Calling self.create_notebook()...')
            if not self.notebooks:
                self.create_notebook()

            # Create a Controller LabelFrame with Buttons and connect shell by TreeView Table selection
            for endpoint in self.server.endpoints:
                if row[2] == endpoint.ip:
                    temp_notebook = {endpoint.ident: {endpoint.ip: self.notebook}}
                    if temp_notebook not in self.notebooks.items():
                        self.notebooks.update(temp_notebook)

                    if not self.running:
                        self.build_controller_buttons(endpoint)
                        shellThread = Thread(target=self.shell,
                                             args=(endpoint,),
                                             daemon=True,
                                             name="Shell Thread")
                        shellThread.start()
                        shellThread.join(timeout=0.1)
                        if not shellThread.is_alive():
                            logIt_thread(log_path, msg=f'Disconnected from endpoint {endpoint.ip}...')
                            self.server.remove_lost_connection(endpoint)
                            self.temp.clear()
                            break

                        self.temp.clear()


def on_icon_clicked(icon, item):
    if str(item) == "About":
        app.about(event=0)

    if str(item) == "Restore":
        app.deiconify()

    if str(item) == "Exit":
        for t in app.targets:
            try:
                t.send('exit'.encode())

            except socket.error:
                pass

        app.destroy()


def logIt_thread(log_path=None, debug=False, msg='') -> None:
    logit_thread = Thread(target=logIt,
                          args=(log_path, debug, msg),
                          daemon=True,
                          name="Log Thread")
    logit_thread.start()


def bytes_to_number(b: int) -> int:
    logIt_thread(log_path, msg=f'Running bytes_to_number({b})...')
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


def main():
    icon_path = fr"{os.path.dirname(__file__)}\HandsOff.png"
    default_socket_timeout = None
    chkdsk_socket_timeout = 10
    sfc_socket_timeout = 5

    # Configure system tray icon
    icon_image = PIL.Image.open(icon_path)
    icon = pystray.Icon("HandsOff", icon_image, menu=pystray.Menu(
        pystray.MenuItem("About", on_icon_clicked),
        pystray.MenuItem("Restore", on_icon_clicked),
        pystray.MenuItem("Exit", on_icon_clicked)
    ))

    # Show system tray icon
    iconThread = Thread(target=icon.run,
                        daemon=True,
                        name="Icon Thread")
    iconThread.start()
    app.mainloop()


if __name__ == '__main__':
    port = 55400
    hostname = socket.gethostname()
    serverIP = str(socket.gethostbyname(hostname))
    path = r'c:\HandsOff'
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--ip', action='store', default=serverIP, type=str, help='Server IP')
    parser.add_argument('-p', '--port', action='store', default=port, type=int, help='Server Port')

    args = parser.parse_args()

    log_path = fr'{path}\server_log.txt'
    # local_tools = Locals()
    app = App()

    main()