'''
    qobuz.node.similar_artist
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    :part_of: xbmc-qobuz
    :copyright: (c) 2012-2016 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
from qobuz.node.inode import INode
from qobuz.node import getNode, Flag
from qobuz.gui.util import lang
from qobuz.api import api
from qobuz import config
from qobuz import debug


class Node_similar_artist(INode):
    def __init__(self, parent=None, parameters={}, data=None):
        super(Node_similar_artist, self).__init__(
            parent=parent, parameters=parameters, data=data)
        self.nt = Flag.SIMILAR_ARTIST
        self.content_type = 'artists'
        self.lang = lang(30156)

    def fetch(self, *a, **ka):
        return api.get('/artist/getSimilarArtists',
                       artist_id=self.nid,
                       offset=self.offset,
                       limit=self.limit)

    def _count(self):
        return len(self.data['artists']['items'])

    def populate(self, *a, **ka):
        for data in self.data['artists']['items']:
            if not config.app.registry.get('display_artist_without_album',
                                           to='bool'):
                if data['albums_count'] <= 0:
                    continue
            artist = getNode(Flag.ARTIST, data=data)
            cache = artist.fetch(noRemote=True)
            if cache is not None:
                #debug.info(self, 'From cache {}', cache)
                artist.data = cache
            self.add_child(artist)
        return True if len(self.data['artists']['items']) > 0 else False
