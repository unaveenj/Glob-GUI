import tkinter as tk
from tkinter import filedialog
import os
import fnmatch
import pandas as pd

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

        self.merge_button = tk.Button(self, text="Merge", command=self.merge_files)
        self.merge_button.pack()

        self.results_label = tk.Label(self, text="Results:")
        self.results_label.pack()

        self.results_text = tk.Text(self, height=10)
        self.results_text.pack()

        self.results_text.bind("<Double-Button-1>", self.open_directory)

        self.files = []

    def choose_directory(self):
        self.directory = filedialog.askdirectory()
        self.dir_label.config(text=f"Selected directory: {self.directory}")

    def search_files(self):
        pattern = self.pattern_entry.get()
        if not os.path.isdir(self.directory):
            self.results_text.insert(tk.END, "Selected directory does not exist.")
            return

        files = []
        for root, dirnames, filenames in os.walk(self.directory):
            for filename in fnmatch.filter(filenames, pattern):
                files.append(os.path.join(root, filename))

        if not files:
            self.results_text.insert(tk.END, "No matching files found.")
            return

        self.files = files
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
                self.results_text.insert(tk.END, f"Error: directory '{directory}' not found.\n")

    def merge_files(self):
        if not self.files:
            self.results_text.insert(tk.END, "No files selected for merge.")
            return

        # Merge files into a single output file
        extension = os.path.splitext(self.files[0])[1]
        if extension in ['.xlsx', '.xls']:
            # Merge Excel files
            merged_df = pd.DataFrame()
            for file in self.files:
                df = pd.read_excel(file)
                merged_df = pd.concat([merged_df, df], axis=0)
            # Ask user for output file name and location
            output_file = filedialog.asksaveasfilename(defaultextension='.xlsx', filetypes=[('Excel Files', '*.xlsx')])
            writer = pd.ExcelWriter(output_file, engine='xlsxwriter')
            merged_df.to_excel(writer, index=False)
            writer.save()
        elif extension == '.csv':
            # Merge CSV files
            merged_df = pd.concat([pd.read_csv(file) for file in self.files], axis=0)
            # Ask user for output file name and location
            output_file = filedialog.asksaveasfilename(defaultextension='.csv', filetypes=[('CSV Files', '*.csv')])
            merged_df.to_csv(output_file, index=False)
        else:
            self.results_text.insert(tk.END, f"Error: unsupported file extension '{extension}'.")
            return

        self.results_text.insert(tk.END, f"Successfully merged {len(self.files)} files to '{output_file}'.")


if __name__ == "__main__":
    root = tk.Tk()
    app = FileSearchApp(master=root)
    app.mainloop()
