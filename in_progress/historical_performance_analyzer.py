import datetime
import os
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import filedialog, messagebox


class HistoricalPerformanceAnalyzer(ttk.Frame):
    def __init__(self, parent, project_dir=None):
        super().__init__(parent)
        self.parent = parent
        self.project_dir = project_dir
        self.load_style()
        self.init_ui()

    def load_style(self):
        style = ttk.Style()
        style.theme_use('clam')
        font_name = "Bahnschrift"
        bg_color = '#2e2e2e'
        fg_color = 'white'
        entry_bg_color = "#4a4a4a"
        button_bg_color = '#4a4a4a'
        button_active_bg_color = '#606060'
        text_color = '#d3d3d3'
        arrow_color = 'white'

        # Configure Styles
        style.configure('.', background=bg_color, foreground=fg_color, font=(font_name, 10))
        style.configure('TLabel', background=bg_color, foreground=fg_color, padding=5, font=(font_name, 12))
        style.configure('TButton', activebackground=button_active_bg_color, foreground=fg_color, padding=8,
                        relief='flat',
                        font=(font_name, 11),
                        borderwidth=0, focuscolor='gray',
                        background=button_active_bg_color, activeforeground=fg_color)
        style.map('TButton',
                  background=[('active', button_active_bg_color), ('disabled', button_bg_color)],
                  foreground=[('disabled', 'gray')])
        style.configure('TEntry', fieldbackground=entry_bg_color, foreground=text_color, font=(font_name, 11))
        style.configure('TCombobox', fieldbackground=entry_bg_color, foreground=text_color, font=(font_name, 11))
        style.map('TCombobox', fieldbackground=[('readonly', entry_bg_color)])
        style.configure('Vertical.TScrollbar', background=button_bg_color, arrowcolor=arrow_color, bordercolor=bg_color,
                        troughcolor=bg_color)
        style.configure('Horizontal.TScrollbar', background=button_bg_color, arrowcolor=arrow_color,
                        bordercolor=bg_color, troughcolor=bg_color)

        self.style = style

    def init_ui(self):
        # --- Project Directory ---
        self.project_dir_label = ttk.Label(self, text="Project Directory:")
        self.project_dir_label.grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.project_dir_var = tk.StringVar(value=self.project_dir or "")
        self.project_dir_entry = ttk.Entry(self, textvariable=self.project_dir_var, width=30, state="disabled")
        self.project_dir_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        self.browse_button = ttk.Button(self, text="Browse", command=self.browse_project_directory)
        self.browse_button.grid(row=0, column=2, sticky="w", padx=5, pady=5)

        # --- Buttons ---
        self.analyze_button = ttk.Button(self, text="Analyze Project", command=self.analyze_project)
        self.analyze_button.grid(row=1, column=1, sticky="e", padx=5, pady=10)

        # --- Report Display ---
        self.report_label = ttk.Label(self, text="Analysis Report:")
        self.report_label.grid(row=2, column=0, sticky="w", padx=5, pady=5)

        self.report_text = tk.Text(self, wrap=tk.WORD, width=80, height=20)
        self.report_text.grid(row=2, column=1, sticky="ew", padx=5, pady=5)
        self.report_text.config(state=tk.DISABLED)  # Make it read-only

        # --- Ideal Names Display ---
        self.ideal_names_label = ttk.Label(self, text="Ideal Task Names:")
        self.ideal_names_label.grid(row=3, column=0, sticky="w", padx=5, pady=5)

        self.ideal_names_text = tk.Text(self, wrap=tk.WORD, width=80, height=5)
        self.ideal_names_text.grid(row=3, column=1, sticky="ew", padx=5, pady=5)
        self.ideal_names_text.config(state=tk.DISABLED)

        self.autocorrect = ttk.Button(self, text="Autocorrect selected", command=self.autocorrect_task)
        self.autocorrect.grid(row=4, column=1, sticky="e", padx=5, pady=10)

        self.ideal_author_label = ttk.Label(self, text="Ideal Authors:")
        self.ideal_author_label.grid(row=5, column=0, sticky="w", padx=5, pady=5)

        self.ideal_author_text = tk.Text(self, wrap=tk.WORD, width=80, height=5)
        self.ideal_author_text.grid(row=5, column=1, sticky="ew", padx=5, pady=5)
        self.ideal_author_text.config(state=tk.DISABLED)

        self.columnconfigure(1, weight=1)

    def browse_project_directory(self):
        directory = filedialog.askdirectory(title="Select Project Directory")
        if directory:
            self.project_dir = directory
            self.project_dir_var.set(directory)

    def analyze_project(self):
        if not self.project_dir:
            messagebox.showerror("Error", "Please select a project directory first.")
            return

        task_data = self.collect_task_data()
        if not task_data:
            messagebox.showinfo("Info", "No task data found in the project directory.")
            return

        analysis_results = self.perform_analysis(task_data)
        self.display_report(analysis_results["report"])
        self.display_ideal_names(analysis_results["ideal_names"])
        self.display_ideal_authors(analysis_results["ideal_authors"])

        self.task_data = task_data
        self.autocorrect_names = analysis_results["ideal_names"]

    def collect_task_data(self):
        """Collects data from task files in the project directory."""
        task_data = []
        for file_name in os.listdir(self.project_dir):
            if file_name.startswith("task for ") and file_name.endswith(".txt"):
                try:
                    task_path = os.path.join(self.project_dir, file_name)
                    with open(task_path, "r") as f:
                        task = {}
                        for line in f:
                            if ":" in line:
                                key, value = line.strip().split(":", 1)
                                task[key.strip()] = value.strip()
                        task_data.append(task)
                except Exception as e:
                    messagebox.showerror("Error", f"Error reading task file {file_name}: {e}")
        return task_data

    def perform_analysis(self, task_data):
        """Performs historical analysis and generates reports."""
        # 1. Task Time Estimation Accuracy (Basic)
        time_differences = []
        for task in task_data:
            try:
                due_date = datetime.datetime.strptime(task["due date"], "%Y-%m-%d").date()

                if task["status"].startswith("Completed on"):
                    completed_date_str = task["status"].split("Completed on ")[1]
                    completed_date = datetime.datetime.strptime(completed_date_str, "%Y-%m-%d").date()
                    time_difference = (completed_date - due_date).days
                    time_differences.append(time_difference)
            except (ValueError, KeyError):
                pass

        avg_time_difference = sum(time_differences) / len(time_differences) if time_differences else 0

        # 2. Artist Performance (Basic)
        artist_task_counts = {}
        for task in task_data:
            artist = task["assigned artist"]
            artist_task_counts[artist] = artist_task_counts.get(artist, 0) + 1

        # 3. Common Problem Identification (Name Analyze)
        task_name_counts = {}
        for task in task_data:
            name = task["task name"]
            task_name_counts[name] = task_name_counts.get(name, 0) + 1

        # Identify "ideal" name
        ideal_names = sorted(task_name_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        ideal_names_list = [name for name, count in ideal_names]

        author_name_counts = {}
        for task in task_data:
            name = task["assigned artist"]
            author_name_counts[name] = author_name_counts.get(name, 0) + 1

        ideal_authors = sorted(author_name_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        ideal_authors_list = [author for author, count in ideal_authors]

        # Generate Report
        report = f"Historical Performance Analysis:\n\n"
        report += f"Average Task Time Difference: {avg_time_difference:.2f} days\n\n"
        report += "Task Counts by Artist:\n"
        for artist, count in artist_task_counts.items():
            report += f" - {artist}: {count}\n"

        analysis_result = {
            "report": report,
            "ideal_names": ideal_names_list,
            "ideal_authors": ideal_authors_list
        }

        return analysis_result  # Change list to directorys to show all tasks and directorys

    def display_report(self, report):
        self.report_text.config(state=tk.NORMAL)  # Enable editing
        self.report_text.delete("1.0", tk.END)  # Clear existing text
        self.report_text.insert("1.0", report)  # Insert the report
        self.report_text.config(state=tk.DISABLED)  # Disable editing

    def display_ideal_names(self, ideal_names):
        """Displays a report for a "better task name" in text."""
        self.ideal_names_text.config(state=tk.NORMAL)
        self.ideal_names_text.delete("1.0", tk.END)
        self.ideal_names_text.insert("1.0", "\n".join(ideal_names))
        self.ideal_names_text.config(state=tk.DISABLED)

    def display_ideal_authors(self, authors):
        """Displays a report for a "better task name" in text."""
        self.ideal_author_text.config(state=tk.NORMAL)
        self.ideal_author_text.delete("1.0", tk.END)
        self.ideal_author_text.insert("1.0", "\n".join(authors))
        self.ideal_author_text.config(state=tk.DISABLED)

    def autocorrect_task(self):
        messagebox.showinfo("showinfo", "Not done yet, still in development")


def integrate_historical_performance_analyzer(main_frame, project_dir=None):
    analyzer = HistoricalPerformanceAnalyzer(main_frame, project_dir)
    analyzer.pack(expand=True, fill="both")


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Historical Performance Analyzer")
    root.geometry("800x600")
    analyzer = HistoricalPerformanceAnalyzer(root)
    analyzer.pack(expand=True, fill="both")
    root.mainloop()
