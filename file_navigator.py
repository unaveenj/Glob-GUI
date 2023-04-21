import tkinter as tk
from tkinter import ttk
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
        # Create style
        style = ttk.Style()
        style.theme_use("clam")

        # Create directory selection frame
        dir_frame = ttk.Frame(self)
        dir_frame.pack(fill=tk.X, padx=20, pady=10)

        self.dir_label = ttk.Label(dir_frame, text="Select directory:")
        self.dir_label.pack(side=tk.LEFT, padx=5)

        self.dir_entry = ttk.Entry(dir_frame)
        self.dir_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        self.dir_button = ttk.Button(dir_frame, text="Choose directory", command=self.choose_directory)
        self.dir_button.pack(side=tk.LEFT, padx=5)

        # Create pattern entry frame
        pattern_frame = ttk.Frame(self)
        pattern_frame.pack(fill=tk.X, padx=20, pady=10)

        self.pattern_label = ttk.Label(pattern_frame, text="Enter glob pattern:")
        self.pattern_label.pack(side=tk.LEFT, padx=5)

        self.pattern_entry = ttk.Entry(pattern_frame)
        self.pattern_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        # Create search button frame
        search_frame = ttk.Frame(self)
        search_frame.pack(fill=tk.X, padx=20, pady=10)

        self.search_button = ttk.Button(search_frame, text="Search", command=self.search_files)
        self.search_button.pack(side=tk.LEFT, padx=5)

        self.merge_button = ttk.Button(search_frame, text="Merge", command=self.merge_files)
        self.merge_button.pack(side=tk.LEFT, padx=5)

        # Create results frame
        results_frame = ttk.Frame(self)
        results_frame.pack(fill=tk.BOTH, padx=20, pady=10, expand=True)

        self.results_label = ttk.Label(results_frame, text="Results:")
        self.results_label.pack(side=tk.TOP, anchor=tk.W, pady=5)

        self.results_text = tk.Text(results_frame, height=10)
        self.results_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        results_scrollbar = ttk.Scrollbar(results_frame, command=self.results_text.yview)
        results_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.results_text.config(yscrollcommand=results_scrollbar.set)

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
