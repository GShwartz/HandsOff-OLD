from threading import Thread
from datetime import datetime
import socket
import time
import os

# Added boot time


class Endpoints:
    def __init__(self, conn, client_mac, ip, ident, user, client_version, boot_time):
        self.boot_time = boot_time
        self.conn = conn
        self.client_mac = client_mac
        self.ip = ip
        self.ident = ident
        self.user = user
        self.client_version = client_version

    def __repr__(self):
        return f"Endpoint({self.conn}, {self.client_mac}, " \
               f"{self.ip}, {self.ident}, {self.user}, " \
               f"{self.client_version}, {self.boot_time})"


class Server:
    def __init__(self, log_path, app, ip, port, path):
        self.path = path
        self.port = port
        self.serverIP = ip
        self.hostname = socket.gethostname()
        self.log_path = log_path
        self.app = app
        self.connHistory = {}
        self.endpoints = []

    # Server listener
    def listener(self) -> None:
        logIt_thread(self.log_path, msg=f'Running listener()...')
        self.server = socket.socket()
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        logIt_thread(self.log_path, msg=f'Binding {self.serverIP}, {self.port}...')
        self.server.bind((self.serverIP, self.port))
        self.server.listen()

    # Send welcome message to connected clients
    def welcome_message(self) -> bool:
        logIt_thread(self.log_path, msg=f'Running welcome_message()...')
        try:
            self.welcome = "Connection Established!"
            logIt_thread(self.log_path, msg=f'Sending welcome message...')
            self.conn.send(f"@Server: {self.welcome}".encode())
            logIt_thread(self.log_path, msg=f'{self.welcome} sent to {self.ident}.')
            return True

        except (WindowsError, socket.error) as e:
            logIt_thread(self.log_path, msg=f'Connection Error: {e}')
            if self.fresh_endpoint in self.endpoints:
                self.remove_lost_connection(self.fresh_endpoint)
                return False

    def run(self) -> None:
        logIt_thread(self.log_path, msg=f'Running run()...')
        logIt_thread(self.log_path, msg=f'Calling connect()...')
        self.connectThread = Thread(target=self.connect,
                                    daemon=True,
                                    name=f"Connect Thread")
        self.connectThread.start()

    def get_mac_address(self) -> str:
        logIt_thread(self.log_path, msg=f'Waiting for MAC address from {self.ip}...')
        self.mac = self.conn.recv(1024).decode()
        logIt_thread(self.log_path, msg=f'MAC Address: {self.mac}')
        logIt_thread(self.log_path, msg=f'Sending confirmation to {self.ip}...')
        self.conn.send('OK'.encode())
        logIt_thread(self.log_path, msg=f'Send completed.')
        return self.mac

    def get_hostname(self) -> str:
        logIt_thread(self.log_path, msg=f'Waiting for remote station name...')
        self.ident = self.conn.recv(1024).decode()
        logIt_thread(self.log_path, msg=f'Remote station name: {self.ident}')
        logIt_thread(self.log_path, msg=f'Sending Confirmation to {self.ip}...')
        self.conn.send('OK'.encode())
        logIt_thread(self.log_path, msg=f'Send completed.')
        return self.ident

    def get_user(self) -> str:
        logIt_thread(self.log_path, msg=f'Waiting for remote station current logged user...')
        self.user = self.conn.recv(1024).decode()
        logIt_thread(self.log_path, msg=f'Remote station user: {self.user}')
        logIt_thread(self.log_path, msg=f'Sending Confirmation to {self.ip}...')
        self.conn.send('OK'.encode())
        logIt_thread(self.log_path, msg=f'Send completed.')
        return self.user

    def get_client_version(self) -> str:
        logIt_thread(self.log_path, msg=f'Waiting for client version...')
        self.client_version = self.conn.recv(1024).decode()
        logIt_thread(self.log_path, msg=f'Client version: {self.client_version}')
        logIt_thread(self.log_path, msg=f'Sending confirmation to {self.ip}...')
        self.conn.send('OK'.encode())
        logIt_thread(self.log_path, msg=f'Send completed.')
        return self.client_version

    def get_boot_time(self) -> str:
        logIt_thread(self.log_path, msg=f'Waiting for client version...')
        self.boot_time = self.conn.recv(1024).decode()
        logIt_thread(self.log_path, debug=True, msg=f'Client Boot Time: {self.boot_time}')
        self.conn.send('OK'.encode())
        return self.boot_time

    # Listen for connections and sort new connections to designated lists/dicts
    def connect(self) -> None:
        logIt_thread(self.log_path, msg=f'Running connect()...')
        while True:
            logIt_thread(self.log_path, msg=f'Accepting connections...')
            self.conn, (self.ip, self.port) = self.server.accept()
            logIt_thread(self.log_path, msg=f'Connection from {self.ip} accepted.')

            try:
                dt = get_date()
                logIt_thread(self.log_path, msg=f'Waiting for MAC Address...')
                self.client_mac = self.get_mac_address()
                logIt_thread(self.log_path, msg=f'MAC: {self.client_mac}.')
                logIt_thread(self.log_path, msg=f'Waiting for station name...')
                self.hostname = self.get_hostname()
                logIt_thread(self.log_path, msg=f'Station name: {self.hostname}.')
                logIt_thread(self.log_path, msg=f'Waiting for logged user...')
                self.loggedUser = self.get_user()
                logIt_thread(self.log_path, msg=f'Logged user: {self.loggedUser}.')
                logIt_thread(self.log_path, msg=f'Waiting for client version...')
                self.client_version = self.get_client_version()
                logIt_thread(self.log_path, msg=f'Client version: {self.client_version}.')
                self.get_boot_time()
                logIt_thread(self.log_path, msg=f'Client Boot time: {self.boot_time}.')

            except (WindowsError, socket.error, UnicodeDecodeError) as e:
                logIt_thread(self.log_path, msg=f'Connection Error: {e}')
                return  # Restart The Loop

            # Apply Data to dataclass Endpoints
            self.fresh_endpoint = Endpoints(self.conn, self.client_mac, self.ip,
                                            self.ident, self.user, self.client_version, self.boot_time)

            if self.fresh_endpoint not in self.endpoints:
                self.endpoints.append(self.fresh_endpoint)

            self.connHistory.update({self.fresh_endpoint: dt})
            Thread(target=self.app.server_information, name="Server Information").start()
            # self.app.display_server_information_thread()
            self.welcome_message()

    # Check if connected stations are still connected
    def vital_signs(self) -> bool:
        logIt_thread(self.log_path, msg=f'Running vital_signs()...')
        if not self.endpoints:
            self.app.update_statusbar_messages_thread(msg='No connected stations.')
            return False

        callback = 'yes'
        i = 0
        self.app.update_statusbar_messages_thread(msg=f'running vitals check...')
        logIt_thread(self.log_path, msg=f'Iterating Through Temp Connected Sockets List...')
        for endpoint in self.endpoints:
            try:
                logIt_thread(self.log_path, msg=f'Sending "alive" to {endpoint.conn}...')
                endpoint.conn.send('alive'.encode())
                logIt_thread(self.log_path, msg=f'Send completed.')
                logIt_thread(self.log_path, msg=f'Waiting for response from {endpoint.conn}...')
                ans = endpoint.conn.recv(1024).decode()
                logIt_thread(self.log_path, msg=f'Response from {endpoint.conn}: {ans}.')
                logIt_thread(self.log_path, msg=f'Waiting for client version from {endpoint.conn}...')
                ver = endpoint.conn.recv(1024).decode()
                logIt_thread(self.log_path, msg=f'Response from {endpoint.conn}: {ver}.')

            except (WindowsError, socket.error, UnicodeDecodeError):
                self.remove_lost_connection(endpoint)
                continue

            if str(ans) == str(callback):
                try:
                    logIt_thread(self.log_path, msg=f'Iterating self.clients dictionary...')
                    self.app.update_statusbar_messages_thread(
                        msg=f'Station IP: {endpoint.ip} | Station Name: {endpoint.ident} | Client Version: {endpoint.client_version} - ALIVE!')
                    i += 1
                    time.sleep(0.5)

                except (IndexError, RuntimeError):
                    continue

            else:
                logIt_thread(self.log_path, msg=f'Iterating self.clients dictionary...')
                try:
                    self.remove_lost_connection(endpoint)

                except (IndexError, RuntimeError):
                    continue

        self.app.update_statusbar_messages_thread(msg=f'Vitals check completed.')
        logIt_thread(self.log_path, msg=f'=== End of vital_signs() ===')
        return True

    # Remove Lost connections
    def remove_lost_connection(self, endpoint) -> bool:
        try:
            logIt_thread(self.log_path, msg=f'Removing '
                                            f'{endpoint.ip} | {endpoint.ident}...')
            self.endpoints.remove(endpoint)
            self.app.refresh_command()

            # Update statusbar message
            self.app.update_statusbar_messages_thread(
                msg=f'{endpoint.ip} | {endpoint.ident} | {endpoint.user} removed from connected list.')
            logIt_thread(self.log_path, msg=f'{endpoint.ip} | {endpoint.ident} removed.')
            return True

        except (ValueError, RuntimeError) as e:
            logIt_thread(self.log_path, msg=f'Runtime Error: {e}.')


def logIt_thread(log_path=None, debug=False, msg='') -> None:
    logit_thread = Thread(target=logIt,
                          args=(log_path, debug, msg),
                          daemon=True,
                          name="Log Thread")
    logit_thread.start()


def bytes_to_number(b: int) -> int:
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
