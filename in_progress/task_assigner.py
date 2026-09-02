import datetime
import os
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import filedialog, messagebox

from tkcalendar import DateEntry


class TaskAssigner(ttk.Frame):
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
        style.configure('.', background=bg_color, foreground=fg_color, font=(font_name, 10))
        style.configure('TLabel', background=bg_color, foreground=fg_color, padding=5, font=(font_name, 12))
        style.configure('TButton', background=button_bg_color, foreground=fg_color, padding=8, relief='flat',
                        font=(font_name, 11),
                        borderwidth=0, focuscolor='gray',
                        activebackground=button_active_bg_color, activeforeground=fg_color)
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

        # --- Task Name ---
        self.task_name_label = ttk.Label(self, text="Task Name:")
        self.task_name_label.grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.task_name_entry = ttk.Entry(self, width=30)
        self.task_name_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=5)

        # --- Assigned Artist ---
        self.artist_label = ttk.Label(self, text="Assigned Artist:")
        self.artist_label.grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.artist_entry = ttk.Entry(self, width=30)
        self.artist_entry.grid(row=2, column=1, sticky="ew", padx=5, pady=5)

        # --- Due Date ---
        self.due_date_label = ttk.Label(self, text="Due Date:")
        self.due_date_label.grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.due_date_entry = DateEntry(self, width=12, background="#4a4a4a",
                                        foreground='white', borderwidth=2,
                                        date_pattern='yyyy-mm-dd', selectmode="day")
        self.due_date_entry.grid(row=3, column=1, sticky="ew", padx=5, pady=5)

        # --- Status ---
        self.status_label = ttk.Label(self, text="Status:")
        self.status_label.grid(row=4, column=0, sticky="w", padx=5, pady=5)
        self.status_choices = ["Not Started", "In Progress", "Blocked", "Completed"]
        self.status_var = tk.StringVar(value=self.status_choices[0])
        self.status_combobox = ttk.Combobox(self, textvariable=self.status_var, values=self.status_choices,
                                            state="readonly", width=20)
        self.status_combobox.grid(row=4, column=1, sticky="w", padx=5, pady=5)

        # --- Task Description ---
        self.description_label = ttk.Label(self, text="Description:")
        self.description_label.grid(row=5, column=0, sticky="w", padx=5, pady=5)
        self.description_text = tk.Text(self, wrap=tk.WORD, width=40, height=5)
        self.description_text.grid(row=5, column=1, sticky="ew", padx=5, pady=5)

        # --- Standardized Folder Structure Options ---
        self.assets_var = tk.BooleanVar(value=False)
        self.assets_check = ttk.Checkbutton(self, text="Assets", variable=self.assets_var)
        self.assets_check.grid(row=6, column=1, sticky="w", padx=5, pady=5)

        self.characters_var = tk.BooleanVar(value=False)
        self.characters_check = ttk.Checkbutton(self, text="Characters", variable=self.characters_var)
        self.characters_check.grid(row=7, column=1, sticky="w", padx=5, pady=5)

        self.locations_var = tk.BooleanVar(value=False)
        self.locations_check = ttk.Checkbutton(self, text="Locations", variable=self.locations_var)
        self.locations_check.grid(row=8, column=1, sticky="w", padx=5, pady=5)

        # --- Custom Polls ---
        self.poll_label = ttk.Label(self, text="Custom Polls:")
        self.poll_label.grid(row=9, column=0, sticky="w", padx=5, pady=5)
        self.poll_entry = ttk.Entry(self, width=30)
        self.poll_entry.grid(row=9, column=1, sticky="ew", padx=5, pady=5)

        # --- Buttons ---
        self.assign_button = ttk.Button(self, text="Assign Task", command=self.assign_task)
        self.assign_button.grid(row=10, column=0, sticky="e", padx=5, pady=10)

        self.delete_button = ttk.Button(self, text="Delete Task", command=self.delete_selected_task)
        self.delete_button.grid(row=10, column=1, sticky="e", padx=5, pady=10)

        # --- Task List ---
        self.task_list_label = ttk.Label(self, text="Task List:")
        self.task_list_label.grid(row=11, column=0, sticky="w", padx=5, pady=5)

        self.task_listbox = tk.Listbox(self, width=60, height=10)
        self.task_listbox.grid(row=12, column=1, sticky="ew", padx=5, pady=5)
        self.task_listbox.bind("<Double-Button-1>", self.load_selected_task)

        # --- Messages ---
        self.message_label = ttk.Label(self, text="")
        self.message_label.grid(row=14, column=1, sticky="w", padx=5, pady=5)

        # Configure column weights
        self.columnconfigure(1, weight=1)

        if self.project_dir:
            self.load_tasks()

    def browse_project_directory(self):
        directory = filedialog.askdirectory(title="Select Project Directory")
        if directory:
            self.project_dir = directory
            self.project_dir_var.set(directory)
            self.load_tasks()

    def assign_task(self):
        task_name = self.task_name_entry.get()
        artist = self.artist_entry.get()
        due_date = self.due_date_entry.get_date()
        status = self.status_var.get()
        description = self.description_text.get("1.0", tk.END).strip()
        poll_string = self.poll_entry.get()

        if not task_name or not artist or not self.project_dir:
            self.message_label.config(text="All fields are required, also a Project Directory.")
            return

        file_name = f"task for {task_name}.txt"
        task_path = os.path.join(self.project_dir, file_name)

        try:
            with open(task_path, "w") as f:
                f.write(f"task name: {task_name}\n")
                f.write(f"assigned artist: {artist}\n")
                f.write(f"due date: {due_date}\n")
                f.write(f"status: {status}\n")
                f.write(f"description: {description}\n")
                f.write(f"polls: {poll_string}\n")
                f.write(f"assets: {self.assets_var.get()}\n")
                f.write(f"characters: {self.characters_var.get()}\n")
                f.write(f"locations: {self.locations_var.get()}\n")
                self.message_label.config(text=f"Task assigned successfully to {task_path}!")

        except Exception as e:
            messagebox.showerror("Error", f"Error assigning task: {e}")

        self.load_tasks()
        self.clear_fields()

    def load_tasks(self):
        self.task_listbox.delete(0, tk.END)
        if not self.project_dir:
            return

        for file_name in os.listdir(self.project_dir):
            if file_name.startswith("task for ") and file_name.endswith(".txt"):
                try:
                    task_path = os.path.join(self.project_dir, file_name)
                    with open(task_path, "r") as f:
                        lines = f.readlines()
                        task = {}
                        for line in lines:
                            if ":" in line:
                                key, value = line.strip().split(":", 1)
                                task[key.strip()] = value.strip()
                        text = f"{task['task name']} - {task['assigned artist']} - {task['due date']}"
                        self.task_listbox.insert(tk.END, text)
                except Exception as e:
                    messagebox.showerror("Error", f"Error loading task from {file_name}: {e}")

    def load_selected_task(self, event=None):
        selection = self.task_listbox.curselection()
        if selection:
            index = selection[0]
            text = self.task_listbox.get(index)
            task_name = text.split(" - ")[0]

            file_name = f"task for {task_name}.txt"
            task_path = os.path.join(self.project_dir, file_name)

            try:
                with open(task_path, "r") as f:
                    lines = f.readlines()
                task = {}
                for line in lines:
                    if ":" in line:
                        key, value = line.strip().split(":", 1)
                        task[key.strip()] = value.strip()
                self.task_name_entry.delete(0, tk.END)
                self.task_name_entry.insert(0, task["task name"])
                self.artist_entry.delete(0, tk.END)
                self.artist_entry.insert(0, task["assigned artist"])
                due_date = datetime.datetime.strptime(task["due date"], "%Y-%m-%d").date()
                self.due_date_entry.set_date(due_date)
                self.status_var.set(task["status"])
                self.description_text.delete("1.0", tk.END)
                self.description_text.insert("1.0", task["description"])
                self.poll_entry.delete(0, tk.END)
                self.poll_entry.insert(0, task["polls"])

                # Load checkbox states
                self.assets_var.set(task.get("assets") == "True")
                self.characters_var.set(task.get("characters") == "True")
                self.locations_var.set(task.get("locations") == "True")

            except Exception as e:
                messagebox.showerror("Error", f"Error loading selected task: {e}")

    def edit_selected_task(self):
        """Edits the selected task by rewriting the file."""
        selection = self.task_listbox.curselection()
        if selection:
            if not self.task_name_entry.get() or not self.artist_entry.get():
                messagebox.showerror("Error", "Task name and Artist are required.")
                return

            index = selection[0]
            # New parameters for the selected directory
            task_name = self.task_listbox.get(index).split(" - ")[0]  # Task Name
            file_name = f"task for {task_name}.txt"
            task_path = os.path.join(self.project_dir, file_name)  # Full task for it to

            # Get a new data
            new_task_name = self.task_name_entry.get()  # new parameter for a folder
            new_artist = self.artist_entry.get()
            new_due_date = self.due_date_entry.get_date()  # new date
            new_status = self.status_var.get()  # check status
            new_description = self.description_text.get("1.0", tk.END).strip()  # rewrite data
            new_polls = self.poll_entry.get().strip()  # rewrite that new data or leave as is

            try:  # Rewrite
                # open data for text file
                with open(task_path, "w") as f:
                    f.write(f"task name: {new_task_name}\n")
                    f.write(f"assigned artist: {new_artist}\n")
                    f.write(f"due date: {new_due_date}\n")
                    f.write(f"status: {new_status}\n")  # rewrite all clear parameters
                    f.write(f"description: {new_description}\n")
                    f.write(f"polls: {new_polls}\n")
                    f.write(f"assets: {self.assets_var.get()}\n")  # to rewrite asset, - clear and good
                    f.write(f"characters: {self.characters_var.get()}\n")
                    f.write(f"locations: {self.locations_var.get()}\n")
                self.message_label.config(text=f"Task '{task_name}' edited successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Can't find dir or permission denied {e}")

            self.load_tasks()

        else:
            self.message_label.config(text="No task selected.")

    def delete_selected_task(self):
        selection = self.task_listbox.curselection()
        if selection:
            index = selection[0]
            text = self.task_listbox.get(index)
            task_name = text.split(" - ")[0]

            file_name = f"task for {task_name}.txt"
            task_path = os.path.join(self.project_dir, file_name)

            try:
                os.remove(task_path)
                self.message_label.config(text=f"Task '{task_name}' deleted successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Error deleting task: {e}")

            self.load_tasks()

        else:
            self.message_label.config(text="No task selected.")

    def save_tasks(self):
        self.load_tasks()
        self.message_label.config(text="Tasks saved successfully!")

    def clear_fields(self):
        self.task_name_entry.delete(0, tk.END)
        self.artist_entry.delete(0, tk.END)
        self.due_date_entry.set_date(datetime.date.today())
        self.status_var.set(self.status_choices[0])
        self.description_text.delete("1.0", tk.END)
        self.poll_entry.delete(0, tk.END)
        self.assets_var.set(False)
        self.characters_var.set(False)
        self.locations_var.set(False)


def integrate_task_assigner(main_frame, project_dir=None):
    task_assigner = TaskAssigner(main_frame, project_dir)
    task_assigner.pack(expand=True, fill="both")


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Task Assigner")
    root.geometry("650x790")
    task_assigner = TaskAssigner(root)
    task_assigner.pack(expand=True, fill="both")
    root.mainloop()
