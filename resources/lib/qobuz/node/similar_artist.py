'''
    qobuz.node.similar_artist
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    :part_of: xbmc-qobuz
    :copyright: (c) 2012 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
from qobuz.node.inode import INode
from qobuz.node import getNode, Flag
from qobuz.gui.util import lang, getSetting
from qobuz.api import api


class Node_similar_artist(INode):
    """NODE ARTIST
    """

    def __init__(self, parent=None, parameters={}, data=None):
        super(Node_similar_artist, self).__init__(parent=parent,
                                                  parameters=parameters,
                                                  data=data)
        self.nt = Flag.SIMILAR_ARTIST
        self.content_type = 'artists'

    def get_label(self):
        return lang(30156)

    def fetch(self, Dir, lvl, whiteFlag, blackFlag):
        data = api.get('/artist/getSimilarArtists', artist_id=self.nid,
                       offset=self.offset, limit=self.limit)
        if not data:
            return False
        self.data = data
        return len(data['artists']['items'])

    def populate(self, Dir, lvl, whiteflag, blackFlag):
        for aData in self.data['artists']['items']:
            artist = getNode(Flag.ARTIST)
            artist.data = aData
            self.add_child(artist)
        return True
