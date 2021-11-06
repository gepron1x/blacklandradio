import shutil


from api import AlbumTemplate, Song, Album, User, Genre, DEFAULT_IMAGE_FILE


class BlackLandDatabase:
    def __init__(self, connection):
        self.connection = connection

    def initialize(self):
        cur = self.connection.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS users ("
                    "id INTEGER NOT NULL, "
                    "username VARCHAR(40) NOT NULL UNIQUE,"
                    "password VARCHAR(60) NOT NULL,"
                    "description TINYTEXT,"
                    "avatar TINYTEXT,"
                    "PRIMARY KEY(id)"
                    ")")
        cur.execute("CREATE TABLE IF NOT EXISTS albums ("
                    "id INTEGER NOT NULL,"
                    "user_id INTEGER NOT NULL,"
                    "name VARCHAR(60) NOT NULL,"
                    "genre INTEGER NOT NULL,"
                    "year  INTEGER NOT NULL,"
                    "cover TINYTEXT,"
                    "PRIMARY KEY(id)"
                    ")"
                    )
        cur.execute("CREATE TABLE IF NOT EXISTS songs ("
                    "id INTEGER NOT NULL,"
                    "album_id INTEGER NOT NULL,"
                    "name VARCHAR(60),"
                    "file TINYTEXT NOT NULL,"
                    "PRIMARY KEY(id)"
                    ")")
        cur.execute("CREATE TABLE IF NOT EXISTS genres ("
                    "id INTEGER NOT NULL,"
                    "name VARCHAR(60) NOT NULL UNIQUE,"
                    "PRIMARY KEY(id AUTOINCREMENT)"
                    ")")
        self.connection.commit()

    def account_exists(self, username):
        cur = self.connection.cursor()
        rs = cur.execute("SELECT * FROM users WHERE username=?", (username,)).fetchall()
        return len(rs) != 0

    def create_account(self, user):
        cur = self.connection.cursor()
        cur.execute("INSERT INTO users(id, username, password, description, avatar) VALUES (?, ?, ?, ?, ?)",
                    (user.get_id(), user.get_username(), user.get_password(),
                     user.get_description(), user.get_avatar()))
        self.connection.commit()

    def check_password(self, username, password):
        cur = self.connection.cursor()
        rs = cur.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password)).fetchall()
        return len(rs) != 0

    def load_user(self, username):
        cur = self.connection.cursor()
        rs = cur.execute("SELECT U.id, U.username, U.password, U.description, U.avatar, "
                         "A.id, A.name, G.id, G.name, A.year, A.cover, "
                         "S.id, S.name, S.file "
                         "FROM users as U "
                         "LEFT JOIN albums as A ON U.id = A.user_id "
                         "LEFT JOIN genres as G ON A.genre = G.id "
                         "LEFT JOIN songs as S ON A.id = S.album_id WHERE U.username=?",
                         (username,)).fetchall()
        if len(rs) == 0:
            return None

        first = rs[0]
        user_id = first[0]
        password = first[2]
        description = first[3]
        avatar = first[4]
        albums = {}
        for results in rs:
            if all(map(lambda r: r is None, results[5:12])):  # it seems that user don't have any albums
                continue
            album_id = results[5]
            album_name = results[6]
            album_genre = Genre(results[7], results[8])
            album_year = results[9]
            album_cover = results[10]

            song_id = results[11]
            song_name = results[12]
            song_file = results[13]

            album = albums.get(album_id, None)
            if album is None:
                album = Album(album_id, album_name, album_genre, album_year, list(), cover=album_cover)
            album.add_song(Song(song_id, song_name, song_file))
            albums[album_id] = album

        return User(user_id, username, password, description, list(albums.values()), avatar=avatar)

    def load_album_templates(self):
        cur = self.connection.cursor()
        results = cur.execute("SELECT A.id, U.username, A.name, A.year, A.cover "
                              "FROM albums as A JOIN users AS U ON A.user_id = U.id").fetchall()
        return list(map(lambda r: AlbumTemplate(r[0], r[1], r[2], r[3], r[4]), results))

    def load_album(self, album_id):
        cur = self.connection.cursor()
        results = cur.execute("SELECT A.name, A.year, A.cover, G.id, G.name, S.id, S.name, S.file "
                              "FROM albums AS A "
                              "JOIN songs AS S ON A.id = S.album_id "
                              "JOIN genres AS G ON A.genre = G.id "
                              "WHERE A.id=?",
                              (album_id,)).fetchall()
        first = results[0]
        album_name = first[0]
        album_year = first[1]
        album_cover = first[2]
        album_genre = Genre(first[3], first[4])
        songs = list()
        for result in results:
            if all(map(lambda r: r is None, result[4:8])):  # no songs
                continue
            song_id = result[5]
            song_name = result[6]
            song_file = result[7]
            songs.append(Song(song_id, song_name, song_file))
        return Album(album_id, album_name, album_genre, album_year, songs, cover=album_cover)

    def save_album(self, user_id, album):
        cur = self.connection.cursor()
        album_id = album.get_id()
        cur.execute("INSERT INTO albums (id, user_id, name, genre, year, cover) VALUES(?, ?, ?, ?, ?, ?)",
                    (album_id, user_id, album.get_name(),
                     album.get_genre().get_id(), album.get_year(), album.get_cover()))
        cur.executemany("INSERT INTO songs (id, album_id, name, file) VALUES (?, ?, ?, ?)",
                        list(map(lambda s: (s.get_id(), album_id, s.get_name(), s.get_file()), album.get_songs())))
        self.connection.commit()

    def load_genres(self):
        cur = self.connection.cursor()
        return list(map(lambda t: Genre(t[0], t[1]), cur.execute("SELECT * FROM genres").fetchall()))

    def add_genres(self, *genres):
        cur = self.connection.cursor()
        # lol
        cur.executemany("INSERT OR IGNORE INTO genres (name) VALUES (?)", list(map(lambda g: (g,), genres)))

    def genre_exists(self, name):
        cur = self.connection.cursor()
        return len(cur.execute("SELECT * FROM genres WHERE name=?", (name,)).fetchall()) != 0

    def shutdown(self):
        self.connection.close()

    def user_editor(self, user):
        return UserEditor(self.connection, user)


class Editor:
    def __init__(self, connection):
        self.connection = connection

    def finish(self):
        self.connection.commit()


class UserEditor(Editor):

    def __init__(self, connection, user):
        super().__init__(connection)
        self.user = user

    def set_avatar(self, avatar):
        cursor = self.connection.cursor()
        cursor.execute("UPDATE users SET avatar=? WHERE id=?", (avatar, self.user.get_id()))

    def set_description(self, description):
        cursor = self.connection.cursor()
        cursor.execute("UPDATE users SET description=? WHERE id=?", (description, self.user.get_id()))

    def remove_album(self, album_id):
        cursor = self.connection.cursor()
        cursor.execute("DELETE FROM albums WHERE id=?", (album_id,))
        cursor.execute("DELETE FROM songs WHERE album_id=?", (album_id,))

    def finish(self):
        super().finish()
