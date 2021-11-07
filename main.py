import sqlite3
import sys

from PyQt5.QtWidgets import QApplication, QMainWindow, QInputDialog
from PyQt5 import uic

from album_creation import AlbumCreationWindow
from album_widget import MiniAlbumWidget
from auth import AuthWindow
from database import BlackLandDatabase
from album_window import AlbumWindow
from user_window import UserEditorWindow
from util import WindowHolder


class MainPage(QMainWindow, WindowHolder):

    def __init__(self, user, database):
        super().__init__()
        self.user = user
        self.database = database
        uic.loadUi('ui/mainpage.ui', self)
        self.initUi()

    def initUi(self):
        self.account_value.setText(self.user.get_username())
        self.add_album_button.clicked.connect(self.create_album)
        self.update_albums()
        self.add_genre_button.clicked.connect(self.add_genre)
        self.update_button.clicked.connect(self.update)
        self.my_profile_button.clicked.connect(self.open_profile)

    def open_album(self, template):
        album = self.database.load_album(template.get_id())
        window = AlbumWindow(template.get_username(), album, self.database)
        self.open_window(window)

    def open_profile(self):
        window = UserEditorWindow(self.user, self.database)
        window.closed.connect(self.update)
        self.open_window(window)

    def update(self):
        self.update_user()
        self.update_albums()

    def update_user(self):
        username = self.user.get_username()
        self.user = self.database.load_user(username)

    def update_albums(self):
        self.clear_albums()
        for template in self.database.load_album_templates():
            widget = MiniAlbumWidget(template, parent=self.scrollContents)
            widget.listen.connect(self.open_album)
            self.scrollLayout.addWidget(widget)

    def clear_albums(self):
        while self.scrollLayout.count() > 0:
            widget = self.scrollLayout.itemAt(0).widget()
            self.scrollLayout.removeWidget(widget)
            widget.deleteLater()

    def create_album(self):
        window = AlbumCreationWindow(self.user, self.database)
        window.closed.connect(self.update)
        self.open_window(window)

    def add_genre(self):
        name, ok = QInputDialog.getText(self, "Создание жанра", "Введите название жанра")

        if not ok:
            return
        if not name:
            self.statusBar().showMessage("Название жанра не может быть пустым!")
            return
        if self.database.genre_exists(name):
            self.statusBar().showMessage("Жанр с таким же названием уже существует!")
            return

        self.database.add_genres(name)
        self.statusBar().showMessage("Жанр добавлен.")

    def closeEvent(self, event):
        self.database.shutdown()


class BlackLandRadio:
    def __init__(self):
        self.database = BlackLandDatabase(sqlite3.connect("blackland.db"))
        self.database.initialize()
        self.database.add_genres("Рок", "Поп", "Хип-хоп", "Метал", "Эмбиент")
        self.auth_window = AuthWindow(self.database)
        self.auth_window.show()
        self.main_page = None
        self.auth_window.finished.connect(self.open_main)

    def open_main(self, user):
        self.main_page = MainPage(user, self.database)
        self.main_page.show()
        self.auth_window.close()
        self.auth_window = None


if __name__ == "__main__":
    app = QApplication(sys.argv)
    radio = BlackLandRadio()
    sys.exit(app.exec())
