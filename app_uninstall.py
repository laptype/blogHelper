import os
import shutil
import tkinter as tk
from tkinter import messagebox


def get_config_path():
    local_app_data = os.getenv('LOCALAPPDATA', os.path.expanduser('~'))
    user_config_dir = os.path.join(local_app_data, 'BlogHelper')
    user_config_path = os.path.join(user_config_dir, 'config.json')
    return user_config_dir, user_config_path


def uninstall():
    user_config_dir, user_config_path = get_config_path()

    # Delete the config file if it exists
    if os.path.exists(user_config_path):
        try:
            os.remove(user_config_path)
            print(f"Deleted config file: {user_config_path}")
        except Exception as e:
            print(f"Error deleting config file: {e}")

    # Delete the user config directory if it is empty
    if os.path.exists(user_config_dir):
        try:
            shutil.rmtree(user_config_dir)
            print(f"Deleted config directory: {user_config_dir}")
        except Exception as e:
            print(f"Error deleting config directory: {e}")

    # Show a message box indicating that the uninstall is complete
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    messagebox.showinfo("Uninstall Complete", "The application has been successfully uninstalled.")

    print("Uninstall complete.")


if __name__ == "__main__":
    uninstall()
