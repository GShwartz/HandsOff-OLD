from Modules.logger import init_logger
from tkinter import messagebox
from tkinter import *
import PIL.ImageTk
import PIL.Image
import socket
import pickle


class Maintenance:
    def __init__(self, app, log_path, endpoint):
        self.app = app
        self.log_path = log_path
        self.endpoint = endpoint
        self.logger = init_logger(self.log_path, __name__)

        # Build GUI
        self.window = Toplevel(self.app)
        self.window.grab_set()
        if self.endpoint:
            self.window.title(f"Maintenance {self.endpoint.ident}")

        else:
            self.window.title(f"Maintenance...?")

        self.window.iconbitmap('HandsOff.ico')

        # Set Window Size & Location & Center Window
        self.window.geometry(f'335x50')
        self.window.configure(background='slate gray', takefocus=True)
        self.window.maxsize(333, 50)
        self.window.minsize(333, 50)

        self.checkbox_frame = Frame(self.window, relief='solid', border=1, height=1)
        self.checkbox_frame.pack(fill=X)
        self.checkbox_frame.configure(background='slate gray')

        self.check_label = Label(self.checkbox_frame, text='Maintenance Options')
        self.check_label.configure(background='slate gray')
        self.check_label.pack(fill=X, anchor=W)

        self.chkdsk_var = BooleanVar()
        self.check_dsk_checkbox = Checkbutton(self.check_label, text="Chkdsk", variable=self.chkdsk_var,
                                              onvalue=True, offvalue=False)
        self.check_dsk_checkbox.pack(anchor=CENTER, side=LEFT)
        self.check_dsk_checkbox.configure(background='slate gray')

        self.cleanup_checkbox_var = BooleanVar()
        self.cleanup_checkbox = Checkbutton(self.check_label, text="Cleanup", variable=self.cleanup_checkbox_var,
                                            onvalue=True, offvalue=False)
        self.cleanup_checkbox.pack(anchor=CENTER, side=LEFT)
        self.cleanup_checkbox.configure(background='slate gray')

        self.sfc_checkbox_var = BooleanVar()
        self.sfc_checkbox = Checkbutton(self.check_label, text="SFC Scan", variable=self.sfc_checkbox_var,
                                        onvalue=True, offvalue=False)
        self.sfc_checkbox.pack(anchor=CENTER, side=LEFT)
        self.sfc_checkbox.configure(background='slate gray')

        self.dism_checkbox_var = BooleanVar()
        self.dism_checkbox = Checkbutton(self.check_label, text="DISM", variable=self.dism_checkbox_var,
                                         onvalue=True, offvalue=False)
        self.dism_checkbox.pack(anchor=CENTER, side=LEFT)
        self.dism_checkbox.configure(background='slate gray')

        self.restart_checkbox_var = BooleanVar()
        self.restart_checkbox = Checkbutton(self.check_label, text="Restart", variable=self.restart_checkbox_var,
                                            onvalue=True, offvalue=False, command='')
        self.restart_checkbox.pack(anchor=CENTER, side=LEFT)
        self.restart_checkbox.configure(background='slate gray')

        self.submit_button = Button(self.checkbox_frame, text='Submit', command=self.submit)
        self.submit_button.pack(anchor=CENTER)

    # noinspection PyTypedDict
    def submit(self):
        todo = {"Chkdsk": self.chkdsk_var.get(),
                "Cleanup": self.cleanup_checkbox_var.get(),
                "SFC Scan": self.sfc_checkbox_var.get(),
                "DISM": self.dism_checkbox_var.get(),
                "Restart": self.restart_checkbox_var.get()
                }

        checklist = {k for k, v in todo.items() if v}
        message = f"{checklist}\n\n" \
                  f"Proceed?"
        self.logger.debug(f'Displaying confirmation pop-up...')
        confirm = messagebox.askyesno("Confirmation", message.replace('{', "").replace('}', ''))
        if confirm:
            self.logger.debug(f'Updating statusbar message...')
            self.app.update_statusbar_messages_thread(
                msg=f"Sending maintenance command to {self.endpoint.ip} | {self.endpoint.ident}...")
            try:
                self.logger.debug(f'Sending maintenance command to {self.endpoint.ip} | {self.endpoint.ident}...')
                self.endpoint.conn.send('maintenance'.encode())
                msg = self.endpoint.conn.recv(1024).decode()
                serialized = pickle.dumps(todo)
                self.endpoint.conn.sendall(serialized)
                msg = self.endpoint.conn.recv(1024).decode()
                self.logger.debug(f'{self.endpoint.ip} | {self.endpoint.ident}: {msg}')
                if 'Restart' in checklist:
                    self.logger.debug(f'Calling server.remove_lost_connection({self.endpoint})...')
                    self.app.server.remove_lost_connection(self.endpoint)

                self.window.destroy()
                self.app.refresh_command()
                return True

            except (WindowsError, socket.error) as e:
                self.logger.debug(f"Error: {e}")
                self.app.server.remove_lost_connection(self.endpoint)
                self.window.destroy()
                return False

        else:
            self.window.destroy()
            self.app.enable_buttons_thread()
            self.app.refresh_command()
            return False
