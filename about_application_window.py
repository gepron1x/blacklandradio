from PyQt5.QtWidgets import QMainWindow
from PyQt5 import uic

from util import Closable


class InfoWindow(QMainWindow, Closable):

    def __init__(self, file):
        super().__init__()
        self.file = file
        uic.loadUi('ui/info.ui', self)
        self.initUi()

    def initUi(self):
        with open(self.file, mode="rt", encoding="utf-8") as f:
            text = "\n".join(f.readlines())
        self.info.setPlainText(text)




