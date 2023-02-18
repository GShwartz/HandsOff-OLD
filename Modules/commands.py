from tkinter import messagebox, filedialog
from datetime import datetime
from threading import Thread
from tkinter import *
import subprocess
import logging
import socket
import time
import csv
import os

# Local Modules
from Modules.screenshot import Screenshot
from Modules.server import Server
from Modules.about import About
from Modules.tasks import Tasks
from Modules.sysinfo import Sysinfo

from tkinter.ttk import Progressbar

# TODO:
#   1. Fix Update all clients messing up status messages - [V]
#   2. Fix restart selected client not refreshing the connections - [V]
#   3. Change datetime format in temp logger - [V]
#   4. Disable refresh button when clicking on system information - []


class Commands:
    def __init__(self, endpoint, app, path, log_path):
        self.endpoint = endpoint
        self.app = app
        self.path = path
        self.log_path = log_path

        self.init_logger()

    # Initiate logger
    def init_logger(self):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        context = logging.FileHandler(self.log_path)
        context.setLevel(logging.DEBUG)
        context.setFormatter(formatter)

        self.logger.addHandler(context)

    # Minimize Window
    def minimize(self):
        self.logger.debug("Minimizing screen...")
        return self.app.withdraw()

    # Clear Notebook
    def clear_notebook_command(self, event=0):
        self.logger.info(f'Running clear_notebook_command...')
        self.logger.debug("Calling create_notebook...")
        self.app.create_notebook()
        self.logger.debug("Updating statusbar message...")
        self.app.update_statusbar_messages_thread(msg='Details window cleared.')
        return

    # Save Connection History Thread
    def save_connection_history_thread(self, event=0):
        saveThread = Thread(target=self.save_connection_history,
                            daemon=True,
                            name="Save Connection History Thread")
        saveThread.start()

    # Save History to CSV
    def _save_to_csv(self, filename):
        self.logger.info(f'Running _save_to_csv...')
        try:
            self.logger.debug("Writing to CSV...")
            with open(filename, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(self.csv_header)
                for endpoint, dt in self.app.server.connHistory.items():
                    writer.writerow([endpoint.client_mac, endpoint.ip, endpoint.ident,
                                     endpoint.user, dt])

                self.logger.debug("Calling refresh_command...")
                self.refresh_command(event=0)
                self.logger.info(f'_save_to_csv completed.')
                return True

        except IOError as e:
            self.logger.debug(f"Error writing to {filename}: {e}")
            self.logger.debug(f"Updating statusbar message: Status: {e}.")
            self.app.update_statusbar_messages_thread(msg=f'Status: {e}.')
            return False

    # Save History to TXT
    def _save_to_txt(self, filename):
        self.logger.info(f'Running _save_to_txt...')
        try:
            self.logger.debug("Writing to TXT...")
            with open(filename, 'w') as file:
                c = 0
                for endpoint, dt in self.app.server.connHistory.items():
                    file.write(f"#{c} | MAC: {endpoint.client_mac} | IP: {endpoint.ip} | "
                               f"Station: {endpoint.ident} | User: {endpoint.user} | Time: {dt} \n")
                    c += 1

                self.logger.debug("Calling refresh_command...")
                self.refresh_command(event=0)
                self.logger.info(f'_save_to_txt completed.')
                return True

        except IOError as e:
            self.logger.debug(f"Error writing to {filename}: {e}")
            self.logger.debug(f"Updating statusbar message: Status: {e}.")
            self.app.update_statusbar_messages_thread(msg=f'Status: {e}.')
            return False

    # Save History
    def save_connection_history(self, event=0) -> bool:
        self.logger.info(f'Running save_connection_history...')
        self.file_types = {'CSV Files': '.csv', 'TXT Files': '.txt'}
        self.csv_header = ['MAC', 'IP', 'Station', 'User', 'Time']

        # Create Saved Files Dir
        saves = fr"{self.path}\Saves"
        if not os.path.exists(saves):
            self.logger.debug(f"Creating {saves}...")
            os.makedirs(saves)

        # Get Filename
        filename = filedialog.asksaveasfilename(initialdir=f"{saves}", defaultextension='.csv',
                                                filetypes=(('CSV files', '.csv'), ('TXT files', '.txt')))
        if not filename:
            self.logger.debug(f'Save canceled.')
            self.logger.debug(f'Calling app.refresh_command...')
            self.app.refresh_command(event=0)
            return False

        if filename.endswith('.csv'):
            self.logger.debug(f'Calling _save_to_csv({filename}...')
            return self._save_to_csv(filename)

        elif filename.endswith('.txt'):
            self.logger.debug(f'Calling _save_to_txt({filename}...')
            return self._save_to_txt(filename)

        else:
            self.logger.debug(f'Unknown file type: {filename}')
            self.logger.debug(f'Updating statusbar message: Unknown file type: {filename}')
            self.app.update_statusbar_messages_thread(msg=f'Unknown file type: {filename}')
            self.refresh_command(event=0)
            self.logger.info(f'save_connection_history completed.')
            return False

    # Restart All Clients
    def restart_all_clients_command(self):
        self.logger.debug(f'Updating statusbar message: waiting for restart confirmation...')
        self.app.update_statusbar_messages_thread(msg=f'waiting for restart confirmation...')
        self.logger.debug(f'Displaying validation pop-up...')
        self.sure = messagebox.askyesno(f"Restart All Clients\t", "Are you sure?")
        logIt_thread(self.log_path, msg=f'self.sure = {self.sure}')
        self.logger.debug(f'Validation: {self.sure}')

        def send_restart(endpoint):
            try:
                endpoint.conn.send('restart'.encode())
                time.sleep(1.15)
                self.logger.debug(f'Calling server.remove_lost_connection({endpoint}...')
                self.app.server.remove_lost_connection(endpoint)

            except (WindowsError, socket.error):
                pass

        if self.sure:
            threads = []

            for endpoint in self.app.server.endpoints:
                self.logger.debug(f'Sending restart to: {endpoint.conn}...')
                restartThread = Thread(target=send_restart, args=(endpoint,), name="Send Restart")
                restartThread.start()
                threads.append(restartThread)

            for thread in threads:
                thread.join()

            time.sleep(0.5)
            self.logger.debug(f'Showing completion pop-up...')
            messagebox.showinfo("Restart All Clients", "Done!\t\t\t\t")

        self.app.enable_buttons_thread()
        self.app.refresh_command()
        self.app.update_statusbar_messages_thread(msg='Restart command completed.')
        self.logger.info(f'restart_all_clients completed.')
        return True

    # Update all clients thread
    def update_all_clients_thread(self, event=0):
        update = Thread(target=self.update_all_clients_command,
                        daemon=True,
                        name="Update All Clients Thread")
        update.start()

    # Broadcast update command to all connected stations
    def update_all_clients_command(self) -> bool:
        logIt_thread(self.log_path, msg=f'Running update_all_clients()...')
        self.app.disable_buttons()
        sure = messagebox.askyesno(f"Update All Clients", "Are you sure?")
        if sure:
            for endpoint in self.app.server.endpoints:
                try:
                    endpoint.conn.send('update'.encode())
                    logIt_thread(self.log_path, msg=f'Send Completed.')

                except (WindowsError, socket.error) as e:
                    logIt_thread(self.log_path, msg=f'ERROR: {e}.')
                    self.app.remove_lost_connection(endpoint)
                    return False

            self.app.refresh_command()
            self.app.enable_buttons_thread()
            self.app.update_statusbar_messages_thread(msg='Update command sent.')
            self.app.refresh_command()
            return True

        else:
            self.refresh_command(event=0)
            return False

    # Show Help Thread
    def show_help_thread(self):
        helpThread = Thread(target=self.show_help,
                            daemon=True,
                            name="Show Help Thread")
        helpThread.start()

    # Show Help
    def show_help(self):
        github_url = 'https://github.com/GShwartz/HandsOff'
        return webbrowser.open_new_tab(github_url)

    # About Window
    def about(self, event=0) -> None:
        About(self.app).run()

    # Vitals Thread
    def vital_signs_thread(self) -> None:
        vitalsThread = Thread(target=self.app.server.vital_signs,
                              daemon=True,
                              name="Vitals Thread")
        vitalsThread.start()

    # Run Anydesk on Client
    def anydesk_command(self) -> bool:
        logIt_thread(self.log_path, msg=f'Running anydesk({self.endpoint.conn}, {self.endpoint.ip})...')
        self.app.update_statusbar_messages_thread(msg=f'running anydesk on '
                                                      f'{self.endpoint.ip} | {self.endpoint.ident}...')
        try:
            logIt_thread(self.log_path, msg=f'Sending anydesk command to {self.endpoint.conn}...')
            self.endpoint.conn.send('anydesk'.encode())
            logIt_thread(self.log_path, msg=f'Send Completed.')

            logIt_thread(self.log_path, msg=f'Waiting for response from client...')
            msg = self.endpoint.conn.recv(1024).decode()
            logIt_thread(self.log_path, msg=f'Client response: {msg}.')
            if "OK" not in msg:
                logIt_thread(self.log_path, msg=f'Printing msg from client...')
                self.app.update_statusbar_messages_thread(
                    msg=f'{self.endpoint.ip} | {self.endpoint.ident}: Anydesk not installed.')
                logIt_thread(self.log_path, msg=f'Display popup confirmation for install anydesk...')
                install_anydesk = messagebox.askyesno("Install Anydesk",
                                                      "Anydesk isn't installed on the remote machine. "
                                                      "do you with to install?")
                logIt_thread(self.log_path, msg=f'Install anydesk: {install_anydesk}.')
                if install_anydesk:
                    self.app.update_statusbar_messages_thread(
                        msg=f'installing anydesk on {self.endpoint.ip} | {self.endpoint.ident}...')
                    logIt_thread(self.log_path, msg=f'Sending install command to {self.endpoint.conn}...')
                    self.endpoint.conn.send('y'.encode())
                    logIt_thread(self.log_path, msg=f'Send Completed.')
                    logIt_thread(self.log_path, msg=f'Initiating StringVar() for textVar...')
                    textVar = StringVar()
                    while "OK" not in msg:
                        logIt_thread(self.log_path, msg=f'Waiting for response from client...')
                        msg = self.endpoint.conn.recv(1024).decode()
                        logIt_thread(self.log_path, msg=f'Client response: {msg}.')
                        textVar.set(msg)
                        logIt_thread(self.log_path, msg=f'textVar: {textVar}')
                        self.app.update_statusbar_messages_thread(msg=f'{msg}')

                    self.app.update_statusbar_messages_thread(msg=f'Status: {textVar}')
                    logIt_thread(self.log_path, msg=f'Display popup infobox')
                    messagebox.showinfo(f"From {self.endpoint.ip} | {self.endpoint.ident}",
                                        f"Anydesk Running.\t\t\t\t")
                    self.app.update_statusbar_messages_thread(msg=f'anydesk running on '
                                                                  f'{self.endpoint.ip} | {self.endpoint.ident}.')
                else:
                    logIt_thread(self.log_path, msg=f'Sending cancel command to {self.endpoint.conn}...')
                    self.endpoint.conn.send('n'.encode())
                    logIt_thread(self.log_path, msg=f'Send Completed.')
                    return

            else:
                self.app.update_statusbar_messages_thread(
                    msg=f'anydesk running on {self.endpoint.ip} | {self.endpoint.ident}.')
                logIt_thread(self.log_path, msg=f'Displaying popup window with "Anydesk Running"...')
                messagebox.showinfo(f"From {self.endpoint.ip} | {self.endpoint.ident}", f"Anydesk Running.\t\t\t\t")
                return True

        except (WindowsError, ConnectionError, socket.error, RuntimeError) as e:
            logIt_thread(self.log_path, debug=False, msg=f'Connection Error: {e}.')
            self.app.update_statusbar_messages_thread(msg=f'{e}.')
            logIt_thread(self.log_path, debug=False,
                         msg=f'Calling server.remove_lost_connection({self.endpoint})...')
            self.app.server.remove_lost_connection(self.endpoint)
            self.app.refresh_command()
            return False

    # Update Selected Client Thread
    def update_selected_endpoint_thread(self):
        updateThread = Thread(target=self.update_selected_endpoint,
                              daemon=True,
                              name="Update Selected Client Thread")
        updateThread.start()

    # Update Selected Client
    def update_selected_endpoint(self) -> bool:
        logIt_thread(self.log_path, msg=f'Displaying confirmation pop-up...')
        sure = messagebox.askyesno(f"Update {self.endpoint.ip} | {self.endpoint.ident}", "Are you sure?\t\t\t\t")
        if sure:
            logIt_thread(self.log_path, msg=f'Sending update command to {self.endpoint.ip} | {self.endpoint.ident}...')
            try:
                self.endpoint.conn.send('update'.encode())
                logIt_thread(self.log_path, msg=f'Send completed.')
                self.app.update_statusbar_messages_thread(msg=f'Update command sent to '
                                                              f'{self.endpoint.ip} | {self.endpoint.ident}.')
                logIt_thread(self.log_path, msg=f'Calling self.refresh()...')
                self.app.refresh_command()
                return True

            except (RuntimeError, WindowsError, socket.error) as e:
                logIt_thread(self.log_path, msg=f'Connection Error: {e}')
                self.app.update_statusbar_messages_thread(msg=f'{e}')
                logIt_thread(self.log_path, msg=f'Calling server.remove_lost_connection({self.endpoint})...')
                self.app.server.remove_lost_connection(self.endpoint)
                self.app.refresh_command()
                return False

        else:
            return False

    # Grab Screenshot Thread
    def screenshot(self):
        Thread(target=Screenshot(self.endpoint, self.app, self.path, self.log_path).run,
               name="Screenshot Thread").start()

    # System Information Thread
    def sysinfo_thread(self):
        Thread(target=Sysinfo(self.endpoint, self.app, self.path, self.log_path).run,
               name="System Information Thread").start()

    # Display/Kill Tasks on Client
    def tasks(self) -> bool:
        Tasks(self.endpoint, self.app, self.path, self.log_path).run()

    # Restart Client
    def restart_command(self) -> bool:
        self.app.disable_buttons()
        logIt_thread(self.log_path, msg=f'Running restart({self.endpoint.conn})')
        self.app.update_statusbar_messages_thread(msg=f' waiting for restart confirmation...')
        logIt_thread(self.log_path, msg=f'Displaying self.sure() popup window...')
        self.sure = messagebox.askyesno(f"Restart for: {self.endpoint.ip} | {self.endpoint.ident}",
                                        f"Are you sure you want to restart {self.endpoint.ident}?\t")
        logIt_thread(self.log_path, msg=f'self.sure = {self.sure}')

        if self.sure:
            try:
                logIt_thread(self.log_path, msg=f'Sending restart command to client...')
                self.endpoint.conn.send('restart'.encode())
                logIt_thread(self.log_path, msg=f'Send completed.')
                time.sleep(2.5)
                logIt_thread(self.log_path, msg=f'Calling self.refresh()...')
                self.app.refresh_command()
                self.app.update_statusbar_messages_thread(msg=f'restart command sent to '
                                                              f'{self.endpoint.ip} | {self.endpoint.ident}.')
                return True

            except (RuntimeError, WindowsError, socket.error) as e:
                logIt_thread(self.log_path, msg=f'Connection Error: {e}')
                self.app.update_statusbar_messages_thread(msg=f'{e}')
                logIt_thread(self.log_path, msg=f'Calling server.remove_lost_connection('
                                                f'{self.endpoint})...')
                self.app.server.remove_lost_connection(self.endpoint)
                self.app.refresh_command()
                return False

        else:
            self.app.update_statusbar_messages_thread(msg=f'restart canceled.')
            return False

    # Browse local files by Clients Station Names
    def browse_local_files_command(self) -> subprocess:
        logIt_thread(self.log_path, msg=fr'Opening explorer window focused on "{self.path}\{self.endpoint.ident}"')
        return subprocess.Popen(rf"explorer {self.path}\{self.endpoint.ident}")

    # Run maintenance thread
    def run_maintenance_thread(self):
        maintenanceThread = Thread(target=self.run_maintenance_command,
                                   daemon=True,
                                   name="Run Maintenance Thread")
        maintenanceThread.start()

    # Run Maintenance on Client
    def run_maintenance_command(self) -> None:
        self.app.running = True
        self.app.disable_buttons()

        logIt_thread(self.log_path, msg=f"Sending maintenance command to {self.endpoint.ip} | {self.endpoint.ident}...")
        self.app.update_statusbar_messages_thread(
            msg=f"Waiting for maintenance confirmation on {self.endpoint.ip} | {self.endpoint.ident}...")
        sure = messagebox.askyesno(f"Maintenance for {self.endpoint.ip} | {self.endpoint.ident}", "Are you sure?")
        if sure:
            self.app.update_statusbar_messages_thread(
                msg=f"Sending maintenance command to {self.endpoint.ip} | {self.endpoint.ident}...")
            try:
                self.endpoint.conn.send('maintenance'.encode())
                logIt_thread(self.log_path, msg=f"Maintenance command sent.")
                self.app.update_statusbar_messages_thread(
                    msg=f"Maintenance command sent to {self.endpoint.ip} | {self.endpoint.ident}.")
                logIt_thread(msg=f"Calling server.remove_lost_connection({self.endpoint})")
                server.remove_lost_connection(self.endpoint)
                self.app.refresh_command()
                time.sleep(0.5)
                logIt_thread(self.log_path, msg=f"Calling self.refresh_command()...")
                self.app.refresh_command()
                return True

            except (WindowsError, socket.error) as e:
                logIt_thread(self.log_path, msg=f"ERROR: {e}.")
                logIt_thread(self.log_path, msg=f"Calling server.remove_lost_connection({self.endpoint})")
                server.remove_lost_connection(self.endpoint)
                time.sleep(0.5)
                logIt_thread(self.log_path, msg=f"Calling self.refresh_command()...")
                self.app.refresh_command()
                self.app.running = False
                self.app.enable_buttons_thread()
                return False

        else:
            self.app.enable_buttons_thread()
            return False


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
