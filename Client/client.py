from subprocess import Popen, PIPE
from datetime import datetime
from threading import Thread
import PySimpleGUI as sg
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

# Local Modules
from freestyle import Freestyle
from tasks import Tasks


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

        logIt_thread(log_path, msg='Calling get_date()...')
        self.dt = get_date()

        logIt_thread(log_path, msg='Defining screenshot file name...')
        self.filename = rf"{app_path}\screenshot {self.client.hostname} {self.client.localIP} {self.dt}.jpg"
        logIt_thread(log_path, msg=f'Screenshot file name: {self.filename}')

    def make_script(self):
        logIt_thread(log_path, msg='Running make_script()...')
        logIt_thread(log_path, msg=f'Writing script to {self.ps_path}...')
        with open(self.ps_path, 'w') as file:
            file.write("Add-Type -AssemblyName System.Windows.Forms\n")
            file.write("Add-Type -AssemblyName System.Drawing\n\n")
            file.write("$Screen = [System.Windows.Forms.SystemInformation]::VirtualScreen\n\n")
            file.write("$Width  = $Screen.Width\n")
            file.write("$Height = $Screen.Height\n")
            file.write("$Left = $Screen.Left\n")
            file.write("$Top = $Screen.Top\n\n")
            file.write("$bitmap = New-Object System.Drawing.Bitmap $Width, $Height\n")
            file.write("$graphic = [System.Drawing.Graphics]::FromImage($bitmap)\n")
            file.write("$graphic.CopyFromScreen($Left, $Top, 0, 0, $bitmap.Size)\n\n")
            file.write(rf"$bitmap.Save('{self.filename}')")

        time.sleep(0.2)
        logIt_thread(log_path, msg=f'Writing script to {self.ps_path} completed.')

    def run_script(self):
        logIt_thread(log_path, msg='Running run_script()...')
        logIt_thread(log_path, msg=f'Running PS script...')
        ps = subprocess.Popen(["powershell.exe", rf"{self.ps_path}"], stdout=sys.stdout)
        ps.communicate()
        logIt_thread(log_path, msg=f'PS script Completed.')

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
            length = os.path.getsize(self.filename)
            logIt_thread(log_path, msg=f'Sending file size to server...')
            self.client.soc.send(convert_to_bytes(length))
            logIt_thread(log_path, msg=f'Send Completed.')

            # Send file content
            logIt_thread(log_path, msg=f'Opening {self.filename} with read bytes permissions...')
            with open(self.filename, 'rb') as img_file:
                img_data = img_file.read(1024)
                logIt_thread(log_path, msg=f'Sending file content...')
                while img_data:
                    self.client.soc.send(img_data)
                    if not img_data:
                        break

                    img_data = img_file.read(1024)

            logIt_thread(log_path, msg=f'Send Completed.')

            return

        except (WindowsError, socket.error, ConnectionError) as e:
            logIt_thread(log_path, msg=f'Connection Error: {e}')
            return False

    def confirm(self):
        try:
            logIt_thread(log_path, msg=f'Sending confirmation...')
            time.sleep(0.2)
            self.client.soc.send(f"{self.client.hostname} | {self.client.localIP}: Screenshot Completed.\n".encode())
            logIt_thread(log_path, msg=f'Send Completed.')

        except (WindowsError, socket.error):
            logIt_thread(log_path, msg=f'Connection Error')
            return False

    def run(self):
        logIt_thread(log_path, msg='Running screenshot()...')
        logIt_thread(log_path, msg='Calling make_script()...')
        self.make_script()
        logIt_thread(log_path, msg='Calling run_script()...')
        self.run_script()
        logIt_thread(log_path, msg='Calling send_file()...')
        self.send_file()
        logIt_thread(log_path, msg='Calling confirm()...')
        self.confirm()

        logIt_thread(log_path, msg=f'Removing \n{self.filename} | \n{self.ps_path}...')
        os.remove(self.filename)
        os.remove(self.ps_path)
        logIt_thread(log_path, msg=f'=== End of screenshot() ===')


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
                    break

                # Freestyle
                if str(command.lower())[:9] == "freestyle":
                    logIt_thread(log_path, msg='Initiating Freestyle class...')
                    free = Freestyle(self.client.soc, log_path, self.client.hostname, self.client.localIP)

                    logIt_thread(log_path, msg='Calling Freestyle class...')
                    free.free_style()

                # Vital Signs
                if str(command.lower())[:5] == "alive":
                    logIt_thread(log_path, msg='Calling Vital Signs...')
                    try:
                        logIt_thread(log_path, msg='Answer yes to server')
                        self.client.soc.send('yes'.encode())
                        logIt_thread(log_path, msg=f'Send completed.')

                        logIt_thread(log_path, msg='Sending client version to server...')
                        self.client.soc.send(client_version.encode())
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
                                             f"{datetime.fromtimestamp(last_reboot).replace(microsecond=0)}".encode())

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
                    task = Tasks(self.client.soc, log_path, self.client.hostname, self.client.localIP)
                    task.run()

                # Restart Machine
                elif str(command.lower())[:7] == "restart":
                    logIt_thread(log_path, msg='Restarting local station...')
                    os.system('shutdown /r /t 1')

                # Run Updater
                elif str(command.lower())[:6] == "update":
                    try:
                        logIt_thread(log_path, msg='Sending confirmation...')
                        self.client.soc.send('Running updater...'.encode())
                        logIt_thread(log_path, msg='Send complete.')

                        logIt_thread(log_path, msg='Running updater...')
                        subprocess.run(f'{updater_file}')

                    except (WindowsError, socket.error) as e:
                        logIt_thread(log_path, msg=f'ERROR: {e}.')
                        break

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
        while True:
            time.sleep(1)
            try:
                logIt_thread(log_path, msg=f'Connecting to Server: {self.server_host} | Port {self.server_port}...')
                self.soc.connect((self.server_host, self.server_port))

            except (TimeoutError, WindowsError, ConnectionAbortedError, ConnectionResetError, socket.timeout) as e:
                logIt_thread(log_path, msg=f'Connection Error: {e}')
                continue

    def welcome(self):
        endpoint_welcome = Welcome(self)
        endpoint_welcome.send_mac_address()
        endpoint_welcome.send_host_name()
        endpoint_welcome.send_current_user()
        endpoint_welcome.send_client_version()
        endpoint_welcome.confirm()

        logIt_thread(log_path, msg='Calling main_menu()...')
        endpoint_welcome.main_menu()
        return True


def get_date() -> str:
    d = datetime.now().replace(microsecond=0)
    dt = str(d.strftime("%b %d %Y %I.%M.%S %p"))

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
    client_version = "1.0.1"
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
