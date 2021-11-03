from datetime import timedelta

from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QWidget
from PyQt5 import uic, QtMultimedia, QtCore

from util import Closable, WindowHolder


def format_timedelta(delta):
    minutes = delta.seconds // 60
    seconds = delta.seconds - minutes * 60
    return f"{minutes:02d}:{seconds:02d}"


class AlbumWindow(QWidget, Closable, WindowHolder):

    def __init__(self, username, album, database):
        super().__init__()
        uic.loadUi('ui/album.ui', self)
        self.playlist = QtMultimedia.QMediaPlaylist()
        self.current_index = 0
        self.player = QtMultimedia.QMediaPlayer()
        self.is_playing = False
        self.username = username
        self.database = database
        self.album = album
        self.initUi()

    def initUi(self):
        self.album_name.setText(self.album.get_name())
        self.album_year.setText(str(self.album.get_year()))
        self.album_genre.setText(self.album.get_genre().get_name())
        self.user_label.setText(self.username)
        pixmap = QPixmap(self.album.get_cover())
        self.album_cover.setPixmap(pixmap)
        self.play_button.clicked.connect(self.play_resume)
        self.load_tracks()
        self.progress_bar.valueChanged.connect(self.slider_value_changed)
        self.player.positionChanged.connect(self.position_changed)
        self.tracklist.currentRowChanged.connect(self.track_chosen)
        self.player.durationChanged.connect(self.duration_changed)
        self.next_button.clicked.connect(self.next)
        self.prev_button.clicked.connect(self.previous)
        self.profile_button.clicked.connect(self.open_profile)

    def load_tracks(self):
        songs = self.album.get_songs()
        for song in songs:
            url = QtCore.QUrl.fromLocalFile(song.get_file())
            self.playlist.addMedia(QtMultimedia.QMediaContent(url))
            self.tracklist.addItem(song.get_name())
        self.choose_track(0)
        self.player.setPlaylist(self.playlist)

    def play_resume(self):
        if self.is_playing:
            self.pause()
        else:
            self.play()

    def play(self):
        self.play_button.setText("Resume")
        self.player.play()
        self.is_playing = True

    def pause(self):
        self.play_button.setText("Play")
        self.player.pause()
        self.is_playing = False

    def open_profile(self):
        user = self.database.load_user(self.username)
        from user_window import UserWindow
        window = UserWindow(user, self.database)
        self.open_window(window)

    def next(self):
        value = self.current_index + 1
        if value > len(self.album.get_songs()) - 1:
            value = 0
        self.track_chosen(value)

    def previous(self):
        value = self.current_index - 1
        if value < 0:
            value = len(self.album.get_songs()) - 1
        self.choose_track(value)

    def choose_track(self, index):
        self.current_index = index
        self.trackname.setText(self.album.get_songs()[index].get_name())
        self.tracklist.setCurrentRow(index)
        self.playlist.setCurrentIndex(index)

    def slider_value_changed(self):
        self.player.setPosition(self.progress_bar.value())

    def track_chosen(self, index):
        self.choose_track(index)
        if self.is_playing:
            self.player.play()

    def next_track(self):
        self.playlist.next()
        self.player.play()

    def position_changed(self, position):
        self.progress_bar.setValue(position)
        delta = timedelta(milliseconds=position)
        self.current_position.setText(format_timedelta(delta))

    def duration_changed(self, duration):
        self.progress_bar.setMaximum(duration)
        self.current_duration.setText(format_timedelta(timedelta(milliseconds=duration)))

    def closeEvent(self, event):
        super().closeEvent(event)
        self.player.stop()
