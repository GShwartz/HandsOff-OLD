from subprocess import Popen, PIPE
import win32com.client as win32
from datetime import datetime
from threading import Thread
import PySimpleGUI as sg
import subprocess
import threading
import PIL.Image
import pystray
import socket
import psutil
import ctypes
import pickle
import time
import wget
import uuid
import sys
import os

# Local Modules
from Modules.logger import init_logger
from Modules.screenshot import Screenshot


# TODO:
#   1. Check double confirmation at the end of anydesk() - [V]


class SystemInformation:
    def __init__(self, client):
        self.client = client
        self.dt = get_date()
        self.sifile = rf"systeminfo {self.client.hostname} {self.dt}.txt"
        self.si_full_path = os.path.join(app_path, self.sifile)

    def command_to_file(self):
        with open(self.si_full_path, 'w') as sysinfo:
            logIt_thread(log_path, msg='Running system information command...')
            sys_info = subprocess.run(['systeminfo'], stdout=subprocess.PIPE, text=True)
            sys_info_str = sys_info.stdout
            logIt_thread(log_path, msg=f'Adding header to {self.si_full_path}...')
            sysinfo.write(f"{'=' * 80}\n")
            sysinfo.write(
                f"IP: {self.client.localIP} | NAME: {self.client.hostname} | LOGGED USER: {os.getlogin()} | {self.dt}\n")
            sysinfo.write(f"{'=' * 80}\n")
            logIt_thread(log_path, msg=f'Adding system information to {self.si_full_path}...')
            sysinfo.write(f"{sys_info_str}\n\n")

    def send_filename(self):
        try:
            logIt_thread(log_path, msg='Sending file name...')
            self.client.soc.send(f"{self.sifile}".encode())
            logIt_thread(log_path, msg=f'Send Completed.')

        except (WindowsError, socket.error) as e:
            logIt_thread(log_path, msg=f'Connection Error: {e}')
            return False

    def send_file_size(self):
        try:
            logIt_thread(log_path, msg='Defining file size...')
            length = os.path.getsize(self.si_full_path)
            logIt_thread(log_path, msg=f'File Size: {length}')

            logIt_thread(log_path, msg='Sending file size...')
            self.client.soc.send(convert_to_bytes(length))
            logIt_thread(log_path, msg=f'Send Completed.')

        except (WindowsError, socket.error) as e:
            logIt_thread(log_path, msg=f'Connection Error: {e}')
            return False

    def send_file_content(self):
        try:
            logIt_thread(log_path, msg=f'Opening {self.si_full_path}...')
            with open(self.si_full_path, 'rb') as sy_file:
                logIt_thread(log_path, msg='Sending file content...')
                sys_data = sy_file.read(buffer_size)
                while sys_data:
                    self.client.soc.send(sys_data)
                    if not sys_data:
                        break

                    sys_data = sy_file.read(buffer_size)

            logIt_thread(log_path, msg=f'Send Completed.')

        except (WindowsError, socket.error, FileExistsError, FileNotFoundError) as e:
            logIt_thread(log_path, msg=f'Error: {e}')
            return False

    def confirm(self):
        try:
            logIt_thread(log_path, msg='Waiting for message from server...')
            msg = self.client.soc.recv(buffer_size).decode()
            logIt_thread(log_path, msg=f'From Server: {msg}')

        except (WindowsError, socket.error) as e:
            logIt_thread(log_path, msg=f'Connection Error: {e}')
            return False

    def run(self):
        self.command_to_file()
        self.send_filename()
        self.send_file_size()
        self.send_file_content()
        self.confirm()
        os.remove(self.si_full_path)
        sys.stdout.flush()


