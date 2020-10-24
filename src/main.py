from src.GUI.gui import *
from src.pdf_processing.extractor import *
from tkinter import Tk

def main():
    app = Application(Tk())
    app.wire_extract_function(lambda: extract(app.working_directory, app.update_progressbar))
    app.mainloop()

if __name__ == "__main__":
    main()