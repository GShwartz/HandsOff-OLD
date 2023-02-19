from datetime import datetime
from threading import Thread
import logging
import socket
import time
import os

from Modules.logger import init_logger

# TODO:
#   1. Remove client version recv in vital_signs


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

        self.logger = init_logger(self.log_path, __name__)

    # Server listener
    def listener(self) -> None:
        self.server = socket.socket()
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.logger.debug(f'Binding {self.serverIP}, {self.port}...')
        self.server.bind((self.serverIP, self.port))
        self.server.listen()

        self.logger.info(f'Running run...')
        self.logger.debug(f'Starting connection thread...')
        self.connectThread = Thread(target=self.connect,
                                    daemon=True,
                                    name=f"Connect Thread")
        self.connectThread.start()

    # Listen for connections and sort new connections to designated lists/dicts
    def connect(self) -> None:
        self.logger.info(f'Running connect...')
        while True:
            self.logger.debug(f'Accepting connection...')
            self.conn, (self.ip, self.port) = self.server.accept()
            self.logger.debug(f'Connection from {self.ip} accepted.')

            try:
                dt = self.get_date()
                self.logger.debug(f'Waiting for MAC Address...')
                self.client_mac = self.get_mac_address()
                self.logger.debug(f'MAC: {self.client_mac}.')
                self.logger.debug(f'Waiting for station name...')
                self.hostname = self.get_hostname()
                self.logger.debug(f'Station name: {self.hostname}.')
                self.logger.debug(f'Waiting for logged user...')
                self.loggedUser = self.get_user()
                self.logger.debug(f'Logged user: {self.loggedUser}.')
                self.logger.debug(f'Waiting for client version...')
                self.client_version = self.get_client_version()
                self.logger.debug(f'Client version: {self.client_version}.')
                self.get_boot_time()
                self.logger.debug(f'Client Boot time: {self.boot_time}.')

            except (WindowsError, socket.error, UnicodeDecodeError) as e:
                self.logger.debug(f'Connection Error: {e}.')
                return  # Restart The Loop

            # Apply Data to dataclass Endpoints
            self.logger.debug(f'Defining fresh endpoint data...')
            self.fresh_endpoint = Endpoints(self.conn, self.client_mac, self.ip,
                                            self.ident, self.user, self.client_version, self.boot_time)
            self.logger.debug(f'Fresh Endpoint: {self.fresh_endpoint}')

            if self.fresh_endpoint not in self.endpoints:
                self.logger.debug(f'{self.fresh_endpoint} not in endpoints list. adding...')
                self.endpoints.append(self.fresh_endpoint)

            self.logger.debug(f'Updating connection history dict...')
            self.connHistory.update({self.fresh_endpoint: dt})

            self.logger.debug(f'Running Server Information thread...')
            Thread(target=self.app.server_information, name="Server Information").start()

            self.logger.debug(f'Calling welcome_message...')
            self.welcome_message()
            self.logger.info(f'connect completed.')

    # Send welcome message to connected clients
    def welcome_message(self) -> bool:
        self.logger.info(f'Running welcome_message...')
        try:
            self.welcome = "Connection Established!"
            self.logger.debug(f'Sending welcome message...')
            self.conn.send(f"@Server: {self.welcome}".encode())
            self.logger.debug(f'{self.welcome} sent to {self.ident}.')
            return True

        except (WindowsError, socket.error) as e:
            self.logger.error(f'Connection Error: {e}.')
            if self.fresh_endpoint in self.endpoints:
                self.logger.debug(f'Calling remove_lost_connection({self.fresh_endpoint})...')
                self.remove_lost_connection(self.fresh_endpoint)
                return False

    # Get remote MAC address
    def get_mac_address(self) -> str:
        self.logger.info(f'Running get_mac_address...')
        self.mac = self.conn.recv(1024).decode()
        self.conn.send('OK'.encode())
        return self.mac

    # Get remote host name
    def get_hostname(self) -> str:
        self.logger.info(f'Running get_hostname...')
        self.ident = self.conn.recv(1024).decode()
        self.conn.send('OK'.encode())
        return self.ident

    # Get remote user
    def get_user(self) -> str:
        self.logger.info(f'Running get_user...')
        self.user = self.conn.recv(1024).decode()
        self.conn.send('OK'.encode())
        return self.user

    # Get client version
    def get_client_version(self) -> str:
        self.logger.info(f'Running get_client_version...')
        self.client_version = self.conn.recv(1024).decode()
        self.conn.send('OK'.encode())
        return self.client_version

    # Get boot time
    def get_boot_time(self) -> str:
        self.logger.info(f'Running get_boot_time...')
        self.boot_time = self.conn.recv(1024).decode()
        self.conn.send('OK'.encode())
        return self.boot_time

    # Get human readable datetime
    def get_date(self) -> str:
        d = datetime.now().replace(microsecond=0)
        dt = str(d.strftime("%d/%b/%y %H:%M:%S"))
        return dt

    # Check vital signs
    def check_vital_signs(self, endpoint):
        self.callback = 'yes'
        self.logger.debug(f'Checking {endpoint.ip}...')

        try:
            endpoint.conn.send('alive'.encode())
            ans = endpoint.conn.recv(1024).decode()

        except (WindowsError, socket.error, UnicodeDecodeError) as e:
            self.logger.debug(f'removing {endpoint}...')
            self.remove_lost_connection(endpoint)
            return

        if str(ans) == str(self.callback):
            try:
                self.app.update_statusbar_messages_thread(
                    msg=f'Station IP: {endpoint.ip} | Station Name: {endpoint.ident} - ALIVE!')

            except (IndexError, RuntimeError):
                return

        else:
            try:
                self.logger.debug(f'removing {endpoint}...')
                self.remove_lost_connection(endpoint)

            except (IndexError, RuntimeError):
                return

    # Run vital signs
    def vital_signs(self) -> bool:
        self.logger.info(f'Running vital_signs...')
        if not self.endpoints:
            self.logger.debug(f'Updating statusbar message: No connected stations.')
            self.app.update_statusbar_messages_thread(msg='No connected stations.')
            return False

        self.callback = 'yes'
        self.logger.debug(f'Updating statusbar message: running vitals check....')
        self.app.update_statusbar_messages_thread(msg=f'running vitals check...')
        threads = []
        for endpoint in self.endpoints:
            thread = Thread(target=self.check_vital_signs, args=(endpoint,))
            thread.start()
            threads.append(thread)

        for thread in threads:
            thread.join()

        self.logger.debug(f'Updating statusbar message: Vitals check completed.')
        self.logger.info(f'=== End of vital_signs() ===')
        return True

    # Remove Lost connections
    def remove_lost_connection(self, endpoint) -> bool:
        self.logger.info(f'Running remove_lost_connection({endpoint})...')
        try:
            self.logger.debug(f'Removing {endpoint.ip} | {endpoint.ident}...')
            self.endpoints.remove(endpoint)

            # Update statusbar message
            self.logger.debug(f'Updating statusbar message: '
                              f'{endpoint.ip} | {endpoint.ident} | {endpoint.user} removed from connected list.')
            self.app.update_statusbar_messages_thread(
                msg=f'{endpoint.ip} | {endpoint.ident} | {endpoint.user} removed from connected list.')
            self.logger.info(f'=== End of remove_lost_connection({endpoint}) ===')
            return True

        except (ValueError, RuntimeError) as e:
            self.logger.error(f'Error: {e}.')
