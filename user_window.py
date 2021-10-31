from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QWidget
from PyQt5 import uic

from album_widget import MiniAlbumWidget
from user import AlbumTemplate
from album_window import AlbumWindow
from util import Closable, WindowHolder


class UserWindow(QWidget, Closable, WindowHolder):

    def __init__(self, user):
        super().__init__()
        self.user = user
        self.album_dict = {}
        uic.loadUi('ui/user.ui', self)
        self.initUi()

    def initUi(self):
        self.username_label.setText(self.user.get_username())
        self.desc.setPlainText(self.user.get_description())
        pixmap = QPixmap(self.user.get_avatar())
        self.pfp.setPixmap(pixmap)
        self.total_albums.setText(str(len(self.user.get_albums())))
        self.load_albums()

    def load_albums(self):
        user_albums = self.user.get_albums()
        for album in user_albums:
            template = AlbumTemplate(album.get_id(), self.user.get_username(),
                                     album.get_name(), album.get_year(), album.get_cover())
            self.album_dict[template] = album
            widget = MiniAlbumWidget(template, parent=self.scrollContents)
            widget.listen.connect(self.open_album)
            self.scrollLayout.addWidget(widget)

    def open_album(self, template):
        album = self.album_dict[template]
        window = AlbumWindow(self.user.get_username(), album)
        self.open_window(window)
