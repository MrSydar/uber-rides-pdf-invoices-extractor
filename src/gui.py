from tkinter import filedialog
import tkinter as tk

class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.master.geometry("200x100")
        self.working_directory = str()
        self.pack()

        self.get_dir_button = tk.Button(self)
        self.extract_button = tk.Button(self)

        self.configure_widgets()

    def wire_extract_function(self, extract):
        self.extract_button["command"] = extract

    def configure_widgets(self):
        self.get_dir_button["text"] = "SELECT DIRECTORY"
        self.get_dir_button["command"] = self.ask_dir
        self.get_dir_button.pack(side="top")

        self.extract_button["text"] = "EXTRACT"
        self.extract_button.pack(side="bottom")

    def ask_dir(self):
        self.working_directory = filedialog.askdirectory()