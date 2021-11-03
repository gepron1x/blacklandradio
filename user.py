

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

    def get_id(self):
        return self.user_id

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
    def __init__(self, song_id, name, file):
        self.song_id = song_id
        self.name = name
        self.file = file

    def get_id(self):
        return self.song_id

    def get_name(self):
        return self.name

    def get_file(self):
        return self.file

    def __str__(self):
        return f"Song {self.name} [" \
               f"id: {self.song_id}," \
               f"file: {self.file}]"

    def __hash__(self):
        return hash((self.song_id, self.name, self.file))


class Genre:
    def __init__(self, genre_id, name):
        self.genre_id = genre_id
        self.name = name

    def get_id(self):
        return self.genre_id

    def get_name(self):
        return self.name


class Album:
    def __init__(self, album_id, name, genre, year, songs, cover=DEFAULT_COVER):
        self.album_id = album_id
        self.year = year
        self.name = name
        self.genre = genre
        self.songs = songs
        self.cover = cover

    def get_id(self):
        return self.album_id

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

    def __hash__(self):
        return hash((self.album_id, self.username, self.name, self.year, self.cover))

