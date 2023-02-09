from subprocess import Popen, PIPE, check_output
from datetime import datetime
from threading import Thread
import subprocess
import threading
import PIL.Image
import pystray
import socket
import psutil
import time
import wget
import uuid
import sys
import os

# GUI
import PySimpleGUI as sg

# Local Modules
from screenshot import Screenshot
from sysinfo import Sysinfo
from tasks import Tasks
from freestyle import Freestyle


class Client:
    def __init__(self, server, main_path, log_path):
        self.threads = []
        self.log_path = log_path
        self.main_path = main_path
        self.server_host = server[0]
        self.server_port = server[1]
        self.buffer_size = 1024
        self.d = datetime.now()
        self.dt = str(self.d.strftime("%b %d %Y %I.%M.%S %p"))
        self.current_user = os.getlogin()
        self.hostname = socket.gethostname()
        self.localIP = str(socket.gethostbyname(self.hostname))
        if not os.path.exists(f'{self.main_path}'):
            os.makedirs(self.main_path)

        self.ps_path = self.ps_path = rf'{self.main_path}\maintenance.ps1'

    def get_date(self) -> str:
        d = datetime.now().replace(microsecond=0)
        dt = str(d.strftime("%b %d %Y %I.%M.%S %p"))

        return dt

    def logIt(self, logfile=None, debug=None, msg=''):
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

    def logIt_thread(self, log_path=None, debug=False, msg=''):
        self.logit_thread = Thread(target=self.logIt, args=(log_path, debug, msg), name="Log Thread")
        self.logit_thread.start()
        self.threads.append(self.logit_thread)
        return

    def convert_to_bytes(self, no):
        result = bytearray()
        result.append(no & 255)
        for i in range(3):
            no = no >> 8
            result.append(no & 255)
        return result

    def connection(self) -> None:
        self.logIt_thread(log_path, msg=f'Running connection()...')
        while True:
            time.sleep(1)
            try:
                self.logIt_thread(log_path,
                                  msg=f'Connecting to Server: {self.server_host} | Port {self.server_port}...')
                soc.connect((self.server_host, self.server_port))

            except (TimeoutError, WindowsError, ConnectionAbortedError, ConnectionResetError, socket.timeout) as e:
                self.logIt_thread(log_path, msg=f'Connection Error: {e}')
                continue

    def anydeskThread(self) -> None:
        self.logIt_thread(log_path, msg=f'Starting Anydesk app...')
        return subprocess.call([r"C:\Program Files (x86)\AnyDesk\anydesk.exe"])

    def anydesk(self):
        # Threaded Process
        def run_ad():
            return subprocess.run([f'{program_path}'])

        self.logIt_thread(log_path, msg=f'Running anydesk()...')
        try:
            if os.path.exists(r"C:\Program Files (x86)\AnyDesk\anydesk.exe"):
                anydeskThread = threading.Thread(target=self.anydeskThread, name="Run Anydesk")
                anydeskThread.daemon = True
                self.logIt_thread(log_path, msg=f'Calling anydeskThread()...')
                anydeskThread.start()
                self.logIt_thread(log_path, msg=f'Sending Confirmation...')
                soc.send("OK".encode())
                self.logIt_thread(log_path, msg=f'Send Complete.')

            else:
                error = "Anydesk not installed."
                self.logIt_thread(log_path, msg=f'Sending error message: {error}...')
                soc.send(error.encode())
                self.logIt_thread(log_path, msg=f'Send Complete.')

                try:
                    self.logIt_thread(log_path, msg=f'Waiting for install confirmation...')
                    soc.settimeout(anydesk_socket_timeout)
                    install = soc.recv(1024).decode()
                    if str(install).lower() == "y":
                        url = "https://download.anydesk.com/AnyDesk.exe"
                        destination = rf'c:\users\{os.getlogin()}\Downloads\anydesk.exe'

                        if not os.path.exists(destination):
                            self.logIt_thread(log_path, msg=f'Sending downloading message...')
                            soc.send("Downloading anydesk...".encode())

                            self.logIt_thread(log_path, msg=f'Downloading anydesk.exe...')
                            wget.download(url, destination)
                            self.logIt_thread(log_path, msg=f'Download complete.')

                        self.logIt_thread(log_path, msg=f'Sending running anydesk message...')
                        soc.send("Running anydesk...".encode())
                        self.logIt_thread(log_path, msg=f'Send Complete.')

                        self.logIt_thread(log_path, msg=f'Running anydesk...')
                        program_path = rf'c:\users\{os.getlogin()}\Downloads\anydesk.exe'
                        programThread = Thread(target=run_ad, name='programThread')
                        programThread.daemon = True
                        programThread.start()

                        self.logIt_thread(log_path, msg=f'Sending Confirmation...')
                        soc.send("Anydesk Running.".encode())
                        self.logIt_thread(log_path, msg=f'Send Complete.')

                        self.logIt_thread(log_path, msg=f'Sending Confirmation...')
                        soc.send("OK".encode())
                        soc.settimeout(default_socket_timeout)
                        self.logIt_thread(log_path, msg=f'Send Completed.')

                    else:
                        return False

                except (WindowsError, socket.error, socket.timeout) as e:
                    return False

        except FileNotFoundError as e:
            self.logIt_thread(log_path, msg=f'File Error: {e}')
            return False

    def maintenance_thread(self):
        mThread = Thread(target=self.maintenance,
                         daemon=True,
                         name="Maintenance Thread")
        mThread.start()

    def maintenance(self) -> bool:
        self.logIt_thread(self.log_path, msg='Running make_script()...')

        # Schedule ChkDsk
        self.logIt_thread(self.log_path, msg=f"Scheduling ChkDsk...")
        p = Popen(['chkdsk', 'c:', '/r', '/x', '/b'], stdin=PIPE, stdout=PIPE)
        output, _ = p.communicate(b'y')

        self.logIt_thread(self.log_path, msg=f'Writing script to {self.ps_path}...')
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
        self.logIt_thread(self.log_path, msg=f'Writing script to {self.ps_path} completed.')
        time.sleep(0.2)

        self.logIt_thread(self.log_path, msg=f'Running maintenance script...')
        ps = subprocess.Popen(["powershell.exe", rf"{self.ps_path}"], stdout=sys.stdout)
        ps.communicate()
        os.remove(self.ps_path)
        self.logIt_thread(self.log_path, msg=f'Rebooting...')
        # os.system('shutdown /r /t 1')

    def updater(self, url):
        try:
            update_url = soc.recv(1024).decode()
            self.logIt_thread(log_path, msg='Sending confirmation...')
            soc.send('Running updater...'.encode())
            self.logIt_thread(log_path, msg='Send complete.')
            self.logIt_thread(log_path, msg='Running updater...')
            subprocess.call([fr'python {self.main_path}\updater.py -u {self.main_path}\test -u {url}'])

        except (WindowsError, socket.error) as e:
            self.logIt_thread(log_path, msg=f'ERROR: {e}')
            return False

    def backdoor(self, soc):
        def intro():
            def send_mac_address() -> str:
                mac = ':'.join(['{:02x}'.format((uuid.getnode() >> ele) & 0xff)
                                for ele in range(0, 8 * 6, 8)][::-1])
                try:
                    self.logIt_thread(log_path, msg=f'Sending MAC address: {mac}...')
                    soc.send(mac.encode())
                    self.logIt_thread(log_path, msg=f'Send completed.')
                    self.logIt_thread(log_path, msg='Waiting for confirmation from server...')
                    soc.settimeout(intro_socket_timeout)
                    message = soc.recv(self.buffer_size).decode()
                    soc.settimeout(default_socket_timeout)
                    self.logIt_thread(log_path, msg=f'Message from server: {message}')

                except (WindowsError, socket.error, socket.timeout):
                    self.logIt_thread(log_path, msg='Connection Error')
                    return False

            def send_host_name() -> str:
                ident = self.hostname
                try:
                    self.logIt_thread(log_path, msg=f'Sending hostname: {self.hostname}...')
                    soc.send(ident.encode())
                    self.logIt_thread(log_path, msg=f'Send completed.')
                    self.logIt_thread(log_path, msg='Waiting for confirmation from server...')
                    soc.settimeout(intro_socket_timeout)
                    message = soc.recv(self.buffer_size).decode()
                    soc.settimeout(default_socket_timeout)
                    self.logIt_thread(log_path, msg=f'Message from server: {message}')

                except (WindowsError, socket.error):
                    self.logIt_thread(log_path, msg='Connection Error')
                    return False

            def send_current_user() -> str:
                user = self.current_user
                try:
                    self.logIt_thread(log_path, msg=f'Sending current user: {user}...')
                    soc.send(user.encode())
                    self.logIt_thread(log_path, msg=f'Send completed.')
                    self.logIt_thread(log_path, msg='Waiting for confirmation from server...')
                    soc.settimeout(intro_socket_timeout)
                    message = soc.recv(self.buffer_size).decode()
                    soc.settimeout(default_socket_timeout)

                    self.logIt_thread(log_path, msg=f'Message from server: {message}')

                except (WindowsError, socket.error):
                    return False

            def send_client_version():
                try:
                    self.logIt_thread(log_path, msg=f'Sending client version: {client_version}...')
                    soc.send(client_version.encode())
                    self.logIt_thread(log_path, msg=f'Send completed.')
                    self.logIt_thread(log_path, msg='Waiting for confirmation from server...')
                    soc.settimeout(intro_socket_timeout)
                    message = soc.recv(self.buffer_size).decode()
                    soc.settimeout(default_socket_timeout)
                    self.logIt_thread(log_path, msg=f'Message from server: {message}')

                except (socket.error, WindowsError, socket.timeout) as e:
                    return False

            def confirm():
                try:
                    self.logIt_thread(log_path, msg='Waiting for confirmation from server...')
                    soc.settimeout(intro_socket_timeout)
                    message = soc.recv(self.buffer_size).decode()
                    soc.settimeout(default_socket_timeout)
                    self.logIt_thread(log_path, msg=f'Message from server: {message}')

                except (WindowsError, socket.error, socket.timeout):
                    self.logIt_thread(log_path, msg='Connection Error')
                    return False

            self.logIt_thread(log_path, msg='Calling send_mac_address()...')
            send_mac_address()
            self.logIt_thread(log_path, msg='Calling send_host_name()...')
            send_host_name()
            self.logIt_thread(log_path, msg='Calling send_current_user()...')
            send_current_user()
            self.logIt_thread(log_path, msg='Calling send_client_version()...')
            send_client_version()

        def main_menu():
            self.logIt_thread(log_path, msg='Starting main menu...')
            soc.settimeout(menu_socket_timeout)
            while True:
                try:
                    self.logIt_thread(log_path, msg='Waiting for command...')
                    command = soc.recv(self.buffer_size).decode()
                    self.logIt_thread(log_path, msg=f'Server Command: {command}')

                except (ConnectionResetError, ConnectionError,
                        ConnectionAbortedError, WindowsError, socket.error) as e:
                    self.logIt_thread(log_path, msg=f'Connection Error: {e}')
                    break

                try:
                    if len(str(command)) == 0:
                        self.logIt_thread(log_path, msg='Connection Lost')
                        break

                    # Freestyle
                    if str(command.lower())[:9] == "freestyle":
                        self.logIt_thread(log_path, msg='Initiating Freestyle class...')
                        free = Freestyle(soc, log_path, self.hostname, self.localIP)

                        self.logIt_thread(log_path, msg='Calling Freestyle class...')
                        free.free_style()

                    # Vital Signs
                    if str(command.lower())[:5] == "alive":
                        self.logIt_thread(log_path, msg='Calling Vital Signs...')
                        try:
                            self.logIt_thread(log_path, msg='Answer yes to server')
                            soc.send('yes'.encode())
                            self.logIt_thread(log_path, msg=f'Send completed.')

                            self.logIt_thread(log_path, msg='Sending client version to server...')
                            soc.send(client_version.encode())
                            self.logIt_thread(log_path, msg=f'Send completed.')

                        except (WindowsError, socket.error):
                            break

                    # Capture Screenshot
                    elif str(command.lower())[:6] == "screen":
                        self.logIt_thread(log_path, msg='Initiating screenshot class...')
                        self.ps_path = rf"{self.main_path}\screenshot.ps1"
                        screenshot = Screenshot(soc, log_path, self.hostname, self.localIP)

                        self.logIt_thread(log_path, msg='Calling screenshot.run()...')
                        screenshot.run()

                    # Get System Information & Users
                    elif str(command.lower())[:2] == "si":
                        dt = self.get_date()
                        sipath = rf"C:\HandsOff"
                        sifile = rf"systeminfo {self.hostname} {dt}.txt"
                        si_full_path = os.path.join(sipath, sifile)

                        if not os.path.exists(si_full_path):
                            with open(si_full_path, 'w') as sysinfo:
                                self.logIt_thread(self.log_path, msg='Running system information command...')
                                sys_info = subprocess.run(['systeminfo'], stdout=subprocess.PIPE, text=True)
                                sys_info_str = sys_info.stdout
                                self.logIt_thread(self.log_path, msg=f'Adding header to {si_full_path}...')
                                sysinfo.write(f"====================================================\n")
                                sysinfo.write(
                                    f"IP: {self.localIP} | NAME: {self.hostname} | LOGGED USED: {os.getlogin()}\n")
                                sysinfo.write(f"====================================================\n")
                                self.logIt_thread(self.log_path, msg=f'Adding system information to {si_full_path}...')
                                sysinfo.write(f"{sys_info_str}\n\n")
                        else:
                            with open(si_full_path, 'w') as sysinfo:
                                self.logIt_thread(self.log_path, msg='Running system information command...')
                                sys_info = subprocess.run(['systeminfo'], stdout=subprocess.PIPE, text=True)
                                sys_info_str = sys_info.stdout
                                self.logIt_thread(self.log_path, msg=f'Adding header to {si_full_path}...')
                                sysinfo.write(f"====================================================\n")
                                sysinfo.write(
                                    f"IP: {self.localIP} | NAME: {self.hostname} | LOGGED USED: {os.getlogin()}\n")
                                sysinfo.write(f"====================================================\n")
                                self.logIt_thread(self.log_path, msg=f'Adding system information to {si_full_path}...')
                                sysinfo.write(f"{sys_info_str}\n\n")

                        try:
                            self.logIt_thread(self.log_path, msg='Sending file name...')
                            soc.send(f"{sifile}".encode())
                            self.logIt_thread(self.log_path, msg=f'Send Completed.')

                        except (WindowsError, socket.error) as e:
                            self.logIt_thread(self.log_path, msg=f'Connection Error: {e}')
                            return False

                        try:
                            self.logIt_thread(self.log_path, msg='Defining file size...')
                            length = os.path.getsize(si_full_path)
                            self.logIt_thread(self.log_path, msg=f'File Size: {length}')

                            self.logIt_thread(self.log_path, msg='Sending file size...')
                            soc.send(self.convert_to_bytes(length))
                            self.logIt_thread(self.log_path, msg=f'Send Completed.')

                        except (WindowsError, socket.error) as e:
                            self.logIt_thread(self.log_path, msg=f'Connection Error: {e}')
                            return False

                        try:
                            self.logIt_thread(self.log_path, msg=f'Opening {si_full_path}...')
                            with open(si_full_path, 'rb') as sy_file:
                                self.logIt_thread(self.log_path, msg='Sending file content...')
                                sys_data = sy_file.read(1024)
                                while sys_data:
                                    soc.send(sys_data)
                                    if not sys_data:
                                        break

                                    sys_data = sy_file.read(1024)

                            self.logIt_thread(self.log_path, msg=f'Send Completed.')

                        except (WindowsError, socket.error, FileExistsError, FileNotFoundError) as e:
                            self.logIt_thread(self.log_path, msg=f'Error: {e}')
                            return False

                        try:
                            self.logIt_thread(self.log_path, msg='Waiting for message from server...')
                            msg = soc.recv(1024).decode()
                            self.logIt_thread(self.log_path, msg=f'From Server: {msg}')

                            self.logIt_thread(self.log_path, msg=f'Sending confirmation message...')
                            soc.send(f"{self.hostname} | {self.localIP}: System Information Sent.\n".encode())
                            self.logIt_thread(self.log_path, msg=f'Send Completed.')

                        except (WindowsError, socket.error) as e:
                            self.logIt_thread(self.log_path, msg=f'Connection Error: {e}')
                            return False

                        os.remove(fr'{si_full_path}')
                        sys.stdout.flush()

                    # Get Last Restart Time
                    elif str(command.lower())[:2] == "lr":
                        self.logIt_thread(log_path, msg='Fetching last restart time...')
                        last_reboot = psutil.boot_time()
                        try:
                            self.logIt_thread(log_path, msg='Sending last restart time...')
                            soc.send(f"{self.hostname} | {self.localIP}: "
                                     f"{datetime.fromtimestamp(last_reboot).replace(microsecond=0)}".encode())

                            self.logIt_thread(log_path, msg=f'Send completed.')

                        except ConnectionResetError as e:
                            self.logIt_thread(log_path, msg=f'Connection Error: {e}')
                            break

                    # Run Anydesk
                    elif str(command.lower())[:7] == "anydesk":
                        self.logIt_thread(log_path, msg='Calling anydesk()...')
                        self.anydesk()
                        continue

                    # Task List
                    elif str(command.lower())[:5] == "tasks":
                        self.logIt_thread(log_path, msg='Calling tasks()...')
                        task = Tasks(soc, self.log_path, self.hostname, self.localIP)
                        task.run()

                    # Restart Machine
                    elif str(command.lower())[:7] == "restart":
                        self.logIt_thread(log_path, msg='Restarting local station...')
                        os.system('shutdown /r /t 1')

                    # Run Updater
                    elif str(command.lower())[:6] == "update":
                        try:
                            update_url = soc.recv(1024).decode()
                            self.logIt_thread(log_path, msg='Sending confirmation...')
                            soc.send('Running updater...'.encode())
                            self.logIt_thread(log_path, msg='Send complete.')

                        except (WindowsError, socket.error) as e:
                            self.logIt_thread(log_path, msg=f'ERROR: {e}.')
                            break

                        self.updater(update_url)
                        self.logIt_thread(log_path, msg='Running updater...')
                        subprocess.call([fr'{self.main_path}\updater.exe'])

                    # Maintenance
                    elif str(command.lower()) == "maintenance":
                        self.logIt_thread(log_path, msg=f'Calling self.maintenance()...')
                        self.maintenance()
                        self.logIt_thread(log_path, msg=f'Calling self.connection()...')
                        self.connection()
                        self.logIt_thread(log_path, msg=f'Calling self.backdoor({soc})...')
                        self.backdoor(soc)

                    # Close Connection
                    elif str(command.lower())[:4] == "exit":
                        self.logIt_thread(log_path, msg='Server closed the connection.')
                        soc.settimeout(1)
                        # sys.exit(0)     # CI CD
                        break  # CICD

                except (Exception, socket.error, socket.timeout) as err:
                    self.logIt_thread(log_path, msg=f'Connection Error: {e}')
                    break

        self.logIt_thread(log_path, msg='Calling intro()...')
        intro()
        self.logIt_thread(log_path, msg='Calling main_menu()...')
        main_menu()

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


