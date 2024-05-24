import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import datetime
from tkinterdnd2 import DND_FILES, TkinterDnD
import json
import os
import utils
import sys
import shutil

# pyinstaller -w -F --add-data "C:\Users\12053\anaconda3\envs\test\lib\site-packages\tkinterdnd2;tkinterdnd2" --add-data "config.json;." gui_test2.py

def get_config_path():
    # Determine if the script is running in a PyInstaller bundle
    if hasattr(sys, '_MEIPASS'):
        # Running in a PyInstaller bundle
        base_path = sys._MEIPASS
    else:
        # Running in a normal Python environment
        base_path = os.path.dirname(__file__)

    # Define the path to the original config file
    original_config_path = os.path.join(base_path, 'config.json')

    # Define the path to the user's local config file
    local_app_data = os.getenv('LOCALAPPDATA', os.path.expanduser('~'))
    user_config_dir = os.path.join(local_app_data, 'BlogHelper')
    os.makedirs(user_config_dir, exist_ok=True)
    user_config_path = os.path.join(user_config_dir, 'config.json')

    # If the user's config file does not exist, copy the original config file to the user's directory
    if not os.path.exists(user_config_path):
        shutil.copyfile(original_config_path, user_config_path)

    return user_config_path

CONFIG_FILE = get_config_path()
LOG_INFO = '''
---
title: {}
date: {}
tags: {}
categories: 
- {}
---

'''
class SimpleExeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("blog helper")
        self.root.geometry("800x500")
        # self.root.resizable(False, False)
        self.config = self.load_config()
        # Variables to store paths
        self.repo_path_var = tk.StringVar(value=self.config.get('repo_path', ''))
        self.output_path = ''
        self.output_path_var = tk.StringVar(value=self.config.get('output_path', ''))
        self.uploaded_file_var = tk.StringVar()
        self.current_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.source_file_path = ''
        self.source_file_content = ''
        self.tags_var = tk.StringVar(value='')
        self.categories_var = tk.StringVar(value='')
        self.title = '<title>'
        self.tag = '<tag>'
        self.categories = '<tag>'
        self.add_file_path = ''
        self.setup_ui()

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as file:
                return json.load(file)
        return {}

    def save_config(self, config):
        with open(CONFIG_FILE, 'w') as file:
            json.dump(config, file, indent=4)

    def open_repo_path(self):
        path = filedialog.askdirectory()
        if path:
            self.repo_path_var.set(path)
            self.config['repo_path'] = path
            self.save_config(self.config)

    def open_output_path(self):
        path = filedialog.askdirectory()
        if path:
            self.output_path_var.set(path)
            self.config['output_path'] = path
            self.save_config(self.config)

    def reset_time(self):
        self.current_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if self.current_date:
            self.date_var.set(self.current_date)

    def pull(self):
        with utils.cd(self.repo_path_var.get()):
            res = utils.git_command('git pull'.split())
            if not res[0]:
                self.append_log(f"Error running command: {res[1]}")
                return
            else:
                self.append_log(f'{res[1]}, {res[2]}, {res[3]}')

    def push(self):
        with utils.cd(self.repo_path_var.get()):
            res = utils.git_command('git push'.split())
            if not res[0]:
                self.append_log(f"Error running command: {res[1]}")
                return
            else:
                self.append_log(f'{res[1]}, {res[2]}, {res[3]}')

    def add_commit(self):
        with utils.cd(self.repo_path_var.get()):
            res = utils.git_command(f'git add {self.add_file_path}'.split())
            if not res[0]:
                self.append_log(f"Error running command: {res[1]}")
                return
            else:
                self.append_log(f'{res[1]}, {res[2]}, {res[3]}')
            res = utils.git_command(f'git commit -m'.split()+[f"add: {self.title}"])
            if not res[0]:
                self.append_log(f"Error running command: {res[1]}")
                return
            else:
                self.append_log(f'{res[1]}, {res[2]}, {res[3]}')

    def save_content(self):
        """Save the content of the large_text to self.file_content."""
        self.file_content = self.large_text.get(1.0, tk.END).strip()
        """Save self.file_content to a markdown file."""
        current_date = datetime.datetime.now().strftime("%Y%m%d%H%M")
        file_path = os.path.join(self.output_path_var.get(), f'{self.title}_{current_date}.md')
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(self.file_content)
                self.append_log(f"File saved successfully at\n {file_path}")
                self.add_file_path = file_path
            except Exception as e:
                self.append_log(f"Failed to save the file. Error: {e}")

    def generate_or_save(self):
        """Handle the button action to generate or save content."""
        if self.button_text.get() == "Generate" or self.button_text.get() == 'ReGenerate':
            # Perform generate action
            self.file_content = LOG_INFO.format(self.title_var.get(), self.current_date, self.tags_var.get(), self.categories_var.get()) + self.source_file_content
            self.large_text.config(state=tk.NORMAL)
            self.large_text.delete(1.0, tk.END)
            self.large_text.insert(tk.END, self.file_content)
            self.large_text.config(state=tk.NORMAL)  # Enable editing
            self.button_text.set("Save Content")
            self.append_log("Generate action completed.")
        else:
            # Perform save content action
            self.save_content()
            self.button_text.set("ReGenerate")
            self.append_log("Save action completed.")

    def on_drop(self, event):
        """Handle file drop events."""
        file_path = event.data
        if file_path and file_path.endswith('.md'):
            self.source_file_path = file_path
            self.uploaded_file_var.set(file_path)

            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    self.source_file_content = file.read()

                self.large_text.config(state=tk.NORMAL)
                self.large_text.delete(1.0, tk.END)
                self.large_text.insert(tk.END, self.source_file_content)
                self.large_text.config(state=tk.NORMAL)  # Enable editing

                self.path_text.config(state=tk.NORMAL)
                self.path_text.delete(1.0, tk.END)
                self.path_text.insert(tk.END, file_path)
                self.path_text.config(state=tk.DISABLED)
                self.scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

                self.file_content = self.source_file_content
                self.append_log(f"File '{file_path}' uploaded and content displayed successfully!")
            except Exception as e:
                self.append_log(f"Failed to read the file '{file_path}'. Error: {e}")
        else:
            self.append_log("Only markdown (.md) files are supported.")

    def setup_ui(self):
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)

        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=1)
        main_frame.grid_rowconfigure(0, weight=1)

        left_frame = tk.Frame(main_frame)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.setup_left_frame(left_frame)

        right_frame = tk.Frame(main_frame, bg="lightgrey", relief=tk.RAISED, bd=2)
        right_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.setup_right_frame(right_frame)

    def setup_left_frame(self, left_frame):
        left_frame.grid_rowconfigure(6, weight=1)  # Allow row 5 to expand

        self.setup_repo_path_section(left_frame)
        self.setup_date_section(left_frame)
        self.setup_output_path_section(left_frame)
        self.setup_button_section(left_frame)
        self.setup_title(left_frame)
        self.setup_tags_and_categories_section(left_frame)

        self.setup_log_section(left_frame)

    def setup_repo_path_section(self, frame):
        repo_path_frame = tk.Frame(frame)
        repo_path_frame.grid(row=0, column=0, pady=5, sticky="ew")

        repo_path_label = tk.Label(repo_path_frame, text="Repo Path:", width=12)
        repo_path_label.pack(side=tk.LEFT)

        repo_path_entry = tk.Entry(repo_path_frame, textvariable=self.repo_path_var, width=20)
        repo_path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        repo_path_button = tk.Button(repo_path_frame, text="Open", command=self.open_repo_path, width=5)
        repo_path_button.pack(side=tk.LEFT)

    def setup_date_section(self, frame):
        date_frame = tk.Frame(frame)
        date_frame.grid(row=1, column=0, pady=5, sticky="ew")

        date_label = tk.Label(date_frame, text="Set Date:", width=12)
        date_label.pack(side=tk.LEFT)

        self.date_var = tk.StringVar(value=self.current_date)
        date_entry = tk.Entry(date_frame, textvariable=self.date_var, width=30)
        date_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        repo_path_button = tk.Button(date_frame, text="Reset", command=self.reset_time, width=5)
        repo_path_button.pack(side=tk.LEFT)

    def setup_output_path_section(self, frame):
        output_path_frame = tk.Frame(frame)
        output_path_frame.grid(row=5, column=0, pady=5, sticky="ew")

        output_path_label = tk.Label(output_path_frame, text="Output Path:", width=12)
        output_path_label.pack(side=tk.LEFT)

        output_path_entry = tk.Entry(output_path_frame, textvariable=self.output_path_var, width=20)
        output_path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        output_path_button = tk.Button(output_path_frame, text="Open", command=self.open_output_path, width=5)
        output_path_button.pack(side=tk.LEFT)

    def setup_button_section(self, frame):
        button_frame = tk.Frame(frame)
        button_frame.grid(row=2, column=0, pady=(20, 0), sticky="ew")

        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)
        button_frame.grid_columnconfigure(2, weight=1)

        pull_button = tk.Button(button_frame, text="Pull", command=self.pull, width=15)
        pull_button.pack(side=tk.LEFT, padx=4)

        commit_button = tk.Button(button_frame, text="Add", command=self.add_commit, width=15)
        commit_button.pack(side=tk.LEFT, padx=4)

        upload_button = tk.Button(button_frame, text="Upload", command=self.push, width=15)
        upload_button.pack(side=tk.LEFT, padx=4)

    def setup_title(self, frame):
        title_frame = tk.Frame(frame)
        title_frame.grid(row=3, column=0, pady=5, sticky="ew")

        title_label = tk.Label(title_frame, text="Title:")
        title_label.pack(side=tk.LEFT, padx=5)

        self.title_var = tk.StringVar(value="<Title Here>")
        title_entry = tk.Entry(title_frame, textvariable=self.title_var)
        title_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.title_var.trace_add("write", self.update_title)

    def update_title(self, *args):
        self.title = self.title_var.get()

    def setup_tags_and_categories_section(self, frame):
        tags_categories_frame = tk.Frame(frame)
        tags_categories_frame.grid(row=4, column=0, pady=5, sticky="ew")

        tags_label = tk.Label(tags_categories_frame, text="Tags:", width=5)
        tags_label.pack(side=tk.LEFT)

        self.tags_combobox = ttk.Combobox(tags_categories_frame, textvariable=self.tags_var, values=self.config.get('tags', []), width=5)
        self.tags_combobox.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.tags_combobox.bind('<<ComboboxSelected>>', self.on_tags_selected)
        self.tags_combobox.bind('<Return>', self.on_tags_entered)

        categories_label = tk.Label(tags_categories_frame, text="Categories:", width=10)
        categories_label.pack(side=tk.LEFT)

        self.categories_combobox = ttk.Combobox(tags_categories_frame, textvariable=self.categories_var, values=self.config.get('categories', []), width=5)
        self.categories_combobox.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.categories_combobox.bind('<<ComboboxSelected>>', self.on_categories_selected)
        self.categories_combobox.bind('<Return>', self.on_categories_entered)

    def on_tags_selected(self, event):
        selected_tag = self.tags_var.get()
        self.tag = selected_tag
        if selected_tag not in self.config.get('tags', []):
            self.config.setdefault('tags', []).append(selected_tag)
            self.save_config(self.config)
        self.output_path = os.path.join(self.repo_path_var.get(), 'source', '_posts', f'{self.tag}')
        if not os.path.exists(self.output_path):
            os.makedirs(self.output_path)
        self.output_path_var.set(self.output_path)
        if self.categories_var.get() == '':
            self.categories_var.set(self.tag)

    def on_tags_entered(self, event):
        entered_tag = self.tags_var.get()
        if entered_tag not in self.config.get('tags', []):
            self.config.setdefault('tags', []).append(entered_tag)
            self.save_config(self.config)
        self.tags_combobox['values'] = self.config['tags']

    def on_categories_selected(self, event):
        selected_category = self.categories_var.get()
        self.categories = selected_category
        if selected_category not in self.config.get('categories', []):
            self.config.setdefault('categories', []).append(selected_category)
            self.save_config(self.config)

    def on_categories_entered(self, event):
        entered_category = self.categories_var.get()
        if entered_category not in self.config.get('categories', []):
            self.config.setdefault('categories', []).append(entered_category)
            self.save_config(self.config)
        self.categories_combobox['values'] = self.config['categories']

    def setup_log_section(self, frame):
        log_frame = tk.Frame(frame)
        log_frame.grid(row=6, column=0, sticky="nsew", pady=10)

        self.log_text = tk.Text(log_frame, wrap=tk.WORD, width=30)
        self.log_text.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)

        self.log_scrollbar = tk.Scrollbar(log_frame, command=self.log_text.yview)
        self.log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=self.log_scrollbar.set)

    def append_log(self, message):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def setup_right_frame(self, right_frame):
        """Set up the right frame UI components."""
        self.setup_path_frame(right_frame)
        self.setup_large_text_section(right_frame)
        right_frame.drop_target_register(DND_FILES)
        right_frame.dnd_bind('<<Drop>>', self.on_drop)

    def on_text_modified(self, event):
        """Save the modified content to self.file_content."""
        self.file_content = self.large_text.get(1.0, tk.END).strip()

    def setup_large_text_section(self, frame):
        """Set up a large text display box with a scrollbar in the right frame."""
        large_text_frame = tk.Frame(frame)
        large_text_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.large_text = tk.Text(large_text_frame, wrap=tk.WORD, width=50)
        self.large_text.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)

        self.large_text_scrollbar = tk.Scrollbar(large_text_frame, command=self.large_text.yview)
        self.large_text_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.large_text.config(yscrollcommand=self.large_text_scrollbar.set)

        # Bind the <KeyRelease> event to track modifications
        self.large_text.bind('<KeyRelease>', self.on_text_modified)

        # Add a button below the text widget
        button_frame = tk.Frame(frame)
        button_frame.pack(fill=tk.X, padx=5, pady=5)

        self.button_text = tk.StringVar(value="Generate")
        self.action_button = tk.Button(button_frame, textvariable=self.button_text, command=self.generate_or_save)
        self.action_button.pack(side=tk.BOTTOM, fill=tk.X)

    def setup_path_frame(self, frame):
        path_frame = tk.Frame(frame)
        path_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)

        self.scrollbar = tk.Scrollbar(path_frame, orient=tk.HORIZONTAL)
        self.path_text = tk.Text(path_frame, height=1, wrap=tk.NONE, xscrollcommand=self.scrollbar.set, width=40)
        self.path_text.pack(side=tk.BOTTOM, fill=tk.X)
        self.path_text.config(state=tk.DISABLED)
        self.scrollbar.config(command=self.path_text.xview)
        self.scrollbar.pack_forget()


if __name__ == "__main__":
    root = TkinterDnD.Tk()
    app = SimpleExeApp(root)
    root.mainloop()


