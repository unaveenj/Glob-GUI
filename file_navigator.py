import tkinter as tk
from tkinter import filedialog
import glob
import os
import fnmatch


class FileSearchApp(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.master.title("File Search")
        self.pack()
        self.create_widgets()

    def create_widgets(self):
        self.dir_label = tk.Label(self, text="Select directory:")
        self.dir_label.pack()

        self.dir_button = tk.Button(self, text="Choose directory", command=self.choose_directory)
        self.dir_button.pack()

        self.pattern_label = tk.Label(self, text="Enter glob pattern:")
        self.pattern_label.pack()

        self.pattern_entry = tk.Entry(self)
        self.pattern_entry.pack()

        self.search_button = tk.Button(self, text="Search", command=self.search_files)
        self.search_button.pack()

        self.results_label = tk.Label(self, text="Results:\nDouble Click to open directory")
        self.results_label.pack()

        self.results_text = tk.Text(self, height=10)
        self.results_text.pack()

        self.results_text.bind("<Double-Button-1>", self.open_directory)

    def choose_directory(self):
        self.directory = filedialog.askdirectory()
        self.dir_label.config(text=f"Selected directory: {self.directory}")

    def search_files(self):
        pattern = self.pattern_entry.get()
        files = []
        for root, dirnames, filenames in os.walk(self.directory):
            for filename in fnmatch.filter(filenames, pattern):
                files.append(os.path.join(root, filename))

        self.results_text.delete("1.0", tk.END)
        for file in files:
            self.results_text.insert(tk.END, file + "\n")

    def open_directory(self, event):
        selection = self.results_text.tag_ranges(tk.SEL)
        if selection:
            filename = self.results_text.get(*selection)
            directory = os.path.dirname(filename)
            if os.path.exists(directory):
                os.startfile(directory)
            else:
                pass
                # self.results_text.insert(tk.END, f"Error: directory '{directory}' not found.\n")


if __name__ == "__main__":
    root = tk.Tk()
    app = FileSearchApp(master=root)
    app.mainloop()
