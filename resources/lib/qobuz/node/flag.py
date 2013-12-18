'''
    qobuz.node.flag
    ~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2012 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''

from exception import QobuzXbmcError
from debug import warn


class __Flag__():
    NODE = 1 << 1
    TRACK = 1 << 2
    PLAYLIST = 1 << 3
    USERPLAYLISTS = 1 << 4
    RECOMMENDATION = 1 << 5
    ROOT = 1 << 6
    ALBUM = 1 << 7
    PURCHASES = 1 << 8
    SEARCH = 1 << 9
    ARTIST = 1 << 10
    SIMILAR_ARTIST = 1 << 11
    FAVORITES = 1 << 12
    FRIEND = 1 << 13
    FRIEND_LIST = 1 << 14
    GENRE = 1 << 15
    LABEL = 1 << 16
    ALBUMS = 1 << 17
    ARTICLES = 1 << 18
    ARTICLE = 1 << 19
    ARTICLE_RUBRICS = 1 << 20
    ALBUMS_BY_ARTIST = 1 << 21
    PUBLIC_PLAYLISTS = 1 << 22
    COLLECTION = 1 << 23

    STOPBUILD = 1 << 100
    NONE = 1 << 101

    def __init__(self):

        self.totalFlag = 23
        self.ALL = 0
        for i in range(1, self.totalFlag + 1):
            self.ALL |= (1 << i)

    def to_s(self, flag):
        if not flag:
            warn(self, "Missing flag parameter")
            return ''
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
        elif flag & self.SEARCH == self.SEARCH:
            return "search"
        elif flag & self.ARTIST == self.ARTIST:
            return "artist"
        elif flag & self.SIMILAR_ARTIST == self.SIMILAR_ARTIST:
            return "similar_artist"
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
        elif flag & self.COLLECTION == self.COLLECTION:
            return "collection"
        else:
            raise QobuzXbmcError(
                who=self, what='invalid_flag', additional=repr(flag))

Flag = __Flag__()
