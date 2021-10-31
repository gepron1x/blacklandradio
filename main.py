import sqlite3
import sys

from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5 import uic

from album_creation import AlbumCreationWindow
from album_widget import MiniAlbumWidget
from auth import AuthWidget
from database import BlackLandDatabase
from album_window import AlbumWindow
from user_window import UserWindow
from util import WindowHolder

ALBUMS_FOLDER = "./albums/"


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
        self.update_button.clicked.connect(self.update_albums)
        self.my_profile_button.clicked.connect(self.open_profile)

    def open_album(self, template):
        album = self.database.load_album(template.get_id())
        window = AlbumWindow(template.get_username(), album)
        self.open_window(window)

    def open_profile(self):
        window = UserWindow(self.user)
        self.open_window(window)

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
        self.open_window(window)

    def closeEvent(self, event):
        self.database.shutdown()


class BlackLandRadio:
    def __init__(self):
        self.database = BlackLandDatabase(sqlite3.connect("blackland.db"))
        self.auth_window = AuthWidget(self.database)
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
