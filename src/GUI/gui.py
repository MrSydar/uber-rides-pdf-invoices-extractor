from tkinter.ttk import Progressbar, Style
from tkinter import Frame, Button, HORIZONTAL, BOTH, BOTTOM, filedialog

class Application(Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.master.geometry("200x150")
        self.master.pack_propagate(0)
        self.master.resizable(0, 0)
        self.working_directory = str()

        self.s = Style(master)
        self.s.layout("LabeledProgressbar",
                      [('LabeledProgressbar.trough',
                        {'children': [('LabeledProgressbar.pbar',
                                       {'side': 'left', 'sticky': 'ns'}),
                                      ("LabeledProgressbar.label",
                                       {"sticky": ""})],
                         'sticky': 'nswe'})])
        self.s.configure("LabeledProgressbar",background='green')

        self.extract_button = Button(self)

        self.get_dir_button = Button(self)

        self.progress_bar = Progressbar(self.master,
                                        orient=HORIZONTAL,
                                        length=180,
                                        mode='determinate',
                                        style="LabeledProgressbar")

        self.configure_widgets()

        self.pack()

    def wire_extract_function(self, extract):
        self.extract_button["command"] = extract

    def update_progressbar(self, value, max_value):
        progress = round(value / max_value * 100, 2)
        self.progress_bar["value"] = progress
        self.s.configure("LabeledProgressbar", text="{0} %      ".format(progress))
        self.master.update_idletasks()

    def configure_widgets(self):

        self.get_dir_button["text"] = "SELECT DIRECTORY"
        self.get_dir_button["command"] = self.ask_dir
        self.get_dir_button.pack(fill=BOTH, pady=10)

        self.extract_button["text"] = "EXTRACT"
        self.extract_button.pack(fill=BOTH, pady=10)

        self.progress_bar.pack(side=BOTTOM, pady=20)
        self.s.configure("LabeledProgressbar", text="0 %      ")

    def ask_dir(self):
        tmp = filedialog.askdirectory()
        self.working_directory = tmp.replace('\\', '/')
