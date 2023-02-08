import socket
from threading import Thread
import time


class Endpoints:
    def __init__(self, conn, client_mac, ip, ident, user, client_version):
        self.conn = conn
        self.client_mac = client_mac
        self.ip = ip
        self.ident = ident
        self.user = user
        self.client_version = client_version

    def __repr__(self):
        return f"Endpoint({self.conn, self.client_mac, self.ip, self.ident, self.user, self.client_version})"


class Server:
    def __init__(self, local_tools, log_path, app, ip, port):
        self.clients = {}
        self.clients_backup = {}
        self.connections = {}
        self.connHistory = {}
        self.ips = []
        self.targets = []
        self.ttl = 5
        self.port = port
        self.hostname = socket.gethostname()
        self.serverIP = ip
        self.local_tools = local_tools
        self.log_path = log_path
        self.app = app
        self.endpoints = []

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

    def run(self) -> None:
        self.local_tools.logIt_thread(self.log_path, msg=f'Running run()...')
        self.local_tools.logIt_thread(self.log_path, msg=f'Calling connect()...')
        self.connectThread = Thread(target=self.connect,
                                    daemon=True,
                                    name=f"Connect Thread")
        self.connectThread.start()

    def get_mac_address(self) -> str:
        self.local_tools.logIt_thread(self.log_path, msg=f'Waiting for MAC address from {self.ip}...')
        self.mac = self.conn.recv(1024).decode()
        self.local_tools.logIt_thread(self.log_path, msg=f'MAC Address: {self.mac}')
        self.local_tools.logIt_thread(self.log_path, msg=f'Sending confirmation to {self.ip}...')
        self.conn.send('OK'.encode())
        self.local_tools.logIt_thread(self.log_path, msg=f'Send completed.')
        return self.mac

    def get_hostname(self) -> str:
        self.local_tools.logIt_thread(self.log_path, msg=f'Waiting for remote station name...')
        self.ident = self.conn.recv(1024).decode()
        self.local_tools.logIt_thread(self.log_path, msg=f'Remote station name: {self.ident}')
        self.local_tools.logIt_thread(self.log_path, msg=f'Sending Confirmation to {self.ip}...')
        self.conn.send('OK'.encode())
        self.local_tools.logIt_thread(self.log_path, msg=f'Send completed.')
        return self.ident

    def get_user(self) -> str:
        self.local_tools.logIt_thread(self.log_path, msg=f'Waiting for remote station current logged user...')
        self.user = self.conn.recv(1024).decode()
        self.local_tools.logIt_thread(self.log_path, msg=f'Remote station user: {self.user}')
        self.local_tools.logIt_thread(self.log_path, msg=f'Sending Confirmation to {self.ip}...')
        self.conn.send('OK'.encode())
        self.local_tools.logIt_thread(self.log_path, msg=f'Send completed.')
        return self.user

    def get_client_version(self) -> str:
        self.local_tools.logIt_thread(self.log_path, msg=f'Waiting for client version...')
        self.client_version = self.conn.recv(1024).decode()
        self.local_tools.logIt_thread(self.log_path, msg=f'Client version: {self.client_version}')
        self.local_tools.logIt_thread(self.log_path, msg=f'Sending confirmation to {self.ip}...')
        self.conn.send('OK'.encode())
        self.local_tools.logIt_thread(self.log_path, msg=f'Send completed.')
        return self.client_version

    # Listen for connections and sort new connections to designated lists/dicts
    def connect(self) -> None:
        self.local_tools.logIt_thread(self.log_path, msg=f'Running connect()...')
        while True:
            dt = self.local_tools.get_date()
            self.local_tools.logIt_thread(self.log_path, msg=f'Accepting connections...')
            self.conn, (self.ip, self.port) = self.server.accept()
            self.local_tools.logIt_thread(self.log_path, msg=f'Connection from {self.ip} accepted.')

            try:
                self.local_tools.logIt_thread(self.log_path, msg=f'Waiting for MAC Address...')
                self.client_mac = self.get_mac_address()
                self.local_tools.logIt_thread(self.log_path, msg=f'MAC: {self.client_mac}.')
                self.local_tools.logIt_thread(self.log_path, msg=f'Waiting for station name...')
                self.hostname = self.get_hostname()
                self.local_tools.logIt_thread(self.log_path, msg=f'Station name: {self.hostname}.')
                self.local_tools.logIt_thread(self.log_path, msg=f'Waiting for logged user...')
                self.loggedUser = self.get_user()
                self.local_tools.logIt_thread(self.log_path, msg=f'Logged user: {self.loggedUser}.')
                self.local_tools.logIt_thread(self.log_path, msg=f'Waiting for client version...')
                self.client_version = self.get_client_version()
                self.local_tools.logIt_thread(self.log_path, msg=f'Client version: {self.client_version}.')

            except (WindowsError, socket.error, UnicodeDecodeError) as e:
                self.local_tools.logIt_thread(self.log_path, msg=f'Connection Error: {e}')
                return  # Restart The Loop

            # Apply Data to dataclass Endpoints
            fresh_endpoint = Endpoints(self.conn, self.client_mac, self.ip, self.ident, self.user, self.client_version)
            if fresh_endpoint not in self.endpoints:
                self.endpoints.append(fresh_endpoint)
                self.targets.append(fresh_endpoint.conn)
                self.ips.append(fresh_endpoint.ip)
                # self.temp_connection = {fresh_endpoint.conn: fresh_endpoint.ip}
                self.connections.update({fresh_endpoint.conn: fresh_endpoint.ip})
                # self.connections.update(self.temp_connection)
                self.temp_ident = {
                    fresh_endpoint.conn: {fresh_endpoint.client_mac: {
                        fresh_endpoint.ip: {
                            fresh_endpoint.ident: {
                                fresh_endpoint.user: fresh_endpoint.client_version}}}}}
                self.clients.update(self.temp_ident)
                self.temp_connection_record = {self.conn: {self.client_mac: {self.ip: {self.ident: {self.user: dt}}}}}

            self.connHistory.update({fresh_endpoint: dt})

            self.app.display_server_information_thread()
            self.welcome_message()

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

            except (WindowsError, socket.error, UnicodeDecodeError):
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
            for endpoint in self.endpoints:
                if endpoint.conn == con and endpoint.ip == ip:
                    self.targets.remove(con)
                    self.ips.remove(ip)

                    del self.connections[con]
                    del self.clients[con]
                    self.endpoints.remove(endpoint)

                    # Update statusbar message
                    self.app.update_statusbar_messages_thread(
                        msg=f'{endpoint.ip} | {endpoint.ident} | {endpoint.user} removed from connected list.')

            self.local_tools.logIt_thread(self.log_path, msg=f'Connections removed.')
            return True

        except RuntimeError as e:
            self.local_tools.logIt_thread(self.log_path, msg=f'Runtime Error: {e}.')
            return False
