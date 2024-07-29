import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageDraw, ImageFont
import ctypes
import os
import shutil
import tempfile
import winreg

from config import root_folder
from config import registry_key
from config import registry_value


class SetWallaper:
    def __init__(self, root, text_input) -> None:
        self.root = root
        self.text_input = text_input

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

    def backup_original_wallpaper(self, src_path):
        # Define the backup path
        backup_dir = os.path.join(os.path.expanduser("~"), root_folder)
        os.makedirs(backup_dir, exist_ok=True)
        backup_path = os.path.join(backup_dir, os.path.basename(src_path))

        # Copy the original wallpaper to the backup location
        shutil.copy2(src_path, backup_path)
        return backup_path

    def apply_changes(self):
        goals_text = self.text_input.get("1.0", tk.END).strip()
        if not goals_text:
            messagebox.showwarning("Input Error", "Please enter some goals.")
            return

        current_wallpaper = self.get_current_wallpaper()
        if current_wallpaper and os.path.isfile(current_wallpaper):
            # Backup the original wallpaper
            backup_path = self.backup_original_wallpaper(current_wallpaper)
            print(f"Original wallpaper backed up to: {backup_path}")

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
