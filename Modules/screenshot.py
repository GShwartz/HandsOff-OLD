from datetime import datetime
from threading import Thread
from tkinter import *
import PIL.ImageTk
import PIL.Image
import shutil
import socket
import glob
import os


class Screenshot:
    def __init__(self, endpoint, app, path, log_path):
        self.endpoint = endpoint
        self.app = app
        self.path = path
        self.log_path = log_path
        self.screenshot_path = fr"{self.path}\{self.endpoint.ident}"

    def make_dir(self):
        try:
            os.makedirs(self.screenshot_path)

        except FileExistsError:
            logIt_thread(self.log_path, debug=False, msg=f'Passing FileExistsError...')
            pass

    def get_file_name(self):
        try:
            self.filename = self.endpoint.conn.recv(1024)
            self.filename = str(self.filename).strip("b'")
            self.endpoint.conn.send("Filename OK".encode())
            self.screenshot_file_path = os.path.join(self.screenshot_path, self.filename)

        except (ConnectionError, socket.error) as e:
            logIt_thread(self.log_path, msg=f'{e}')
            self.app.server.remove_lost_connection(self.endpoint)
            return False

    def get_file_size(self):
        try:
            self.size = self.endpoint.conn.recv(4)
            self.endpoint.conn.send("OK".encode())
            self.size = bytes_to_number(self.size)

        except (ConnectionError, socket.error) as e:
            logIt_thread(self.log_path, msg=f'{e}')
            self.app.server.remove_lost_connection(self.endpoint)
            return False

    def get_file_content(self):
        current_size = 0
        buffer = b""
        try:
            logIt_thread(self.log_path, debug=False, msg=f'Opening file: {self.filename} for writing...')
            with open(self.screenshot_file_path, 'wb') as file:
                logIt_thread(self.log_path, debug=False, msg=f'Fetching file content...')
                while current_size < self.size:
                    data = self.endpoint.conn.recv(1024)
                    if not data:
                        break

                    if len(data) + current_size > self.size:
                        data = data[:self.size - current_size]

                    buffer += data
                    current_size += len(data)
                    file.write(data)

            logIt_thread(self.log_path, debug=False, msg=f'Fetch completed.')

        except FileExistsError:
            logIt_thread(self.log_path, debug=False, msg=f'File Exists error.')
            pass

    def confirm(self):
        try:
            logIt_thread(self.log_path, debug=False, msg=f'Waiting for answer from client...')
            self.ans = self.endpoint.conn.recv(1024).decode()
            logIt_thread(self.log_path, debug=False, msg=f'Client answer: {self.ans}')

        except (ConnectionError, socket.error) as e:
            logIt_thread(log_path, msg=f'{e}')
            self.app.server.remove_lost_connection(self.endpoint)
            return False

    def show_picture_thread(self):
        Thread(target=self.show_picture, name="Show Picture").start()

    def show_picture(self):
        self.sc.show()

    def display_notebook_frame(self):
        logIt_thread(self.log_path, msg=f'Building working frame...')
        self.tab = Frame(self.app.notebook, height=350, background='slate gray')
        logIt_thread(self.log_path, msg=f'Building Preview Button...')
        self.button = Button(self.tab, image=self.last_screenshot, command=self.show_picture_thread,
                             background='slate gray')
        self.button.pack(padx=5, pady=5)
        self.endpoint.conn.send("OK".encode())

        logIt_thread(self.log_path, msg=f'Adding tab to notebook...')
        self.app.notebook.add(self.tab, text=f"Screenshot {self.endpoint.ident}")
        logIt_thread(self.log_path, msg=f'Displaying latest notebook tab...')
        self.app.notebook.select(self.tab)
        self.app.displayed_screenshot_files.append(self.last_screenshot)
        self.app.tabs += 1

        self.app.enable_buttons_thread()
        self.app.update_statusbar_messages_thread(msg=f'Screenshot received from '
                                                      f'{self.endpoint.ip} | {self.endpoint.ident}.')

    def run(self):
        self.app.refresh_btn.config(state=DISABLED)
        self.app.disable_buttons_thread()
        self.app.update_statusbar_messages_thread(
            msg=f'Fetching screenshot from {self.endpoint.ip} | {self.endpoint.ident}...')

        self.make_dir()

        try:
            logIt_thread(self.log_path, msg=f'Sending screen command to client...')
            self.endpoint.conn.send('screen'.encode())

        except (ConnectionError, socket.error) as e:
            logIt_thread(self.log_path, msg=f'{e}')
            self.app.server.remove_lost_connection(self.endpoint)
            return False

        self.get_file_name()
        self.get_file_size()
        self.get_file_content()

        try:
            logIt_thread(self.log_path, msg=f'Sorting jpg files by creation time...')
            self.images = glob.glob(fr"{self.screenshot_path}\*.jpg")
            self.images.sort(key=os.path.getmtime)
            logIt_thread(self.log_path, msg=f'Opening latest screenshot...')
            self.sc = PIL.Image.open(self.images[-1])

        except IndexError:
            pass

        logIt_thread(self.log_path, msg=f'Resizing to 650x350...')
        self.sc_resized = self.sc.resize((650, 350))
        self.last_screenshot = PIL.ImageTk.PhotoImage(self.sc_resized)

        logIt_thread(self.log_path, msg=f'Building working frame...')
        self.display_notebook_frame()
        self.app.refresh_btn.config(state=NORMAL)


def logIt_thread(log_path=None, debug=False, msg='') -> None:
    logit_thread = Thread(target=logIt,
                          args=(log_path, debug, msg),
                          daemon=True,
                          name="Log Thread")
    logit_thread.start()


def bytes_to_number(b: int) -> int:
    dt = get_date()
    res = 0
    for i in range(4):
        res += b[i] << (i * 8)
    return res


def get_date() -> str:
    d = datetime.now().replace(microsecond=0)
    dt = str(d.strftime("%d/%b/%y %H:%M:%S"))

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
