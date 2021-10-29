import sqlite3
import sys

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QWidget, QMainWindow, QApplication
from PyQt5 import uic
from PySide6.QtCore import Signal, Slot

from database import BlackLandDatabase
from user import Album, User, AlbumWidget, AlbumTemplate


class MiniAlbumWidget(QWidget):
    listen = pyqtSignal(AlbumTemplate)

    def __init__(self, album_template, parent=None):
        super().__init__(parent)
        uic.loadUi("ui/album_widget.ui", self)
        self.album_template = album_template
        self.initUi()

    def initUi(self):
        pixmap = QPixmap(self.album_template.get_cover())
        self.cover.setPixmap(pixmap)
        self.album_name.setText(self.album_template.get_name())
        self.username.setText(self.album_template.get_username())
        self.year.setText(str(self.album_template.get_year()))
        self.listen_button.clicked.connect(self.press_listen)

    def press_listen(self):
        self.listen.emit(self.album_template)


class MainPage(QMainWindow):

    def __init__(self, user, database):
        super().__init__()
        self.user = user
        self.active_windows = list()
        self.database = database
        uic.loadUi('mainpage.ui', self)
        for template in database.load_album_templates():
            widget = MiniAlbumWidget(template, parent=self.scrollContents)
            widget.listen.connect(self.open_album)
            self.scrollLayout.addWidget(widget)

    def initUi(self):
        self.account_value.setText(self.user.get_username())

    def open_album(self, template):
        album = self.database.load_album(template.get_id())
        window = AlbumWidget(template.get_username(), album)
        self.active_windows.append(window)
        window.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    db = BlackLandDatabase(sqlite3.connect("blackland.db"))
    db.initialize()
    ex = MainPage(User(1, "Георгий Пронюк", "1245", "dd", list()), db)
    ex.show()
    sys.exit(app.exec())
