from datetime import datetime
from threading import Thread
import subprocess
import time
import os
import sys


class Sysinfo:
    def __init__(self, soc, path, hostname, localIP):
        self.soc = soc
        self.log_path = path
        self.hostname = hostname
        self.localIP = localIP

    def get_date(self):
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
        return

    def command_to_file(self):
        try:
            self.logIt_thread(self.log_path, msg='Opening system information file...')
            sysinfo = open(self.sifile, 'w')
            self.logIt_thread(self.log_path, msg='Running systeminfo command...')
            sinfo = subprocess.call(['systeminfo'], stdout=sysinfo)
            sysinfo.write("\n")
            self.logIt_thread(self.log_path, msg='Running net user command...')
            allusers = subprocess.call(['net', 'user'], stdout=sysinfo)
            sysinfo.write("\n")
            self.logIt_thread(self.log_path, msg='Closing system information file...')
            sysinfo.close()
            self.logIt_thread(self.log_path, msg=f'{sysinfo} closed.')

            return True

        except (FileNotFoundError, FileExistsError) as e:
            self.logIt_thread(self.log_path, msg=f'File Error: {e}')
            return False

    def send_file_name(self):
        try:
            self.logIt_thread(self.log_path, msg='Sending file name...')
            self.soc.send(f"{self.sifile}".encode())
            self.logIt_thread(self.log_path, msg=f'Send Completed.')

        except (WindowsError, socket.error) as e:
            self.logIt_thread(self.log_path, msg=f'Connection Error: {e}')
            return False

    def send_file_size(self):
        try:
            self.logIt_thread(self.log_path, msg='Defining file size...')
            length = os.path.getsize(self.sifile)
            self.logIt_thread(self.log_path, msg=f'File Size: {length}')

            self.logIt_thread(self.log_path, msg='Sending file size...')
            self.soc.send(self.convert_to_bytes(length))
            self.logIt_thread(self.log_path, msg=f'Send Completed.')

            return True

        except (WindowsError, socket.error) as e:
            self.logIt_thread(self.log_path, msg=f'Connection Error: {e}')
            return False

    def send_file_content(self):
        try:
            self.logIt_thread(self.log_path, msg=f'Opening {self.sifile}...')
            with open(self.sifile, 'rb') as sy_file:
                self.logIt_thread(self.log_path, msg='Sending file content...')
                sys_data = sy_file.read(1024)
                while sys_data:
                    self.soc.send(sys_data)
                    if not sys_data:
                        break

                    sys_data = sy_file.read(1024)

            self.logIt_thread(self.log_path, msg=f'Send Completed.')

        except (WindowsError, socket.error, FileExistsError, FileNotFoundError) as e:
            self.logIt_thread(self.log_path, msg=f'Error: {e}')
            return False

    def confirm(self):
        try:
            self.logIt_thread(self.log_path, msg='Waiting for message from server...')
            msg = self.soc.recv(1024).decode()
            self.logIt_thread(self.log_path, msg=f'From Server: {msg}')

            self.logIt_thread(self.log_path, msg=f'Sending confirmation message...')
            self.soc.send(f"{self.hostname} | {self.localIP}: System Information Sent.\n".encode())
            self.logIt_thread(self.log_path, msg=f'Send Completed.')

        except (WindowsError, socket.error) as e:
            self.logIt_thread(self.log_path, msg=f'Connection Error: {e}')
            return False

    def convert_to_bytes(self, no):
        result = bytearray()
        result.append(no & 255)
        for i in range(3):
            no = no >> 8
            result.append(no & 255)
        return result

    def run(self):
        self.logIt_thread(self.log_path, msg='Calling get_date()...')
        dt = self.get_date()

        self.logIt_thread(self.log_path, msg='Defining file name...')
        self.sifile = rf"C:\HandsOff\systeminfo {self.hostname} {str(self.localIP)} {dt}.txt"
        self.logIt_thread(self.log_path, msg=f'File name: {self.sifile}')

        self.logIt_thread(self.log_path, msg='Calling command_to_file()...')
        self.command_to_file()
        self.logIt_thread(self.log_path, msg='Calling send_file_name()...')
        self.send_file_name()
        self.logIt_thread(self.log_path, msg='Calling send_file_size()...')
        self.send_file_size()
        self.logIt_thread(self.log_path, msg='Calling send_file_content()...')
        self.send_file_content()
        self.logIt_thread(self.log_path, msg='Calling confirm()...')
        self.confirm()

        time.sleep(1)
        self.logIt_thread(self.log_path, msg='Removing system information file...')
        os.remove(fr'{self.sifile}')
        self.logIt_thread(self.log_path, msg=f'=== End of system_information() ===')
