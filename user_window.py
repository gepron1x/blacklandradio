from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QWidget, QFileDialog, QMainWindow
from PyQt5 import uic

from album_widget import MiniAlbumWidget
from api import AlbumTemplate
from album_window import AlbumWindow
from util import Closable, WindowHolder, IMAGE_EXTENSIONS


class AbstractUserWindow(QMainWindow, Closable, WindowHolder):
    def __init__(self, user, database):
        super().__init__()
        self.database = database
        self.user = user
        self.album_dict = dict()

    def load_albums(self, scroll_contents, scroll_layout):
        user_albums = self.user.get_albums()
        for album in user_albums:
            template = AlbumTemplate(album.get_id(), self.user.get_username(),
                                     album.get_name(), album.get_year(), album.get_cover())
            self.album_dict[template] = album
            widget = self.create_album_widget(template, scroll_contents)
            widget.listen.connect(self.open_album)
            scroll_layout.addWidget(widget)

    def create_album_widget(self, template, parent):
        return MiniAlbumWidget(template, parent=parent)

    def open_album(self, template):
        album = self.album_dict[template]
        window = AlbumWindow(self.user.get_username(), album, self.database)
        self.open_window(window)


class UserWindow(AbstractUserWindow):

    def __init__(self, user, database):
        super().__init__(user, database)
        uic.loadUi('ui/user.ui', self)
        self.initUi()

    def initUi(self):
        self.username_label.setText(self.user.get_username())
        self.desc.setPlainText(self.user.get_description())
        pixmap = QPixmap(self.user.get_avatar())
        self.pfp.setPixmap(pixmap)
        self.total_albums.setText(str(len(self.user.get_albums())))
        self.load_albums(self.scrollContents, self.scrollLayout)


class UserEditorWindow(AbstractUserWindow):

    def __init__(self, user, database):
        super().__init__(user, database)
        self.editor = database.user_editor(user)
        uic.loadUi("ui/user_edit.ui", self)
        self.initUi()

    def initUi(self):
        self.username_label.setText(self.user.get_username())
        self.avatar_label.setPixmap(QPixmap(self.user.get_avatar()))
        self.description.setPlainText(self.user.get_description())
        self.edit_description_button.clicked.connect(self.edit_description)
        self.edit_avatar_button.clicked.connect(self.edit_avatar)
        self.load_albums(self.scrollContents, self.scrollLayout)

    def create_album_widget(self, template, parent):
        widget = MiniAlbumWidget(template, parent=parent, deletable=True)
        widget.delete.connect(self.remove_album)
        return widget

    def edit_description(self):
        self.editor.set_description(self.description.toPlainText())

    def edit_avatar(self):
        avatar = QFileDialog.getOpenFileName(
            self, 'Выбрать картинку', '', IMAGE_EXTENSIONS)[0]
        self.avatar_label.setPixmap(QPixmap(avatar))
        self.editor.set_avatar(avatar)

    def remove_album(self, template):
        self.scrollLayout.removeWidget(self.sender())
        self.editor.remove_album(template.get_id())

    def closeEvent(self, event):
        Closable.closeEvent(self, event)
        self.editor.finish()
