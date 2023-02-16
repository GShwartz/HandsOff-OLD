from tkinter import simpledialog, filedialog, messagebox, ttk
from datetime import datetime
from threading import Thread
from tkinter import *
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
    HEIGHT = 875

    def __init__(self):
        super().__init__()
        self.style = ttk.Style()
        self.server = Server(log_path, self, args.ip, args.port, path)
        self.running = False

        # Start listener
        logger.info("Calling listener")
        self.server.listener()

        # Create local app DIR
        if not os.path.exists(path):
            os.makedirs(path)

        # Run Listener Thread
        listenerThread = Thread(target=self.server.run, daemon=True, name="Listener Thread").start()

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
        logger.info("Calling make_style")
        self.make_style()

        # Build and display
        logger.info("Calling build_menubar...")
        self.build_menubar(None)
        logger.info("Calling build_main_window_frames...")
        self.build_main_window_frames()
        logger.info("Calling build_connected_table...")
        self.build_connected_table()
        logger.info("Calling server_information_table...")
        self.build_server_information_table()
        logger.info("Calling server_information...")
        self.server_information()
        logger.info("Calling build_controller_buttons...")
        self.build_controller_buttons(None)
        logger.info("Calling create_notebook...")
        self.create_notebook()
        logger.info("Calling show_available_connections...")
        self.show_available_connections()
        logger.info("Calling connection_history...")
        self.connection_history()

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
                "map": {"background": [("selected", 'green')]}}
        })

        self.style.theme_use("HandsOff")
        self.style.configure("Treeview.Heading", font=('Arial Bold', 8))
        self.style.map("Treeview", background=[('selected', 'sea green')])
        logger.info("make_style completed.")

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

        logger.info("update_tools completed.")

    # Create Menubar
    def build_menubar(self, endpoint):
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

        self.config(menu=menubar)
        logger.info("build_menubar completed.")
        return

    # Build Main Frame GUI
    def build_main_window_frames(self) -> None:
        logger.debug("Building main frame...")
        self.main_frame = Frame(self, relief="raised", bd=1, background='snow')
        self.main_frame.configure(border=1)
        self.main_frame.grid(row=0, column=0, sticky="nswe", padx=1)
        self.main_frame.rowconfigure(5, weight=1)
        self.main_frame.columnconfigure(0, weight=1)

        logger.debug("Building server information frame...")
        self.srvinfo_frame = Frame(self.main_frame, relief='solid', border=1, height=1, background='ghost white')
        self.srvinfo_frame.grid(row=0, column=0, sticky="nwes")

        logger.debug("Building connected table frame...")
        self.connected_table = Frame(self.main_frame, relief='flat')
        self.connected_table.grid(row=1, column=0, sticky="news", pady=2)

        logger.debug("Building controller frame in main frame...")
        self.controller_frame = Frame(self.main_frame, relief='flat', background='white', height=60)
        self.controller_frame.grid(row=2, column=0, sticky='news', pady=2)

        logger.debug("Building controller buttons label frame in main frame...")
        self.controller_btns = LabelFrame(self.controller_frame, text="Controller", relief='solid', height=60,
                                          background='gainsboro')
        self.controller_btns.pack(fill=BOTH)

        logger.debug("Building connected table in main frame...")
        self.table_frame = LabelFrame(self.connected_table, text="Connected Stations",
                                      relief='solid', background='gainsboro')
        self.table_frame.pack(fill=BOTH)

        logger.debug("Building details frame in main frame...")
        self.details_frame = Frame(self.main_frame, relief='flat', pady=2, height=310)
        self.details_frame.grid(row=3, column=0, sticky='news')

        logger.debug("Building statusbar frame in main frame...")
        self.statusbar_frame = Frame(self.main_frame, relief=SUNKEN, bd=1)
        self.statusbar_frame.grid(row=5, column=0, sticky='news')

        logger.debug("Building statusbar label frame in main frame...")
        self.status_label = Label(self.statusbar_frame, text='Status', relief=FLAT, anchor=W)
        self.status_label.pack(fill=BOTH)

        logger.debug("build_main_window_frames completed.")

    # Build Table for Server Information
    def build_server_information_table(self):
        logger.debug("Displaying server information table...")
        self.svrinfo_table = ttk.Treeview(self.srvinfo_frame,
                                          columns=("Serving On", "Server IP", "Server Port",
                                                   "Boot Time", "Connected Stations"),
                                          show="headings", height=1, selectmode=NONE)
        self.svrinfo_table.pack(fill=BOTH)

        # Columns & Headings config
        logger.debug("Building server information table columns...")
        self.svrinfo_table.column("#1", anchor=CENTER, width=300, stretch=NO)
        self.svrinfo_table.heading("#1", text="Serving On")
        self.svrinfo_table.column("#2", anchor=CENTER, width=220, stretch=NO)
        self.svrinfo_table.heading("#2", text="Server IP")
        self.svrinfo_table.column("#3", anchor=CENTER, width=100, stretch=NO)
        self.svrinfo_table.heading("#3", text="Server Port")
        self.svrinfo_table.column("#4", anchor=CENTER, width=250, stretch=YES)
        self.svrinfo_table.heading("#4", text="Boot Time")
        self.svrinfo_table.column("#5", anchor=CENTER, width=170, stretch=YES)
        self.svrinfo_table.heading("#5", text="Connected Stations")
        self.svrinfo_table.tag_configure('evenrow', background='snow')
        logger.info("server_information_table completed.")

    # Create Treeview Table for connected stations
    def build_connected_table(self) -> None:
        def highlight(event):
            self.connected_table = event.widget
            item = self.connected_table.identify_row(event.y)
            self.connected_table.tk.call(self.connected_table, "tag", "remove", "highlight")
            self.connected_table.tk.call(self.connected_table, "tag", "add", "highlight", item)

        logger.debug("Displaying Scrollbar...")
        self.table_sb = Scrollbar(self.table_frame, orient=VERTICAL)
        self.table_sb.pack(side=LEFT, fill=Y)

        logger.debug("Displaying connected table...")
        self.connected_table = ttk.Treeview(self.table_frame,
                                            columns=("ID", "MAC Address",
                                                     "IP Address", "Station Name",
                                                     "Logged User", "Client Version", "Boot Time"),
                                            show="headings", height=7,
                                            selectmode='browse', yscrollcommand=self.table_sb.set)
        self.connected_table.pack(fill=BOTH)
        self.table_sb.config(command=self.connected_table.yview)
        logger.debug("Defining highlight event for Connected Table...")
        self.connected_table.tag_configure('highlight', background='lightblue')

        # Columns & Headings config
        logger.debug("Building connected table columns...")
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

        logger.debug("Stying table row colors...")
        self.connected_table.tag_configure('oddrow', background='snow')
        self.connected_table.tag_configure('evenrow', background='ghost white')

        logger.info("build_connected_table completed.")

    # Create Controller Buttons
    def build_controller_buttons(self, endpoint):
        logger.debug("Defining refresh button's image...")
        refresh_img = PIL.ImageTk.PhotoImage(
            PIL.Image.open('images/refresh_green.png').resize((17, 17), PIL.Image.LANCZOS))

        logger.debug("Building refresh button...")
        self.refresh_btn = Button(self.controller_btns, text=" Refresh", image=refresh_img,
                                  compound=LEFT, anchor=W,
                                  width=75, pady=5, command=self.refresh_command)
        self.refresh_btn.image = refresh_img
        self.refresh_btn.grid(row=0, column=0, pady=5, padx=2)

        logger.debug("Building screenshot button...")
        self.screenshot_btn = Button(self.controller_btns, text="Screenshot", width=10,
                                     pady=5, padx=10,
                                     command=lambda: Commands(endpoint, self, path, log_path).screenshot_thread())
        self.screenshot_btn.grid(row=0, column=1, sticky="w", pady=5, padx=2, ipadx=2)
        logger.debug("Updating controller buttons list...")
        self.buttons.append(self.screenshot_btn)

        logger.debug("Building anydesk button...")
        self.anydesk_btn = Button(self.controller_btns, text="Anydesk", width=14, pady=5,
                                  command=lambda: Commands(endpoint, self, path, log_path).anydesk_command())
        self.anydesk_btn.grid(row=0, column=2, sticky="w", pady=5, padx=2, ipadx=2)
        logger.debug("Updating controller buttons list...")
        self.buttons.append(self.anydesk_btn)

        logger.debug("Building last restart button...")
        self.last_restart_btn = Button(self.controller_btns, text="Last Restart", width=14,
                                       pady=5,
                                       command=lambda: self.last_restart_command(endpoint))
        self.last_restart_btn.grid(row=0, column=3, sticky="w", pady=5, padx=2, ipadx=2)
        logger.debug("Updating controller buttons list...")
        self.buttons.append(self.last_restart_btn)

        logger.debug("Building system information button...")
        self.sysinfo_btn = Button(self.controller_btns, text="SysInfo", width=14, pady=5,
                                  command=lambda: Commands(endpoint, self, path, log_path).sysinfo_thread())
        self.sysinfo_btn.grid(row=0, column=4, sticky="w", pady=5, padx=2, ipadx=2)
        logger.debug("Updating controller buttons list...")
        self.buttons.append(self.sysinfo_btn)

        logger.debug("Building tasks button...")
        self.tasks_btn = Button(self.controller_btns, text="Tasks", width=14, pady=5,
                                command=lambda: Commands(endpoint, self, path, log_path).tasks())
        self.tasks_btn.grid(row=0, column=5, sticky="w", pady=5, padx=2, ipadx=2)
        logger.debug("Updating controller buttons list...")
        self.buttons.append(self.tasks_btn)

        logger.debug("Building restart button...")
        self.restart_btn = Button(self.controller_btns, text="Restart", width=14, pady=5,
                                  command=lambda: Commands(endpoint, self, path, log_path).restart_command())
        self.restart_btn.grid(row=0, column=6, sticky="w", pady=5, padx=2, ipadx=2)
        logger.debug("Updating controller buttons list...")
        self.buttons.append(self.restart_btn)

        logger.debug("Building local files button....")
        self.browse_btn = Button(self.controller_btns, text="Local Files", width=14, pady=5,
                                 command=lambda: Commands(endpoint, self, path, log_path).browse_local_files_command())
        self.browse_btn.grid(row=0, column=7, sticky="w", pady=5, padx=2, ipadx=2)
        logger.debug("Updating controller buttons list...")
        self.buttons.append(self.browse_btn)

        logger.debug("Building Update Client button...")
        self.update_client = Button(self.controller_btns, text="Update Client", width=14,
                                    pady=5, state=NORMAL,
                                    command=lambda: Commands(endpoint, self, path,
                                                             log_path).update_selected_endpoint_thread())
        self.update_client.grid(row=0, column=8, sticky="w", pady=5, padx=2, ipadx=2)
        logger.debug("Updating controller buttons list...")
        self.buttons.append(self.update_client)

        logger.debug("Building Maintenance button...")
        self.maintenance = Button(self.controller_btns, text="Maintenance", width=14,
                                  pady=5, state=DISABLED,
                                  command=lambda: Commands(endpoint, self, path, log_path).run_maintenance_thread())
        self.maintenance.grid(row=0, column=9, sticky="w", pady=5, padx=2, ipadx=2)
        # logger.debug("Updating controller buttons list...")
        # self.buttons.append(self.maintenance)
        logger.info("build_controller_buttons completed.")

    # Build Table for Connection History
    def create_connection_history_table(self) -> None:
        logger.debug("Displaying connection history labelFrame...")
        self.history_labelFrame = LabelFrame(self.main_frame, text="Connection History",
                                             relief='solid', background='gainsboro')
        self.history_labelFrame.grid(row=4, column=0, sticky='news')

        logger.debug("Displaying Scrollbar in history labelFrame...")
        self.history_table_scrollbar = Scrollbar(self.history_labelFrame, orient=VERTICAL)
        self.history_table_scrollbar.pack(side=LEFT, fill=Y)

        logger.debug("Displaying connection history table in labelFrame...")
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
        logger.debug("Building connection history table columns...")
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

        logger.debug(f'Stying table row colors...')
        self.history_table.tag_configure('oddrow', background='snow')
        self.history_table.tag_configure('evenrow', background='ghost white')

        logger.info("create_connection_history_table completed.")

    # Build Notebook
    def create_notebook(self, event=0):
        def on_tab_change(event):
            t = event.widget.tab('current')['text']
            if self.tabs == 0:
                return

        logger.debug("Building details LabelFrame...")
        self.details_labelFrame = LabelFrame(self.main_frame, text="Details", relief='solid',
                                             foreground='white', height=400, background='slate gray')
        self.details_labelFrame.grid(row=3, sticky='news', columnspan=3)

        logger.debug("Clearing frames list...")
        self.frames.clear()

        logger.debug("Building notebook...")
        self.notebook = ttk.Notebook(self.details_labelFrame, height=250)
        self.notebook.pack(expand=True, pady=5, fill=X)
        self.notebook.bind("<<NotebookTabChanged>>", on_tab_change)

        logger.debug("Defining screenshot tab...")
        self.screenshot_tab = Frame(self.notebook, height=330)

        logger.debug("Defining system information tab...")
        self.system_information_tab = Frame(self.notebook, height=330)
        self.tasks_tab = Frame(self.notebook, height=330)

        logger.debug("Building sysinfo scrollbar...")
        self.system_scrollbar = Scrollbar(self.system_information_tab, orient=VERTICAL)
        self.system_scrollbar.pack(side=LEFT, fill=Y)

        logger.debug("Building sysinfo textbox...")
        self.system_information_textbox = Text(self.system_information_tab,
                                               yscrollcommand=self.system_scrollbar.set)
        self.system_information_textbox.pack(fill=BOTH)

        logger.debug("Building tasks scrollbar...")
        self.tasks_scrollbar = Scrollbar(self.tasks_tab, orient=VERTICAL)
        self.tasks_scrollbar.pack(side=LEFT, fill=Y)

        logger.debug("Building tasks textbox...")
        self.tasks_tab_textbox = Text(self.tasks_tab, yscrollcommand=self.tasks_scrollbar.set)
        self.tasks_tab_textbox.pack(fill=X)

        logger.info("create_notebook completed.")

    # Update Status Bar Messages
    def update_statusbar_messages(self, msg=''):
        logger.debug(f"Displaying statusbar message: {msg}...")
        self.status_label.config(text=f"Status: {msg}")

    # Close App
    def on_closing(self, event=0) -> None:
        logger.debug("Displaying minimize popup window...")
        minimize = messagebox.askyesnocancel("Exit or Minimize", "Minimize to Tray?")
        logger.debug("Minimize: {minimize}")
        if minimize is None:
            return

        elif minimize:
            logger.debug("Hiding app window...")
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

            self.withdraw()
            logger.debug("Destroying app window...")
            self.destroy()
            sys.exit(0)

    # Enable Controller Buttons
    def enable_buttons(self):
        for button in list(self.buttons):
            logger.debug(f'Enabling {button.config("text")[-1]} button...')
            button.config(state=NORMAL)

        logger.info("enable_buttons completed.")

    # Disable Controller Buttons
    def disable_buttons(self):
        for button in list(self.buttons):
            logger.debug(f'Disabling {button.config("text")[-1]}...')
            button.config(state=DISABLED)

        logger.info("disable_buttons completed.")

    # Display Clients Last Restart
    def last_restart_command(self, endpoint) -> bool:
        logger.info(f'Running last_restart on {endpoint.ip} | {endpoint.ident})...')
        try:
            logger.debug(f'Sending lr command to client...')
            endpoint.conn.send('lr'.encode())
            logger.debug(f'Send completed. waiting for response from client...')
            msg = endpoint.conn.recv(1024).decode()
            logger.debug(f'Client response: {msg}')
            logger.debug(f'Updating statusbar message: restart for {endpoint.ident}: {msg.split("|")[1][15:]}')
            self.update_statusbar_messages_thread(msg=f'restart for {endpoint.ident}: {msg.split("|")[1][15:]}')
            logger.debug(f'Displaying popup:  Last Restart for: {endpoint.ip} | {endpoint.ident}...')
            messagebox.showinfo(f"Last Restart for: {endpoint.ip} | {endpoint.ident}",
                                f"\t{msg.split('|')[1][15:]}\t\t\t")

            logger.info(f'last_restart_command completed.')
            return True

        except (WindowsError, socket.error, ConnectionResetError) as e:
            logger.error(f'Connection Error: {e}.')
            logger.debug(f'Updating statusbar message')
            self.update_statusbar_messages_thread(msg=f'{e}')
            logger.debug(f'Calling server.remove_lost_connection({endpoint}...')
            self.server.remove_lost_connection(endpoint)
            logger.debug(f'Calling refresh_command')
            self.refresh_command()
            return False

    # Display Server Information
    def server_information(self) -> None:
        logger.info(f'Running server_information...')
        logger.debug(f'Retrieving server last boot time...')
        last_reboot = psutil.boot_time()
        bt = datetime.fromtimestamp(last_reboot).strftime('%d/%b/%y %H:%M:%S %p')
        try:
            logger.debug(f'Clearing system information table...')
            self.svrinfo_table.delete(*self.svrinfo_table.get_children())

        except Exception:
            pass

        c = 0
        logger.debug(f'Updating system information table...')
        if c % 2 == 0:
            self.svrinfo_table.insert('', 'end', values=(serving_on, self.server.serverIP, self.server.port, bt,
                                                         len(self.server.endpoints)), tags=('evenrow',))

        logger.info(f'server_information completed.')
        return

    # Display Available Stations
    def show_available_connections(self) -> None:
        logger.info(f'Running show_available_connections...')
        # Clear previous entries in GUI table
        try:
            logger.debug(f'Clearing system information table...')
            self.connected_table.delete(*self.connected_table.get_children())

        except Exception:
            pass

        if not self.server.endpoints:
            logger.debug(f'No connected Stations')
            return

        logger.debug(f'Updating connected table...')
        for count, endpoint in enumerate(self.server.endpoints):
            tag = 'evenrow' if count % 2 == 0 else 'oddrow'
            self.connected_table.insert('', 'end', values=(count, endpoint.client_mac, endpoint.ip,
                                                           endpoint.ident, endpoint.user,
                                                           endpoint.client_version, endpoint.boot_time),
                                        tags=(tag,))

        logger.info(f'show_available_connections completed.')

    # Display Connection History
    def connection_history(self) -> bool:
        logger.info(f'Running connection_history...')
        logger.debug(f'Calling show_available_connections...')
        self.show_available_connections()
        logger.debug(f'disable_buttons_thread...')
        self.disable_buttons_thread()
        logger.debug(f'Calling create_connection_history_table...')
        self.create_connection_history_table()
        try:
            logger.debug(f'Updating history table...')
            c = 0
            for entry, t in self.server.connHistory.items():
                tag = 'evenrow' if c % 2 == 0 else 'oddrow'
                self.history_table.insert('', 'end', values=(c, entry.client_mac, entry.ip,
                                                             entry.ident, entry.user,
                                                             t), tags=(tag,))
                c += 1

            logger.debug(f'Updating statusbar message: displaying connection history...')
            self.update_statusbar_messages_thread(msg=f'displaying connection history.')
            logger.info(f'connection_history completed.')
            return True

        except (KeyError, socket.error, ConnectionResetError) as e:
            logger.error(f'ERROR: {e}.')
            logger.debug(f'Updating statusbar message...')
            self.update_statusbar_messages_thread(msg=f'Status: {e}.')
            return False

    # Shell Connection to Client
    def shell(self, endpoint) -> None:
        logger.info(f'Running shell({endpoint.conn}, {endpoint.ip})...')
        logger.debug(f'Updating statusbar message: shell connected to {endpoint.ip} | {endpoint.ident}...')
        self.update_statusbar_messages_thread(msg=f'shell connected to {endpoint.ip} | {endpoint.ident}.')
        while True:
            logger.debug(f'Waiting for input...')
            cmd = input(f"")

    # Refresh server info & connected stations table with vital signs
    def refresh_command(self, event=0) -> None:
        logger.info(f'Running refresh...')
        logger.debug(f'Calling self_disable_buttons_thread...')
        self.disable_buttons_thread()
        logger.debug(f'Clearing self.temp...')
        self.temp.clear()
        logger.debug(f'Calling server.vital_signs...')
        self.server.vital_signs()
        logger.debug(f'Calling self.server_information...')
        self.server_information()
        logger.debug(f'Calling self.update_tools_menu...')
        self.update_tools_menu(None)
        logger.debug(f'Calling show_available_connections...')
        self.show_available_connections()
        logger.debug(f'Calling connection_history...')
        self.connection_history()
        logger.debug(f'Updating statusbar message: refresh complete...')
        self.update_statusbar_messages_thread(msg='refresh complete.')
        logger.info(f'refresh completed.')

    # Manage Connected Table & Controller LabelFrame Buttons
    def select_item(self, event) -> bool:
        logger.info(f'Running select_item...')
        # Respond to mouse clicks on connected table
        rowid = self.connected_table.identify_row(event.y)
        row = self.connected_table.item(rowid)['values']
        if row:
            try:
                if row[2] not in self.temp.values():
                    logger.debug(f'Updating temp dictionary...')
                    self.temp[row[0]] = row[2]

                    logger.debug(f'Calling create_notebook...')
                    if not self.notebooks:
                        self.create_notebook()

            # Error can raise when clicking on empty space so the row is None or empty.
            except IndexError:
                pass

            # Connect shell by TreeView Table selection
            for endpoint in self.server.endpoints:
                if row[2] == endpoint.ip:
                    self.enable_buttons_thread()
                    temp_notebook = {endpoint.ident: {endpoint.ip: self.notebook}}
                    if temp_notebook not in self.notebooks.items():
                        self.notebooks.update(temp_notebook)

                    if not self.running:
                        self.build_controller_buttons(endpoint)
                        logger.debug(f'Connecting shell to {endpoint.ip} | {endpoint.ident}...')
                        shellThread = Thread(target=self.shell,
                                             args=(endpoint,),
                                             daemon=True,
                                             name="Shell Thread")
                        shellThread.start()
                        shellThread.join(timeout=0.1)
                        if not shellThread.is_alive():
                            logger.debug(f'Disconnected from endpoint {endpoint.ip}...')
                            logger.debug(f'Calling server.remove_lost_connection({endpoint})...')
                            self.server.remove_lost_connection(endpoint)
                            logger.debug(f'Clearing temp dict...')
                            self.temp.clear()
                            logger.debug(f'Calling refresh_command...')
                            self.refresh_command()
                            break

                        logger.debug(f'Clearing temp dict...')
                        self.temp.clear()
                        logger.info(f'select_item completed.')


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
    log_path = fr'{path}\server_log.txt'
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    info = logging.FileHandler(log_path)
    info.setLevel(logging.INFO)
    info.setFormatter(formatter)

    debug = logging.FileHandler(log_path)
    debug.setLevel(logging.DEBUG)
    debug.setFormatter(formatter)

    error = logging.FileHandler(log_path)
    error.setLevel(logging.ERROR)
    error.setFormatter(info)

    logger.addHandler(info)
    logger.addHandler(debug)
    logger.addHandler(error)

    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--ip', action='store', default=serverIP, type=str, help='Server IP')
    parser.add_argument('-p', '--port', action='store', default=port, type=int, help='Server Port')
    args = parser.parse_args()

    app = App()
    main()
