from subprocess import Popen, PIPE
from datetime import datetime
from threading import Thread
import PySimpleGUI as sg
import subprocess
import threading
import PIL.Image
import win32gui
import win32con
import win32ui
import pystray
import socket
import psutil
import ctypes
import time
import wget
import uuid
import sys
import os


# TODO:
#   1. Change datetime format to look like main - [V]
#   2. Add a psutil.net_connections option


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

            logIt_thread(log_path, msg=f'Sending confirmation message...')
            self.client.soc.send(f"{self.client.hostname} | {self.client.localIP}: System Information Sent.\n".encode())
            logIt_thread(log_path, msg=f'Send Completed.')

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


class Screenshot:
    def __init__(self, client):
        self.ps_path = rf'{app_path}\screenshot.ps1'
        self.client = client

        # d = datetime.now().replace(microsecond=0).strftime("%d-%b-%y %I.%M.%S %p")
        logIt_thread(log_path, msg='Defining screenshot file name...')
        self.filename = rf"screenshot {self.client.hostname} {self.client.localIP} {get_date()}.jpg"
        self.file_path = os.path.join(app_path, self.filename)
        logIt_thread(log_path, msg=f'Screenshot file name: {self.filename}')

    def run_script(self):
        logIt_thread(log_path, msg=f'Capturing screenshot...')
        desktop = win32gui.GetDesktopWindow()

        SM_CXVIRTUALSCREEN = 78
        SM_CYVIRTUALSCREEN = 79
        SM_XVIRTUALSCREEN = 76
        SM_YVIRTUALSCREEN = 77

        width = ctypes.windll.user32.GetSystemMetrics(SM_CXVIRTUALSCREEN)
        height = ctypes.windll.user32.GetSystemMetrics(SM_CYVIRTUALSCREEN)
        left = ctypes.windll.user32.GetSystemMetrics(SM_XVIRTUALSCREEN)
        top = ctypes.windll.user32.GetSystemMetrics(SM_YVIRTUALSCREEN)

        desktop_dc = win32gui.GetWindowDC(desktop)
        img_dc = win32ui.CreateDCFromHandle(desktop_dc)

        mem_dc = img_dc.CreateCompatibleDC()
        screenshot = win32ui.CreateBitmap()
        screenshot.CreateCompatibleBitmap(img_dc, width, height)
        mem_dc.SelectObject(screenshot)
        mem_dc.BitBlt((0, 0), (width, height), img_dc, (left, top), win32con.SRCCOPY)

        screenshot.SaveBitmapFile(mem_dc, self.file_path)

        mem_dc.DeleteDC()
        win32gui.DeleteObject(screenshot.GetHandle())
        logIt_thread(log_path, msg=f'Screenshot captured.')

    def send_file(self):
        try:
            # Send filename to server
            logIt_thread(log_path, msg='Sending file name to server...')
            self.client.soc.send(f"{self.filename}".encode())
            logIt_thread(log_path, msg=f'Send Completed.')

            # Receive filename Confirmation from the server
            logIt_thread(log_path, msg='Waiting for confirmation from server...')
            msg = self.client.soc.recv(1024).decode()
            logIt_thread(log_path, msg=f'Server confirmation: {msg}')
            logIt_thread(log_path, msg=f'Getting file size...')
            length = os.path.getsize(self.file_path)
            logIt_thread(log_path, msg=f'Sending file size to server...')
            self.client.soc.send(convert_to_bytes(length))
            logIt_thread(log_path, msg=f'Send Completed.')

            # Send file content
            logIt_thread(log_path, msg=f'Opening {self.filename} with read bytes permissions...')
            with open(self.file_path, 'rb') as img_file:
                img_data = img_file.read(1024)
                logIt_thread(log_path, msg=f'Sending file content...')
                while img_data:
                    self.client.soc.send(img_data)
                    if not img_data:
                        break

                    img_data = img_file.read(1024)

            logIt_thread(log_path, msg=f'Send Completed.')

        except (WindowsError, socket.error, ConnectionError) as e:
            logIt_thread(log_path, msg=f'Connection Error: {e}')
            return False

    def confirm(self):
        try:
            logIt_thread(log_path, msg=f'Sending confirmation...')
            self.client.soc.send(f"{self.client.hostname} | {self.client.localIP}: Screenshot Completed.\n".encode())
            logIt_thread(log_path, msg=f'Send Completed.')

        except (WindowsError, socket.error):
            logIt_thread(log_path, msg=f'Connection Error')
            return False

    def run(self):
        logIt_thread(log_path, msg='Calling run_script()...')
        self.run_script()
        logIt_thread(log_path, msg='Calling send_file()...')
        self.send_file()
        logIt_thread(log_path, msg='Calling confirm()...')
        self.confirm()
        os.remove(self.file_path)
        logIt_thread(log_path, msg=f'=== End of screenshot() ===')


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

    def print_file_content(self):
        logIt_thread(log_path, msg=f'Running print_file_content()...')
        logIt_thread(log_path, msg=f'Opening file: {self.task_path}...')
        with open(self.task_path, 'r') as file:
            logIt_thread(log_path, msg=f'Adding content to list...')
            for line in file.readlines():
                self.task_list.append(line)

        # logIt_thread(log_path, msg=f'Printing content from list...')
        # for t in self.task_list:
        #     print(t)

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
        logIt_thread(log_path, msg=f'Calling print_file_content()...')
        self.print_file_content()
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


