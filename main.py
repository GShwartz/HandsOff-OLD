from datetime import datetime
from threading import Thread
import PIL.ImageTk
import subprocess
import webbrowser
import threading
import PIL.Image
import argparse
import logging
import pystray
import os.path
import socket
import psutil
import shutil
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

# Local Modules
from Modules.screenshot import Screenshot
from Modules.commands import Commands
from Modules.sysinfo import Sysinfo
from Modules.server import Server
from Modules.about import About
from Modules.tasks import Tasks


class App(Tk):
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
        self.server = Server(log_path, self, args.ip, args.port, path)
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
        self.bind("<F1>", Commands(None, self, path, log_path).about)
        self.bind("<F5>", self.refresh_command)
        self.bind("<F6>", Commands(None, self, path, log_path).clear_notebook_command)

        # Set Closing protocol
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Main Window Frames
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(5, weight=1)

        # Initiate app's styling
        self.make_style()

        # Build and display
        self.build_menubar(None)
        self.build_main_window_frames()
        self.build_connected_table()
        self.server_information_table()
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

            "Sysinfo.Heading": {
                "configure": {"padding": 1,
                              "background": 'slate grey',
                              'relief': 'ridge',
                              'foreground': 'ghost white'}}
        })

        self.style.theme_use("HandsOff")
        self.style.configure("Treeview.Heading", font=('Arial Bold', 8))
        self.style.map("Treeview", background=[('selected', 'sea green')])

    # Update menubar
    def update_tools_menu(self, endpoint):
        if len(self.server.connHistory) > 0:
            self.tools.entryconfig(2, state=NORMAL)
            self.bind("<F10>", Commands(endpoint, self, path, log_path).save_connection_history_thread)

        else:
            self.tools.entryconfig(2, state=DISABLED)
            self.unbind("<F10>")

        if len(self.server.endpoints) > 1:
            self.tools.entryconfig(3, state=NORMAL)
            self.tools.entryconfig(4, state=NORMAL)
            self.bind("<F11>", Commands(endpoint, self, path, log_path).restart_all_clients_thread)
            self.bind("<F12>", Commands(endpoint, self, path, log_path).update_all_clients_thread)

        else:
            self.tools.entryconfig(3, state=DISABLED)
            self.tools.entryconfig(4, state=DISABLED)
            self.unbind("<F11>")
            self.unbind("<F12>")

    # Create Menubar
    def build_menubar(self, endpoint):
        logIt_thread(log_path, msg=f'Running build_menubar()...')
        menubar = Menu(self, tearoff=0)
        file = Menu(menubar, tearoff=0)
        self.tools = Menu(self, tearoff=0)
        helpbar = Menu(self, tearoff=0)

        file.add_command(label="Minimize", command=Commands(None, self, path, log_path).minimize)
        file.add_separator()
        file.add_command(label="Exit", command=self.on_closing)

        self.tools.add_command(label="Refresh <F5>", command=self.refresh_command)
        self.tools.add_command(label="Clear Details <F6>",
                               command=Commands(None, self, path, log_path).clear_notebook_command)
        self.tools.add_command(label="Save Connection History <F10>",
                               command=Commands(None, self, path, log_path).save_connection_history_thread,
                               state=DISABLED)
        self.tools.add_command(label="Restart All Clients <F11>",
                               command=Commands(None, self, path, log_path).restart_all_clients_thread,
                               state=DISABLED)
        self.tools.add_command(label="Update All Clients <F12>",
                               command=Commands(None, self, path, log_path).update_all_clients_thread,
                               state=DISABLED)

        helpbar.add_command(label="Help", command=Commands(None, self, path, log_path).show_help_thread)
        helpbar.add_command(label="About", command=Commands(None, self, path, log_path).about)

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
        # self.top_bar_label.grid(row=0, column=0, sticky='news')

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
                                                     "Logged User", "Client Version", "Boot Time"),
                                            show="headings", height=7,
                                            selectmode='browse', yscrollcommand=self.table_sb.set)
        self.connected_table.pack(fill=BOTH)
        self.table_sb.config(command=self.connected_table.yview)
        logIt_thread(log_path, msg=f'Defining highlight event for Connected Table...')
        self.connected_table.tag_configure('highlight', background='lightblue')

        # Columns & Headings config
        self.connected_table.column("#1", anchor=CENTER, width=71, stretch=NO)
        self.connected_table.heading("#1", text="ID")
        self.connected_table.column("#2", anchor=CENTER, width=170, stretch=NO)
        self.connected_table.heading("#2", text="MAC")
        self.connected_table.column("#3", anchor=CENTER, width=170, stretch=NO)
        self.connected_table.heading("#3", text="IP")
        self.connected_table.column("#4", anchor=CENTER, width=200, stretch=NO)
        self.connected_table.heading("#4", text="Station Name")
        self.connected_table.column("#5", anchor=CENTER, width=170, stretch=NO)
        self.connected_table.heading("#5", text="Logged User")
        self.connected_table.column("#6", anchor=CENTER, width=170, stretch=NO)
        self.connected_table.heading("#6", text="Client Version")
        self.connected_table.column("#7", anchor=CENTER, width=170, stretch=NO)
        self.connected_table.heading("#7", text="Boot Time")
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
                                     command=lambda: Commands(endpoint, self, path, log_path).screenshot_thread())
        self.screenshot_btn.grid(row=0, column=1, sticky="w", pady=5, padx=2, ipadx=2)
        logIt_thread(log_path, msg=f'Updating controller buttons list...')
        self.buttons.append(self.screenshot_btn)

        logIt_thread(log_path, msg=f'Building anydesk button...')
        self.anydesk_btn = Button(self.controller_btns, text="Anydesk", width=14, pady=5,
                                  command=lambda: Commands(endpoint, self, path, log_path).anydesk_command())
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

        logIt_thread(log_path, msg=f'Building system information button...')
        self.sysinfo_btn = Button(self.controller_btns, text="SysInfo", width=14, pady=5,
                                  command=lambda: Commands(endpoint, self, path, log_path).sysinfo_thread())
        self.sysinfo_btn.grid(row=0, column=4, sticky="w", pady=5, padx=2, ipadx=2)
        logIt_thread(log_path, msg=f'Updating controller buttons list...')
        self.buttons.append(self.sysinfo_btn)

        logIt_thread(log_path, msg=f'Building tasks button...')
        self.tasks_btn = Button(self.controller_btns, text="Tasks", width=14, pady=5,
                                command=lambda: Commands(endpoint, self, path, log_path).tasks())
        self.tasks_btn.grid(row=0, column=5, sticky="w", pady=5, padx=2, ipadx=2)
        logIt_thread(log_path, msg=f'Updating controller buttons list...')
        self.buttons.append(self.tasks_btn)

        logIt_thread(log_path, msg=f'Building restart button...')
        self.restart_btn = Button(self.controller_btns, text="Restart", width=14, pady=5,
                                  command=lambda: Commands(endpoint, self, path, log_path).restart_command())
        self.restart_btn.grid(row=0, column=6, sticky="w", pady=5, padx=2, ipadx=2)
        logIt_thread(log_path, msg=f'Updating controller buttons list...')
        self.buttons.append(self.restart_btn)

        logIt_thread(log_path, msg=f'Building local files button...')
        self.browse_btn = Button(self.controller_btns, text="Local Files", width=14, pady=5,
                                 command=lambda: Commands(endpoint, self, path, log_path).browse_local_files_command())
        self.browse_btn.grid(row=0, column=7, sticky="w", pady=5, padx=2, ipadx=2)
        self.buttons.append(self.browse_btn)

        logIt_thread(log_path, msg=f'Building Update Client button...')
        self.update_client = Button(self.controller_btns, text="Update Client", width=14,
                                    pady=5, state=NORMAL,
                                    command=lambda: Commands(endpoint, self, path,
                                                             log_path).update_selected_endpoint_thread())
        self.update_client.grid(row=0, column=8, sticky="w", pady=5, padx=2, ipadx=2)
        self.buttons.append(self.update_client)

        logIt_thread(log_path, msg=f'Building Maintenance button...')
        self.maintenance = Button(self.controller_btns, text="Maintenance", width=14,
                                  pady=5, state=DISABLED,
                                  command=lambda: Commands(endpoint, self, path, log_path).run_maintenance_thread())
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
                        endpoint.conn.close()

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
            self.server.remove_lost_connection(endpoint)
            return False

    def server_information_table(self):
        self.sysinfo_table = ttk.Treeview(self.main_frame_top,
                                          columns=("Serving On", "Server IP", "Server Port",
                                                   "Boot Time", "Connected Stations"),
                                          show="headings", height=1)
        # self.style.configure("Sysinfo.Heading")
        self.sysinfo_table.pack(fill=BOTH)
        logIt_thread(log_path, msg=f'Defining highlight event for Connected Table...')

        # Columns & Headings config
        self.sysinfo_table.column("#1", anchor=CENTER, width=300, stretch=NO)
        self.sysinfo_table.heading("#1", text="Serving On")
        self.sysinfo_table.column("#2", anchor=CENTER, width=220, stretch=NO)
        self.sysinfo_table.heading("#2", text="Server IP")
        self.sysinfo_table.column("#3", anchor=CENTER, width=100, stretch=NO)
        self.sysinfo_table.heading("#3", text="Server Port")
        self.sysinfo_table.column("#4", anchor=CENTER, width=250, stretch=NO)
        self.sysinfo_table.heading("#4", text="Boot Time")
        self.sysinfo_table.column("#5", anchor=CENTER, width=170, stretch=YES)
        self.sysinfo_table.heading("#5", text="Connected Stations")

    # Display Server Information
    def server_information(self) -> None:
        logIt_thread(log_path, msg=f'Running show server information...')
        last_reboot = psutil.boot_time()
        bt = datetime.fromtimestamp(last_reboot).replace(microsecond=0)
        self.sysinfo_table.delete(*self.sysinfo_table.get_children())
        self.sysinfo_table.insert('', 'end', values=(serving_on, self.server.serverIP, self.server.port, bt,
                                                     len(self.server.endpoints)))
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
                                                           endpoint.ident, endpoint.user,
                                                           endpoint.client_version, endpoint.boot_time),
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

    # Refresh server info & connected stations table with vital signs
    def refresh_command(self, event=0) -> None:
        logIt_thread(log_path, msg=f'Running refresh()...')
        logIt_thread(log_path, msg=f'Calling self_disable_buttons_thread(sidebar=False)...')
        self.disable_buttons_thread()
        logIt_thread(log_path, msg=f'Resetting tmp_availables list...')
        self.server.tmp_availables = []
        self.temp.clear()
        logIt_thread(log_path, msg=f'Calling vital_signs_thread()...')
        Commands(None, self, path, log_path).vital_signs_thread()
        logIt_thread(log_path, msg=f'Running thread: server_information')
        Thread(target=self.server_information, name="Server Information Thread").start()
        logIt_thread(log_path, msg=f'Calling update_tools_menu()...')
        self.update_tools_menu(None)
        logIt_thread(log_path, msg=f'Calling show_available_connections()...')
        self.show_available_connections()
        logIt_thread(log_path, msg=f'Calling connection_history()...')
        self.connection_history()
        self.update_statusbar_messages_thread(msg='refresh complete.')

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

                    logIt_thread(log_path, msg=f'Calling self.create_notebook()...')
                    if not self.notebooks:
                        self.create_notebook()

            # Error can raise when clicking on empty space so the row is None or empty.
            except IndexError:
                pass

            # Create a Controller LabelFrame with Buttons and connect shell by TreeView Table selection
            for endpoint in self.server.endpoints:
                if row[2] == endpoint.ip:
                    self.enable_buttons_thread()
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
                            self.refresh_command()
                            break

                        self.temp.clear()


def on_icon_clicked(icon, item):
    if str(item) == "About":
        app.about(event=0)

    if str(item) == "Restore":
        app.deiconify()

    if str(item) == "Exit":
        for endpoint in app.server.endpoints:
            try:
                endpoint.conn.send('exit'.encode())

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
    serving_on = "handsoff.home.lab"
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
