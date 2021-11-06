

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QMainWindow
from PyQt5 import uic

import util
from api import User


class AuthWidget(QMainWindow):
    finished = pyqtSignal(User)

    def __init__(self, database):
        super().__init__()
        self.database = database
        uic.loadUi('ui/auth.ui', self)
        self.initUi()

    def initUi(self):
        self.login_button.clicked.connect(self.login)
        self.register_button.clicked.connect(self.register)

    def register(self):
        username = self.login_input.text()
        if self.database.account_exists(username):
            self.statusBar().showMessage("Аккаунт с таким именем уже существует!")
            return
        password = self.password_input.text()
        self.database.create_account(User(util.random_id(), username, password, "", list()))
        self.finish()

    def login(self):
        username = self.login_input.text()
        password = self.password_input.text()
        if not self.database.check_password(username, password):
            self.statusBar().showMessage("Неверный логин или пароль")
            return
        self.finish()

    def finish(self):
        self.finished.emit(self.database.load_user(self.login_input.text()))