class Tasks:
    def __init__(self, client):
        self.client = client
        self.task_list = []
        logIt_thread(log_path, msg=f'Defining tasks file name...')
        self.dt = get_date()
        self.taskfile = rf"tasks {self.client.hostname} {str(self.client.localIP)} {self.dt}.txt"
        self.task_path = os.path.join(app_path, self.taskfile)

    def command_to_file(self):
        logIt_thread(log_path, msg=f'Running command_to_file()...')
        try:
            logIt_thread(log_path, msg=f'Opening file: {self.task_path}...')
            with open(self.task_path, 'w') as task_file:
                task_file.write(f"{'=' * 80}\n")
                task_file.write(f"IP: {self.client.localIP} | NAME: {self.client.hostname} | "
                                f"LOGGED USER: {os.getlogin()} | {self.dt}\n")
                task_file.write(f"{'=' * 80}\n")

            with open(self.task_path, 'a') as task_file:
                subprocess.run(['tasklist'], stdout=task_file)
                task_file.write('\n')

            return True

        except (FileNotFoundError, FileExistsError) as e:
            logIt_thread(log_path, msg=f'File Error: {e}')
            return False

    def send_file_name(self):
        logIt_thread(log_path, msg=f'Running send_file_name()...')
        try:
            logIt_thread(log_path, msg=f'Sending file name: {self.taskfile}...')
            self.client.soc.send(f"{self.taskfile}".encode())
            logIt_thread(log_path, msg=f'Send Completed.')
            return True

        except (WindowsError, socket.error) as e:
            logIt_thread(log_path, msg=f'Connection Error: {e}')
            return False

    def send_file_size(self):
        logIt_thread(log_path, msg=f'Running send_file_size()...')
        logIt_thread(log_path, msg=f'Defining file size...')
        length = os.path.getsize(self.task_path)
        logIt_thread(log_path, msg=f'File Size: {length}')

        try:
            logIt_thread(log_path, msg=f'Sending file size...')
            self.client.soc.send(convert_to_bytes(length))
            logIt_thread(log_path, msg=f'Send Completed.')
            return True

        except (WindowsError, socket.error) as e:
            logIt_thread(log_path, msg=f'Connection Error: {e}')
            return False

    def send_file_content(self):
        logIt_thread(log_path, msg=f'Running send_file_content()...')
        logIt_thread(log_path, msg=f'Opening file: {self.task_path}...')
        with open(self.task_path, 'rb') as tsk_file:
            logIt_thread(log_path, msg=f'Reading content from {self.task_path}...')
            tsk_data = tsk_file.read(1024)
            try:
                logIt_thread(log_path, msg=f'Sending file content...')
                while tsk_data:
                    self.client.soc.send(tsk_data)
                    if not tsk_data:
                        break

                    tsk_data = tsk_file.read(1024)

                logIt_thread(log_path, msg=f'Send Completed.')

            except (WindowsError, socket.error) as e:
                logIt_thread(log_path, msg=f'Connection Error: {e}')
                return False

    def confirm(self) -> bool:
        logIt_thread(log_path, msg=f'Running confirm()...')
        try:
            logIt_thread(log_path, msg=f'Waiting for confirmation from server...')
            self.client.soc.settimeout(10)
            msg = self.client.soc.recv(1024).decode()
            self.client.soc.settimeout(None)
            logIt_thread(log_path, msg=f'Server Confirmation: {msg}')

        except (WindowsError, socket.error) as e:
            logIt_thread(log_path, msg=f'Connection Error: {e}')
            return False

        try:
            logIt_thread(log_path, msg=f'Sending confirmation...')
            self.client.soc.send(f"{self.client.hostname} | {self.client.localIP}: Task List Sent.\n".encode())
            logIt_thread(log_path, msg=f'Send Completed.')
            return True

        except (WindowsError, socket.error) as e:
            logIt_thread(log_path, msg=f'Connection Error: {e}')
            return False

    def kill(self) -> bool:
        logIt_thread(log_path, msg=f'Waiting for task name...')
        try:
            self.client.soc.settimeout(10)
            task2kill = self.client.soc.recv(1024).decode()
            self.client.soc.settimeout(None)
            logIt_thread(log_path, msg=f'Task name: {task2kill}')

        except (WindowsError, socket.error) as e:
            logIt_thread(log_path, msg=f'Connection Error: {e}')
            return False

        if str(task2kill).lower()[:1] == 'q':
            return True

        logIt_thread(log_path, msg=f'Killing {task2kill}...')
        os.system(f'taskkill /IM {task2kill} /F')
        logIt_thread(log_path, msg=f'{task2kill} killed.')

        logIt_thread(log_path, msg=f'Sending killed confirmation to server...')
        try:
            self.client.soc.send(f"Task: {task2kill} Killed.".encode())
            logIt_thread(log_path, msg=f'Send Completed.')

        except (WindowsError, socket.error) as e:
            logIt_thread(log_path, msg=f'Connection Error: {e}')
            return False

        return True

    def run(self) -> bool:
        logIt_thread(log_path, msg=f'Calling command_to_file()...')
        self.command_to_file()
        logIt_thread(log_path, msg=f'Calling send_file_name()...')
        self.send_file_name()
        logIt_thread(log_path, msg=f'Calling send_file_size()...')
        self.send_file_size()
        logIt_thread(log_path, msg=f'Calling send_file_content()...')
        self.send_file_content()
        logIt_thread(log_path, msg=f'Calling confirm()...')
        self.confirm()
        logIt_thread(log_path, msg=f'Removing file: {self.task_path}...')
        os.remove(self.task_path)
        sys.stdout.flush()

        try:
            self.client.soc.settimeout(10)
            kil = self.client.soc.recv(1024).decode()
            self.client.soc.settimeout(None)

        except (WindowsError, socket.error):
            return False

        if str(kil)[:4].lower() == "kill":
            logIt_thread(log_path, msg=f'Calling kill()...')
            self.kill()
            return True


