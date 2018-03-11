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
        ''' Convert flag (int) to string '''
        return flag_to_string(flag)

    @classmethod
    def flag_from_string(cls, text):
        ''' Convert string to flag (int) '''
        for flag, value in FLAG_STRING.items():
            if value == text:
                return flag
        return None


FLAG_STRING = {
    FlagEnum.ALBUM: 'album',
    FlagEnum.ALBUMS: 'albums',
    FlagEnum.ALBUMS_BY_ARTIST: 'albums_by_artist',
    FlagEnum.ARTICLE: 'article',
    FlagEnum.ARTICLES: 'articles',
    FlagEnum.ARTICLE_RUBRICS: 'article_rubrics',
    FlagEnum.ARTIST: 'artist',
    FlagEnum.COLLECTION: 'collection',
    FlagEnum.FAVORITE: 'favorite',
    FlagEnum.FRIEND: 'friend',
    FlagEnum.FRIENDS: 'friends',
    FlagEnum.GENRE: 'genre',
    FlagEnum.LABEL: 'label',
    FlagEnum.NODE: 'node',
    FlagEnum.NONE: 'none',
    FlagEnum.PLAYLIST: 'playlist',
    FlagEnum.PUBLIC_PLAYLISTS: 'public_playlists',
    FlagEnum.PURCHASE: 'purchase',
    FlagEnum.RECOMMENDATION: 'recommendation',
    FlagEnum.ROOT: 'root',
    FlagEnum.SEARCH: 'search',
    FlagEnum.SIMILAR_ARTIST: 'similar_artist',
    FlagEnum.STOPBUILD: 'stop_build_down',
    FlagEnum.TESTING: 'testing',
    FlagEnum.TEXT: 'text',
    FlagEnum.TRACK: 'track',
    FlagEnum.USER: 'user',
    FlagEnum.USERPLAYLISTS: 'user_playlists',
}


def flag_to_string(flag):
    ''' Return string from integer flag '''
    cls = FlagEnum
    if not flag:
        logger.warn(cls, 'Missing flag parameter')
        return ''
    flag = int(flag)
    return FLAG_STRING[flag]


Flag = FlagEnum()
