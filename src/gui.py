import os
import shutil
import subprocess
import sys
import tkinter
from tkinter import Tk, filedialog
from tkinter import ttk
import tkinter.messagebox
import customtkinter
import json
from tkinter import PhotoImage
from PIL import Image, ImageTk

# Set up the appearance mode and color theme for custom tkinter
customtkinter.set_appearance_mode("System")
customtkinter.set_default_color_theme("blue")

# Initialize some global variables
script_directory = os.path.dirname(os.path.abspath(__file__))
images = None
settings = None
current_folder = "keybinds"
current_button = -1
file_path1 = None
file_path2 = None


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.folder_button = None
        self.img_label = None
        self.img_label2 = None

        # Load settings and set up the main window
        load_settings()
        self.setup_window()
        self.left_bar()
        self.gen_buttons(200, 60)
        self.right_bar()
        self.bottom_bar()

    def setup_window(self):
        self.title("Py Deck Editor")
        self.geometry(f"{1100}x{580}")
        self.resizable(False, False)
        self.grid_columnconfigure(1, weight=0, pad=10)
        self.grid_columnconfigure((2, 3, 4, 5), weight=0, pad=10)
        self.grid_rowconfigure((0, 1, 2), weight=1)

    def left_bar(self):
        self.sidebar_frame = customtkinter.CTkFrame(self, width=140, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)
        self.logo_label = customtkinter.CTkLabel(
            self.sidebar_frame,
            text="Py Deck",
            font=customtkinter.CTkFont(size=30, weight="bold"),
        )
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        self.sidebar_button_1 = customtkinter.CTkButton(
            self.sidebar_frame, command=self.home_click, text="Home"
        )
        self.sidebar_button_1.grid(row=1, column=0, padx=20, pady=10)
        self.sidebar_button_2 = customtkinter.CTkButton(
            self.sidebar_frame, command=self.sidebar_button_event, text="Save"
        )
        self.sidebar_button_2.grid(row=2, column=0, padx=20, pady=10)
        self.appearance_mode_label = customtkinter.CTkLabel(
            self.sidebar_frame, text="Appearance Mode:", anchor="w"
        )
        self.appearance_mode_label.grid(row=5, column=0, padx=20, pady=(10, 0))
        self.appearance_mode_optionemenu = customtkinter.CTkOptionMenu(
            self.sidebar_frame,
            values=["Light", "Dark", "System"],
            command=self.change_appearance_mode_event,
        )
        self.appearance_mode_optionemenu.grid(row=6, column=0, padx=20, pady=(10, 10))
        self.appearance_mode_optionemenu.set("Dark")

    def bottom_bar(self):
        self.edit_bar = customtkinter.CTkLabel(
            self,
            text="Settings",
            font=customtkinter.CTkFont(size=23, weight="bold"),
        )
        self.edit_bar.place(x=380, y=360)

        self.currentKey = customtkinter.CTkLabel(
            self,
            text="",
            font=customtkinter.CTkFont(size=18, weight="bold"),
        )
        self.currentKey.place(x=220, y=390)

        self.currentImage = customtkinter.CTkLabel(
            self,
            text="",
            font=customtkinter.CTkFont(size=18, weight="bold"),
        )
        self.currentImage.place(x=220, y=420)

        self.currentFolder = customtkinter.CTkLabel(
            self,
            text=f"Current Folder: {current_folder}",
            font=customtkinter.CTkFont(size=18, weight="bold"),
            text_color="yellow"
        )
        self.currentFolder.place(x=315, y=20)

    def right_bar(self):
        global current_button
        self.rsidebar_frame = customtkinter.CTkFrame(
            self, width=400, height=580, corner_radius=0
        )
        self.rsidebar_frame.place(x=700, y=0)
        self.edit_bar = customtkinter.CTkLabel(
            self.rsidebar_frame,
            text="Edit Key",
            font=customtkinter.CTkFont(size=23, weight="bold"),
        )
        self.edit_bar.place(x=160, y=20)

        self.label = customtkinter.CTkLabel(
            self.rsidebar_frame,
            text="KeyBind:",
            font=customtkinter.CTkFont(size=18, weight="bold"),
        )
        self.label.place(x=40, y=80)

        self.entry = customtkinter.CTkEntry(
            self.rsidebar_frame,
            placeholder_text="examples: 'keybind: win+r' or 'command: pwd'",
            width=260,
        )
        self.entry.place(x=120, y=80)

        self.released_image_button = customtkinter.CTkButton(
            self.rsidebar_frame,
            text="Select Released Image",
            command=self.select_released_image,
        )
        self.released_image_button.place(x=60, y=140)

        self.pressed_image_button = customtkinter.CTkButton(
            self.rsidebar_frame,
            text="Select Pressed Image",
            command=self.select_pressed_image,
        )
        self.pressed_image_button.place(x=210, y=140)

        self.save = customtkinter.CTkButton(
            self.rsidebar_frame,
            text="Save",
            command=lambda: self.update_button_settings(
                current_button, self.entry.get(), file_path1, file_path2
            ),
        )
        self.save.place(x=140, y=540)

    def gen_buttons(self, x_offset, y_offset):
        self.main_button_1 = customtkinter.CTkButton(
            self,
            text="Button 1",
            width=70,
            height=70,
            command=lambda: self.select_button(1),
        )
        self.main_button_1.place(x=x_offset, y=y_offset)

        self.main_button_2 = customtkinter.CTkButton(
            self,
            text="Button 2",
            width=70,
            height=70,
            command=lambda: self.select_button(2),
        )
        self.main_button_2.place(x=x_offset + 100, y=y_offset)

        self.main_button_3 = customtkinter.CTkButton(
            self,
            text="Button 3",
            width=70,
            height=70,
            command=lambda: self.select_button(3),
        )
        self.main_button_3.place(x=x_offset + 200, y=y_offset)

        self.main_button_4 = customtkinter.CTkButton(
            self,
            text="Button 4",
            width=70,
            height=70,
            command=lambda: self.select_button(4),
        )
        self.main_button_4.place(x=x_offset + 300, y=y_offset)

        self.main_button_5 = customtkinter.CTkButton(
            self,
            text="Button 5",
            width=70,
            height=70,
            command=lambda: self.select_button(5),
        )
        self.main_button_5.place(x=x_offset + 400, y=y_offset)

        # Second Row
        self.main_button_6 = customtkinter.CTkButton(
            self,
            text="Button 6",
            width=70,
            height=70,
            command=lambda: self.select_button(6),
        )
        self.main_button_6.place(x=x_offset, y=y_offset + 100)

        self.main_button_7 = customtkinter.CTkButton(
            self,
            text="Button 7",
            width=70,
            height=70,
            command=lambda: self.select_button(7),
        )
        self.main_button_7.place(x=x_offset + 100, y=y_offset + 100)

        self.main_button_8 = customtkinter.CTkButton(
            self,
            text="Button 8",
            width=70,
            height=70,
            command=lambda: self.select_button(8),
        )
        self.main_button_8.place(x=x_offset + 200, y=y_offset + 100)

        self.main_button_9 = customtkinter.CTkButton(
            self,
            text="Button 9",
            width=70,
            height=70,
            command=lambda: self.select_button(9),
        )
        self.main_button_9.place(x=x_offset + 300, y=y_offset + 100)

        self.main_button_10 = customtkinter.CTkButton(
            self,
            text="Button 10",
            width=70,
            height=70,
            command=lambda: self.select_button(10),
        )
        self.main_button_10.place(x=x_offset + 400, y=y_offset + 100)

        # Third Row
        self.main_button_11 = customtkinter.CTkButton(
            self,
            text="Button 11",
            width=70,
            height=70,
            command=lambda: self.select_button(11),
        )
        self.main_button_11.place(x=x_offset, y=y_offset + 200)

        self.main_button_12 = customtkinter.CTkButton(
            self,
            text="Button 12",
            width=70,
            height=70,
            command=lambda: self.select_button(12),
        )
        self.main_button_12.place(x=x_offset + 100, y=y_offset + 200)

        self.main_button_13 = customtkinter.CTkButton(
            self,
            text="Button 13",
            width=70,
            height=70,
            command=lambda: self.select_button(13),
        )
        self.main_button_13.place(x=x_offset + 200, y=y_offset + 200)

        self.main_button_14 = customtkinter.CTkButton(
            self,
            text="Button 14",
            width=70,
            height=70,
            command=lambda: self.select_button(14),
        )
        self.main_button_14.place(x=x_offset + 300, y=y_offset + 200)

        self.main_button_15 = customtkinter.CTkButton(
            self,
            text="Button 15",
            width=70,
            height=70,
            command=lambda: self.select_button(15),
        )
        self.main_button_15.place(x=x_offset + 400, y=y_offset + 200)

    def home_click(self):
        global current_folder
        current_folder = "keybinds"
        folder = getattr(self, f"currentFolder")
        folder.configure(text=f"Current Folder: keybinds")

    def select_released_image(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp")]
        )
        global file_path1
        result = file_path.split("/")
        file_path1 = result[-1]

        if file_path:
            try:
                destination = os.path.join("src", "Assets")
                shutil.copy(file_path, destination)

                print("Image copied to:", destination)
            except Exception as e:
                print("Error copying the image:", str(e))

    def select_pressed_image(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp")]
        )
        global file_path2
        result = file_path.split("/")
        file_path2 = result[-1]

        if file_path:
            try:
                destination = os.path.join("src", "Assets")
                shutil.copy(file_path, destination)

                print("Image copied to:", destination)
            except Exception as e:
                print("Error copying the image:", str(e))

    active_button = -1

    def enter_folder(self, button, keybinds):
        global current_folder
        print("entering folder")
        print(keybinds)
        current_folder = keybinds.get(str(button - 1))[8:]
        folder = getattr(self, f"currentFolder")
        folder.configure(text=f"Current Folder: {current_folder}")

    def select_button(self, button):
        global images, current_folder, settings, current_button, file_path1, file_path2
        file_path1, file_path2 = None, None
        current_button = button
        keybinds = settings.get(current_folder + "-keybind")
        bind = keybinds.get(str(button - 1), None)
        self.currentKey.configure(text="Button " + str(button) + " " + bind)
        images = settings.get(current_folder + "-image")
        if self.folder_button is not None:
            self.folder_button.destroy()
            self.folder_button = None

        image = images.get(str(button - 1), None)
        self.currentImage.configure(
            text="Images:   Released                          Pressed"
        )

        if self.img_label is not None:
            self.img_label.destroy()
            self.img_label = None
        if self.img_label2 is not None:
            self.img_label2.destroy()
            self.img_label2 = None

        img = Image.open(
            os.path.join(script_directory, "Assets", image.get("released"))
        )
        max_width, max_height = 100, 100
        width, height = img.size
        if width > max_width or height > max_height:
            ratio = min(max_width / width, max_height / height)
            new_width, new_height = int(width * ratio), int(height * ratio)
            img = img.resize((new_width, new_height))
        photo = ImageTk.PhotoImage(img)
        self.img_label = customtkinter.CTkLabel(self, image=photo, text="")
        self.img_label.image = photo
        self.img_label.place(x=280, y=450)

        img = Image.open(os.path.join(script_directory, "Assets", image.get("pressed")))
        max_width, max_height = 100, 100
        width, height = img.size
        if width > max_width or height > max_height:
            ratio = min(max_width / width, max_height / height)
            new_width, new_height = int(width * ratio), int(height * ratio)
            img = img.resize((new_width, new_height))
        photo = ImageTk.PhotoImage(img)
        self.img_label2 = customtkinter.CTkLabel(self, image=photo, text="")
        self.img_label2.image = photo
        self.img_label2.place(x=485, y=450)

        if keybinds.get(str(button - 1))[:6] == "folder":
            self.folder_button = customtkinter.CTkButton(
                self,
                text="Enter Folder",
                width=70,
                fg_color="orange",
                hover_color="green",
                command=lambda: self.enter_folder(button, keybinds),
            )
            self.folder_button.place(x=200, y=350)

        if self.active_button != -1:
            old_button = getattr(self, f"main_button_{self.active_button}")
            old_button.configure(border_width=0)

        clicked_button = getattr(self, f"main_button_{button}")

        if self.active_button == button:
            self.active_button = -1
            clicked_button.configure(border_width=0)
            self.currentKey.configure(text="")
            self.currentImage.configure(text="")
            self.img_label.destroy()
            self.img_label2.destroy()
        else:
            clicked_button.configure(border_width=5)
            clicked_button.configure(border_color="yellow")
            self.active_button = button

    def create_image_label(self, x, image_path):
        img = Image.open(image_path)
        max_width, max_height = 100, 100
        width, height = img.size
        if width > max_width or height > max_height:
            ratio = min(max_width / width, max_height / height)
            new_width, new_height = int(width * ratio), int(height * ratio)
            img = img.resize((new_width, new_height))
        photo = ImageTk.PhotoImage(img)
        self.img_label = customtkinter.CTkLabel(self, image=photo, text="")
        self.img_label.image = photo
        self.img_label.place(x=x, y=450)

    def change_appearance_mode_event(self, new_appearance_mode: str):
        customtkinter.set_appearance_mode(new_appearance_mode)

    def sidebar_button_event(self):
        self.restart_script()

    def restart_script(self):
        current_script = os.path.basename(
            os.path.join(os.path.abspath(__file__), "hotkeys_terminal.py")
        )
        try:
            subprocess.run(["pkill", "-f", current_script])
        except Exception as e:
            print(f"Error while killing the process: {e}")
        python = sys.executable
        script_to_restart = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "hotkeys_terminal.py"
        )
        subprocess.Popen([python, script_to_restart])
        # self.destroy()

    def update_button_settings(
        self, button_number, keybind, released_image, pressed_image
    ):
        if released_image is None or pressed_image is None or keybind is None:
            tkinter.messagebox.showinfo("Py Deck Warning", "You Must Enter All Bind Information")
            return

        script_directory = os.path.dirname(os.path.abspath(__file__))
        settings_file_path = os.path.join(script_directory, "settings.json")
        global settings
        if settings:
            current_folder_key = current_folder + "-keybind"
            current_folder_image = current_folder + "-image"

            # Update keybind and image settings for the selected button
            keybinds = settings.get(current_folder_key, {})
            keybinds[str(button_number - 1)] = keybind

            images = settings.get(current_folder_image, {})
            images[str(button_number - 1)] = {
                "released": released_image,
                "pressed": pressed_image,
            }

            settings[current_folder_key] = keybinds
            settings[current_folder_image] = images

            # Write the updated settings back to the JSON file
            with open(settings_file_path, "w") as json_file:
                json.dump(settings, json_file, indent=4)
        if str(keybind.split(" ")[0][:-1]) == "folder":
            data = {
                f"{keybind.split(' ')[1]}-keybind": {
                    "0": "keybind:",
                    "1": "keybind:",
                    "2": "keybind:",
                    "3": "keybind:",
                    "4": "keybind:",
                    "5": "keybind:",
                    "6": "command:",
                    "7": "command:",
                    "8": "command:",
                    "9": "command:",
                    "10": "command:",
                    "11": "command:",
                    "12": "command:",
                    "13": "command:",
                    "14": "command:",
                },
                f"{keybind.split(' ')[1]}-image": {
                    "0": {"pressed": "blank.png", "released": "blank.png"},
                    "1": {"pressed": "blank.png", "released": "blank.png"},
                    "2": {"pressed": "blank.png", "released": "blank.png"},
                    "3": {"pressed": "blank.png", "released": "blank.png"},
                    "4": {"pressed": "blank.png", "released": "blank.png"},
                    "5": {"pressed": "blank.png", "released": "blank.png"},
                    "6": {"pressed": "blank.png", "released": "blank.png"},
                    "7": {"pressed": "blank.png", "released": "blank.png"},
                    "8": {"pressed": "blank.png", "released": "blank.png"},
                    "9": {"pressed": "blank.png", "released": "blank.png"},
                    "10": {"pressed": "back.png", "released": "back.png"},
                    "11": {"pressed": "blank.png", "released": "blank.png"},
                    "12": {"pressed": "blank.png", "released": "blank.png"},
                    "13": {"pressed": "blank.png", "released": "blank.png"},
                    "14": {"pressed": "blank.png", "released": "blank.png"},
                },
            }
            with open(settings_file_path, "r") as json_file:
                existing_data = json.load(json_file)
            existing_data.update(data)
            with open(settings_file_path, "w") as json_file:
                json.dump(existing_data, json_file, indent=4)

        self.entry = customtkinter.CTkEntry(
            self.rsidebar_frame,
            placeholder_text="examples: 'keybind: win+r' or 'command: pwd'",
            width=260,
        )
        self.entry.place(x=120, y=80)

        load_settings()


def load_settings():
    global keybinds, images, settings
    script_directory = os.path.dirname(os.path.abspath(__file__))
    settings_file_path = os.path.join(script_directory, "settings.json")
    print("Loading Settings...")
    try:
        with open(settings_file_path, "r") as json_file:
            settings = json.load(json_file)
            images = settings.get("images", {})
    except Exception as e:
        print(f"Error loading settings: {str(e)}")

    print("Done")


if __name__ == "__main__":
    app = App()
    app.mainloop()