class Maintenance:
    def __init__(self, ps_path, client, log_path):
        self.ps_path = ps_path
        self.client = client
        self.log_path = log_path

    def maintenance(self) -> bool:
        try:
            checklist = pickle.loads(self.client.soc.recv(buffer_size))
            logIt_thread(log_path, msg=f"Checklist: {checklist}")

        except (WindowsError, socket.error) as e:
            return False

        # Make sure checklist is a dictionary
        if not isinstance(checklist, dict):
            logIt_thread(log_path, msg=f"Invalid checklist format: {checklist}")
            try:
                self.client.soc.send(f"Invalid checklist format: {checklist}")
                return False

            except (WindowsError, socket.error) as e:
                return False

        # Validate and sanitize checklist values
        for key, value in checklist.items():
            if not isinstance(value, bool):
                logIt_thread(log_path, msg=f"Invalid value for key '{key}': {value}")
                try:
                    self.client.soc.send(f"Invalid value for key '{key}': {value}")
                    return False

                except (WindowsError, socket.error) as e:
                    return False

        try:
            self.client.soc.send("OK".encode())

        except (WindowsError, socket.error) as e:
            return False

        logIt_thread(log_path, msg=f'Writing script to {self.ps_path}...')
        with open(self.ps_path, 'w') as file:
            for k, v in checklist.items():
                if v and str(k).lower() == 'chkdsk':
                    logIt_thread(log_path, msg=f"Scheduling ChkDsk...")
                    file.write("schtasks /create /tn 'CheckDisk' /tr 'chkdsk.exe c: /r /f' /sc onstart\n")

                if v and str(k).lower() == 'cleanup':
                    file.write('$HKLM = [UInt32] “0x80000002” \n')
                    file.write('$strKeyPath = “SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Explorer\\VolumeCaches"\n')
                    file.write('$strValueName = “StateFlags0065” \n')
                    file.write('$subkeys = Get-ChildItem -Path HKLM:\\$strKeyPath | Where-Object $strValueName\n')
                    file.write('Try {\n')
                    file.write(
                        '\tNew-ItemProperty -Path HKLM:\\$strKeyPath\\$subkey -Name $strValueName -PropertyType DWord -Value 2 -ErrorAction SilentlyContinue| Out-Null \n')
                    file.write('}\n')
                    file.write('\tCatch {\n')
                    file.write('}\n')
                    file.write('Try {\n')
                    file.write(
                        '\tStart-Process cleanmgr -ArgumentList “/sagerun:65” -Wait -NoNewWindow -ErrorAction SilentlyContinue -WarningAction SilentlyContinue\n')
                    file.write('}\n')
                    file.write('\tCatch {\n')
                    file.write('}\n')
                    file.write('Try {\n')
                    file.write(
                        '\tRemove-ItemProperty -Path HKLM:\\$strKeyPath\\$subkey -Name $strValueName | Out-Null\n')
                    file.write('}\n')
                    file.write('\tCatch {\n')
                    file.write('}\n\n')

                if v and str(k).lower() == 'sfc scan':
                    file.write('echo "Performing SFC scan..."\n')
                    file.write('sfc /scannow\n')

                if v and str(k).lower() == 'dism':
                    file.write('echo "Performing DISM Restore..."\n')
                    file.write('DISM /Online /Cleanup-Image /Restorehealth\n')

                if v and str(k).lower() == 'restart':
                    self.client.soc.close()
                    file.write('shutdown /r /t 0\n')

        logIt_thread(log_path, msg=f'Writing script to {self.ps_path} completed.')
        time.sleep(0.2)

        logIt_thread(log_path, msg=f'Running maintenance script...')
        # subprocess.run(["powershell.exe", "Set-ExecutionPolicy", "-ExecutionPolicy", "AllSigned", "-Scope", "Process"])
        ps = subprocess.Popen(["powershell.exe", rf"{self.ps_path}"], stdout=sys.stdout).communicate()
        os.remove(self.ps_path)
        return True


