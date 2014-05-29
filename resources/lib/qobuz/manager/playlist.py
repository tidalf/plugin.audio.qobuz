'''
    qobuz.manager.playlist
    ~~~~~~~~~~~~~~~~~~~~~~

    :part_of: xbmc-qobuz
    :copyright: (c) 2012 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''


class BaseManager(object):
    pass


class PlaylistManager(BaseManager):

    def exists(self, pid):
        pass

    def create(self, name, tracks):
        pass

    def delete(self, pid):
        pass