if __name__ == "__main__":
    client_version = "1.0.1"
    default_socket_timeout = None
    menu_socket_timeout = None
    intro_socket_timeout = 10
    connection_socket_timeout = 10
    anydesk_socket_timeout = 30
    chkdsk_socket_timeout = 30
    task_list = []
    powershell = r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe"

    app_path = r'c:\HandsOff'
    if not os.path.exists(app_path):
        os.makedirs(app_path)

    log_path = fr'{app_path}\client_log.txt'
    servers = [('192.168.1.10', 55400)]

    # Configure system tray icon
    icon_image = PIL.Image.open(rf"{app_path}\client.png")
    icon = pystray.Icon("HandsOff", icon_image, menu=pystray.Menu(
        pystray.MenuItem("About", on_clicked)
    ))

    # Show system tray icon
    iconThread = Thread(target=icon.run, name="Icon Thread")
    iconThread.daemon = True
    iconThread.start()

    # Start Client
    while True:
        for server in servers:
            client = Client(server, app_path, log_path)

            try:
                client.logIt_thread(log_path, msg='Creating Socket...')
                soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                client.logIt_thread(log_path, msg='Defining socket to Reuse address...')
                soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                client.logIt_thread(log_path, msg=f'connecting to {server}...')
                soc.connect(server)
                client.logIt_thread(log_path, msg=f'Calling backdoor({soc})...')
                client.backdoor(soc)

            except (WindowsError, socket.error) as e:
                client.logIt_thread(log_path, msg=f'Connection Error: {e}')
                soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                client.logIt_thread(log_path, msg=f'Closing socket...')
                soc.close()
                time.sleep(1)
