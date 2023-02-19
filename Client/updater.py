from datetime import datetime
from threading import Thread
import subprocess
import threading
import argparse
import requests
import time
import wget
import sys
import os


class Updater:
    def __init__(self, url, destination, task, path, log_path):
        self.url = url
        self.destination = destination
        self.task = task
        self.path = path
        self.log_path = log_path

    def download(self):
        logIt_thread(self.log_path, msg='Downloading new client.exe file...')
        wget.download(self.url, self.destination)
        logIt_thread(self.log_path, msg='Download complete.')
        return True

    def restart_client(self):
        logIt_thread(self.log_path, msg='Running client.vbs...')
        subprocess.run([r'wscript', rf'{self.path}\client.vbs'])
        logIt_thread(self.log_path, msg='Waiting 5 seconds for process restart...')
        time.sleep(5)

        if self.process_exists():
            logIt_thread(self.log_path, msg='\n\n=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-'
                                            '\n********** End of Updater **********\n\n')
            return True

        else:
            return False

    def process_exists(self):
        output = subprocess.run(['TASKLIST', '/FI', f'imagename eq {self.task}'],
                                capture_output=True, text=True).stdout
        last_process_line = output.strip().split('\r\n')[-1]
        return last_process_line.lower().startswith(last_process_line.lower())

    def run_client(self):
        subprocess.Popen([self.destination])

    def check_source_connection(self):
        try:
            response = requests.head(self.url)
            return response.status_code == 200

        except WindowsError:
            return False

    def update(self):
        if self.process_exists():
            logIt_thread(self.log_path, msg='Killing client.exe process...')
            subprocess.run(['taskkill', '/IM', self.task, '/F'])
            time.sleep(2)

        # Delete current client.exe file
        if self.check_source_connection() and os.path.exists(self.destination):
            logIt_thread(self.log_path, msg=f'Removing {self.destination}...')
            os.remove(self.destination)
            self.download()
            time.sleep(1)
            self.restart_client()

        else:
            self.restart_client()

        for i in range(3):
            if i == 3:
                os.system('shutdown /r /t 1')

            if not self.process_exists():
                self.restart_client()
                time.sleep(3)
                i += 1


def get_date():
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


def main():
    task = 'client.exe'
    path = rf'c:\HandsOff'
    client_file = rf'{path}\client.exe'
    log_path = rf'{path}\updater_log.txt'
    url = 'http://192.168.1.36/client.exe'
    # url = 'http://handsoff.home.lab/client.exe'

    logIt_thread(log_path, msg='\n\n********** Starting Updater **********')
    updater = Updater(url, client_file, task, path, log_path)
    updater.update()


if __name__ == '__main__':
    main()
