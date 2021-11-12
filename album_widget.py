from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QGroupBox
from PyQt5 import uic
from api import AlbumTemplate


# Мини-Виджет альбома, используется в списках
class MiniAlbumWidget(QGroupBox):
    listen = pyqtSignal(AlbumTemplate)  # Если нажата кнопка "Слушать"
    delete = pyqtSignal(AlbumTemplate)  # Если нажата кнопка "Удалить"

    def __init__(self, album_template, deletable=False, parent=None):
        super().__init__(parent)
        uic.loadUi("ui/album_widget.ui", self)
        self.deletable = deletable
        self.album_template = album_template
        self.initUi()

    def initUi(self):
        pixmap = QPixmap(self.album_template.get_cover())
        self.cover_label.setPixmap(pixmap)
        self.title_label.setText(self.album_template.get_name())
        self.user_label.setText(self.album_template.get_username())
        self.year_label.setText(str(self.album_template.get_year()))
        self.listen_button.clicked.connect(self.listen_pressed)
        if not self.deletable:
            self.delete_button.hide()
        else:
            self.delete_button.clicked.connect(self.delete_pressed)

    def listen_pressed(self):
        self.listen.emit(self.album_template)

    def delete_pressed(self):
        self.delete.emit(self.album_template)
