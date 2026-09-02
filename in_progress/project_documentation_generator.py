import json
import os
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import filedialog, messagebox


class DocumentationGenerator(ttk.Frame):
    def __init__(self, parent, metadata_dir=None):
        super().__init__(parent)
        self.parent = parent
        self.metadata_dir = metadata_dir
        self.load_style()
        self.init_ui()

    def load_style(self):
        # Load the style
        style = ttk.Style()
        style.theme_use('clam')
        # Font and Colors
        font_name = "Bahnschrift"
        bg_color = '#2e2e2e'
        fg_color = 'white'
        entry_bg_color = "#4a4a4a"  # Entry background color
        button_bg_color = '#4a4a4a'
        button_active_bg_color = '#606060'
        text_color = '#d3d3d3'
        arrow_color = 'white'

        # Configure Styles
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
        self.metadata_dir_label = ttk.Label(self, text="Metadata Directory:")
        self.metadata_dir_label.grid(row=0, column=0, sticky="w", padx=5, pady=5)

        self.metadata_dir_var = tk.StringVar(value=self.metadata_dir if self.metadata_dir else "")
        self.metadata_dir_entry = ttk.Entry(self, textvariable=self.metadata_dir_var, width=50, state="disabled")
        self.metadata_dir_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)

        self.browse_button = ttk.Button(self, text="Browse", command=self.browse_directory)
        self.browse_button.grid(row=0, column=2, sticky="w", padx=5, pady=5)

        # --- Project Status ---
        self.status_label = ttk.Label(self, text="Project Status:")
        self.status_label.grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.status_choices = ["In Development", "Pre-Production", "Production", "Ready"]
        self.status_var = tk.StringVar(value=self.status_choices[0])
        self.status_combobox = ttk.Combobox(self, textvariable=self.status_var, values=self.status_choices,
                                            state="readonly", width=20)
        self.status_combobox.grid(row=1, column=1, sticky="w", padx=5, pady=5)
        self.status_combobox.bind("<<ComboboxSelected>>", self.update_markdown)

        # --- License ---
        self.license_label = ttk.Label(self, text="License:")
        self.license_label.grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.license_choices = ["MIT", "GNU GPL v3", "Apache License 2.0", "Other"]
        self.license_var = tk.StringVar(value=self.license_choices[0])
        self.license_combobox = ttk.Combobox(self, textvariable=self.license_var, values=self.license_choices,
                                             state="readonly", width=20)
        self.license_combobox.grid(row=2, column=1, sticky="w", padx=5, pady=5)
        self.license_combobox.bind("<<ComboboxSelected>>", self.update_markdown)

        # --- Synopsis ---
        self.synopsis_label = ttk.Label(self, text="Synopsis:")
        self.synopsis_label.grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.synopsis_text = tk.Text(self, wrap=tk.WORD, width=50, height=3)
        self.synopsis_text.grid(row=3, column=1, columnspan=2, sticky="ew", padx=5, pady=5)
        self.synopsis_text.bind("<KeyRelease>", self.update_markdown)

        # --- Project Code ---
        self.project_code_label = ttk.Label(self, text="Project Code:")
        self.project_code_label.grid(row=4, column=0, sticky="w", padx=5, pady=5)
        self.project_code_entry = ttk.Entry(self, width=50)
        self.project_code_entry.grid(row=4, column=1, columnspan=2, sticky="ew", padx=5, pady=5)
        self.project_code_entry.bind("<KeyRelease>", self.update_markdown)

        # --- Client ---
        self.client_label = ttk.Label(self, text="Client:")
        self.client_label.grid(row=5, column=0, sticky="w", padx=5, pady=5)
        self.client_entry = ttk.Entry(self, width=50)
        self.client_entry.grid(row=5, column=1, columnspan=2, sticky="ew", padx=5, pady=5)
        self.client_entry.bind("<KeyRelease>", self.update_markdown)

        # --- Pipeline Version ---
        self.pipeline_version_label = ttk.Label(self, text="Pipeline Version:")
        self.pipeline_version_label.grid(row=6, column=0, sticky="w", padx=5, pady=5)
        self.pipeline_version_entry = ttk.Entry(self, width=50)
        self.pipeline_version_entry.grid(row=6, column=1, columnspan=2, sticky="ew", padx=5, pady=5)
        self.pipeline_version_entry.bind("<KeyRelease>", self.update_markdown)

        # --- Lead Artist ---
        self.lead_artist_label = ttk.Label(self, text="Lead Artist:")
        self.lead_artist_label.grid(row=7, column=0, sticky="w", padx=5, pady=5)
        self.lead_artist_entry = ttk.Entry(self, width=50)
        self.lead_artist_entry.grid(row=7, column=1, columnspan=2, sticky="ew", padx=5, pady=5)
        self.lead_artist_entry.bind("<KeyRelease>", self.update_markdown)

        # --- Key Themes ---
        self.key_themes_label = ttk.Label(self, text="Key Themes (comma-separated):")
        self.key_themes_label.grid(row=8, column=0, sticky="w", padx=5, pady=5)
        self.key_themes_entry = ttk.Entry(self, width=50)
        self.key_themes_entry.grid(row=8, column=1, columnspan=2, sticky="ew", padx=5, pady=5)
        self.key_themes_entry.bind("<KeyRelease>", self.update_markdown)

        # --- Contact Info ---
        self.contact_label = ttk.Label(self, text="Contact Info:")
        self.contact_label.grid(row=9, column=0, sticky="w", padx=5, pady=5)
        self.contact_var = tk.StringVar()
        self.contact_entry = ttk.Entry(self, textvariable=self.contact_var, width=50)
        self.contact_entry.grid(row=9, column=1, columnspan=2, sticky="ew", padx=5, pady=5)
        self.contact_var.trace_add("write", self.update_markdown)

        # --- Crew ---
        self.crew_label = ttk.Label(self, text="Crew:")
        self.crew_label.grid(row=10, column=0, sticky="w", padx=5, pady=5)
        self.crew_text = tk.Text(self, wrap=tk.WORD, width=50, height=4)
        self.crew_text.grid(row=10, column=1, columnspan=2, sticky="ew", padx=5, pady=5)
        self.crew_text.bind("<KeyRelease>", self.update_markdown)

        # --- Acknowledgements ---
        self.acknowledgements_label = ttk.Label(self, text="Acknowledgements:")
        self.acknowledgements_label.grid(row=11, column=0, sticky="w", padx=5, pady=5)
        self.acknowledgements_text = tk.Text(self, wrap=tk.WORD, width=50, height=4)
        self.acknowledgements_text.grid(row=11, column=1, columnspan=2, sticky="ew", padx=5, pady=5)
        self.acknowledgements_text.bind("<KeyRelease>", self.update_markdown)

        # --- Text Editor ---
        self.text_editor = tk.Text(self, wrap=tk.WORD, width=80, height=15)
        self.text_editor.grid(row=12, column=0, columnspan=3, sticky="nsew", padx=5, pady=5)

        self.generate_button = ttk.Button(self, text="Generate/Save", command=self.generate_and_save)
        self.generate_button.grid(row=13, column=1, sticky="e", padx=5, pady=10)

        # row and column weights
        self.columnconfigure(1, weight=1)
        self.rowconfigure(12, weight=1)

        if self.metadata_dir:
            self.load_metadata_and_populate()

    def browse_directory(self):
        directory = filedialog.askdirectory(title="Select Project Metadata Directory")
        if directory:
            self.metadata_dir = directory
            self.metadata_dir_var.set(directory)
            self.load_metadata_and_populate()

    def load_metadata_and_populate(self):
        try:
            metadata = self.load_metadata()
            if metadata:
                self.populate_gui_elements(metadata)
                initial_text = self.create_initial_markdown(metadata)
                self.text_editor.delete("1.0", tk.END)
                self.text_editor.insert("1.0", initial_text)
        except Exception as e:
            messagebox.showerror("Error", f"Error loading meta{e}")

    def load_metadata(self):
        if not self.metadata_dir:
            messagebox.showerror("Error", "No metadata directory selected.")
            return None

        metadata_file_path = os.path.join(self.metadata_dir, "project_metadata.json")
        try:
            with open(metadata_file_path, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            messagebox.showerror("Error", f"Metadata file not found at {metadata_file_path}")
            return None
        except json.JSONDecodeError:
            messagebox.showerror("Error", "Error decoding JSON. The metadata file may be corrupted.")
            return None

    def populate_gui_elements(self, metadata):
        """Populates GUI elements with values from metadata."""
        self.status_var.set(metadata.get("project_status", self.status_choices[0]))
        self.license_var.set(metadata.get("license", self.license_choices[0]))
        self.synopsis_text.delete("1.0", tk.END)
        self.synopsis_text.insert("1.0", metadata.get("project_description", ""))
        self.project_code_entry.delete(0, tk.END)  # Clear before inserting
        self.project_code_entry.insert(0, metadata.get("project_code", ""))
        self.client_entry.delete(0, tk.END)
        self.client_entry.insert(0, metadata.get("client", ""))
        self.pipeline_version_entry.delete(0, tk.END)
        self.pipeline_version_entry.insert(0, metadata.get("pipeline_version", ""))
        self.lead_artist_entry.delete(0, tk.END)
        self.lead_artist_entry.insert(0, metadata.get("lead_artist", ""))
        self.key_themes_entry.delete(0, tk.END)
        self.key_themes_entry.insert(0, metadata.get("key_themes", ""))
        self.contact_var.set(metadata.get("contact", ""))
        self.crew_text.delete("1.0", tk.END)
        self.crew_text.insert("1.0", metadata.get("crew", ""))
        self.acknowledgements_text.delete("1.0", tk.END)
        self.acknowledgements_text.insert("1.0", metadata.get("acknowledgements", ""))

    def create_initial_markdown(self, metadata):
        project_name = metadata.get("project_name", "[Project Name Placeholder]")

        # Get values from the GUI
        project_status = self.status_var.get()
        license_badge = self.license_var.get()
        synopsis = self.synopsis_text.get("1.0", tk.END).strip()
        project_code = self.project_code_entry.get()
        client = self.client_entry.get()
        pipeline_version = self.pipeline_version_entry.get()
        lead_artist = self.lead_artist_entry.get()
        key_themes_str = self.key_themes_entry.get()
        contact_info = self.contact_var.get()
        crew_members_text = self.crew_text.get("1.0", tk.END).strip()
        acknowledgements = self.acknowledgements_text.get("1.0", tk.END).strip()

        # Format Key Themes (comma-separated)
        key_themes = [theme.strip() for theme in key_themes_str.split(",")]
        formatted_themes = "\n".join([f"* {theme}" for theme in key_themes])

        # Format Crew
        crew_members = [member.strip() for member in crew_members_text.split("\n")]
        formatted_crew = "\n".join([f"* **{member}**" for member in crew_members])

        markdown = f"""# {project_name}

[![Project Status](https://img.shields.io/badge/status-{project_status.replace(" ", "%20")}-yellow)](https://shields.io/)
[![License](https://img.shields.io/badge/license-{license_badge.replace(" ", "%20")}-blue.svg)](LICENSE)

## Synopsis

{synopsis}

## Project Code:

{project_code}

## Client:

{client}

## Pipeline Version:

{pipeline_version}

## Lead Artist:

{lead_artist}

## Key Themes

{formatted_themes}

## Crew

{formatted_crew}

## Contact

{contact_info}

## Acknowledgements

{acknowledgements}
"""
        return markdown

    def update_markdown(self, *args):
        """Updates the Markdown content in the text editor."""
        try:
            # Get values from the GUI
            metadata = self.load_metadata()  # Load metadata
            project_name = metadata.get("project_name", "[Project Name Placeholder]")  # Get project name
            project_status = self.status_var.get()
            license_badge = self.license_var.get()
            synopsis = self.synopsis_text.get("1.0", tk.END).strip()
            project_code = self.project_code_entry.get()
            client = self.client_entry.get()
            pipeline_version = self.pipeline_version_entry.get()
            lead_artist = self.lead_artist_entry.get()
            key_themes_str = self.key_themes_entry.get()
            contact_info = self.contact_var.get()
            crew_members_text = self.crew_text.get("1.0", tk.END).strip()
            acknowledgements = self.acknowledgements_text.get("1.0", tk.END).strip()

            # Format Key Themes (comma-separated)
            key_themes = [theme.strip() for theme in key_themes_str.split(",")]
            formatted_themes = "\n".join([f"* {theme}" for theme in key_themes])

            # Format Crew
            crew_members = [member.strip() for member in crew_members_text.split("\n")]
            formatted_crew = "\n".join([f"* **{member}**" for member in crew_members])

            markdown = f"""# {project_name}

[![Project Status](https://img.shields.io/badge/status-{project_status.replace(" ", "%20")}-yellow)](https://shields.io/)
[![License](https://img.shields.io/badge/license-{license_badge.replace(" ", "%20")}-blue.svg)](LICENSE)

## Synopsis

{synopsis}

## Project Code:

{project_code}

## Client:

{client}

## Pipeline Version:

{pipeline_version}

## Lead Artist:

{lead_artist}

## Key Themes

{formatted_themes}

## Crew

{formatted_crew}

## Contact

{contact_info}

## Acknowledgements

{acknowledgements}
"""
            self.text_editor.delete("1.0", tk.END)
            self.text_editor.insert("1.0", markdown)
        except Exception as e:
            messagebox.showerror("Error", f"Error updating Markdown: {e}")

    def generate_and_save(self):
        if not self.metadata_dir:
            messagebox.showerror("Error", "No metadata directory selected.")
            return

        output_file_path = os.path.join(self.metadata_dir, "project_documentation.md")
        documentation = self.text_editor.get("1.0", tk.END)

        try:
            with open(output_file_path, "w") as f:
                f.write(documentation)
            messagebox.showinfo("Success", f"Project documentation saved successfully at {output_file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Error writing documentation file: {e}")


def integrate_documentation_generator(main_frame):
    documentation_generator = DocumentationGenerator(main_frame,
                                                     metadata_dir=None)  # Pass metadata_dir as None
    documentation_generator.pack(expand=True, fill="both")


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Project Documentation Generator")
    root.geometry("1000x700")

    style = ttk.Style()
    style.theme_use('clam')

    main_frame = ttk.Frame(root, padding=20)
    main_frame.pack(expand=True, fill="both")


    def generate_documentation_callback():  # Added code
        """Call generate_documentation with a directory selection."""
        # Removed call from inside the call function
        metadata_dir = filedialog.askdirectory(title="Select Project Metadata Directory")
        if metadata_dir:
            integrate_documentation_generator(main_frame)


    generate_documentation_callback()

    root.mainloop()