class Welcome:
    def __init__(self, client):
        self.client = client
        self.ps_path = rf'{app_path}\maintenance.ps1'

    def send_mac_address(self) -> str:
        logger.info(f"Running send_mac_address...")
        mac = ':'.join(['{:02x}'.format((uuid.getnode() >> ele) & 0xff)
                        for ele in range(0, 8 * 6, 8)][::-1])
        try:
            logger.debug(f"Sending MAC address: {mac}...")
            self.client.soc.send(mac.encode())
            logger.debug(f"Waiting for confirmation...")
            self.client.soc.settimeout(intro_socket_timeout)
            message = self.client.soc.recv(buffer_size).decode()
            self.client.soc.settimeout(default_socket_timeout)
            logger.debug(f"Server: {message}")
            logger.info(f"send_mac_address completed.")

        except (WindowsError, socket.error, socket.timeout) as e:
            logger.debug(f"Connection Error: {e}")
            return False

    def send_host_name(self) -> str:
        logger.info(f"Running send_host_name...")
        try:
            logger.debug(f"Sending hostname: {self.client.hostname}...")
            self.client.soc.send(self.client.hostname.encode())
            logger.debug(f"Waiting for confirmation...")
            self.client.soc.settimeout(intro_socket_timeout)
            message = self.client.soc.recv(buffer_size).decode()
            self.client.soc.settimeout(default_socket_timeout)
            logger.debug(f"Server: {message}")
            logger.info(f"send_host_name completed.")

        except (WindowsError, socket.error):
            logger.debug(f"Connection Error: {e}")
            return False

    def send_current_user(self) -> str:
        logger.info(f"Running send_current_user...")
        try:
            logger.debug(f"Sending current user: {self.client.current_user}...")
            self.client.soc.send(self.client.current_user.encode())
            logger.debug(f"Waiting for confirmation...")
            self.client.soc.settimeout(intro_socket_timeout)
            message = self.client.soc.recv(buffer_size).decode()
            self.client.soc.settimeout(default_socket_timeout)
            logger.debug(f"Server: {message}")
            logger.info(f"send_current_user completed.")

        except (WindowsError, socket.error) as e:
            logger.debug(f"Connection error: {e}")
            return False

    def send_client_version(self):
        logger.info(f"Running send_client_version...")
        try:
            logger.debug(f"Sending client version: {client_version}...")
            self.client.soc.send(client_version.encode())
            logger.debug(f"Waiting for confirmation...")
            self.client.soc.settimeout(intro_socket_timeout)
            message = self.client.soc.recv(buffer_size).decode()
            self.client.soc.settimeout(default_socket_timeout)
            logger.debug(f"Server: {message}")
            logger.info(f"send_client_version completed.")

        except (socket.error, WindowsError, socket.timeout) as e:
            logger.debug(f"Connection error: {e}")
            return False

    def send_boot_time(self):
        logger.info(f"Running send_boot_time...")
        try:
            logger.debug(f"Sending Boot Time version: {client_version}...")
            bt = self.get_boot_time()
            self.client.soc.send(str(bt).encode())
            logger.debug(f"Waiting for confirmation...")
            message = self.client.soc.recv(buffer_size).decode()
            logger.debug(f"Server: {message}")
            logger.info(f"send_boot_time completed.")

        except (socket.error, WindowsError, socket.timeout) as e:
            logger.debug(f"Connection error: {e}")
            return False

    def get_boot_time(self):
        logger.info(f"Running get_boot_time...")
        last_reboot = psutil.boot_time()
        return datetime.fromtimestamp(last_reboot).strftime('%d/%b/%y %H:%M:%S')

    def confirm(self):
        logger.info(f"Running confirm...")
        try:
            logger.debug(f"Waiting for confirmation...")
            self.client.soc.settimeout(intro_socket_timeout)
            message = self.client.soc.recv(buffer_size).decode()
            self.client.soc.settimeout(default_socket_timeout)
            logger.debug(f"Server: {message}")
            logger.info(f"confirm completed.")

        except (WindowsError, socket.error, socket.timeout) as e:
            logger.debug(f"Connection error: {e}")
            return False

    def anydeskThread(self) -> None:
        logger.debug(f"Running Anydesk App...")
        return subprocess.call([r"C:\Program Files (x86)\AnyDesk\anydesk.exe"])

    def anydesk(self):
        # Threaded Process
        def run_ad():
            return subprocess.run(anydesk_path)

        logger.debug(f"Running anydesk()...")
        try:
            if os.path.exists(r"C:\Program Files (x86)\AnyDesk\anydesk.exe"):
                anydeskThread = threading.Thread(target=self.anydeskThread, name="Run Anydesk")
                anydeskThread.daemon = True
                logger.debug(f"Calling anydeskThread()...")
                anydeskThread.start()
                logger.debug(f"Sending Confirmation...")
                self.client.soc.send("OK".encode())

            else:
                error = "Anydesk not installed."
                logger.debug(f"Sending error message: {error}...")
                self.client.soc.send(error.encode())

                try:
                    logger.debug(f"Waiting for install confirmation...")
                    install = self.client.soc.recv(buffer_size).decode()
                    if str(install).lower() == "y":
                        url = "https://download.anydesk.com/AnyDesk.exe"
                        destination = rf'c:\users\{os.getlogin()}\Downloads\anydesk.exe'

                        if not os.path.exists(destination):
                            logger.debug(f"Sending downloading message...")
                            self.client.soc.send("Downloading anydesk...".encode())

                            logger.debug(f"Downloading anydesk.exe..")
                            wget.download(url, destination)
                            logger.debug(f"Download complete.")

                        logger.debug(f"Sending running anydesk message...")
                        self.client.soc.send("Running anydesk...".encode())

                        logger.debug(f"Running anydesk...")
                        programThread = Thread(target=run_ad, name='programThread')
                        programThread.daemon = True
                        programThread.start()

                        logger.debug(f"Sending Confirmation...")
                        self.client.soc.send("Anydesk Running.".encode())

                        logger.debug(f"Sending final confirmation...")
                        self.client.soc.send("OK".encode())

                    else:
                        return False

                except (WindowsError, socket.error, socket.timeout) as e:
                    logger.debug(f"Error: {e}")
                    return False

        except FileNotFoundError as e:
            logger.debug(f"File Error: {e}")
            return False

    def main_menu(self):
        logger.info(f"Running main_menu...")
        self.client.soc.settimeout(menu_socket_timeout)
        while True:
            try:
                logger.debug(f"Waiting for command...")
                command = self.client.soc.recv(buffer_size).decode()
                logger.debug(f"Server Command: {command}")

            except (ConnectionResetError, ConnectionError,
                    ConnectionAbortedError, WindowsError, socket.error) as e:
                logger.debug(f"Connection Error: {e}")
                break

            try:
                if len(str(command)) == 0:
                    logger.debug(f"Connection Lost")
                    return False

                # Vital Signs
                elif str(command.lower())[:5] == "alive":
                    logger.debug(f"Calling Vital Signs...")
                    try:
                        logger.debug(f"Answer yes to server...")
                        self.client.soc.send('yes'.encode())

                    except (WindowsError, socket.error) as e:
                        logger.debug(f"Error: {e}")
                        break

                # Capture Screenshot
                elif str(command.lower())[:6] == "screen":
                    logger.debug(f"Initiating screenshot class...")
                    screenshot = Screenshot(self.client, log_path, app_path)
                    logger.debug(f"Calling screenshot.run...")
                    screenshot.run()

                # Get System Information & Users
                elif str(command.lower())[:2] == "si":
                    logger.debug(f"Initiating SystemInformation class...")
                    system = SystemInformation(self.client)
                    logger.debug(f"Calling system.run...")
                    system.run()

                # Get Last Restart Time
                elif str(command.lower())[:2] == "lr":
                    logger.debug(f"Fetching last restart time...")
                    last_reboot = psutil.boot_time()
                    try:
                        logger.debug(f"Sending last restart time...")
                        self.client.soc.send(f"{self.client.hostname} | {self.client.localIP}: "
                                             f"{self.get_boot_time()}".encode())

                    except ConnectionResetError as e:
                        logger.debug(f"Connection Error: {e}")
                        break

                # Run Anydesk
                elif str(command.lower())[:7] == "anydesk":
                    logger.debug(f"Calling anydesk...")
                    self.anydesk()
                    continue

                # Task List
                elif str(command.lower())[:5] == "tasks":
                    logger.debug(f"Calling tasks...")
                    task = Tasks(self.client)
                    task.run()

                # Restart Machine
                elif str(command.lower())[:7] == "restart":
                    logger.debug(f"Restarting local station...")
                    os.system('shutdown /r /t 1')

                # Run Updater
                elif str(command.lower())[:6] == "update":
                    try:
                        logger.debug(f"Running updater...")
                        subprocess.run(f'{updater_file}')
                        sys.exit(0)

                    except (WindowsError, socket.error) as e:
                        logger.debug(f"ERROR: {e}")
                        return False

                # Maintenance
                elif str(command.lower()) == "maintenance":
                    waiting_msg = "waiting"
                    try:
                        logger.debug(f"Sending waiting message...")
                        self.client.soc.send(waiting_msg.encode())

                    except (WindowsError, socket.error) as e:
                        logger.debug(f"ERROR: {e}")
                        return False

                    logger.debug(f"Initializing maintenance class...")
                    maintenance = Maintenance(self.ps_path, self.client, log_path)
                    logger.debug(f"Calling maintenance...")
                    maintenance.maintenance()
                    logger.debug(f"Calling self.connection...")
                    self.client.connection()
                    logger.debug(f"Calling main_menu...")
                    self.main_menu()

                # Close Connection
                elif str(command.lower())[:4] == "exit":
                    logger.debug(f"Server closed the connection.")
                    self.client.soc.settimeout(1)
                    # sys.exit(0)     # CI CD
                    break  # CICD

            except (Exception, socket.error, socket.timeout) as err:
                logger.debug(f"Connection Error: {e}")
                break


