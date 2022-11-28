from datetime import datetime
from threading import Thread
import PIL.ImageTk
import subprocess
import webbrowser
import PIL.Image
import argparse
import pystray
import os.path
import socket
import psutil
import time
import glob
import sys
import csv

# GUI
from tkinter import simpledialog
from tkinter import filedialog
from tkinter import messagebox
from tkinter import ttk
from tkinter import *
import tkinter as tk
import tkinter

# Secure
import hashlib
import sqlite3
import rsa

# Local Modules
from Modules import vital_signs
from Modules import screenshot
from Modules import freestyle
from Modules import sysinfo
from Modules import tasks


class App(tk.Tk):
    top_windows = []
    buttons = []
    sidebar_buttons = []
    social_buttons = []
    maintenance_buttons = []

    # List to hold captured screenshot images
    displayed_screenshot_files = []
    frames = []
    tabs = 0
    notebooks = {}

    # Temp dict to hold connected station's ID# & IP
    temp = {}

    WIDTH = 1150
    HEIGHT = 870

    def __init__(self):
        super().__init__()
        self.style = ttk.Style()
        self.update_url = StringVar()
        self.new_url = ''

        # ======== Server Config ==========
        # Start listener
        server.listener()

        # Create local app DIR
        if not os.path.exists(path):
            os.makedirs(path)

        # Run Listener Thread
        listenerThread = Thread(target=server.run,
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
        self.bind("<F10>", self.save_connection_history_thread)
        self.bind("<F11>", self.restart_all_clients_thread)
        self.bind("<F12>", self.update_all_clients_thread)

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
        self.build_controller_buttons(None, None, None)
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
        vitalsThread = Thread(target=server.vital_signs,
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
    def update_selected_client_thread(self, con: str, ip: str, sname: str):
        updateThread = Thread(target=self.update_selected_client_command,
                              args=(con, ip, sname),
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
    def client_system_information_thread(self, con: str, ip: str, sname: str):
        clientSystemInformationThread = Thread(target=self.sysinfo_command,
                                               args=(con, ip, sname),
                                               daemon=True,
                                               name="Client System Information Thread")
        clientSystemInformationThread.start()

    # Grab Screenshot
    def screenshot_thread(self, con: str, ip: str, sname: str):
        screenThread = Thread(target=self.screenshot_command,
                              args=(con, ip, sname),
                              daemon=True,
                              name='Screenshot Thread')
        screenThread.start()

    # Show Available Connections
    def show_available_connections_thread(self):
        historyThread = Thread(target=self.show_available_connections,
                               daemon=True,
                               name="Available Connections Thread")
        historyThread.start()

    def run_maintenance_thread(self, con: str, ip: str, sname: str):
        maintenanceThread = Thread(target=self.run_maintenance_command,
                                   args=(con, ip, sname),
                                   daemon=True,
                                   name="Run Maintenance Thread")
        maintenanceThread.start()

    # ==++==++==++== END THREADED FUNCS ==++==++==++== #

    # ==++==++==++== GUI ==++==++==++==
    # Define GUI Styles
    def make_style(self):
        local_tools.logIt_thread(log_path, msg=f'Styling App...')
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

    # Create Menubar
    def build_menubar(self):
        local_tools.logIt_thread(log_path, msg=f'Running build_menubar()...')
        menubar = Menu(self, tearoff=0)
        file = Menu(menubar, tearoff=0)
        tools = Menu(self, tearoff=0)
        helpbar = Menu(self, tearoff=0)

        file.add_command(label="Minimize", command=self.minimize)
        file.add_separator()
        file.add_command(label="Exit", command=self.on_closing)

        tools.add_command(label="Refresh                                   <F5>", command=self.refresh_command)
        tools.add_command(label="Clear Details                          <F6>", command=self.clear_notebook_command)
        tools.add_command(label="Save Connection History    <F10>", command=self.save_connection_history_thread)
        tools.add_command(label="Restart All Clients                 <F11>", command=self.restart_all_clients_thread)
        tools.add_command(label="Update All Clients                <F12>", command=self.update_all_clients_thread,
                          state=NORMAL)

        helpbar.add_command(label="Help", command=self.show_help_thread)
        helpbar.add_command(label="About", command=self.about)

        menubar.add_cascade(label='File', menu=file)
        menubar.add_cascade(label='Tools', menu=tools)
        menubar.add_cascade(label="Help", menu=helpbar)

        local_tools.logIt_thread(log_path, msg=f'Displaying Menubar...')
        self.config(menu=menubar)
        return

    # Build Main Frame GUI
    def build_main_window_frames(self) -> None:
        local_tools.logIt_thread(log_path, msg=f'Running build_main_window_frames()...')
        local_tools.logIt_thread(log_path, msg=f'Building main frame...')
        self.main_frame = Frame(self, relief="raised", bd=1)
        self.main_frame.configure(border=1)
        self.main_frame.grid(row=0, column=0, sticky="nswe", padx=1)
        self.main_frame.rowconfigure(5, weight=1)
        self.main_frame.columnconfigure(0, weight=1)

        local_tools.logIt_thread(log_path, msg=f'Building main frame top bar...')
        self.main_frame_top = Frame(self.main_frame, relief='flat')
        self.main_frame_top.grid(row=0, column=0, sticky="nwes")

        local_tools.logIt_thread(log_path, msg=f'Building main frame top bar labelFrame...')
        self.top_bar_label = LabelFrame(self.main_frame, text="Server Information", relief='solid',
                                        background='gainsboro')
        self.top_bar_label.grid(row=0, column=0, sticky='news')

        local_tools.logIt_thread(log_path, msg=f'Building table frame in main frame...')
        self.main_frame_table = Frame(self.main_frame, relief='flat')
        self.main_frame_table.grid(row=1, column=0, sticky="news", pady=2)

        local_tools.logIt_thread(log_path, msg=f'Building controller frame in main frame...')
        self.controller_frame = Frame(self.main_frame, relief='flat', background='gainsboro', height=60)
        self.controller_frame.grid(row=2, column=0, sticky='news', pady=2)

        local_tools.logIt_thread(log_path,
                                 msg=f'Building controller buttons label frame in main frame...')
        self.controller_btns = LabelFrame(self.controller_frame, text="Controller", relief='solid', height=60,
                                          background='gainsboro')
        self.controller_btns.pack(fill=BOTH)

        local_tools.logIt_thread(log_path, msg=f'Building connected table in main frame...')
        self.table_frame = LabelFrame(self.main_frame_table, text="Connected Stations",
                                      relief='solid', background='gainsboro')
        self.table_frame.pack(fill=BOTH)

        local_tools.logIt_thread(log_path, msg=f'Building details frame in main frame...')
        self.details_frame = Frame(self.main_frame, relief='flat', pady=2, height=310)
        self.details_frame.grid(row=3, column=0, sticky='news')

        local_tools.logIt_thread(log_path, msg=f'Building details LabelFrame...')
        self.details_labelFrame = LabelFrame(self.main_frame, text="Details", relief='solid',
                                             height=250, background='slate gray')
        self.details_labelFrame.grid(row=3, column=0, sticky='news')

        local_tools.logIt_thread(log_path, msg=f'Building statusbar frame in main frame...')
        self.statusbar_frame = Frame(self.main_frame, relief=SUNKEN, bd=1)
        self.statusbar_frame.grid(row=5, column=0, sticky='news')

        local_tools.logIt_thread(log_path, msg=f'Building statusbar label frame in main frame...')
        self.status_label = Label(self.statusbar_frame, text='Status', relief=FLAT, anchor=W)
        self.status_label.pack(fill=BOTH)

    # Create Treeview Table for connected stations
    def build_connected_table(self) -> None:
        def highlight(event):
            self.connected_table = event.widget
            item = self.connected_table.identify_row(event.y)
            self.connected_table.tk.call(self.connected_table, "tag", "remove", "highlight")
            self.connected_table.tk.call(self.connected_table, "tag", "add", "highlight", item)

        local_tools.logIt_thread(log_path, msg=f'Running build_connected_table()...')
        local_tools.logIt_thread(log_path, msg=f'Displaying Scrollbar...')
        self.table_sb = Scrollbar(self.table_frame, orient=VERTICAL)
        self.table_sb.pack(side=LEFT, fill=Y)
        local_tools.logIt_thread(log_path, msg=f'Displaying connected table...')
        self.connected_table = ttk.Treeview(self.table_frame,
                                            columns=("ID", "MAC Address",
                                                     "IP Address", "Station Name",
                                                     "Logged User", "Client Version"),
                                            show="headings", height=7,
                                            selectmode='browse', yscrollcommand=self.table_sb.set)
        self.connected_table.pack(fill=BOTH)
        self.table_sb.config(command=self.connected_table.yview)
        local_tools.logIt_thread(log_path, msg=f'Defining highlight event for Connected Table...')
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

        local_tools.logIt_thread(log_path, msg=f'Stying table row colors...')
        self.connected_table.tag_configure('oddrow', background='snow')
        self.connected_table.tag_configure('evenrow', background='ghost white')

    # Create Controller Buttons
    def build_controller_buttons(self, clientConn, clientIP, sname):
        local_tools.logIt_thread(log_path, msg=f'Building refresh button...')
        refresh_img = PIL.ImageTk.PhotoImage(
            PIL.Image.open('images/refresh_green.png').resize((17, 17), PIL.Image.ANTIALIAS))

        self.refresh_btn = Button(self.controller_btns, text=" Refresh", image=refresh_img,
                                  compound=LEFT, anchor=W,
                                  width=75, pady=5, command=self.refresh_command)
        self.refresh_btn.image = refresh_img
        self.refresh_btn.grid(row=0, column=0, pady=5, padx=2)

        local_tools.logIt_thread(log_path, msg=f'Building screenshot button...')
        self.screenshot_btn = Button(self.controller_btns, text="Screenshot", width=10,
                                     pady=5, padx=10,
                                     command=lambda: self.screenshot_thread(clientConn,
                                                                            clientIP,
                                                                            sname))
        self.screenshot_btn.grid(row=0, column=1, sticky="w", pady=5, padx=2, ipadx=2)
        local_tools.logIt_thread(log_path, msg=f'Updating controller buttons list...')
        self.buttons.append(self.screenshot_btn)
        local_tools.logIt_thread(log_path, msg=f'Building anydesk button...')
        self.anydesk_btn = Button(self.controller_btns, text="Anydesk", width=14, pady=5,
                                  command=lambda: self.anydesk_command(clientConn, clientIP, sname))
        self.anydesk_btn.grid(row=0, column=2, sticky="w", pady=5, padx=2, ipadx=2)
        local_tools.logIt_thread(log_path,
                                 msg=f'Updating controller buttons list...')
        self.buttons.append(self.anydesk_btn)
        local_tools.logIt_thread(log_path, msg=f'Building last restart button...')
        self.last_restart_btn = Button(self.controller_btns, text="Last Restart", width=14,
                                       pady=5,
                                       command=lambda: self.last_restart_command(clientConn, clientIP,
                                                                                 sname))
        self.last_restart_btn.grid(row=0, column=3, sticky="w", pady=5, padx=2, ipadx=2)
        local_tools.logIt_thread(log_path, msg=f'Updating controller buttons list...')
        self.buttons.append(self.last_restart_btn)
        local_tools.logIt_thread(log_path,
                                 msg=f'Building system information button...')
        self.sysinfo_btn = Button(self.controller_btns, text="SysInfo", width=14, pady=5,
                                  command=lambda: self.client_system_information_thread(
                                      clientConn, clientIP, sname))
        self.sysinfo_btn.grid(row=0, column=4, sticky="w", pady=5, padx=2, ipadx=2)
        local_tools.logIt_thread(log_path, msg=f'Updating controller buttons list...')
        self.buttons.append(self.sysinfo_btn)
        local_tools.logIt_thread(log_path, msg=f'Building tasks button...')
        self.tasks_btn = Button(self.controller_btns, text="Tasks", width=14, pady=5,
                                command=lambda: self.tasks(clientConn, clientIP, sname))
        self.tasks_btn.grid(row=0, column=5, sticky="w", pady=5, padx=2, ipadx=2)
        local_tools.logIt_thread(log_path, msg=f'Updating controller buttons list...')
        self.buttons.append(self.tasks_btn)
        local_tools.logIt_thread(log_path, msg=f'Building restart button...')
        self.restart_btn = Button(self.controller_btns, text="Restart", width=14, pady=5,
                                  command=lambda: self.restart_command(clientConn, clientIP, sname))
        self.restart_btn.grid(row=0, column=6, sticky="w", pady=5, padx=2, ipadx=2)
        local_tools.logIt_thread(log_path, msg=f'Updating controller buttons list...')
        self.buttons.append(self.restart_btn)

        local_tools.logIt_thread(log_path, msg=f'Building local files button...')
        self.browse_btn = Button(self.controller_btns, text="Local Files", width=14, pady=5,
                                 command=lambda: self.browse_local_files_command(sname))
        self.browse_btn.grid(row=0, column=7, sticky="w", pady=5, padx=2, ipadx=2)
        self.buttons.append(self.browse_btn)

        local_tools.logIt_thread(log_path, msg=f'Building Update Client button...')
        self.update_client = Button(self.controller_btns, text="Update Client", width=14,
                                    pady=5, state=DISABLED,
                                    command=lambda: self.update_selected_client_thread(
                                        clientConn, clientIP, sname))
        self.update_client.grid(row=0, column=8, sticky="w", pady=5, padx=2, ipadx=2)
        # self.buttons.append(self.update_client)

        local_tools.logIt_thread(log_path, msg=f'Building Maintenance button...')
        self.maintenance = Button(self.controller_btns, text="Maintenance", width=14,
                                  pady=5, state=DISABLED,
                                  command=lambda: self.run_maintenance_thread(clientConn, clientIP, sname))
        self.maintenance.grid(row=0, column=9, sticky="w", pady=5, padx=2, ipadx=2)
        # self.buttons.append(self.maintenance)

    # Build Table for Connection History
    def create_connection_history_table(self) -> None:
        local_tools.logIt_thread(log_path, msg=f'Running create_connection_history_table()...')
        local_tools.logIt_thread(log_path, msg=f'Displaying connection history labelFrame...')
        self.history_labelFrame = LabelFrame(self.main_frame, text="Connection History",
                                             relief='solid', background='gainsboro')
        self.history_labelFrame.grid(row=4, column=0, sticky='news')
        local_tools.logIt_thread(log_path, msg=f'Displaying Scrollbar in history labelFrame...')
        self.history_table_scrollbar = Scrollbar(self.history_labelFrame, orient=VERTICAL)
        self.history_table_scrollbar.pack(side=LEFT, fill=Y)
        local_tools.logIt_thread(log_path, msg=f'Displaying connection history table in labelFrame...')
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

        local_tools.logIt_thread(log_path, msg=f'Building details LabelFrame...')
        self.details_labelFrame = LabelFrame(self.main_frame, text="Details", relief='solid',
                                             height=400, background='slate gray')
        self.details_labelFrame.grid(row=3, sticky='news', columnspan=3)

        local_tools.logIt_thread(log_path, msg=f'Clearing frames list...')
        self.frames.clear()

        local_tools.logIt_thread(log_path, msg=f'Building notebook...')
        self.notebook = ttk.Notebook(self.details_labelFrame, height=250)
        self.notebook.pack(expand=True, pady=5, fill=X)
        self.notebook.bind("<<NotebookTabChanged>>", on_tab_change)

        local_tools.logIt_thread(log_path, msg=f'Building tabs...')
        self.screenshot_tab = Frame(self.notebook, height=330)

        self.system_information_tab = Frame(self.notebook, height=330)
        self.tasks_tab = Frame(self.notebook, height=330)

        local_tools.logIt_thread(log_path, msg=f'Building sysinfo scrollbar...')
        self.system_scrollbar = Scrollbar(self.system_information_tab, orient=VERTICAL)
        self.system_scrollbar.pack(side=LEFT, fill=Y)

        local_tools.logIt_thread(log_path, msg=f'Building sysinfo textbox...')
        self.system_information_textbox = Text(self.system_information_tab,
                                               yscrollcommand=self.system_scrollbar.set)
        self.system_information_textbox.pack(fill=BOTH)
        local_tools.logIt_thread(log_path, msg=f'Building tasks scrollbar...')
        self.tasks_scrollbar = Scrollbar(self.tasks_tab, orient=VERTICAL)
        self.tasks_scrollbar.pack(side=LEFT, fill=Y)

        local_tools.logIt_thread(log_path, msg=f'Building tasks textbox...')
        self.tasks_tab_textbox = Text(self.tasks_tab, yscrollcommand=self.tasks_scrollbar.set)
        self.tasks_tab_textbox.pack(fill=X)

    # Update Status Bar Messages
    def update_statusbar_messages(self, msg=''):
        self.status_label.config(text=f"Status: {msg}")

    # Close App
    def on_closing(self, event=0) -> None:
        local_tools.logIt_thread(log_path, msg=f'Displaying minimize popup window...')
        minimize = messagebox.askyesno("Exit or Minimize", "Minimize to Tray?")
        local_tools.logIt_thread(log_path, msg=f'Minimize: {minimize}')
        if minimize:
            local_tools.logIt_thread(log_path, msg=f'Hiding app window...')
            self.withdraw()

        else:
            local_tools.logIt_thread(log_path, msg=f'Hiding app window...')
            self.withdraw()
            local_tools.logIt_thread(log_path, msg=f'Destroying app window...')
            if len(server.targets) > 0:
                for t in server.targets:
                    try:
                        t.send('exit'.encode())

                    except socket.error:
                        pass

            self.destroy()

    # Minimize Window
    def minimize(self):
        return self.withdraw()

    # Enable Controller Buttons
    def enable_buttons(self):
        local_tools.logIt_thread(log_path, msg=f'Running enable_buttons()...')
        for button in list(self.buttons):
            local_tools.logIt_thread(log_path, msg=f'Enabling {button.config("text")[-1]} button...')
            button.config(state=NORMAL)

        for sbutton in list(self.sidebar_buttons):
            local_tools.logIt_thread(log_path,
                                     msg=f'Enabling sidebar {sbutton.config("text")[-1]} button...')
            sbutton.config(state=NORMAL)

    # Disable Controller Buttons
    def disable_buttons(self):
        local_tools.logIt_thread(log_path, msg=f'Running disable_buttons(sidebar=None)...')
        for button in list(self.buttons):
            local_tools.logIt_thread(log_path, msg=f'Disabling {button.config("text")[-1]}...')
            button.config(state=DISABLED)

        return

    # Display file content in notebook
    def display_file_content(self, screenshot_path: str, filepath: str, tab: str, sname: str, txt='') -> bool:
        local_tools.logIt_thread(log_path,
                                 msg=f'Running display_file_content({screenshot_path}, {filepath}, {tab}, txt="")...')

        def text():
            local_tools.logIt_thread(log_path, msg=f'opening {filepath}...')
            with open(filepath, 'r') as file:
                data = file.read()
                local_tools.logIt_thread(log_path, msg=f'Building notebook tab...')
                tab = Frame(self.notebook, height=350)

                local_tools.logIt_thread(log_path, msg=f'Building text scrollbar...')
                self.tab_scrollbar = Scrollbar(tab, orient=VERTICAL)
                self.tab_scrollbar.pack(side=LEFT, fill=Y)

                local_tools.logIt_thread(log_path, msg=f'Building text Textbox...')
                self.tab_textbox = Text(tab, yscrollcommand=self.tab_scrollbar.set)
                self.tab_textbox.pack(fill=BOTH)

                local_tools.logIt_thread(log_path, msg=f'Adding tab to notebook...')
                self.notebook.add(tab, text=f"{txt} {sname}")

                local_tools.logIt_thread(log_path, msg=f'Enabling scroller buttons...')
                self.tab_scrollbar.configure(command=self.tab_textbox.yview)
                local_tools.logIt_thread(log_path, msg=f'Enabling textbox entry...')
                self.tab_textbox.config(state=NORMAL)
                local_tools.logIt_thread(log_path, msg=f'Clearing textbox...')
                self.tab_textbox.delete(1.0, END)
                local_tools.logIt_thread(log_path, msg=f'Inserting file content to Textbox...')
                self.tab_textbox.insert(END, data)
                local_tools.logIt_thread(log_path, msg=f'Disabling Textbox entry...')
                self.tab_textbox.config(state=DISABLED)

                local_tools.logIt_thread(log_path, msg=f'Displaying latest notebook tab...')
                self.notebook.select(tab)
                self.tabs += 1
                return True

        def picture():
            local_tools.logIt_thread(log_path, msg=f'Building working frame...')
            fr = Frame(self.notebook, height=350, background='slate gray')
            self.frames.append(fr)
            tab = self.frames[-1]
            local_tools.logIt_thread(log_path, msg=f'Building Preview Button...')
            button = Button(tab, image=self.last_screenshot, command=show_picture_thread, border=5, bd=3)
            button.pack(padx=5, pady=10)
            local_tools.logIt_thread(log_path, msg=f'Adding tab to notebook...')
            self.notebook.add(tab, text=f"{txt} {sname}")

            local_tools.logIt_thread(log_path, msg=f'Displaying latest notebook tab...')
            self.notebook.select(tab)
            self.tabs += 1
            return True

        def show_picture_thread():
            showThread = Thread(target=show_picture, daemon=True, name="Show Picture Thread")
            showThread.start()

        def show_picture():
            self.sc.show()

        if len(filepath) > 0 and filepath.endswith('.txt'):
            local_tools.logIt_thread(log_path, msg=f'Calling text()...')
            text()

        elif len(screenshot_path) > 0:
            local_tools.logIt_thread(log_path, msg=f'Sorting jpg files by creation time...')
            images = glob.glob(fr"{screenshot_path}\*.jpg")
            images.sort(key=os.path.getmtime)

            # Last Screenshot
            local_tools.logIt_thread(log_path, msg=f'Opening latest screenshot...')
            self.sc = PIL.Image.open(images[-1])
            local_tools.logIt_thread(log_path, msg=f'Resizing to 650x350...')
            self.sc_resized = self.sc.resize((650, 350))
            self.last_screenshot = PIL.ImageTk.PhotoImage(self.sc_resized)
            self.displayed_screenshot_files.append(self.last_screenshot)

            if self.tabs > 0:
                local_tools.logIt_thread(log_path, msg=f'Calling picture()...')
                picture()

            else:
                local_tools.logIt_thread(log_path, msg=f'Building working frame...')
                tab = Frame(self.notebook, height=350, background='slate gray')

                local_tools.logIt_thread(log_path, msg=f'Building Preview Button...')
                button = Button(tab, image=self.last_screenshot, command=show_picture_thread, border=5, bd=3)
                button.pack(padx=5, pady=10)

                local_tools.logIt_thread(log_path, msg=f'Adding tab to notebook...')
                self.notebook.add(tab, text=f"{txt} {sname}")

                local_tools.logIt_thread(log_path, msg=f'Displaying latest notebook tab...')
                self.notebook.select(tab)
                self.tabs += 1
                return True

    # ==++==++==++== CONTROLLER BUTTONS COMMANDS==++==++==++==
    # Refresh server info & connected stations table with vital signs
    def refresh_command(self, event=0) -> None:
        local_tools.logIt_thread(log_path, msg=f'Running refresh()...')
        local_tools.logIt_thread(log_path, msg=f'Calling self_disable_buttons_thread(sidebar=False)...')
        self.disable_buttons_thread()
        local_tools.logIt_thread(log_path, msg=f'Resetting self.tmp_availables list...')
        server.tmp_availables = []
        local_tools.logIt_thread(log_path, msg=f'Calling self.vital_signs_thread()...')
        self.vital_signs_thread()
        local_tools.logIt_thread(log_path, msg=f'Calling self.server_information()...')
        self.server_information()
        local_tools.logIt_thread(log_path, msg=f'Calling self.show_available_connections()...')
        self.show_available_connections()
        local_tools.logIt_thread(log_path, msg=f'Calling connection_history()...')
        self.connection_history()
        self.update_statusbar_messages_thread(msg='refresh complete.')

    # Clear Notebook
    def clear_notebook_command(self, event=0):
        self.create_notebook()
        self.update_statusbar_messages_thread(msg='Details window cleared.')
        return

    # Screenshot from Client
    def screenshot_command(self, con: str, ip: str, sname: str) -> bool:
        local_tools.logIt_thread(log_path, msg=f'Running screenshot({con}, {ip}, {sname})...')
        local_tools.logIt_thread(log_path, msg=f'Calling self.disable_buttons_thread()...')
        self.disable_buttons_thread()
        self.update_statusbar_messages_thread(msg=f'fetching screenshot from {ip} | {sname}...')
        try:
            local_tools.logIt_thread(log_path, msg=f'Sending screen command to client...')
            con.send('screen'.encode())
            local_tools.logIt_thread(log_path, msg=f'Send Completed.')
            local_tools.logIt_thread(log_path, msg=f'Initializing screenshot module...')
            scrnshot = screenshot.Screenshot(con, path, server.tmp_availables,
                                             server.clients, log_path, server.targets)
            local_tools.logIt_thread(log_path, msg=f'Calling screenshot.recv_file({ip})...')
            scrnshot.recv_file(ip)
            self.update_statusbar_messages_thread(msg=f'screenshot received from  {ip} | {sname}.')
            local_tools.logIt_thread(log_path,
                                     msg=fr'Calling self.display_file_content({path}\{sname}, "", {self.screenshot_tab}, txt="Screenshot")...')
            self.display_file_content(fr"{path}\{sname}", '', self.screenshot_tab,
                                      txt='Screenshot', sname=sname)
            local_tools.logIt_thread(log_path, msg=f'Calling self.enable_buttons_thread()...')
            self.enable_buttons_thread()
            return True

        except (WindowsError, socket.error, ConnectionResetError) as e:
            local_tools.logIt_thread(log_path, msg=f'Connection Error: {e}')
            self.update_statusbar_messages_thread(msg=f'{e}.')
            local_tools.logIt_thread(log_path, msg=f'Calling server.remove_lost_connection({con}, {ip}...)')
            server.remove_lost_connection(con, ip)
            return False

    # Run Anydesk on Client
    def anydesk_command(self, con: str, ip: str, sname: str) -> bool:
        local_tools.logIt_thread(log_path, msg=f'Running anydesk({con}, {ip})...')
        self.update_statusbar_messages_thread(msg=f'running anydesk on {ip} | {sname}...')
        try:
            local_tools.logIt_thread(log_path, msg=f'Sending anydesk command to {con}...')
            con.send('anydesk'.encode())
            local_tools.logIt_thread(log_path, msg=f'Send Completed.')

            local_tools.logIt_thread(log_path, msg=f'Waiting for response from client...')
            msg = con.recv(1024).decode()
            local_tools.logIt_thread(log_path, msg=f'Client response: {msg}.')
            if "OK" not in msg:
                local_tools.logIt_thread(log_path, msg=f'Printing msg from client...')
                self.update_statusbar_messages_thread(msg=f'{ip} | {sname}: Anydesk not installed.')
                local_tools.logIt_thread(log_path, msg=f'Display popup confirmation for install anydesk...')
                install_anydesk = messagebox.askyesno("Install Anydesk",
                                                      "Anydesk isn't installed on the remote machine. do you with to install?")
                local_tools.logIt_thread(log_path, msg=f'Install anydesk: {install_anydesk}.')
                if install_anydesk:
                    self.update_statusbar_messages_thread(msg=f'installing anydesk on {ip} | {sname}...')
                    local_tools.logIt_thread(log_path, msg=f'Sending install command to {con}...')
                    con.send('y'.encode())
                    local_tools.logIt_thread(log_path, msg=f'Send Completed.')
                    local_tools.logIt_thread(log_path, msg=f'Initiating StringVar() for textVar...')
                    textVar = StringVar()
                    while True:
                        local_tools.logIt_thread(log_path, msg=f'Waiting for response from client...')
                        msg = con.recv(1024).decode()
                        local_tools.logIt_thread(log_path, msg=f'Client response: {msg}.')
                        textVar.set(msg)
                        local_tools.logIt_thread(log_path, msg=f'textVar: {textVar}')
                        if "OK" not in str(msg):
                            self.update_statusbar_messages_thread(msg=f'{msg}')

                        else:
                            self.update_statusbar_messages_thread(msg=f'Status: {textVar}')
                            local_tools.logIt_thread(log_path, msg=f'Display popup infobox')
                            messagebox.showinfo(f"From {ip} | {sname}", f"Anydesk Running.\t\t\t\t")
                            self.update_statusbar_messages_thread(msg=f'anydesk running on {ip} | {sname}.')
                            return True

                else:
                    local_tools.logIt_thread(log_path, msg=f'Sending cancel command to {con}...')
                    con.send('n'.encode())
                    local_tools.logIt_thread(log_path, msg=f'Send Completed.')
                    return

            else:
                self.update_statusbar_messages_thread(msg=f'anydesk running on {ip} | {sname}.')
                local_tools.logIt_thread(log_path, msg=f'Displaying popup window with "Anydesk Running"...')
                messagebox.showinfo(f"From {ip} | {sname}", f"Anydesk Running.\t\t\t\t")
                return True

        except (WindowsError, ConnectionError, socket.error, RuntimeError) as e:
            local_tools.logIt_thread(log_path, msg=f'Connection Error: {e}.')
            self.update_statusbar_messages_thread(msg=f'{e}.')
            local_tools.logIt_thread(log_path, msg=f'Calling server.remove_lost_connection({con}, {ip})...')
            server.remove_lost_connection(con, ip)
            return False

    # Display Clients Last Restart
    def last_restart_command(self, con: str, ip: str, sname: str) -> bool:
        local_tools.logIt_thread(log_path, msg=f'Running last_restart({con}, {ip}, {sname})...')
        try:
            local_tools.logIt_thread(log_path, msg=f'Sending lr command to client...')
            con.send('lr'.encode())
            local_tools.logIt_thread(log_path, msg=f'Send Completed.')
            local_tools.logIt_thread(log_path, msg=f'Waiting for response from client...')
            msg = con.recv(4096).decode()
            local_tools.logIt_thread(log_path, msg=f'Client response: {msg}')
            self.update_statusbar_messages_thread(msg=f'restart for {sname}: {msg.split("|")[1][15:]}')
            local_tools.logIt_thread(log_path, msg=f'Display popup with last restart info...')
            messagebox.showinfo(f"Last Restart for: {ip} | {sname}", f"\t{msg.split('|')[1][15:]}\t\t\t")
            return True

        except (WindowsError, socket.error, ConnectionResetError) as e:
            local_tools.logIt_thread(log_path, msg=f'Connection Error: {e}.')
            self.update_statusbar_messages_thread(msg=f'{e}')
            local_tools.logIt_thread(log_path, msg=f'Calling server.remove_lost_connection({con}, {ip})...')
            server.remove_lost_connection(con, ip)
            return False

    # Client System Information
    def sysinfo_command(self, con: str, ip: str, sname: str):
        local_tools.logIt_thread(log_path, msg=f'Running self.sysinfo({con}, {ip}, {sname})...')
        local_tools.logIt_thread(log_path, msg=f'Calling self.disable_buttons_thread(sidebar=True)...')
        self.disable_buttons_thread()
        self.update_statusbar_messages_thread(msg=f'waiting for system information from {ip} | {sname}...')
        try:
            local_tools.logIt_thread(log_path, msg=f'Initializing Module: sysinfo...')
            sinfo = sysinfo.Sysinfo(con, server.ttl, self.path, server.tmp_availables,
                                    server.clients, server.log_path, ip)
            local_tools.logIt_thread(log_path, msg=f'Calling sysinfo.run()...')
            filepath = sinfo.run(ip)
            self.update_statusbar_messages_thread(msg=f'system information file received from {ip} | {sname}.')
            local_tools.logIt_thread(log_path,
                                     msg=f'Calling self.display_file_content(None, {filepath}, {self.system_information_tab}, txt="System Information")...')
            self.display_file_content(None, filepath, self.system_information_tab,
                                      txt='System Information', sname=sname)
            local_tools.logIt_thread(log_path, msg=f'Calling self.enable_buttons_thread()...')
            self.enable_buttons_thread()

        except (WindowsError, socket.error, ConnectionResetError) as e:
            local_tools.logIt_thread(log_path, debug=True, msg=f'Connection Error: {e}.')
            self.update_statusbar_messages_thread(msg=f'{e}.')
            try:
                local_tools.logIt_thread(log_path, msg=f'Calling server.remove_lost_connection({con}, {ip})...')
                server.remove_lost_connection(con, ip)
                local_tools.logIt_thread(log_path, msg=f'Calling self.enable_buttons_thread...')
                self.enable_buttons_thread()
                return

            except RuntimeError:
                local_tools.logIt_thread(log_path, msg=f'Calling self.enable_buttons_thread...')
                self.enable_buttons_thread()
                return

    # Display/Kill Tasks on Client
    def tasks(self, con: str, ip: str, sname: str) -> bool:
        def what_task(filepath) -> str:
            local_tools.logIt_thread(log_path, msg=f'Waiting for task name...')
            task_to_kill = simpledialog.askstring(parent=self, title='Task To Kill', prompt="Task to kill\t\t\t\t")
            local_tools.logIt_thread(log_path, msg=f'Task Name: {task_to_kill}.')
            if task_to_kill is None:
                try:
                    local_tools.logIt_thread(log_path, msg=f'Sending "n" to {ip}...')
                    con.send('n'.encode())
                    local_tools.logIt_thread(log_path, msg=f'Send completed.')
                    local_tools.logIt_thread(log_path, msg=f'Calling self.enable_buttons_thread()...')
                    self.enable_buttons_thread()
                    local_tools.logIt_thread(log_path, msg=f'Displaying warning popup window..')
                    messagebox.showwarning(f"From {ip} | {sname}", "Task Kill canceled.\t\t\t\t\t\t\t\t")
                    local_tools.logIt_thread(log_path, msg=f'Warning received.')
                    return False

                except (WindowsError, socket.error) as e:
                    local_tools.logIt_thread(log_path, msg=f'Error: {e}.')
                    self.update_statusbar_messages_thread(msg=f"{e}")
                    local_tools.logIt_thread(log_path, msg=f'Calling server.remove_lost_connection({con}, {ip})...')
                    server.remove_lost_connection(con, ip)
                    local_tools.logIt_thread(log_path, msg=f'Calling self.enable_buttons_thread()...')
                    self.enable_buttons_thread()
                    return False

            if len(task_to_kill) == 0:
                try:
                    local_tools.logIt_thread(log_path, msg=f'Sending "n" to {ip}...')
                    con.send('n'.encode())
                    local_tools.logIt_thread(log_path, msg=f'Send completed.')
                    local_tools.logIt_thread(log_path, msg=f'Calling self.enable_buttons_thread()...')
                    self.enable_buttons_thread()
                    local_tools.logIt_thread(log_path, msg=f'Displaying warning popup window...')
                    messagebox.showwarning(f"From {ip} | {sname}", "Task Kill canceled.\t\t\t\t\t\t\t\t")
                    return False

                except (WindowsError, socket.error) as e:
                    local_tools.logIt_thread(log_path, msg=f'Error: {e}.')
                    self.update_statusbar_messages_thread(msg=f"{e}")
                    local_tools.logIt_thread(log_path,
                                             msg=f'Calling server.remove_lost_connection({con}, {ip})...')
                    server.remove_lost_connection(con, ip)
                    local_tools.logIt_thread(log_path, msg=f'Calling self.enable_buttons_thread()...')
                    self.enable_buttons_thread()
                    return False

            if not str(task_to_kill).endswith('.exe'):
                try:
                    local_tools.logIt_thread(log_path, msg=f'Calling sysinfo.run()...')
                    con.send('n'.encode())
                    local_tools.logIt_thread(log_path, msg=f'Send completed.')
                    local_tools.logIt_thread(log_path, msg=f'Calling self.enable_buttons_thread()...')
                    self.enable_buttons_thread()
                    local_tools.logIt_thread(log_path, msg=f'Displaying warning popup window...')
                    messagebox.showwarning(f"From {ip} | {sname}", "Task Kill canceled.\t\t\t\t\t\t\t\t")
                    return False

                except (WindowsError, socket.error) as e:
                    local_tools.logIt_thread(log_path, msg=f'Error: {e}.')
                    self.update_statusbar_messages_thread(msg=f"{e}")
                    local_tools.logIt_thread(log_path, msg=f'Calling server.remove_lost_connection({con}, {ip})...')
                    server.remove_lost_connection(con, ip)
                    return False

            local_tools.logIt_thread(log_path, msg=f'Calling self.enable_buttons_thread()...')
            self.enable_buttons_thread()
            return task_to_kill

        def kill_task(task_to_kill):
            try:
                local_tools.logIt_thread(log_path, msg=f'Sending kill command to {ip}.')
                con.send('kill'.encode())
                local_tools.logIt_thread(log_path, msg=f'Send complete.')

            except (WindowsError, socket.error) as e:
                local_tools.logIt_thread(log_path, msg=f'Error: {e}.')
                self.update_statusbar_messages_thread(msg=f'{e}.')
                local_tools.logIt_thread(log_path, msg=f'Calling server.remove_lost_connection({con}, {ip})')
                server.remove_lost_connection(con, ip)
                return False

            try:
                local_tools.logIt_thread(log_path, msg=f'Sending {task_to_kill} to {ip}...')
                con.send(task_to_kill.encode())
                local_tools.logIt_thread(log_path, msg=f'Send complete.')

            except (WindowsError, socket.error) as e:
                local_tools.logIt_thread(log_path, msg=f'Error: {e}.')
                self.update_statusbar_messages_thread(msg=f'{e}.')
                local_tools.logIt_thread(log_path, msg=f'Calling server.remove_lost_connection({con}, {ip})')
                server.remove_lost_connection(con, ip)
                return False

            try:
                local_tools.logIt_thread(log_path, msg=f'Waiting for confirmation from {ip}...')
                msg = con.recv(1024).decode()
                local_tools.logIt_thread(log_path, msg=f'{ip}: {msg}')

            except (WindowsError, socket.error) as e:
                local_tools.logIt_thread(log_path, msg=f'Error: {e}.')
                self.update_statusbar_messages_thread(msg=f'{e}.')
                local_tools.logIt_thread(log_path, msg=f'Calling server.remove_lost_connection({con}, {ip})')
                server.remove_lost_connection(con, ip)
                return False

            local_tools.logIt_thread(log_path, msg=f'Displaying {msg} in popup window...')
            messagebox.showinfo(f"From {ip} | {sname}", f"{msg}.\t\t\t\t\t\t\t\t")
            local_tools.logIt_thread(log_path, msg=f'Message received.')
            self.update_statusbar_messages_thread(msg=f'killed task {task_to_kill} on {ip} | {sname}.')
            local_tools.logIt_thread(log_path, msg=f'Calling self.enable_buttons_thread()...')
            self.enable_buttons_thread()
            return True

        # Disable controller buttons
        local_tools.logIt_thread(log_path, msg=f'Calling self.disable_buttons_thread()...')
        self.disable_buttons_thread()
        self.update_statusbar_messages_thread(msg=f'running tasks command on {ip} | {sname}.')
        local_tools.logIt_thread(log_path, debug=False, msg=f'Initializing Module: tasks...')
        tsks = tasks.Tasks(con, ip, server.clients, server.connections,
                           server.targets, server.ips, server.tmp_availables,
                           log_path, path, sname)
        local_tools.logIt_thread(log_path, debug=False, msg=f'Calling tasks.tasks()...')
        filepath = tsks.tasks(ip)
        local_tools.logIt_thread(log_path, msg=f'filepath: {filepath}')

        local_tools.logIt_thread(log_path,
                                 msg=f'Calling self.display_file_content(None, {filepath}, {self.system_information_tab}, txt="Tasks")...')
        self.display_file_content(None, filepath, self.system_information_tab,
                                  txt='Tasks', sname=sname)
        local_tools.logIt_thread(log_path, msg=f'Displaying popup to kill a task...')
        killTask = messagebox.askyesno(f"Tasks from {ip} | {sname}", "Kill Task?\t\t\t\t\t\t\t\t")
        local_tools.logIt_thread(log_path, msg=f'Kill task: {killTask}.')
        if killTask:
            local_tools.logIt_thread(log_path, msg=f'Calling what_task({filepath})')
            task_to_kill = what_task(filepath)
            if str(task_to_kill) == '' or str(task_to_kill).startswith(' '):
                local_tools.logIt_thread(log_path, msg=f'task_to_kill: {task_to_kill}')
                local_tools.logIt_thread(log_path, msg=f'Calling self.enable_buttons_thread()...')
                self.enable_buttons_thread()
                return False

            if not task_to_kill:
                local_tools.logIt_thread(log_path, msg=f'Calling self.enable_buttons_thread()...')
                self.enable_buttons_thread()
                return False

            local_tools.logIt_thread(log_path, msg=f'Displaying popup for kill confirmation...')
            confirmKill = messagebox.askyesno(f'Kill task: {task_to_kill} on {sname}',
                                              f'Are you sure you want to kill {task_to_kill}?')
            local_tools.logIt_thread(log_path, msg=f'Kill confirmation: {confirmKill}.')
            if confirmKill:
                local_tools.logIt_thread(log_path, msg=f'Calling kill_task({task_to_kill})...')
                kill_task(task_to_kill)

            else:
                try:
                    local_tools.logIt_thread(log_path, msg=f'Sending pass command to {ip}.')
                    con.send('pass'.encode())
                    local_tools.logIt_thread(log_path, msg=f'Send completed.')
                    return False

                except (WindowsError, socket.error) as e:
                    local_tools.logIt_thread(log_path, msg=f'Error: {e}')
                    self.update_statusbar_messages_thread(msg=f'{e}.')
                    local_tools.logIt_thread(log_path,
                                             msg=f'Calling server.remove_lost_connection({con}, {ip})...')
                    server.remove_lost_connection(con, ip)
                    return False

        else:
            try:
                local_tools.logIt_thread(log_path, msg=f'Sending "n" to {ip}.')
                con.send('n'.encode())
                local_tools.logIt_thread(log_path, msg=f'Send completed.')
                self.update_statusbar_messages_thread(msg=f'tasks file received from {ip} | {sname}.')
                local_tools.logIt_thread(log_path, msg=f'Calling self.enable_buttons_thread()...')
                self.enable_buttons_thread()
                return True

            except (WindowsError, socket.error) as e:
                local_tools.logIt_thread(log_path, msg=f'Error: {e}.')
                self.update_statusbar_messages_thread(msg=f'{e}.')
                local_tools.logIt_thread(log_path, msg=f'Calling server.remove_lost_connection({con}, {ip})...')
                server.remove_lost_connection(con, ip)
                return False

    # Restart Client
    def restart_command(self, con: str, ip: str, sname: str) -> bool:
        local_tools.logIt_thread(log_path, msg=f'Running restart({con}, {ip}, {sname})')
        self.update_statusbar_messages_thread(msg=f' waiting for restart confirmation...')
        local_tools.logIt_thread(log_path, msg=f'Displaying self.sure() popup window...')
        self.sure = messagebox.askyesno(f"Restart for: {ip} | {sname}",
                                        f"Are you sure you want to restart {sname}?\t")
        local_tools.logIt_thread(log_path, msg=f'self.sure = {self.sure}')
        if self.sure:
            try:
                local_tools.logIt_thread(log_path, msg=f'Sending restart command to client...')
                con.send('restart'.encode())
                local_tools.logIt_thread(log_path, msg=f'Send completed.')
                local_tools.logIt_thread(log_path, msg=f'Calling server.remove_lost_connection({con}, {ip})...')
                server.remove_lost_connection(con, ip)
                local_tools.logIt_thread(log_path, msg=f'Calling self.refresh()...')
                self.refresh_command(event=0)
                local_tools.logIt_thread(log_path, msg=f'Restart command completed.')
                self.update_statusbar_messages_thread(msg=f'restart command sent to {ip} | {sname}.')
                return True

            except (RuntimeError, WindowsError, socket.error) as e:
                local_tools.logIt_thread(log_path, msg=f'Connection Error: {e}')
                self.update_statusbar_messages_thread(msg=f'{e}')
                local_tools.logIt_thread(log_path, msg=f'Calling server.remove_lost_connection({con}, {ip})...')
                server.remove_lost_connection(con, ip)
                return False

        else:
            self.update_statusbar_messages_thread(msg=f'restart canceled.')
            return False

    # Browse local files by Clients Station Names
    def browse_local_files_command(self, sname: str) -> subprocess:
        local_tools.logIt_thread(log_path, msg=fr'Opening explorer window focused on "{self.path}\{sname}"')
        return subprocess.Popen(rf"explorer {self.path}\{sname}")

    # Update Selected Client
    def update_selected_client_command(self, con: str, ip: str, sname: str) -> bool:
        local_tools.logIt_thread(log_path, msg=f'Running update_selected_client()...')
        local_tools.logIt_thread(log_path, msg=f'Calling self.disable_buttons_thread()...')
        self.disable_buttons_thread()
        local_tools.logIt_thread(log_path, msg=f'Sending update command to {ip} | {sname}...')
        try:
            con.send('update'.encode())
            local_tools.logIt_thread(log_path, msg=f'Send Completed.')
            local_tools.logIt_thread(log_path, msg=f'Waiting for response from {ip} | {sname}...')
            msg = con.recv(1024).decode()
            local_tools.logIt_thread(log_path, msg=f'{ip}|{sname}: {msg}')

        except (WindowsError, socket.error) as e:
            local_tools.logIt_thread(log_path, msg=f'ERROR: {e}.')
            return False

        local_tools.logIt_thread(log_path, msg=f'Calling self.refresh()...')
        local_tools.logIt_thread(log_path, msg=f'Displaying update info popup window...')
        time.sleep(2)
        messagebox.showinfo(f"Update {sname}", "Update command sent.")
        self.refresh_command(event=0)
        return True

    # Run Maintenance on Client
    def run_maintenance_command(self, con: str, ip: str, sname: str) -> None:
        local_tools.logIt_thread(log_path, msg=f"Sending maintenance command to {ip} | {sname}...")
        self.update_statusbar_messages_thread(msg=f"Waiting for maintenance confirmation on {ip} | {sname}...")
        sure = messagebox.askyesno(f"Maintenance for {ip} | {sname}", "Are you sure?")
        if sure:
            self.update_statusbar_messages_thread(msg=f"Sending maintenance command to {ip} | {sname}...")
            try:
                con.send('maintenance'.encode())
                local_tools.logIt_thread(log_path, msg=f"Maintenance command sent.")
                local_tools.logIt_thread(log_path, msg=f"Calling server.remove_lost_connection({con}, {ip})")
                self.update_statusbar_messages_thread(msg=f"Maintenance command sent to {ip} | {sname}.")
                local_tools.logIt_thread(msg=f"Calling server.remove_lost_connection({con}, {ip})")
                server.remove_lost_connection(con, ip)
                time.sleep(0.5)
                local_tools.logIt_thread(log_path, msg=f"Calling self.refresh_command()...")
                self.refresh_command()
                return True

            except (WindowsError, socket.error) as e:
                local_tools.logIt_thread(log_path, msg=f"ERROR: {e}.")
                local_tools.logIt_thread(log_path, msg=f"Calling server.remove_lost_connection({con}, {ip})")
                server.remove_lost_connection(con, ip)
                time.sleep(0.5)
                local_tools.logIt_thread(log_path, msg=f"Calling self.refresh_command()...")
                self.refresh_command()
                return False

        else:
            return False

    # ==++==++==++== END Controller Buttons ==++==++==++==

    # # ==++==++==++== Server Processes ==++==++==++==
    # Display Server Information
    def server_information(self) -> None:
        local_tools.logIt_thread(log_path, msg=f'Running show server information...')
        last_reboot = psutil.boot_time()
        local_tools.logIt_thread(log_path, msg=f'Displaying Label: '
                                               f'{server.serverIP} | {server.port} | '
                                               f'{datetime.fromtimestamp(last_reboot).replace(microsecond=0)}" | '
                                               f'{len(server.targets)}')
        label = Label(self.top_bar_label, background='ghost white',
                      text=f"\t\t\t\tServer IP: {server.serverIP}\t\tServer Port: {server.port}\t"
                           f"\t\tLast Boot: {datetime.fromtimestamp(last_reboot).replace(microsecond=0)}"
                           f"\t\tConnected Stations: {len(server.targets)}\t\t\t\t          ")
        label.grid(row=0, sticky='news')
        return

    # Display Available Stations
    def show_available_connections(self) -> None:
        local_tools.logIt_thread(log_path, msg=f'Running show_available_connections()...')
        if len(server.ips) == 0 and len(server.targets) == 0:
            local_tools.logIt_thread(log_path, msg=f'No connected Stations')

        def make_tmp():
            local_tools.logIt_thread(log_path, msg=f'Running make_tmp()...')
            count = 0
            for conKey, macValue in server.clients.items():
                for macKey, ipValue in macValue.items():
                    for ipKey, identValue in ipValue.items():
                        for con in server.targets:
                            if con == conKey:
                                for identKey, userValue in identValue.items():
                                    for userV, clientVer in userValue.items():
                                        if (count, macKey, ipKey, identKey, userValue) in server.tmp_availables:
                                            continue

                                local_tools.logIt_thread(log_path, msg=f'Updating self.tmp_availables list...')
                                server.tmp_availables.append((count, macKey, ipKey, identKey, userV, clientVer))
                count += 1

            local_tools.logIt_thread(log_path, msg=f'Available list created.')

        def extract():
            local_tools.logIt_thread(log_path, msg=f'Running extract()...')
            for item in server.tmp_availables:
                for conKey, ipValue in server.clients.items():
                    for macKey, ipVal in ipValue.items():
                        for ipKey, identVal in ipVal.items():
                            if item[2] == ipKey:
                                session = item[0]
                                stationMAC = item[1]
                                stationIP = item[2]
                                stationName = item[3]
                                loggedUser = item[4]
                                clientVersion = item[5]

                                # Show results in GUI table
                                if session % 2 == 0:
                                    local_tools.logIt_thread(log_path, msg=f'Updating connected table...')
                                    self.connected_table.insert('', 'end', values=(session, stationMAC, stationIP,
                                                                                   stationName, loggedUser,
                                                                                   clientVersion),
                                                                tags=('evenrow',))
                                else:
                                    local_tools.logIt_thread(log_path, msg=f'Updating connected table...')
                                    self.connected_table.insert('', 'end', values=(session, stationMAC, stationIP,
                                                                                   stationName, loggedUser,
                                                                                   clientVersion), tags=('oddrow',))

            local_tools.logIt_thread(log_path, msg=f'Extraction completed.')

        # Cleaning availables list
        local_tools.logIt_thread(log_path, msg=f'Cleaning availables list...')
        server.tmp_availables = []

        # Clear previous entries in GUI table
        local_tools.logIt_thread(log_path, msg=f'Cleaning connected table entries...')
        self.connected_table.delete(*self.connected_table.get_children())

        local_tools.logIt_thread(log_path, msg=f'Calling make_tmp()...')
        make_tmp()
        local_tools.logIt_thread(log_path, msg=f'Calling extract()...')
        extract()

    # Display Connection History
    def connection_history(self) -> bool:
        local_tools.logIt_thread(log_path, msg=f'Running connection_history()...')
        local_tools.logIt_thread(log_path, msg=f'Calling self.show_available_connections()...')
        self.show_available_connections()
        local_tools.logIt_thread(log_path, msg=f'Calling self.disable_buttons_thread(sidebar=False)...')
        self.disable_buttons_thread()
        local_tools.logIt_thread(log_path, msg=f'Calling self.create_connection_history_table()...')
        self.create_connection_history_table()

        self.update_statusbar_messages_thread(msg=f'Status: displaying connection history.')
        c = 0  # Initiate Counter for Connection Number
        try:
            for connection in server.connHistory:
                for conKey, macValue in connection.items():
                    for macKey, ipVal in macValue.items():
                        for ipKey, identValue in ipVal.items():
                            for identKey, userValue in identValue.items():
                                for userKey, timeValue in userValue.items():
                                    # Show results in GUI table
                                    if c % 2 == 0:
                                        self.history_table.insert('', 'end', values=(c, macKey, ipKey,
                                                                                     identKey, userKey,
                                                                                     timeValue), tags=('evenrow',))
                                    else:
                                        self.history_table.insert('', 'end', values=(c, macKey, ipKey,
                                                                                     identKey, userKey,
                                                                                     timeValue), tags=('oddrow',))

                                    local_tools.logIt_thread(log_path, msg=f'Stying table row colors...')
                                    self.history_table.tag_configure('oddrow', background='snow')
                                    self.history_table.tag_configure('evenrow', background='ghost white')
                        c += 1
            return True

        except (KeyError, socket.error, ConnectionResetError) as e:
            local_tools.logIt_thread(log_path, msg=f'ERROR: {e}')
            self.update_statusbar_messages_thread(msg=f'Status: {e}.')
            return False

    # Shell Connection to Client
    def shell(self, con: str, ip: str, sname: str) -> None:
        local_tools.logIt_thread(log_path, msg=f'Running shell({con}, {ip})...')
        self.update_statusbar_messages_thread(msg=f'shell connected to {ip} | {sname}.')
        while True:
            # Wait for User Input & hide print
            local_tools.logIt_thread(log_path, msg=f'Waiting for input...')
            cmd = input(f"")

            # Run Custom Command // FUTURE add-on for expert mode
            if cmd == 100:
                local_tools.logIt_thread(log_path, msg=f'Command: 100')
                try:
                    local_tools.logIt_thread(log_path, msg=f'Send freestyle command...')
                    con.send("freestyle".encode())
                    local_tools.logIt_thread(log_path, msg=f'Send Completed.')

                except (WindowsError, socket.error) as e:
                    local_tools.logIt_thread(log_path, msg=f'Connection Error: {e}')
                    break

                for item, connection in zip(server.tmp_availables, server.connections):
                    for conKey, ipValue in server.clients.items():
                        if conKey == connection:
                            for ipKey in ipValue.keys():
                                if item[1] == ipKey:
                                    ipval = item[1]
                                    host = item[2]
                                    user = item[3]

                local_tools.logIt_thread(log_path, msg=f'Initializing Freestyle Module...')
                free = freestyle.Freestyle(con, path, server.tmp_availables, server.clients,
                                           log_path, host, user)
                local_tools.logIt_thread(log_path, msg=f'Calling freestyle module...')
                free.freestyle(ip)

    # ==++==++==++== MENUBAR ==++==++==++==
    # Restart All Clients
    def restart_all_clients_command(self):
        local_tools.logIt_thread(log_path, msg=f'Running restart_all_clients()...')
        if len(self.targets) == 0:
            local_tools.logIt_thread(log_path, msg=f'Displaying popup window: "No connected stations"...')
            messagebox.showwarning("Update All Clients", "No connected stations.")
            return False

        self.update_statusbar_messages_thread(msg=f'waiting for restart confirmation...')
        local_tools.logIt_thread(log_path, msg=f'Displaying self.sure() popup window...')
        self.sure = messagebox.askyesno(f"Restart All Clients\t", "Are you sure?")
        local_tools.logIt_thread(log_path, msg=f'self.sure = {self.sure}')
        for item in self.tmp_availables:
            for conKey, ipValue in self.clients.items():
                for macKey, ipVal in ipValue.items():
                    for ipKey, identVal in ipVal.items():
                        if item[2] == ipKey:
                            session = item[0]
                            stationMAC = item[1]
                            stationIP = item[2]
                            stationName = item[3]
                            loggedUser = item[4]
                            clientVersion = item[5]
        if self.sure:
            for t in self.targets:
                try:
                    self.update_statusbar_messages_thread(msg=f'Restarting {t}...')
                    t.send('restart'.encode())
                    msg = t.recv(1024).decode()
                    self.update_statusbar_messages_thread(msg=f"{msg}")
                    server.remove_lost_connection(t, stationIP)

                except (WindowsError, socket.error) as e:
                    local_tools.logIt_thread(log_path, msg=f'ERROR: {e}')
                    server.remove_lost_connection(t, stationIP)
                    pass

            for i in range(len(self.targets)):
                refreshThread = Thread(target=self.refresh_command)
                refreshThread.start()
                time.sleep(0.5)
                # self.refresh()

            messagebox.showinfo("Restart All Clients", "Done!\t\t\t\t")
            self.update_statusbar_messages_thread(msg='Restart command completed.')
            return True

        else:
            return False

    # Broadcast update command to all connected stations
    def update_all_clients_command(self) -> bool:
        local_tools.logIt_thread(log_path, msg=f'Running update_all_clients()...')
        if len(self.targets) == 0:
            local_tools.logIt_thread(log_path, msg=f'Displaying popup window: "No connected stations"...')
            messagebox.showwarning("Update All Clients", "No connected stations.")
            return False

        def submit_url(event=0):
            url = self.update_url.get()
            sure = messagebox.askyesno(f"New URL: {url}", "Are you sure?")
            if sure:
                try:
                    for t in self.targets:
                        local_tools.logIt_thread(log_path, msg=f'Sending update command to all connected stations...')
                        try:
                            t.send('update'.encode())
                            local_tools.logIt_thread(self.log_path, msg=f'Send completed.')
                            t.send(str(url).encode())
                            msg = t.recv(1024).decode()
                            self.update_statusbar_messages_thread(msg=f'{msg}')
                            local_tools.logIt_thread(self.log_path, msg=f'Station: {msg}')

                        except (WindowsError, socket.error) as e:
                            local_tools.logIt_thread(log_path, msg=f'ERROR: {e}')
                            self.update_statusbar_messages_thread(msg=f'ERROR: {e}')
                            for clientConn, clientValues in self.clients.items():
                                for clientMac, clientIPv in clientValues.items():
                                    for clientIP, vals in clientIPv.items():
                                        if clientConn == t:
                                            for sname in vals.keys():
                                                server.remove_lost_connection(t, clientIP)
                            continue

                except RuntimeError:
                    pass

                local_tools.logIt_thread(log_path, msg=f'Calling self.refresh()...')
                local_tools.logIt_thread(log_path, msg=f'Displaying update info popup window...')
                messagebox.showinfo("Update All Clients", "Update command sent.")
                self.refresh_command(event=0)
                url_window.destroy()
                return True

            else:
                return False

        url_window = tk.Toplevel()
        url_window.title("HandsOff - client.exe URL")
        url_window.iconbitmap('HandsOff.ico')

        # Set Mid Screen Coordinates
        x = (self.WIDTH / 2) - (300 / 2)
        y = (self.HEIGHT / 2) - (100 / 2)

        # Set Window Size & Location & Center Window
        url_window.geometry(f'{300}x{100}+{int(x)}+{int(y)}')
        url_window.configure(background='slate gray', takefocus=True)
        url_window.grid_columnconfigure(0, weight=1)
        url_window.grid_rowconfigure(2, weight=2)
        url_window.maxsize(300, 100)
        url_window.minsize(300, 100)
        url_window.bind("<Return>", submit_url)

        url_label = Label(url_window, text="EXE file URL", relief='ridge',
                          background='slate gray', foreground='white')
        url_label.grid(row=0, sticky='n')

        url_entry = Entry(url_window, textvariable=self.update_url)
        url_entry.grid(row=1, column=0, sticky='news')
        url_entry.delete(0, END)
        url_entry.focus()

        url_submit = Button(url_window, text="Submit", command=submit_url)
        url_submit.grid(row=2, column=0, pady=5)

        local_tools.logIt_thread(log_path, msg=f'Calling self.disable_buttons_thread()...')
        self.disable_buttons_thread()
        url_window.wait_window(self)

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
        local_tools.logIt_thread(log_path, msg=f'Running self.save_connection_history()...')
        if len(server.targets) == 0:
            messagebox.showwarning("Save Connection History", "Nothing to save yet.")
            return

        file_types = {'CSV Files': '.csv', 'TXT Files': '.txt'}

        # Create Saved Files Dir
        saves = fr"{path}\Saves"
        if not os.path.exists(saves):
            os.makedirs(saves)

        # Get Filename
        filename = filedialog.asksaveasfilename(initialdir=f"{saves}", defaultextension='.csv',
                                                filetypes=(('CSV files', '.csv'), ('TXT files', '.txt')))
        if len(filename) == 0 or str(filename) == '':
            local_tools.logIt_thread(log_path, msg=f'Save canceled.')
            return False

        c = 0
        for name, ftype in file_types.items():
            if str(filename).endswith(ftype) and ftype == '.csv':
                header = ['MAC', 'IP', 'Station', 'User', 'Time']
                with open(filename, 'w') as file:
                    writer = csv.writer(file)
                    try:
                        writer.writerow(header)
                        for connection in server.connHistory:
                            for conKey, macValue in connection.items():
                                for macKey, ipVal in macValue.items():
                                    for ipKey, identValue in ipVal.items():
                                        for identKey, userValue in identValue.items():
                                            for userKey, timeValue in userValue.items():
                                                writer.writerow([macKey, ipKey, identKey, userKey, timeValue])

                                c += 1
                        return True

                    except Exception as e:
                        local_tools.logIt_thread(log_path, msg=f'ERROR: {e}')
                        self.update_statusbar_messages_thread(msg=f'Status: {e}.')
                        return False

            else:
                with open(filename, 'w') as file:
                    for connection in server.connHistory:
                        for conKey, macValue in connection.items():
                            for macKey, ipVal in macValue.items():
                                for ipKey, identValue in ipVal.items():
                                    for identKey, userValue in identValue.items():
                                        for userKey, timeValue in userValue.items():
                                            file.write(
                                                f"#{c} | MAC: {macKey} | IP: {ipKey} | Station: {identKey} | User: {userKey} | Time: {timeValue} \n")
                                c += 1
                    return True

    # Manage Connected Table & Controller LabelFrame Buttons
    def select_item(self, event) -> bool:
        local_tools.logIt_thread(log_path, msg=f'Running select_item()...')
        # Respond to mouse clicks on connected table
        rowid = self.connected_table.identify_row(event.y)
        row = self.connected_table.item(rowid)['values']
        try:
            if not row[2] in self.temp.values():
                local_tools.logIt_thread(log_path, msg=f'Updating self.temp dictionary...')
                self.temp[row[0]] = row[2]

        # Error can raise when clicking on empty space so the row is None or empty.
        except IndexError:
            pass

        local_tools.logIt_thread(log_path, msg=f'Calling self.create_notebook()...')
        if len(self.notebooks) == 0:
            self.create_notebook()

        # Create a Controller LabelFrame with Buttons and connect shell by TreeView Table selection
        for id, ip in self.temp.items():
            for clientConn, clientValues in server.clients.items():
                for clientMac, clientIPv in clientValues.items():
                    for clientIP, vals in clientIPv.items():
                        if clientIP == ip:
                            for sname in vals.keys():
                                temp_notebook = {clientIP: {sname: self.notebook}}
                                if not temp_notebook[clientIP][sname] in self.notebooks:
                                    self.notebooks.update(temp_notebook)

                                self.build_controller_buttons(clientConn, clientIP, sname)
                                local_tools.logIt_thread(log_path, msg=f'Calling self.enable_buttons_thread...')
                                self.enable_buttons_thread()
                                local_tools.logIt_thread(log_path, msg=f'Running shell thread...')
                                shellThread = Thread(target=self.shell,
                                                     args=(clientConn, clientIP, sname),
                                                     daemon=True,
                                                     name="Shell Thread")
                                shellThread.start()

                                local_tools.logIt_thread(log_path, msg=f'Clearing self.temp dictionary...')
                                self.temp.clear()
                                return True


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
            PIL.Image.open('images/github_black.png').resize((50, 50), PIL.Image.ANTIALIAS))
        self.github_purple = PIL.ImageTk.PhotoImage(
            PIL.Image.open('images/github_purple.png').resize((50, 50), PIL.Image.ANTIALIAS))
        self.linkedin_black = PIL.ImageTk.PhotoImage(
            PIL.Image.open('images/linkedin_black.png').resize((50, 50), PIL.Image.ANTIALIAS))
        self.linkedin_blue = PIL.ImageTk.PhotoImage(
            PIL.Image.open('images/linkedin_blue.png').resize((50, 50), PIL.Image.ANTIALIAS))
        self.youtube_red = PIL.ImageTk.PhotoImage(
            PIL.Image.open('images/youtube_red.png').resize((50, 50), PIL.Image.ANTIALIAS))
        self.youtube_black = PIL.ImageTk.PhotoImage(
            PIL.Image.open('images/youtube_black.png').resize((50, 50), PIL.Image.ANTIALIAS))
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
        self.github_label.bind("<Button-1>", lambda x: self.on_github_click(github_url))
        self.github_label.bind("<Enter>", self.on_github_hover)
        self.github_label.bind("<Leave>", self.on_github_leave)

        self.youtube_label = Label(self.about_window, image=self.youtube_red, background='slate gray')
        self.youtube_label.image = [self.youtube_red, self.youtube_black]
        self.youtube_label.place(x=173, y=130)
        self.youtube_label.bind("<Button-1>", lambda x: self.on_youtube_click(youtube_url))
        self.youtube_label.bind("<Enter>", self.on_youtube_hover)
        self.youtube_label.bind("<Leave>", self.on_youtube_leave)

        self.linkedIn_label = Label(self.about_window, image=self.linkedin_blue, background='slate gray')
        self.linkedIn_label.image = [self.linkedin_black, self.linkedin_blue]
        self.linkedIn_label.place(x=264, y=130)
        self.linkedIn_label.bind("<Button-1>", lambda x: self.on_youtube_click(linkedIn_url))
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


class Locals:
    # Run log func in new Thread
    def logIt_thread(self, log_path=None, debug=False, msg='') -> None:
        self.logit_thread = Thread(target=self.logIt,
                                   args=(log_path, debug, msg),
                                   daemon=True,
                                   name="Log Thread")
        self.logit_thread.start()

    # Convert bytes to numbers for file transfers
    def bytes_to_number(self, b: int) -> int:
        self.logIt_thread(self.log_path, msg=f'Running bytes_to_number({b})...')
        dt = self.get_date()
        res = 0
        for i in range(4):
            res += b[i] << (i * 8)
        return res

    # Get current date & time
    def get_date(self) -> str:
        d = datetime.now().replace(microsecond=0)
        dt = str(d.strftime("%m/%d/%Y %H:%M:%S"))

        return dt

    # Log & Debugger
    def logIt(self, logfile=None, debug=None, msg='') -> bool:
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


class Server:
    def __init__(self):
        self.clients = {}
        self.clients_backup = {}
        self.connections = {}
        self.connHistory = []
        self.ips = []
        self.targets = []
        self.ttl = 5
        self.port = 55400
        self.hostname = socket.gethostname()
        self.serverIP = str(socket.gethostbyname(self.hostname))

    def run(self) -> None:
        local_tools.logIt_thread(log_path, msg=f'Running run()...')
        local_tools.logIt_thread(log_path, msg=f'Calling connect()...')
        self.connectThread = Thread(target=self.connect,
                                    daemon=True,
                                    name=f"Connect Thread")
        self.connectThread.start()

    # Listen for connections and sort new connections to designated lists/dicts
    def connect(self) -> None:
        def get_mac_address() -> str:
            local_tools.logIt_thread(log_path, msg=f'Waiting for MAC address from {self.ip}...')
            self.mac = self.conn.recv(1024).decode()
            local_tools.logIt_thread(log_path, msg=f'MAC Address: {self.mac}')
            local_tools.logIt_thread(log_path, msg=f'Sending confirmation to {self.ip}...')
            self.conn.send('OK'.encode())
            local_tools.logIt_thread(log_path, msg=f'Send completed.')
            return self.mac

        def get_hostname() -> str:
            local_tools.logIt_thread(log_path, msg=f'Waiting for remote station name...')
            self.ident = self.conn.recv(1024).decode()
            local_tools.logIt_thread(log_path, msg=f'Remote station name: {self.ident}')
            local_tools.logIt_thread(log_path, msg=f'Sending Confirmation to {self.ip}...')
            self.conn.send('OK'.encode())
            local_tools.logIt_thread(log_path, msg=f'Send completed.')
            return self.ident

        def get_user() -> str:
            local_tools.logIt_thread(log_path, msg=f'Waiting for remote station current logged user...')
            self.user = self.conn.recv(1024).decode()
            local_tools.logIt_thread(log_path, msg=f'Remote station user: {self.user}')
            local_tools.logIt_thread(log_path, msg=f'Sending Confirmation to {self.ip}...')
            self.conn.send('OK'.encode())
            local_tools.logIt_thread(log_path, msg=f'Send completed.')
            return self.user

        def get_client_version() -> str:
            local_tools.logIt_thread(log_path, msg=f'Waiting for client version...')
            self.client_version = self.conn.recv(1024).decode()
            local_tools.logIt_thread(log_path, msg=f'Client version: {self.client_version}')
            local_tools.logIt_thread(log_path, msg=f'Sending confirmation to {self.ip}...')
            self.conn.send('OK'.encode())
            local_tools.logIt_thread(log_path, msg=f'Send completed.')
            return self.client_version

        local_tools.logIt_thread(log_path, msg=f'Running connect()...')
        while True:
            local_tools.logIt_thread(log_path, msg=f'Accepting connections...')
            self.conn, (self.ip, self.port) = self.server.accept()
            local_tools.logIt_thread(log_path, msg=f'Connection from {self.ip} accepted.')

            try:
                local_tools.logIt_thread(log_path, msg=f'Waiting for MAC Address...')
                self.client_mac = get_mac_address()
                local_tools.logIt_thread(log_path, msg=f'MAC: {self.client_mac}.')
                local_tools.logIt_thread(log_path, msg=f'Waiting for station name...')
                self.hostname = get_hostname()
                local_tools.logIt_thread(log_path, msg=f'Station name: {self.hostname}.')
                local_tools.logIt_thread(log_path, msg=f'Waiting for logged user...')
                self.loggedUser = get_user()
                local_tools.logIt_thread(log_path, msg=f'Logged user: {self.loggedUser}.')
                local_tools.logIt_thread(log_path, msg=f'Waiting for client version...')
                self.client_version = get_client_version()
                local_tools.logIt_thread(log_path, msg=f'Client version: {self.client_version}.')

            except (WindowsError, socket.error) as e:
                local_tools.logIt_thread(log_path, msg=f'Connection Error: {e}')
                return  # Restart The Loop

            # Update Thread Dict and Connection Lists
            if self.conn not in self.targets and self.ip not in self.ips:
                local_tools.logIt_thread(log_path, msg=f'New Connection!')

                # Add Socket Connection To Targets list
                local_tools.logIt_thread(log_path, msg=f'Adding {self.conn} to targets list...')
                self.targets.append(self.conn)
                local_tools.logIt_thread(log_path, msg=f'targets list updated.')

                # Add IP Address Connection To IPs list
                local_tools.logIt_thread(log_path, msg=f'Adding {self.ip} to ips list...')
                self.ips.append(self.ip)
                local_tools.logIt_thread(log_path, msg=f'ips list updated.')

                # Set Temp Dict To Update Live Connections List
                local_tools.logIt_thread(log_path,
                                         msg=f'Adding {self.conn} | {self.ip} to temp live connections dict...')
                self.temp_connection = {self.conn: self.ip}
                local_tools.logIt_thread(log_path, msg=f'Temp connections dict updated.')

                # Add Temp Dict To Connections List
                local_tools.logIt_thread(log_path, msg=f'Updating connections list...')
                self.connections.update(self.temp_connection)
                local_tools.logIt_thread(log_path, msg=f'Connections list updated.')

                # Set Temp Idents Dict For Idents
                local_tools.logIt_thread(log_path, msg=f'Creating dict to hold ident details...')
                self.temp_ident = {
                    self.conn: {self.client_mac: {self.ip: {self.ident: {self.user: self.client_version}}}}}
                local_tools.logIt_thread(log_path, msg=f'Dict created: {self.temp_ident}')

                # Add Temp Idents Dict To Idents Dict
                local_tools.logIt_thread(log_path, msg=f'Updating live clients list...')
                self.clients.update(self.temp_ident)
                local_tools.logIt_thread(log_path, msg=f'Live clients list updated.')

            # Create a Dict of Connection, IP, Computer Name, Date & Time
            local_tools.logIt_thread(log_path, msg=f'Fetching current date & time...')
            dt = local_tools.get_date()
            local_tools.logIt_thread(log_path, msg=f'Creating a connection dict...')
            self.temp_connection_record = {self.conn: {self.client_mac: {self.ip: {self.ident: {self.user: dt}}}}}
            local_tools.logIt_thread(log_path, msg=f'Connection dict created: {self.temp_connection_record}')

            # Add Connection to Connection History
            local_tools.logIt_thread(log_path, msg=f'Adding connection to connection history...')
            self.connHistory.append(self.temp_connection_record)
            local_tools.logIt_thread(log_path, msg=f'Connection added to connection history.')

            local_tools.logIt_thread(log_path, msg=f'Calling self.welcome_message()...')

            app.display_server_information_thread()
            self.welcome_message()

    # Server listener
    def listener(self) -> None:
        local_tools.logIt_thread(log_path, msg=f'Running listener()...')
        self.server = socket.socket()
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        local_tools.logIt_thread(log_path, msg=f'Binding {self.serverIP}, {self.port}...')
        self.server.bind((self.serverIP, self.port))
        self.server.listen()

    # Send welcome message to connected clients
    def welcome_message(self) -> bool:
        local_tools.logIt_thread(log_path, msg=f'Running welcome_message()...')
        try:
            self.welcome = "Connection Established!"
            local_tools.logIt_thread(log_path, msg=f'Sending welcome message...')
            self.conn.send(f"@Server: {self.welcome}".encode())
            local_tools.logIt_thread(log_path, msg=f'{self.welcome} sent to {self.ident}.')
            return True

        except (WindowsError, socket.error) as e:
            local_tools.logIt_thread(log_path, msg=f'Connection Error: {e}')
            if self.conn in self.targets and self.ip in self.ips:
                local_tools.logIt_thread(log_path, msg=f'Removing {self.conn} from self.targets...')
                self.targets.remove(self.conn)
                local_tools.logIt_thread(log_path, msg=f'Removing {self.ip} from self.ips list...')
                self.ips.remove(self.ip)
                local_tools.logIt_thread(log_path, msg=f'Deleting {self.conn} from self.connections.')
                del self.connections[self.conn]
                local_tools.logIt_thread(log_path, msg=f'Deleting {self.conn} from self.clients...')
                del self.clients[self.conn]
                local_tools.logIt_thread(log_path, msg=f'[V]{self.ip} removed from lists.')
                return False

    # Check if connected stations are still connected
    def vital_signs(self) -> bool:
        local_tools.logIt_thread(log_path, msg=f'Running vital_signs()...')
        if len(self.targets) == 0:
            app.update_statusbar_messages_thread(msg='No connected stations.')
            return False

        callback = 'yes'
        i = 0
        app.update_statusbar_messages_thread(msg=f'running vitals check...')
        local_tools.logIt_thread(log_path, msg=f'Iterating Through Temp Connected Sockets List...')
        for t in self.targets:
            try:
                local_tools.logIt_thread(log_path, msg=f'Sending "alive" to {t}...')
                t.send('alive'.encode())
                local_tools.logIt_thread(log_path, msg=f'Send completed.')
                local_tools.logIt_thread(log_path, msg=f'Waiting for response from {t}...')
                ans = t.recv(1024).decode()
                local_tools.logIt_thread(log_path, msg=f'Response from {t}: {ans}.')
                local_tools.logIt_thread(log_path, msg=f'Waiting for client version from {t}...')
                ver = t.recv(1024).decode()
                local_tools.logIt_thread(log_path, msg=f'Response from {t}: {ver}.')

            except (WindowsError, socket.error):
                self.remove_lost_connection(t, self.ips[i])
                break

            if str(ans) == str(callback):
                try:
                    local_tools.logIt_thread(log_path, msg=f'Iterating self.clients dictionary...')
                    for conKey, ipValue in self.clients.items():
                        for ipKey, identValue in ipValue.items():
                            if t == conKey:
                                for name, version in identValue.items():
                                    for v, v1 in version.items():
                                        for n, ver in v1.items():
                                            app.update_statusbar_messages_thread(
                                                msg=f'Station IP: {self.ips[i]} | Station Name: {v} | Client Version: {ver} - ALIVE!')
                                            i += 1
                                            time.sleep(0.5)

                except (IndexError, RuntimeError):
                    pass

            else:
                local_tools.logIt_thread(log_path, msg=f'Iterating self.clients dictionary...')
                try:
                    for conKey, macValue in self.clients.items():
                        for con in self.targets:
                            if conKey == con:
                                for macKey, ipVal in macValue.items():
                                    for ipKey, identValue in ipVal.items():
                                        if ipKey == self.ips[i]:
                                            self.remove_lost_connection(conKey, ipKey)

                except (IndexError, RuntimeError):
                    pass

        app.update_statusbar_messages_thread(msg=f'Vitals check completed.')
        local_tools.logIt_thread(log_path, msg=f'=== End of vital_signs() ===')
        return True

    # Remove Lost connections
    def remove_lost_connection(self, con: str, ip: str) -> bool:
        local_tools.logIt_thread(log_path, msg=f'Running remove_lost_connection({con}, {ip})...')
        try:
            local_tools.logIt_thread(log_path, msg=f'Removing connections...')
            for conKey, macValue in self.clients.items():
                if conKey == con:
                    for macKey, ipVal in macValue.items():
                        for ipKey, identValue in ipVal.items():
                            if ipKey == ip:
                                for identKey, userValue in identValue.items():
                                    self.targets.remove(con)
                                    self.ips.remove(ip)

                                    del self.connections[con]
                                    del self.clients[con]

                                    # Update statusbar message
                                    app.update_statusbar_messages_thread(
                                        msg=f'{ip} | {identValue} | {userValue} removed from connected list.')

            local_tools.logIt_thread(log_path, msg=f'Connections removed.')
            return True

        except RuntimeError as e:
            local_tools.logIt_thread(log_path, msg=f'Runtime Error: {e}.')
            return False


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
    path = r'c:\HandsOff'
    log_path = fr'{path}\server_log.txt'
    local_tools = Locals()
    server = Server()
    app = App()

    main()
