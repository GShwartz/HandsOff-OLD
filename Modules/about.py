from tkinter import *
import PIL.ImageTk
import webbrowser
import PIL.Image


class About:
    def __init__(self, app):
        self.app = app

        # Build GUI
        self.about_window = Toplevel()
        self.about_window.title("HandsOff - About")
        self.about_window.iconbitmap('HandsOff.ico')

        # Update screen geometry variables
        self.app.update_idletasks()

        # Set Mid Screen Coordinates
        x = (app.WIDTH / 2) - (400 / 2)
        y = (app.HEIGHT / 2) - (200 / 2)

        # Set Window Size & Location & Center Window
        self.about_window.geometry(f'{400}x{200}+{int(x)}+{int(y)}')
        self.about_window.configure(background='slate gray', takefocus=True)
        self.about_window.grid_columnconfigure(2, weight=1)
        self.about_window.grid_rowconfigure(3, weight=1)
        self.about_window.maxsize(400, 200)
        self.about_window.minsize(400, 200)

        self.github_url = 'https://github.com/GShwartz/PeachGUI'
        self.youtube_url = 'https://www.youtube.com/channel/UC5jHVur21yVo7nu7nLnuyoQ'
        self.linkedIn_url = 'https://www.linkedin.com/in/gilshwartz/'

        self.github_black = PIL.ImageTk.PhotoImage(
            PIL.Image.open('images/github_black.png').resize((50, 50), PIL.Image.LANCZOS))
        self.github_purple = PIL.ImageTk.PhotoImage(
            PIL.Image.open('images/github_purple.png').resize((50, 50), PIL.Image.LANCZOS))
        self.linkedin_black = PIL.ImageTk.PhotoImage(
            PIL.Image.open('images/linkedin_black.png').resize((50, 50), PIL.Image.LANCZOS))
        self.linkedin_blue = PIL.ImageTk.PhotoImage(
            PIL.Image.open('images/linkedin_blue.png').resize((50, 50), PIL.Image.LANCZOS))
        self.youtube_red = PIL.ImageTk.PhotoImage(
            PIL.Image.open('images/youtube_red.png').resize((50, 50), PIL.Image.LANCZOS))
        self.youtube_black = PIL.ImageTk.PhotoImage(
            PIL.Image.open('images/youtube_black.png').resize((50, 50), PIL.Image.LANCZOS))
        self.app.social_buttons.append([self.github_black, self.github_purple,
                                        self.youtube_red, self.youtube_black,
                                        self.linkedin_blue, self.linkedin_black])

    def run(self):
        self.app_name_label = Label(self.about_window, relief='ridge', background='ghost white', width=45)
        self.app_name_label.configure(text='HandsOff\n\n'
                                           'Copyright 2022 Gil Shwartz. All rights reserved.\n'
                                           'handsoffapplication@gmail.com\n'
                                           '=====----=====\n')
        self.app_name_label.pack(ipady=10, ipadx=10, pady=5)

        self.github_label = Label(self.about_window, image=self.github_purple, background='slate gray')
        self.github_label.image = [self.github_purple, self.github_black]
        self.github_label.place(x=80, y=130)
        self.github_label.bind("<Button-1>", lambda x: self.on_github_click(self.github_url))
        self.github_label.bind("<Enter>", self.on_github_hover)
        self.github_label.bind("<Leave>", self.on_github_leave)

        self.youtube_label = Label(self.about_window, image=self.youtube_red, background='slate gray')
        self.youtube_label.image = [self.youtube_red, self.youtube_black]
        self.youtube_label.place(x=173, y=130)
        self.youtube_label.bind("<Button-1>", lambda x: self.on_youtube_click(self.youtube_url))
        self.youtube_label.bind("<Enter>", self.on_youtube_hover)
        self.youtube_label.bind("<Leave>", self.on_youtube_leave)

        self.linkedIn_label = Label(self.about_window, image=self.linkedin_blue, background='slate gray')
        self.linkedIn_label.image = [self.linkedin_black, self.linkedin_blue]
        self.linkedIn_label.place(x=264, y=130)
        self.linkedIn_label.bind("<Button-1>", lambda x: self.on_youtube_click(self.linkedIn_url))
        self.linkedIn_label.bind("<Enter>", self.on_linkedIn_hover)
        self.linkedIn_label.bind("<Leave>", self.on_linkedIn_leave)

    def on_github_hover(self, event):
        return self.github_label.config(image=self.github_black)

    def on_github_leave(self, event):
        return self.github_label.config(image=self.github_purple)

    def on_youtube_hover(self, event):
        return self.youtube_label.config(image=self.youtube_black)

    def on_youtube_leave(self, event):
        return self.youtube_label.config(image=self.youtube_red)

    def on_linkedIn_hover(self, event):
        return self.linkedIn_label.config(image=self.linkedin_black)

    def on_linkedIn_leave(self, event):
        return self.linkedIn_label.config(image=self.linkedin_blue)

    def on_github_click(self, url):
        return webbrowser.open_new_tab(url)

    def on_youtube_click(self, url):
        return webbrowser.open_new_tab(url)

    def on_linkedin_click(self, url):
        return webbrowser.open_new_tab(url)
