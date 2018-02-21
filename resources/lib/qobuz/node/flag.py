'''
    qobuz.node.flag
    ~~~~~~~~~~~~~~~

    :part_of: xbmc-qobuz
    :copyright: (c) 2012-2016 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
from qobuz import exception
from qobuz.debug import getLogger
logger = getLogger(__name__)

class FlagEnum(object):
    NODE = 1 << 1
    TRACK = 1 << 2
    PLAYLIST = 1 << 3
    USERPLAYLISTS = 1 << 4
    RECOMMENDATION = 1 << 5
    ROOT = 1 << 6
    ALBUM = 1 << 7
    SEARCH = 1 << 8
    ARTIST = 1 << 9
    SIMILAR_ARTIST = 1 << 10
    FRIEND = 1 << 11
    FRIENDS = 1 << 12
    GENRE = 1 << 13
    LABEL = 1 << 14
    ALBUMS = 1 << 15
    ARTICLES = 1 << 16
    ARTICLE = 1 << 17
    ARTICLE_RUBRICS = 1 << 18
    ALBUMS_BY_ARTIST = 1 << 19
    PUBLIC_PLAYLISTS = 1 << 20
    COLLECTION = 1 << 21
    FAVORITE = 1 << 22
    PURCHASE = 1 << 23
    TESTING = 1 << 24
    TEXT = 1 << 25
    USER = 1 << 26

    STOPBUILD = 1 << 100
    NONE = 1 << 101

    def __init__(self):
        self.totalFlag = 26
        self.ALL = 0
        for i in range(1, self.totalFlag + 1):
            self.ALL |= (1 << i)

    @classmethod
    def to_s(cls, flag):
        if not flag:
            logger.warn(cls, 'Missing flag parameter')
            return ''
        flag = int(flag)
        if flag & cls.TRACK == cls.TRACK:
            return 'track'
        elif flag & cls.PLAYLIST == cls.PLAYLIST:
            return 'playlist'
        elif flag & cls.USERPLAYLISTS == cls.USERPLAYLISTS:
            return 'user_playlists'
        elif flag & cls.RECOMMENDATION == cls.RECOMMENDATION:
            return 'recommendation'
        elif flag & cls.ROOT == cls.ROOT:
            return 'root'
        elif flag & cls.ALBUM == cls.ALBUM:
            return 'album'
        elif flag & cls.PURCHASE == cls.PURCHASE:
            return 'purchase'
        elif flag & cls.FAVORITE == cls.FAVORITE:
            return 'favorite'
        elif flag & cls.SEARCH == cls.SEARCH:
            return 'search'
        elif flag & cls.ARTIST == cls.ARTIST:
            return 'artist'
        elif flag & cls.SIMILAR_ARTIST == cls.SIMILAR_ARTIST:
            return 'similar_artist'
        elif flag & cls.FRIEND == cls.FRIEND:
            return 'friend'
        elif flag & cls.FRIENDS == cls.FRIENDS:
            return 'friends'
        elif flag & cls.GENRE == cls.GENRE:
            return 'genre'
        elif flag & cls.LABEL == cls.LABEL:
            return 'label'
        elif flag & cls.NODE == cls.NODE:
            return 'inode'
        elif flag & cls.STOPBUILD == cls.STOPBUILD:
            return 'stop_build_down'
        elif flag & cls.ARTICLES == cls.ARTICLES:
            return 'articles'
        elif flag & cls.ARTICLE == cls.ARTICLE:
            return 'article'
        elif flag & cls.PUBLIC_PLAYLISTS == cls.PUBLIC_PLAYLISTS:
            return 'public_playlists'
        elif flag & cls.ARTICLE_RUBRICS == cls.ARTICLE_RUBRICS:
            return 'article_rubrics'
        elif flag & cls.ALBUMS_BY_ARTIST == cls.ALBUMS_BY_ARTIST:
            return 'albums_by_artist'
        elif flag & cls.COLLECTION == cls.COLLECTION:
            return 'collection'
        elif flag & cls.TESTING == cls.TESTING:
            return 'testing'
        elif flag & cls.TEXT == cls.TEXT:
            return 'text'
        elif flag & cls.USER == cls.USER:
            return 'user'
        else:
            raise exception.InvalidFlag(repr(flag))


Flag = FlagEnum()
