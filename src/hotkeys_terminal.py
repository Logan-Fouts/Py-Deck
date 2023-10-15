#!/usr/bin/env python3

import os
import sys
import threading
from PIL import Image, ImageDraw, ImageFont
from StreamDeck.DeviceManager import DeviceManager
from StreamDeck.ImageHelpers import PILHelper
import pyautogui
import tkinter as tk
import subprocess
import json

script_dir = os.path.dirname(os.path.abspath(__file__))
config_dir = "/home/lfouts/config.json"
in_folder = False

with open(config_dir, "r") as config_file:
    config_data = json.load(config_file)

password = config_data.get("password", "")

ASSETS_PATH = os.path.join(os.path.dirname(__file__), "Assets")


def read_settings_file(type0, type1):
    button_to_settings_mapping = {}
    button_to_images_mapping = {}

    with open(os.path.join(script_dir, "settings.json"), "r") as file:
        data = json.load(file)

    keybinds = data.get(type0, {})
    for button, keybind in keybinds.items():
        tmp_keybind = keybind.split()
        if tmp_keybind[0][:-1] == "keybind":
            button_to_settings_mapping[int(button)] = {"keybind": tmp_keybind[1:]}
        elif tmp_keybind[0][:-1] == "command":
            button_to_settings_mapping[int(button)] = {"command": tmp_keybind[1:]}
        elif tmp_keybind[0][:-1] == "folder":
            button_to_settings_mapping[int(button)] = {"folder": tmp_keybind[1:]}

    images = data.get(type1, {})
    for button, image in images.items():
        button_to_images_mapping[int(button)] = {
            "pressed": image.get("pressed", ""),
            "released": image.get("released", ""),
        }

    return button_to_settings_mapping, button_to_images_mapping


button_to_settings_mapping, button_to_images_mapping = read_settings_file(
    "keybinds-keybind", "keybinds-image"
)


def setup_keys(button_to_settings_mapping, button_to_images_mapping):
    keybinds = {
        key: mapping["keybind"]
        for key, mapping in button_to_settings_mapping.items()
        if "keybind" in mapping
    }
    commands = {
        key: mapping["command"]
        for key, mapping in button_to_settings_mapping.items()
        if "command" in mapping
    }
    folders = {
        key: mapping["folder"]
        for key, mapping in button_to_settings_mapping.items()
        if "folder" in mapping
    }
    images = {key: mapping for key, mapping in button_to_images_mapping.items()}

    return keybinds, commands, folders, images


def render_key_image(deck, icon_filename, font_filename, label_text):
    icon = Image.open(icon_filename)
    image = PILHelper.create_scaled_image(deck, icon, margins=[0, 0, 20, 0])

    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype(font_filename, 14)
    draw.text(
        (image.width / 2, image.height - 5),
        text=label_text,
        font=font,
        anchor="ms",
        fill="white",
    )

    return PILHelper.to_native_format(deck, image)


def get_key_style(deck, key, state):
    exit_key_index = deck.key_count() - 1

    name = "emoji"
    icon_filename = images[key]["pressed" if state else "released"]
    font = "Roboto-Regular.ttf"
    label = "Pressed!" if state else "Key {}".format(key)

    return {
        "name": name,
        "icon": os.path.join(ASSETS_PATH, icon_filename),
        "font": os.path.join(ASSETS_PATH, font),
        "label": label,
    }


def update_key_image(deck, key, state):
    key_style = get_key_style(deck, key, state)

    image = render_key_image(
        deck, key_style["icon"], key_style["font"], key_style["label"]
    )

    with deck:
        deck.set_key_image(key, image)


def clear_buttons(deck, folder):
    for key in range(deck.key_count()):
        deck.set_key_image(key, None)


def key_change_callback(deck, key, state):
    global keybinds, commands, folders, images, button_to_settings_mapping, button_to_images_mapping, in_folder

    if key == 10 and state and in_folder:
        print("Restarting the script...")
        python = sys.executable
        os.execl(python, python, *sys.argv)

    print("Deck {} Key {} = {}".format(deck.id(), key, state), flush=True)

    update_key_image(deck, key, state)

    if state:
        if key in keybinds:
            command = keybinds[key]
            if len(command) > 0:
                if command[0] != "echo":
                    tmp_command = command[0].split("+")
                    pyautogui.hotkey(tmp_command)

        elif key in commands:
            command = commands[key]

            if len(command) > 0:
                if command[0] == "echo":
                    command = f'echo "{password}" | {" ".join(command[3:])}'
                    subprocess.Popen(command + " " + command[1], shell=True)
                    return

            print("\n", " ".join(command), "\n")
            subprocess.Popen(" ".join(command), shell=True)
        elif key in folders:
            print("here")
            clear_buttons(deck, str(folders[key]))
            button_to_settings_mapping, button_to_images_mapping = read_settings_file(
                f'{str(folders[key]).strip("[]")}-{"keybind"}'.replace("'", ""),
                f'{str(folders[key]).strip("[]")}-{"image"}'.replace("'", ""),
            )
            keybinds, commands, folders, images = setup_keys(
                button_to_settings_mapping, button_to_images_mapping
            )
            in_folder = True
            for key in range(deck.key_count()):
                update_key_image(deck, key, False)


if __name__ == "__main__":
    streamdecks = DeviceManager().enumerate()

    print("Found {} Stream Deck(s).\n".format(len(streamdecks)))

    keybinds, commands, folders, images = setup_keys(
        button_to_settings_mapping, button_to_images_mapping
    )

    for index, deck in enumerate(streamdecks):
        if not deck.is_visual():
            continue

        deck.open()
        deck.reset()

        print(
            "Opened '{}' device (serial number: '{}', fw: '{}')".format(
                deck.deck_type(), deck.get_serial_number(), deck.get_firmware_version()
            )
        )

        deck.set_brightness(100)

        for key in range(deck.key_count()):
            update_key_image(deck, key, False)

        deck.set_key_callback(key_change_callback)

        for t in threading.enumerate():
            try:
                t.join()
            except RuntimeError:
                pass
