from PyQt5.QtWidgets import QMainWindow
from PyQt5 import uic

from user import DEFAULT_IMAGE_FILE, User, Album, Song, AlbumTemplate


class AuthWidget(QMainWindow):

    def __init__(self, db):
        super().__init__()
        self.db = db
        uic.loadUi('ui/auth.ui', self)

    def register(self):
        username = self.login_input.text()
        if self.db.account_exists(username):
            self.statusBar().showMessage("Аккаунт с таким именем уже существует!")
            return
        password = self.password_input.text()
        self.db.create_account(username, password)
        self.finish()

    def login(self):
        username = self.login_input.text()
        password = self.password_input.text()
        if not self.db.check_password(username, password):
            self.statusBar().showMessage("Неверный логин или пароль")
            return
        self.finish()

    def finish(self):
        self.load_user(self.login_input().text())



