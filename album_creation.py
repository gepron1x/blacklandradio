import sqlite3
import sys

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QPixmap
from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QFileDialog, QGroupBox

import util
import os.path
import datetime
from util import IMAGE_EXTENSIONS, MUSIC_EXTENSIONS
from api import DEFAULT_COVER, Genre, Album, Song

MAX_NAME_LEN = 60


# Виджет создания песни
class SongCreation(QGroupBox):
    deleted = pyqtSignal()  # Сигнал вызывется если нажата кнопка удаления

    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi('ui/song_creation.ui', self)
        self.initUi()

    def initUi(self):
        self.choose_file_btn.clicked.connect(self.choose_file)
        self.delete_button.clicked.connect(self.on_delete)

    def choose_file(self):
        self.file_input.setText(QFileDialog.getOpenFileName(
            self, 'Выбери песню', '', MUSIC_EXTENSIONS)[0])

    def on_delete(self):
        self.deleted.emit()

    def get_song_name(self):
        return self.name_input.text()

    def get_file(self):
        return self.file_input.text()


# Окно создания альбома
class AlbumCreationWindow(QMainWindow, util.Closable):

    def __init__(self, user, database):
        super().__init__()
        uic.loadUi('ui/album_creation.ui', self)
        self.user = user
        self.genres_by_name = {}
        self.album_cover = DEFAULT_COVER
        self.album_name = ""
        self.year = -1  # ...
        self.database = database
        self.initUi()

    def initUi(self):
        genres = self.database.load_genres()
        for genre in genres:
            self.genres_by_name[genre.get_name()] = genre

        self.genres_combobox.addItems(list(map(Genre.get_name, genres)))
        self.refresh_cover()
        self.cancel_button.clicked.connect(self.cancel)
        self.choose_cover_button.clicked.connect(self.choose_cover)
        self.add_song_button.clicked.connect(self.add_song)
        self.create_album_button.clicked.connect(self.finish)

    def refresh_cover(self):
        pixmap = QPixmap(self.album_cover)
        self.cover.setPixmap(pixmap)

    def add_song(self):
        widget = SongCreation(parent=self.songs_contents)
        widget.deleted.connect(self.remove_song)
        self.songs_layout.addWidget(widget)

    def remove_song(self):
        self.songs_layout.removeWidget(self.sender())

    def finish(self):
        album_id = util.random_id()
        name = self.name_input.text()
        year = self.year_input.text()
        genre = self.genres_by_name[self.genres_combobox.currentText()]

        # Провярем, все ли верно

        if not name or len(name) > MAX_NAME_LEN:
            self.statusBar().showMessage(f"Название не может быть пустым и иметь размер более {MAX_NAME_LEN} символов!")
            return

        if not year.isdigit():
            self.statusBar().showMessage("Год может содержать только числа!")
            return
        year_integer = int(year)

        if year_integer < 1000:
            self.statusBar().showMessage("Вы писали музыку в каменном веке? Введите настоящий год! :)")
            return

        if year_integer > datetime.datetime.now().year:
            self.statusBar().showMessage("Вы из будущего? Введите настоящий год!")
            return

        if not os.path.isfile(self.album_cover):
            self.statusBar().showMessage("Файла аватарки не существует!")
            return
        song_count = self.songs_layout.count()
        if song_count == 0:
            self.statusBar().showMessage("Добавьте хоть одну песню!")
            return

        # Добавляем песни

        songs = list()
        for i in range(self.songs_layout.count()):
            widget = self.songs_layout.itemAt(i).widget()
            song_name = widget.get_song_name()
            # Снова защита от Ольги Александровны
            if not song_name:
                self.statusBar().showMessage("У песен должно быть название!")
                return
            if len(song_name) > MAX_NAME_LEN:
                self.statusBar().showMessage(f"Название песен не должно быть больше {MAX_NAME_LEN} символов!")
            song_file = widget.get_file()
            if not os.path.isfile(song_file):
                self.statusBar().showMessage(f"У песни {song_name} файл не существует, либо он вовсе не указан.")
                return
            song_id = util.random_id()
            songs.append(Song(song_id, song_name, song_file))
        album = Album(album_id, name, genre, int(year), songs, cover=self.album_cover)
        self.database.save_album(self.user.get_id(), album)
        self.close()

    def cancel(self):
        self.close()

    def choose_cover(self):
        self.album_cover = QFileDialog.getOpenFileName(
            self, 'Выбрать картинку', '', IMAGE_EXTENSIONS)[0]
        self.refresh_cover()