class Client:
    def __init__(self, server, soc):
        self.server_host = server[0]
        self.server_port = server[1]
        self.current_user = os.getlogin()
        self.hostname = socket.gethostname()
        self.localIP = str(socket.gethostbyname(self.hostname))
        self.soc = soc

        if not os.path.exists(f'{app_path}'):
            logger.debug(f"Creating App dir...")
            os.makedirs(app_path)

    def connection(self) -> None:
        logger.info(f"Running connection...")
        try:
            logger.debug(f"Connecting to Server: {self.server_host} | Port {self.server_port}...")
            self.soc.connect((self.server_host, self.server_port))

        except (TimeoutError, WindowsError, ConnectionAbortedError, ConnectionResetError, socket.timeout) as e:
            logger.debug(f"Connection error: {e}")
            return False

    def welcome(self):
        logger.info(f"Running welcome...")
        logger.debug(f"Initiating Welcome class..")
        endpoint_welcome = Welcome(self)
        logger.debug(f"Calling endpoint_welcome.send_mac_address...")
        endpoint_welcome.send_mac_address()
        logger.debug(f"Calling endpoint_welcome.send_host_name...")
        endpoint_welcome.send_host_name()
        logger.debug(f"Calling endpoint_welcome.send_current_user...")
        endpoint_welcome.send_current_user()
        logger.debug(f"Calling endpoint_welcome.send_client_version...")
        endpoint_welcome.send_client_version()
        logger.debug(f"Calling endpoint_welcome.send_boot_time...")
        endpoint_welcome.send_boot_time()
        logger.debug(f"Calling endpoint_welcome.confirm...")
        endpoint_welcome.confirm()

        logger.debug(f"Calling endpoint_welcome.main_menu...")
        endpoint_welcome.main_menu()
        return True


