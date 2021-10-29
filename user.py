import sys
from datetime import timedelta

from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QWidget, QTableWidgetItem, QApplication, QLabel
from PyQt5 import uic, QtCore, QtMultimedia

DEFAULT_IMAGE_FILE = "default_pfp.jpg"
DEFAULT_COVER = "default_cover.jpg"


class User:

    def __init__(self, user_id, username, password, description, albums, avatar=DEFAULT_IMAGE_FILE):
        self.user_id = user_id
        self.username = username
        self.password = password
        self.description = description
        self.avatar = avatar
        self.albums = albums

    def get_username(self):
        return self.username

    def get_password(self):
        return self.password

    def get_avatar(self):
        return self.avatar

    def get_description(self):
        return self.description

    def get_albums(self):
        return self.albums

    def __str__(self):
        return f"User {self.username} [" \
               f"id: {self.user_id}," \
               f"description: {self.description}," \
               f"albums: {self.albums}]"

    def __hash__(self):
        return hash((self.user_id, self.username,
                     self.password, self.description,
                     self.avatar, self.albums))


class Song:
    def __init__(self, song_id, name, duration=0):
        self.song_id = song_id
        self.name = name
        self.duration = duration

    def get_name(self):
        return self.name

    def get_duration(self):
        return self.duration

    def __str__(self):
        return f"Song {self.name} [" \
               f"id: {self.song_id}," \
               f"duration: {self.duration}]"

    def __hash__(self):
        return hash((self.song_id, self.name, self.duration))


class Album:
    def __init__(self, album_id, name, genre, year, songs, cover=DEFAULT_COVER):
        self.album_id = album_id
        self.year = year
        self.name = name
        self.genre = genre
        self.songs = songs
        self.cover = cover

    def get_name(self):
        return self.name

    def get_cover(self):
        return self.cover

    def get_genre(self):
        return self.genre

    def add_song(self, song):
        self.songs.append(song)

    def get_songs(self):
        return self.songs

    def get_year(self):
        return self.year

    def __str__(self):
        return f"Album {self.name} [" \
               f"id: {self.album_id}," \
               f"year: {self.year}" \
               f"genre: {self.genre}," \
               f"songs: {self.songs}]"

    def __hash__(self):
        return hash((self.album_id, self.name, self.cover, self.genre))


class AlbumTemplate:
    def __init__(self, album_id, username, name, year, cover):
        self.username = username
        self.album_id = album_id
        self.name = name
        self.year = year
        self.cover = cover

    def get_id(self):
        return self.album_id

    def get_username(self):
        return self.username

    def get_name(self):
        return self.name

    def get_year(self):
        return self.year

    def get_cover(self):
        return self.cover


ALBUM_TITLE = 0
ALBUM_GENRE = 1
ALBUM_YEAR = 2


def unmodifiable(text):
    item = QTableWidgetItem(text)
    item.setFlags(QtCore.Qt.ItemIsEnabled)
    return item


class UserWidget(QWidget):

    def __init__(self, user):
        super().__init__()
        self.user = user
        self.album_list = list()
        uic.loadUi('design/user.ui', self)
        self.initUi()

    def initUi(self):
        self.username_label.setText(self.user.get_username())
        self.desc.setPlainText(self.user.get_description())
        pixmap = QPixmap(self.user.get_avatar())
        self.pfp.setPixmap(pixmap)
        self.total_albums.setText(str(len(self.user.get_albums())))
        self.load_albums()
        self.albums_table.cellDoubleClicked.connect(self.open_album)

    def load_albums(self):
        user_albums = self.user.get_albums()
        self.albums_table.setRowCount(len(user_albums))
        for index, album in enumerate(user_albums):
            self.album_list.append(album)
            self.albums_table.setItem(index, ALBUM_TITLE, unmodifiable(album.get_name()))
            self.albums_table.setItem(index, ALBUM_GENRE, unmodifiable(album.get_genre()))
            self.albums_table.setItem(index, ALBUM_YEAR, unmodifiable(str(album.get_year())))

    def open_album(self, i, j):
        print("hey")
        album = self.album_list[i]
        widget = AlbumWidget(self.user, album)
        widget.show()


def format_timedelta(delta):
    minutes = delta.seconds // 60
    seconds = delta.seconds - minutes * 60
    return f"{minutes:02d}:{seconds:02d}"


class AlbumWidget(QWidget):
    def __init__(self, username, album, parent=None):
        super(AlbumWidget, self).__init__(parent)
        uic.loadUi('design/album.ui', self)
        self.playlist = QtMultimedia.QMediaPlaylist()
        self.current_index = 0
        self.player = QtMultimedia.QMediaPlayer()
        self.is_playing = False
        self.username = username
        self.album = album
        self.initUi()

    def initUi(self):
        self.album_name.setText(self.album.get_name())
        self.album_year.setText(str(self.album.get_year()))
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

    def load_tracks(self):
        album_folder = QtCore.QDir.current().absolutePath() + "/albums/" + f"album_{self.album.album_id}/"

        songs = self.album.get_songs()
        for song in songs:
            url = QtCore.QUrl.fromLocalFile(album_folder + f"track_{song.song_id}.mp3")
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
        self.player.stop()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    sgp_mix = Album(1, "SPACEGHOSTPURRP AUTUMN MIXX", "DARKTRAP", 2021,
                    [Song(1, "MIXX", 27), Song(2, "everybody acting like a gangster", 30)])
    blackland_radio_pt2 = Album(2, "BLACKLAND 2 EPISODE 1 , EP (2016)", "DARKTRAP", 2016, [
        Song(1, "OPPRESSION (INTRO)"), Song(2, "PURRP THE KING OF KINGS"), Song(3, "T.R.I.L.L"), Song(4, "GOTH SEASON"),
        Song(5, "REVENGE 2"), Song(6, "BETTER DAYZ"), Song(7, "BIG TYMER 2K16"), Song(8, "BOSS MOB RBMG"),
        Song(9, "NONCHALANT MUSIC"), Song(10, " SO ICEY GOTH LA FLEXICOS")
    ], cover="./blacklandradiopt2.jpg")

    ex = AlbumWidget(
        User(1, "spaceghostpurrp", "sex", "nothing",
             [blackland_radio_pt2],
             avatar="dot.jpg"), blackland_radio_pt2)
    ex.show()
    sys.exit(app.exec())
