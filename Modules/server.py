import socket
from threading import Thread
import time


class Server:
    def __init__(self, local_tools, log_path, app):
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
        self.local_tools = local_tools
        self.log_path = log_path
        self.app = app

    def run(self) -> None:
        self.local_tools.logIt_thread(self.log_path, msg=f'Running run()...')
        self.local_tools.logIt_thread(self.log_path, msg=f'Calling connect()...')
        self.connectThread = Thread(target=self.connect,
                                    daemon=True,
                                    name=f"Connect Thread")
        self.connectThread.start()

    # Listen for connections and sort new connections to designated lists/dicts
    def connect(self) -> None:
        def get_mac_address() -> str:
            self.local_tools.logIt_thread(self.log_path, msg=f'Waiting for MAC address from {self.ip}...')
            self.mac = self.conn.recv(1024).decode()
            self.local_tools.logIt_thread(self.log_path, msg=f'MAC Address: {self.mac}')
            self.local_tools.logIt_thread(self.log_path, msg=f'Sending confirmation to {self.ip}...')
            self.conn.send('OK'.encode())
            self.local_tools.logIt_thread(self.log_path, msg=f'Send completed.')
            return self.mac

        def get_hostname() -> str:
            self.local_tools.logIt_thread(self.log_path, msg=f'Waiting for remote station name...')
            self.ident = self.conn.recv(1024).decode()
            self.local_tools.logIt_thread(self.log_path, msg=f'Remote station name: {self.ident}')
            self.local_tools.logIt_thread(self.log_path, msg=f'Sending Confirmation to {self.ip}...')
            self.conn.send('OK'.encode())
            self.local_tools.logIt_thread(self.log_path, msg=f'Send completed.')
            return self.ident

        def get_user() -> str:
            self.local_tools.logIt_thread(self.log_path, msg=f'Waiting for remote station current logged user...')
            self.user = self.conn.recv(1024).decode()
            self.local_tools.logIt_thread(self.log_path, msg=f'Remote station user: {self.user}')
            self.local_tools.logIt_thread(self.log_path, msg=f'Sending Confirmation to {self.ip}...')
            self.conn.send('OK'.encode())
            self.local_tools.logIt_thread(self.log_path, msg=f'Send completed.')
            return self.user

        def get_client_version() -> str:
            self.local_tools.logIt_thread(self.log_path, msg=f'Waiting for client version...')
            self.client_version = self.conn.recv(1024).decode()
            self.local_tools.logIt_thread(self.log_path, msg=f'Client version: {self.client_version}')
            self.local_tools.logIt_thread(self.log_path, msg=f'Sending confirmation to {self.ip}...')
            self.conn.send('OK'.encode())
            self.local_tools.logIt_thread(self.log_path, msg=f'Send completed.')
            return self.client_version

        self.local_tools.logIt_thread(self.log_path, msg=f'Running connect()...')
        while True:
            self.local_tools.logIt_thread(self.log_path, msg=f'Accepting connections...')
            self.conn, (self.ip, self.port) = self.server.accept()
            self.local_tools.logIt_thread(self.log_path, msg=f'Connection from {self.ip} accepted.')

            try:
                self.local_tools.logIt_thread(self.log_path, msg=f'Waiting for MAC Address...')
                self.client_mac = get_mac_address()
                self.local_tools.logIt_thread(self.log_path, msg=f'MAC: {self.client_mac}.')
                self.local_tools.logIt_thread(self.log_path, msg=f'Waiting for station name...')
                self.hostname = get_hostname()
                self.local_tools.logIt_thread(self.log_path, msg=f'Station name: {self.hostname}.')
                self.local_tools.logIt_thread(self.log_path, msg=f'Waiting for logged user...')
                self.loggedUser = get_user()
                self.local_tools.logIt_thread(self.log_path, msg=f'Logged user: {self.loggedUser}.')
                self.local_tools.logIt_thread(self.log_path, msg=f'Waiting for client version...')
                self.client_version = get_client_version()
                self.local_tools.logIt_thread(self.log_path, msg=f'Client version: {self.client_version}.')

            except (WindowsError, socket.error) as e:
                self.local_tools.logIt_thread(self.log_path, msg=f'Connection Error: {e}')
                return  # Restart The Loop

            # Update Thread Dict and Connection Lists
            if self.conn not in self.targets and self.ip not in self.ips:
                self.local_tools.logIt_thread(self.log_path, msg=f'New Connection!')

                # Add Socket Connection To Targets list
                self.local_tools.logIt_thread(self.log_path, msg=f'Adding {self.conn} to targets list...')
                self.targets.append(self.conn)
                self.local_tools.logIt_thread(self.log_path, msg=f'targets list updated.')

                # Add IP Address Connection To IPs list
                self.local_tools.logIt_thread(self.log_path, msg=f'Adding {self.ip} to ips list...')
                self.ips.append(self.ip)
                self.local_tools.logIt_thread(self.log_path, msg=f'ips list updated.')

                # Set Temp Dict To Update Live Connections List
                self.local_tools.logIt_thread(self.log_path,
                                              msg=f'Adding {self.conn} | {self.ip} to temp live connections dict...')
                self.temp_connection = {self.conn: self.ip}
                self.local_tools.logIt_thread(self.log_path, msg=f'Temp connections dict updated.')

                # Add Temp Dict To Connections List
                self.local_tools.logIt_thread(self.log_path, msg=f'Updating connections list...')
                self.connections.update(self.temp_connection)
                self.local_tools.logIt_thread(self.log_path, msg=f'Connections list updated.')

                # Set Temp Idents Dict For Idents
                self.local_tools.logIt_thread(self.log_path, msg=f'Creating dict to hold ident details...')
                self.temp_ident = {
                    self.conn: {self.client_mac: {self.ip: {self.ident: {self.user: self.client_version}}}}}
                self.local_tools.logIt_thread(self.log_path, msg=f'Dict created: {self.temp_ident}')

                # Add Temp Idents Dict To Idents Dict
                self.local_tools.logIt_thread(self.log_path, msg=f'Updating live clients list...')
                self.clients.update(self.temp_ident)
                self.local_tools.logIt_thread(self.log_path, msg=f'Live clients list updated.')

            # Create a Dict of Connection, IP, Computer Name, Date & Time
            self.local_tools.logIt_thread(self.log_path, msg=f'Fetching current date & time...')
            dt = self.local_tools.get_date()
            self.local_tools.logIt_thread(self.log_path, msg=f'Creating a connection dict...')
            self.temp_connection_record = {self.conn: {self.client_mac: {self.ip: {self.ident: {self.user: dt}}}}}
            self.local_tools.logIt_thread(self.log_path, msg=f'Connection dict created: {self.temp_connection_record}')

            # Add Connection to Connection History
            self.local_tools.logIt_thread(self.log_path, msg=f'Adding connection to connection history...')
            self.connHistory.append(self.temp_connection_record)
            self.local_tools.logIt_thread(self.log_path, msg=f'Connection added to connection history.')

            self.local_tools.logIt_thread(self.log_path, msg=f'Calling self.welcome_message()...')

            self.app.display_server_information_thread()
            self.welcome_message()

    # Server listener
    def listener(self) -> None:
        self.local_tools.logIt_thread(self.log_path, msg=f'Running listener()...')
        self.server = socket.socket()
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.local_tools.logIt_thread(self.log_path, msg=f'Binding {self.serverIP}, {self.port}...')
        self.server.bind((self.serverIP, self.port))
        self.server.listen()

    # Send welcome message to connected clients
    def welcome_message(self) -> bool:
        self.local_tools.logIt_thread(self.log_path, msg=f'Running welcome_message()...')
        try:
            self.welcome = "Connection Established!"
            self.local_tools.logIt_thread(self.log_path, msg=f'Sending welcome message...')
            self.conn.send(f"@Server: {self.welcome}".encode())
            self.local_tools.logIt_thread(self.log_path, msg=f'{self.welcome} sent to {self.ident}.')
            return True

        except (WindowsError, socket.error) as e:
            self.local_tools.logIt_thread(self.log_path, msg=f'Connection Error: {e}')
            if self.conn in self.targets and self.ip in self.ips:
                self.local_tools.logIt_thread(self.log_path, msg=f'Removing {self.conn} from self.targets...')
                self.targets.remove(self.conn)
                self.local_tools.logIt_thread(self.log_path, msg=f'Removing {self.ip} from self.ips list...')
                self.ips.remove(self.ip)
                self.local_tools.logIt_thread(self.log_path, msg=f'Deleting {self.conn} from self.connections.')
                del self.connections[self.conn]
                self.local_tools.logIt_thread(self.log_path, msg=f'Deleting {self.conn} from self.clients...')
                del self.clients[self.conn]
                self.local_tools.logIt_thread(self.log_path, msg=f'[V]{self.ip} removed from lists.')
                return False

    # Check if connected stations are still connected
    def vital_signs(self) -> bool:
        self.local_tools.logIt_thread(self.log_path, msg=f'Running vital_signs()...')
        if len(self.targets) == 0:
            self.app.update_statusbar_messages_thread(msg='No connected stations.')
            return False

        callback = 'yes'
        i = 0
        self.app.update_statusbar_messages_thread(msg=f'running vitals check...')
        self.local_tools.logIt_thread(self.log_path, msg=f'Iterating Through Temp Connected Sockets List...')
        for t in self.targets:
            try:
                self.local_tools.logIt_thread(self.log_path, msg=f'Sending "alive" to {t}...')
                t.send('alive'.encode())
                self.local_tools.logIt_thread(self.log_path, msg=f'Send completed.')
                self.local_tools.logIt_thread(self.log_path, msg=f'Waiting for response from {t}...')
                ans = t.recv(1024).decode()
                self.local_tools.logIt_thread(self.log_path, msg=f'Response from {t}: {ans}.')
                self.local_tools.logIt_thread(self.log_path, msg=f'Waiting for client version from {t}...')
                ver = t.recv(1024).decode()
                self.local_tools.logIt_thread(self.log_path, msg=f'Response from {t}: {ver}.')

            except (WindowsError, socket.error):
                self.remove_lost_connection(t, self.ips[i])
                break

            if str(ans) == str(callback):
                try:
                    self.local_tools.logIt_thread(self.log_path, msg=f'Iterating self.clients dictionary...')
                    for conKey, ipValue in self.clients.items():
                        for ipKey, identValue in ipValue.items():
                            if t == conKey:
                                for name, version in identValue.items():
                                    for v, v1 in version.items():
                                        for n, ver in v1.items():
                                            self.app.update_statusbar_messages_thread(
                                                msg=f'Station IP: {self.ips[i]} | Station Name: {v} | Client Version: {ver} - ALIVE!')
                                            i += 1
                                            time.sleep(0.5)

                except (IndexError, RuntimeError):
                    pass

            else:
                self.local_tools.logIt_thread(self.log_path, msg=f'Iterating self.clients dictionary...')
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

        self.app.update_statusbar_messages_thread(msg=f'Vitals check completed.')
        self.local_tools.logIt_thread(self.log_path, msg=f'=== End of vital_signs() ===')
        return True

    # Remove Lost connections
    def remove_lost_connection(self, con: str, ip: str) -> bool:
        self.local_tools.logIt_thread(self.log_path, msg=f'Running remove_lost_connection({con}, {ip})...')
        try:
            self.local_tools.logIt_thread(self.log_path, msg=f'Removing connections...')
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
                                    self.app.update_statusbar_messages_thread(
                                        msg=f'{ip} | {identValue} | {userValue} removed from connected list.')

            self.local_tools.logIt_thread(self.log_path, msg=f'Connections removed.')
            return True

        except RuntimeError as e:
            self.local_tools.logIt_thread(self.log_path, msg=f'Runtime Error: {e}.')
            return False