class Welcome:
    def __init__(self, client):
        self.client = client
        self.ps_path = rf'{app_path}\maintenance.ps1'

    def send_mac_address(self) -> str:
        mac = ':'.join(['{:02x}'.format((uuid.getnode() >> ele) & 0xff)
                        for ele in range(0, 8 * 6, 8)][::-1])
        try:
            logIt_thread(log_path, msg=f'Sending MAC address: {mac}...')
            self.client.soc.send(mac.encode())
            logIt_thread(log_path, msg=f'Send completed.')
            logIt_thread(log_path, msg='Waiting for confirmation from server...')
            self.client.soc.settimeout(intro_socket_timeout)
            message = self.client.soc.recv(buffer_size).decode()
            self.client.soc.settimeout(default_socket_timeout)
            logIt_thread(log_path, msg=f'Message from server: {message}')

        except (WindowsError, socket.error, socket.timeout):
            logIt_thread(log_path, msg='Connection Error')
            return False

    def send_host_name(self) -> str:
        try:
            logIt_thread(log_path, msg=f'Sending hostname: {self.client.hostname}...')
            self.client.soc.send(self.client.hostname.encode())
            logIt_thread(log_path, msg=f'Send completed.')
            logIt_thread(log_path, msg='Waiting for confirmation from server...')
            self.client.soc.settimeout(intro_socket_timeout)
            message = self.client.soc.recv(buffer_size).decode()
            self.client.soc.settimeout(default_socket_timeout)
            logIt_thread(log_path, msg=f'Message from server: {message}')

        except (WindowsError, socket.error):
            logIt_thread(log_path, msg='Connection Error')
            return False

    def send_current_user(self) -> str:
        try:
            logIt_thread(log_path, msg=f'Sending current user: {self.client.current_user}...')
            self.client.soc.send(self.client.current_user.encode())
            logIt_thread(log_path, msg=f'Send completed.')
            logIt_thread(log_path, msg='Waiting for confirmation from server...')
            self.client.soc.settimeout(intro_socket_timeout)
            message = self.client.soc.recv(buffer_size).decode()
            self.client.soc.settimeout(default_socket_timeout)
            logIt_thread(log_path, msg=f'Message from server: {message}')

        except (WindowsError, socket.error):
            return False

    def send_client_version(self):
        try:
            logIt_thread(log_path, msg=f'Sending client version: {client_version}...')
            self.client.soc.send(client_version.encode())
            logIt_thread(log_path, msg=f'Send completed.')
            logIt_thread(log_path, msg='Waiting for confirmation from server...')
            self.client.soc.settimeout(intro_socket_timeout)
            message = self.client.soc.recv(buffer_size).decode()
            self.client.soc.settimeout(default_socket_timeout)
            logIt_thread(log_path, msg=f'Message from server: {message}')

        except (socket.error, WindowsError, socket.timeout) as e:
            return False

    def send_boot_time(self):
        try:
            logIt_thread(log_path, msg=f'Sending Boot Time version: {client_version}...')
            bt = self.get_boot_time()
            self.client.soc.send(str(bt).encode())
            logIt_thread(log_path, msg=f'Send completed.')
            logIt_thread(log_path, msg='Waiting for confirmation from server...')
            message = self.client.soc.recv(buffer_size).decode()
            logIt_thread(log_path, msg=f'Message from server: {message}')

        except (socket.error, WindowsError, socket.timeout) as e:
            return False

    def get_boot_time(self):
        logIt_thread(log_path, msg='Fetching last restart time...')
        last_reboot = psutil.boot_time()
        return datetime.fromtimestamp(last_reboot).strftime('%d/%b/%y %H:%M:%S')

    def confirm(self):
        try:
            logIt_thread(log_path, msg='Waiting for confirmation from server...')
            self.client.soc.settimeout(intro_socket_timeout)
            message = self.client.soc.recv(buffer_size).decode()
            self.client.soc.settimeout(default_socket_timeout)
            logIt_thread(log_path, msg=f'Message from server: {message}')

        except (WindowsError, socket.error, socket.timeout):
            logIt_thread(log_path, msg='Connection Error')
            return False

    def anydeskThread(self) -> None:
        logIt_thread(log_path, msg=f'Starting Anydesk app...')
        return subprocess.call([r"C:\Program Files (x86)\AnyDesk\anydesk.exe"])

    def anydesk(self):
        # Threaded Process
        def run_ad():
            return subprocess.run(anydesk_path)

        logIt_thread(log_path, msg=f'Running anydesk()...')
        try:
            if os.path.exists(r"C:\Program Files (x86)\AnyDesk\anydesk.exe"):
                anydeskThread = threading.Thread(target=self.anydeskThread, name="Run Anydesk")
                anydeskThread.daemon = True
                logIt_thread(log_path, msg=f'Calling anydeskThread()...')
                anydeskThread.start()
                logIt_thread(log_path, msg=f'Sending Confirmation...')
                self.client.soc.send("OK".encode())
                logIt_thread(log_path, msg=f'Send Complete.')

            else:
                error = "Anydesk not installed."
                logIt_thread(log_path, msg=f'Sending error message: {error}...')
                self.client.soc.send(error.encode())
                logIt_thread(log_path, msg=f'Send Complete.')

                try:
                    logIt_thread(log_path, msg=f'Waiting for install confirmation...')
                    install = self.client.soc.recv(buffer_size).decode()
                    if str(install).lower() == "y":
                        url = "https://download.anydesk.com/AnyDesk.exe"
                        destination = rf'c:\users\{os.getlogin()}\Downloads\anydesk.exe'

                        if not os.path.exists(destination):
                            logIt_thread(log_path, msg=f'Sending downloading message...')
                            self.client.soc.send("Downloading anydesk...".encode())

                            logIt_thread(log_path, msg=f'Downloading anydesk.exe...')
                            wget.download(url, destination)
                            logIt_thread(log_path, msg=f'Download complete.')

                        logIt_thread(log_path, msg=f'Sending running anydesk message...')
                        self.client.soc.send("Running anydesk...".encode())
                        logIt_thread(log_path, msg=f'Send Complete.')

                        logIt_thread(log_path, msg=f'Running anydesk...')
                        programThread = Thread(target=run_ad, name='programThread')
                        programThread.daemon = True
                        programThread.start()

                        logIt_thread(log_path, msg=f'Sending Confirmation...')
                        self.client.soc.send("Anydesk Running.".encode())
                        logIt_thread(log_path, msg=f'Send Complete.')

                        logIt_thread(log_path, msg=f'Sending Confirmation...')
                        self.client.soc.send("OK".encode())
                        logIt_thread(log_path, msg=f'Send Completed.')

                    else:
                        return False

                except (WindowsError, socket.error, socket.timeout) as e:
                    logIt_thread(log_path, msg=f'{e}')
                    return False

        except FileNotFoundError as e:
            logIt_thread(self.client.log_path, msg=f'File Error: {e}')
            return False

    def maintenance_thread(self):
        mThread = Thread(target=self.maintenance,
                         daemon=True,
                         name="Maintenance Thread")
        mThread.start()

    def maintenance(self) -> bool:
        logIt_thread(log_path, msg='Running make_script()...')

        # Schedule ChkDsk
        logIt_thread(log_path, msg=f"Scheduling ChkDsk...")
        p = Popen(['chkdsk', 'c:', '/r', '/x', '/b'], stdin=PIPE, stdout=PIPE)
        output, _ = p.communicate(b'y')

        logIt_thread(log_path, msg=f'Writing script to {self.ps_path}...')
        with open(self.ps_path, 'w') as file:
            file.write(r"""
$HKLM = [UInt32] “0x80000002”
$strKeyPath = “SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\VolumeCaches”
$strValueName = “StateFlags0065”
$subkeys = gci -Path HKLM:\$strKeyPath -Name
Try {
    New-ItemProperty -Path HKLM:\$strKeyPath\$subkey -Name $strValueName -PropertyType DWord -Value 2 -ErrorAction SilentlyContinue| Out-Null
}
    Catch {
}
try {
    Start-Process cleanmgr -ArgumentList “/sagerun:65” -Wait -NoNewWindow -ErrorAction SilentlyContinue -WarningAction SilentlyContinue
}
catch {
}
Try {
    Remove-ItemProperty -Path HKLM:\$strKeyPath\$subkey -Name $strValueName | Out-Null
}
Catch {
}
""")
            file.write('\nsfc /scannow\n')
            file.write('DISM /Online /Cleanup-Image /Restorehealth\n')
            file.write('                 ')
        logIt_thread(log_path, msg=f'Writing script to {self.ps_path} completed.')
        time.sleep(0.2)

        logIt_thread(log_path, msg=f'Running maintenance script...')
        ps = subprocess.Popen(["powershell.exe", rf"{self.ps_path}"], stdout=sys.stdout)
        ps.communicate()
        os.remove(self.ps_path)
        logIt_thread(log_path, msg=f'Rebooting...')
        # os.system('shutdown /r /t 1')

    def main_menu(self):
        logIt_thread(log_path, msg='Starting main menu...')
        self.client.soc.settimeout(menu_socket_timeout)
        while True:
            try:
                logIt_thread(log_path, msg='Waiting for command...')
                command = self.client.soc.recv(buffer_size).decode()
                logIt_thread(log_path, msg=f'Server Command: {command}')

            except (ConnectionResetError, ConnectionError,
                    ConnectionAbortedError, WindowsError, socket.error) as e:
                logIt_thread(log_path, msg=f'Connection Error: {e}')
                break

            try:
                if len(str(command)) == 0:
                    logIt_thread(self.client.log_path, msg='Connection Lost')
                    return False

                # Vital Signs
                elif str(command.lower())[:5] == "alive":
                    logIt_thread(log_path, msg='Calling Vital Signs...')
                    try:
                        logIt_thread(log_path, msg='Answer yes to server')
                        self.client.soc.send('yes'.encode())
                        logIt_thread(log_path, msg=f'Send completed.')

                    except (WindowsError, socket.error) as e:
                        logIt_thread(log_path, msg=f'{e}')
                        break

                # Capture Screenshot
                elif str(command.lower())[:6] == "screen":
                    logIt_thread(log_path, msg='Initiating screenshot class...')
                    screenshot = Screenshot(self.client)
                    screenshot.run()

                # Get System Information & Users
                elif str(command.lower())[:2] == "si":
                    system = SystemInformation(self.client)
                    system.run()

                # Get Last Restart Time
                elif str(command.lower())[:2] == "lr":
                    logIt_thread(log_path, msg='Fetching last restart time...')
                    last_reboot = psutil.boot_time()
                    try:
                        logIt_thread(log_path, msg='Sending last restart time...')
                        self.client.soc.send(f"{self.client.hostname} | {self.client.localIP}: "
                                             f"{self.get_boot_time()}".encode())

                        logIt_thread(log_path, msg=f'Send completed.')

                    except ConnectionResetError as e:
                        logIt_thread(log_path, msg=f'Connection Error: {e}')
                        break

                # Run Anydesk
                elif str(command.lower())[:7] == "anydesk":
                    logIt_thread(log_path, msg='Calling anydesk()...')
                    self.anydesk()
                    continue

                # Task List
                elif str(command.lower())[:5] == "tasks":
                    logIt_thread(log_path, msg='Calling tasks()...')
                    task = Tasks(self.client)
                    task.run()

                # Restart Machine
                elif str(command.lower())[:7] == "restart":
                    logIt_thread(log_path, msg='Restarting local station...')
                    os.system('shutdown /r /t 1')

                # Run Updater
                elif str(command.lower())[:6] == "update":
                    try:
                        logIt_thread(log_path, msg='Running updater...')
                        subprocess.run(f'{updater_file}')
                        sys.exit(0)

                    except (WindowsError, socket.error) as e:
                        logIt_thread(log_path, msg=f'ERROR: {e}.')
                        return False

                # Maintenance
                elif str(command.lower()) == "maintenance":
                    logIt_thread(log_path, msg=f'Calling self.maintenance()...')
                    self.client.maintenance()
                    logIt_thread(log_path, msg=f'Calling self.connection()...')
                    self.client.connection()
                    logIt_thread(log_path, msg=f'Calling backdoor({self.client.soc})...')
                    self.main_menu()

                # Close Connection
                elif str(command.lower())[:4] == "exit":
                    logIt_thread(log_path, msg='Server closed the connection.')
                    self.client.soc.settimeout(1)
                    # sys.exit(0)     # CI CD
                    break  # CICD

            except (Exception, socket.error, socket.timeout) as err:
                logIt_thread(log_path, msg=f'Connection Error: {e}')
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
            os.makedirs(app_path)

    def connection(self) -> None:
        logIt_thread(log_path, msg=f'Running connection()...')
        try:
            logIt_thread(log_path, msg=f'Connecting to Server: {self.server_host} | Port {self.server_port}...')
            self.soc.connect((self.server_host, self.server_port))

        except (TimeoutError, WindowsError, ConnectionAbortedError, ConnectionResetError, socket.timeout) as e:
            logIt_thread(log_path, msg=f'Connection Error: {e}')
            return False

    def welcome(self):
        endpoint_welcome = Welcome(self)
        endpoint_welcome.send_mac_address()
        endpoint_welcome.send_host_name()
        endpoint_welcome.send_current_user()
        endpoint_welcome.send_client_version()
        endpoint_welcome.send_boot_time()
        endpoint_welcome.confirm()

        logIt_thread(log_path, msg='Calling main_menu()...')
        endpoint_welcome.main_menu()
        return True


