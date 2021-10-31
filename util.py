# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import os
from random import randint
import shutil

from PyQt5.QtCore import pyqtSignal, QObject

IMAGE_EXTENSIONS = "Картинка (*.jpg);;Картинка (*.png);;Все файлы (*)"
MUSIC_EXTENSIONS = "Файл MP3 (*.mp3);;Все файлы (*)"
ID_MIN = 0
ID_MAX = 2_147_483_647


def random_string(alphabet, length):
    s = ""
    i_len = len(alphabet) - 1
    for i in range(length):
        s += alphabet[randint(0, i_len)]
    return s


def random_id():
    return randint(ID_MIN, ID_MAX)


class Closable:
    closed = pyqtSignal()

    def closeEvent(self, event):
        self.closed.emit()


class WindowHolder(QObject):
    def __init__(self):
        super().__init__()
        self.active_windows = list()

    def open_window(self, window):
        self.active_windows.append(window)
        window.closed.connect(self.remove_active)
        window.show()

    def remove_active(self):
        self.active_windows.remove(self.sender())


def copy_file(file, destination):
    os.makedirs(os.path.dirname(destination), exist_ok=True)
    shutil.copyfile(file, destination)


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+8 to toggle the breakpoint.
