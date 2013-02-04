'''
    qobuz.node.friend_list
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    This file is part of qobuz-xbmc

    :copyright: (c) 2012 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''

class __Flag__():
    def __init__(self):
        self.NODE = 1 << 1
        self.TRACK = 1 << 2
        self.PLAYLIST = 1 << 3
        self.USERPLAYLISTS = 1 << 4
        self.RECOMMENDATION = 1 << 5
        self.ROOT = 1 << 6
        self.ALBUM = 1 << 7
        self.PURCHASES = 1 << 8
        self.SEARCH = 1 << 9
        self.ARTIST = 1 << 10
        self.SIMILAR_ARTIST = 1 << 11
        self.FAVORITES = 1 << 12
        self.FRIEND = 1 << 13
        self.FRIEND_LIST = 1 << 14
        self.GENRE = 1 << 15
        self.LABEL = 1 << 16
        self.ALBUMS = 1 << 17
        self.ARTICLES = 1 << 18
        self.ARTICLE = 1 << 19
        self.ARTICLE_RUBRICS = 1 << 20
        self.ALBUMS_BY_ARTIST = 1 << 21
        self.PUBLIC_PLAYLISTS = 1 << 22
        self.STOPBUILD = 1 <<  100
        self.NONE = 1 << 101

        self.totalFlag = 22
        self.ALL = 0
        for i in range(1, self.totalFlag+1):
            self.ALL |= (1 << i)

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
        else:
            raise Exception('invalid_flag')

Flag = __Flag__()