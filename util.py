from random import randint

from PyQt5.QtCore import pyqtSignal, QObject

IMAGE_EXTENSIONS = "Картинка (*.jpg);;Картинка (*.png);;Все файлы (*)"
MUSIC_EXTENSIONS = "Файл MP3 (*.mp3);;Все файлы (*)"
ID_MIN = 0
ID_MAX = 2_147_483_647


# Рандомные id для альбомов, песен и пользователей
def random_id():
    return randint(ID_MIN, ID_MAX)


# Окно, которое при закрытии вызывает сигнал closed
class Closable:
    closed = pyqtSignal()

    def closeEvent(self, event):
        self.closed.emit()


# Окно, в котором можно открывать другие окна.
# Из-за того, как работает python, объекты окон приходится сохранять,
# В противном случае они будут удалены очистителем мусора
# И тупо не откроются.
# Данный вспомогательный класс решает эту проблему.
# Каждое открытое окно сохраняется в список и удаляется по закрытию.
class WindowHolder(QObject):
    def __init__(self):
        super().__init__()
        self.active_windows = list()

    def open_window(self, window):
        self.active_windows.append(window)
        window.closed.connect(self.remove_active)
        window.show()

    def remove_active(self):
        self.active_windows.remove(self.sender())
