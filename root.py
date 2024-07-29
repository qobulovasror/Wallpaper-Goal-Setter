import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageDraw, ImageFont
import sqlite3
import ctypes
import os
import shutil
import tempfile
import winreg

from config import root_folder
from config import registry_key
from config import registry_value


class SetWallaper:
    def __init__(self, root) -> None:
        self.root = root
        self.root.title("Wallpaper Goal Setter")
        self.cur = None
        self.initial_folder_and_DB()
        self.createDBTables()
        self.backup_original_wallpaper()
        self.create_widgets()
        self.getOldGoals()

    def initial_folder_and_DB(self):
        # create folder
        self.backup_dir = os.path.join(os.path.expanduser("~"), root_folder)
        os.makedirs(self.backup_dir, exist_ok=True)

        self.currentlyImg = os.path.join(
            os.path.expanduser("~"), root_folder + "\\currentlyImg"
        )
        os.makedirs(self.currentlyImg, exist_ok=True)

        # create database
        self.con = sqlite3.connect(self.backup_dir + "\\goals.db")
        self.cur = self.con.cursor()

    def createDBTables(self):
        self.cur.execute(
            "CREATE TABLE IF NOT EXISTS goals(id INTEGER  PRIMARY KEY AUTOINCREMENT, title TEXT, checked INTEGER)"
        )
        self.cur.execute(
            "CREATE TABLE IF NOT EXISTS isCreated(name TEXT, status TEXT)"
        )

    def backup_original_wallpaper(self):
        res = self.cur.execute("SELECT status FROM isCreated WHERE name='backup'")
        statusBackUp = res.fetchone()
        if statusBackUp is None or statusBackUp[0] == 'NULL':
            current_wallpaper = self.get_current_wallpaper()
            if current_wallpaper and os.path.isfile(current_wallpaper):
                backup_path = os.path.join(
                    self.backup_dir, os.path.basename(current_wallpaper)
                )
                shutil.copy2(current_wallpaper, backup_path)
                self.backup_path = backup_path
                self.cur.execute(f"INSERT INTO isCreated VALUES ('backup', '{backup_path}')")
                self.con.commit()
        else:
            self.backup_path = statusBackUp[0]

    def create_widgets(self):
        # app title
        app_title = tk.Label(
            self.root, text="Set a goal for the wallaper:", font=("Arial", 15)
        )
        app_title.grid(row=0, column=0, pady=5, sticky="n")

        frame = tk.Frame(self.root)
        frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        # Listbox to display tasks
        self.task_listbox = tk.Listbox(
            frame, selectmode=tk.SINGLE, height=7, width=50, activestyle="none"
        )
        self.task_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Scrollbar
        scrollbar = tk.Scrollbar(
            frame, orient=tk.VERTICAL, command=self.task_listbox.yview
        )
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Attach scrollbar to listbox
        self.task_listbox.config(yscrollcommand=scrollbar.set)

        # Entry widget to enter new tasks
        self.task_entry = tk.Entry(self.root, width=30)
        self.task_entry.grid(row=2, column=0, padx=10, pady=5, sticky="W")

        # Buttons
        add_button = tk.Button(
            self.root, text="Add New Goal", command=self.add_task, width=15
        )
        add_button.grid(row=2, column=0, padx=10, pady=5, sticky="E")

        remove_button = tk.Button(
            self.root, text="Remove Task", command=self.remove_task
        )
        remove_button.grid(row=3, column=0, padx=10, pady=5, sticky="e")

        complete_button = tk.Button(
            self.root, text="Mark as Completed", command=self.mark_completed
        )
        complete_button.grid(row=3, column=0, padx=10, pady=5, sticky="w")

        applay_changed = tk.Button(
            self.root, text="Apply Changes", command=self.apply_changes, width="30"
        )
        applay_changed.grid(row=4, column=0, padx=10, pady=5, sticky="N")

    def getOldGoals(self):
        res = self.cur.execute("SELECT title, checked FROM goals")
        tasks = res.fetchall()
        print(tasks)
        if tasks is None:
            return
        for t in tasks:
            if t[1] == 1:
                self.task_listbox.insert(tk.END, "✅ " + t[0])
            else:
                self.task_listbox.insert(tk.END, t[0])

    def add_task(self):
        task = self.task_entry.get().strip()
        if task:
            self.task_listbox.insert(tk.END, task)
            self.task_entry.delete(0, tk.END)
        else:
            messagebox.showwarning("Warning", "The task entry cannot be empty!")

    def remove_task(self):
        try:
            selected_index = self.task_listbox.curselection()[0]
            self.task_listbox.delete(selected_index)
        except IndexError:
            messagebox.showwarning("Warning", "Select a task to remove!")

    def mark_completed(self):
        try:
            selected_index = self.task_listbox.curselection()[0]
            task = self.task_listbox.get(selected_index)
            if task.startswith("✅ "):
                self.task_listbox.delete(selected_index)
                self.task_listbox.insert(tk.END, task[2:])
            else:
                self.task_listbox.delete(selected_index)
                self.task_listbox.insert(tk.END, f"✅ {task}")
        except IndexError:
            messagebox.showwarning("Warning", "Select a task to mark as completed!")

    def get_current_wallpaper(self):
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, registry_key) as key:
            wallpaper_path, _ = winreg.QueryValueEx(key, registry_value)
        return wallpaper_path

    def set_wallpaper(self, image_path):
        ctypes.windll.user32.SystemParametersInfoW(20, 0, image_path, 3)

    def add_text_to_image(self, image_path, text, position, font_size):
        image = Image.open(image_path)
        draw = ImageDraw.Draw(image)
        try:
            font = ImageFont.truetype(
                "arial", font_size
            )  # Try to use a default Windows font
        except IOError:
            font = (
                ImageFont.load_default()
            )  # Use a basic default font if "arial" isn't found

        # Calculate text size and position using textbbox
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        x, y = position
        x = x - text_width  # Align text to the right
        draw.text((x, y), text, (255, 255, 255), font=font)  # White text color

        # Save the modified image to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmpfile:
            temp_image_path = tmpfile.name
            image.save(temp_image_path)

        return temp_image_path

    def copy_backuped_img(self):
        if self.backup_path and os.path.isfile(self.backup_path):
            currentlyImg_path = os.path.join(
                self.currentlyImg, os.path.basename(self.backup_path)
            )
            shutil.copy2(self.backup_path, currentlyImg_path)
            self.currentlyImg_path = currentlyImg_path

    def apply_changes(self):
        self.copy_backuped_img()
        goals_text = ''.join(self.task_listbox.get(0, tk.END)).strip()
        if not goals_text:
            messagebox.showwarning("Input Error", "Please enter some goals.")
            return

        current_wallpaper = self.get_current_wallpaper()
        if current_wallpaper and os.path.isfile(current_wallpaper):
            with Image.open(current_wallpaper) as img:
                width, height = img.size

            padding = 10
            position = (width - padding, padding)

            modified_wallpaper_path = self.add_text_to_image(
                current_wallpaper, goals_text, position, 30
            )
            self.set_wallpaper(modified_wallpaper_path)
            messagebox.showinfo("Success", "Wallpaper updated successfully.")
        else:
            messagebox.showerror("Error", "Could not find the current wallpaper.")