def get_date() -> str:
    d = datetime.now().replace(microsecond=0)
    dt = str(d.strftime("%d-%b-%y %I.%M.%S %p"))

    return dt


def logIt(logfile=None, debug=None, msg=''):
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


def logIt_thread(log_path=None, debug=False, msg=''):
    logit_thread = Thread(target=logIt, args=(log_path, debug, msg), name="Log Thread")
    logit_thread.start()
    return


def convert_to_bytes(no):
    result = bytearray()
    result.append(no & 255)
    for i in range(3):
        no = no >> 8
        result.append(no & 255)
    return result


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
    iconThread = Thread(target=icon.run, name="Icon Thread")
    iconThread.daemon = True
    iconThread.start()

    # servers = [('handsoff.home.lab', 55400)]
    server = ('handsoff.home.lab', 55400)

    # Start Client
    while True:
        try:
            logIt_thread(log_path, msg='Creating Socket...')
            soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            logIt_thread(log_path, msg='Defining socket to Reuse address...')
            soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            logIt_thread(log_path, msg='Initiating client Class...')
            client = Client(server, soc)

            logIt_thread(log_path, msg=f'connecting to {server}...')
            soc.connect(server)
            logIt_thread(log_path, msg=f'Calling backdoor({soc})...')
            client.welcome()

        except (WindowsError, socket.error) as e:
            logIt_thread(log_path, msg=f'Connection Error: {e}')
            soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            logIt_thread(log_path, msg=f'Closing socket...')
            soc.close()
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

    main()
