'''
    qobuz.node.friend_list
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    This file is part of qobuz-xbmc

    :copyright: (c) 2012 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''


class __Flag__():

    def __init__(self):
        self.count = 0

        self.NODE = self._gv()
        self.TRACK = self._gv()
        self.PLAYLIST = self._gv()
        self.USERPLAYLISTS = self._gv()
        self.RECOMMENDATION = self._gv()
        self.ROOT = self._gv()
        self.ALBUM = self._gv()
        self.PURCHASES = self._gv()
        self.SEARCH = self._gv()
        self.ARTIST = self._gv()
        self.ARTIST_SIMILAR = self._gv()
        self.FAVORITES = self._gv()
        self.FRIEND = self._gv()
        self.FRIEND_LIST = self._gv()
        self.GENRE = self._gv()
        self.LABEL = self._gv()
        self.ALBUMS = self._gv()
        self.ARTICLES = self._gv()
        self.ARTICLE = self._gv()
        self.ARTICLE_RUBRICS = self._gv()
        self.ALBUMS_BY_ARTIST = self._gv()
        self.PUBLIC_PLAYLISTS = self._gv()
        self.FAVORITE = self._gv()

        self.STOPBUILD = 1 << 100
        self.NONE = 1 << 101

        self.ALL = 0
        for i in range(1, self.count + 1):
            self.ALL |= (1 << i)

    def _gv(self):
        self.count += 1
        return 1 << self.count

    def to_s(self, flag):
        if not flag:
            raise Exception("Missing flag parameter")
        flag = int(flag)
        if flag & self.TRACK == self.TRACK:
            return "track"
        elif flag & self.PLAYLIST == self.PLAYLIST:
            return "playlist"
        elif flag & self.USERPLAYLISTS == self.USERPLAYLISTS:
            return "user_playlists"
        elif flag & self.RECOMMENDATION == self.RECOMMENDATION:
            return "recommendation"
        elif flag & self.ROOT == self.ROOT:
            return "root"
        elif flag & self.ALBUM == self.ALBUM:
            return "album"
        elif flag & self.PURCHASES == self.PURCHASES:
            return "purchases"
        elif flag & self.FAVORITES == self.FAVORITES:
            return "favorites"
        elif flag & self.FAVORITE == self.FAVORITE:
            return "favorite"
        elif flag & self.SEARCH == self.SEARCH:
            return "search"
        elif flag & self.ARTIST == self.ARTIST:
            return "artist"
        elif flag & self.ARTIST_SIMILAR == self.ARTIST_SIMILAR:
            return "artist_similar"
        elif flag & self.FRIEND == self.FRIEND:
            return "friend"
        elif flag & self.FRIEND_LIST == self.FRIEND_LIST:
            return "friend_list"
        elif flag & self.GENRE == self.GENRE:
            return "genre"
        elif flag & self.LABEL == self.LABEL:
            return "label"
        elif flag & self.NODE == self.NODE:
            return "inode"
        elif flag & self.STOPBUILD == self.STOPBUILD:
            return "stop_build_down"
        elif flag & self.ARTICLES == self.ARTICLES:
            return "articles"
        elif flag & self.ARTICLE == self.ARTICLE:
            return "article"
        elif flag & self.PUBLIC_PLAYLISTS == self.PUBLIC_PLAYLISTS:
            return "public_playlists"
        elif flag & self.ARTICLE_RUBRICS == self.ARTICLE_RUBRICS:
            return "article_rubrics"
        elif flag & self.ALBUMS_BY_ARTIST == self.ALBUMS_BY_ARTIST:
            return "albums_by_artist"
        else:
            raise Exception('invalid_flag')

Flag = __Flag__()
