'''
    qobuz.node.similar_artist
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    :part_of: kodi-qobuz
    :copyright: (c) 2012-2018 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
from qobuz import config
from qobuz.api import api
from qobuz.gui.util import lang
from qobuz.node import getNode, Flag
from qobuz.node.inode import INode


class Node_similar_artist(INode):
    def __init__(self, parent=None, parameters=None, data=None):
        parameters = {} if parameters is None else parameters
        super(Node_similar_artist, self).__init__(
            parent=parent, parameters=parameters, data=data)
        self.nt = Flag.SIMILAR_ARTIST
        self.content_type = 'artists'
        self.lang = lang(30156)

    def fetch(self, options=None):
        return api.get('/artist/getSimilarArtists',
                       artist_id=self.nid,
                       offset=self.offset,
                       limit=self.limit)

    def _count(self):
        return len(self.data['artists']['items'])

    def populate(self, options=None):
        skip_empty = not config.app.registry.get(
            'display_artist_without_album', to='bool')
        for data in self.data['artists']['items']:
            if skip_empty and data['albums_count'] < 1:
                continue
            artist = getNode(Flag.ARTIST, data=data)
            cache = artist.fetch(noRemote=True)
            if cache is not None:
                artist.data = cache
            self.add_child(artist)
        return True if len(self.data['artists']['items']) > 0 else False
