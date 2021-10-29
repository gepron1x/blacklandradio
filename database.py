from user import AlbumTemplate, Song, Album


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
                    "PRIMARY KEY(id AUTOINCREMENT)"
                    ")")
        cur.execute("CREATE TABLE IF NOT EXISTS albums ("
                    "id INTEGER NOT NULL,"
                    "user_id INTEGER NOT NULL,"
                    "name VARCHAR(60) NOT NULL,"
                    "genre INTEGER NOT NULL,"
                    "year  INTEGER NOT NULL,"
                    "cover TINYTEXT,"
                    "PRIMARY KEY(id AUTOINCREMENT)"
                    ")"
                    )
        cur.execute("CREATE TABLE IF NOT EXISTS songs ("
                    "id INTEGER NOT NULL,"
                    "album_id INTEGER NOT NULL,"
                    "name VARCHAR(60),"
                    "PRIMARY KEY(id AUTOINCREMENT)"
                    ")")
        cur.execute("CREATE TABLE IF NOT EXISTS genres ("
                    "id INTEGER NOT NULL,"
                    "name VARCHAR(60) NOT NULL,"
                    "PRIMARY KEY(id AUTOINCREMENT)"
                    ")")
        self.connection.commit()

    def account_exists(self, username):
        cur = self.connection.cursor()
        rs = cur.execute("SELECT * FROM users WHERE username=?", (username,)).fetchall()
        return len(rs) != 0

    def create_account(self, username, password):
        cur = self.connection.cursor()
        cur.execute("INSERT INTO users(username, password, description, avatar) VALUES (?, ?, ?, ?)",
                    (username, password, "", DEFAULT_IMAGE_FILE))
        self.connection.commit()

    def check_password(self, username, password):
        cur = self.connection.cursor()
        rs = cur.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password)).fetchall()
        return len(rs) != 0

    def load_user(self, username):
        cur = self.connection.cursor()
        rs = cur.execute("SELECT U.id, U.username, U.password, U.description, U.avatar, "
                         "A.id, A.name, A.genre, A.year, A.cover, "
                         "S.id, S.name "
                         "FROM users as U "
                         "JOIN albums as A ON U.id = A.user_id "
                         "JOIN songs as S ON A.id = S.album_id WHERE U.username=?",
                         (username,)).fetchall()
        print(rs)
        first = rs[0]
        user_id = first[0]
        password = first[2]
        description = first[3]
        avatar = first[4]
        albums = {}
        for results in rs:
            album_id = results[5]
            album_name = results[6]
            album_genre = results[7]
            album_year = results[8]
            album_cover = results[9]

            song_id = results[10]
            song_name = results[11]

            album = albums.get(album_id, None)
            if album is None:
                album = Album(album_id, album_name, album_genre, album_year, list(), cover=album_cover)
            album.add_song(Song(song_id, song_name))
            albums[album_id] = album

        return User(user_id, username, password, description, list(albums.values()), avatar=avatar)

    def load_album_templates(self):
        cur = self.connection.cursor()
        results = cur.execute("SELECT A.id, U.username, A.name, A.year, A.cover "
                              "FROM albums as A JOIN users AS U ON A.user_id = U.id")
        return list(map(lambda r: AlbumTemplate(r[0], r[1], r[2], r[3], r[4]), results))

    def load_album(self, album_id):
        cur = self.connection.cursor()
        results = cur.execute("SELECT A.name, A.genre, A.year, A.cover, S.id, S.name "
                              "FROM albums AS A JOIN songs AS S ON A.id = S.album_id WHERE A.id=?",
                              (album_id,)).fetchall()
        first = results[0]
        album_name = first[0]
        album_genre = first[1]
        album_year = first[2]
        album_cover = first[3]
        songs = list()
        for result in results:
            print(result)
            song_id = result[4]
            song_name = result[5]
            songs.append(Song(song_id, song_name))
        return Album(album_id, album_name, album_genre, album_year, songs, cover=album_cover)

    def shutdown(self):
        self.connection.close()