def on_clicked(icon, item):
    if str(item) == "About":
        layout = [[sg.Text("By Gil Shwartz\n@2022")], [sg.Button("OK")]]
        window = sg.Window("About", layout)
        window.set_icon('client.ico')

        while True:
            event, values = window.read()
            # End program if user closes window or
            # presses the OK button
            if event == "OK" or event == sg.WIN_CLOSED:
                break

        window.close()


def main():
    # Configure system tray icon
    icon_image = PIL.Image.open(rf"{app_path}\client.png")
    icon = pystray.Icon("HandsOff", icon_image, menu=pystray.Menu(
        pystray.MenuItem("About", on_clicked)
    ))

    # Show system tray icon
    logger.info("Displaying HandsOff icon...")
    iconThread = Thread(target=icon.run, name="Icon Thread")
    iconThread.daemon = True
    iconThread.start()

    server = ('handsoff.home.lab', 55400)

    # Start Client
    while True:
        try:
            logger.debug(f"Creating Socket...")
            soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            logger.debug(f"Defining socket to Reuse address...")
            soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            logger.debug(f"Initiating client Class...")
            client = Client(server, soc)

            logger.debug(f"connecting to {server}...")
            soc.settimeout(default_socket_timeout)
            soc.connect(server)
            logger.debug(f"Calling backdoor({soc})...")
            client.welcome()

        except (WindowsError, socket.error) as e:
            logger.debug(f"Connection Error: {e}")
            soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            logger.debug(f"Closing socket...")
            soc.close()
            logger.debug(f"Sleeping for 1s...")
            time.sleep(1)


if __name__ == "__main__":
    client_version = "1.0.0"
    app_path = r'c:\HandsOff'
    updater_file = rf'{app_path}\updater.exe'
    log_path = fr'{app_path}\client_log.txt'
    powershell = r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe"
    anydesk_path = rf'c:\users\{os.getlogin()}\Downloads\anydesk.exe'

    default_socket_timeout = None
    menu_socket_timeout = None
    intro_socket_timeout = 10
    buffer_size = 1024

    if not os.path.exists(app_path):
        os.makedirs(app_path)

    logger = init_logger(log_path, __name__)
    main()
