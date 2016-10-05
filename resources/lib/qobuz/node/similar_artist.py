'''
    qobuz.node.similar_artist
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    :part_of: xbmc-qobuz
    :copyright: (c) 2012-2016 by Joachim Basmaison, Cyril Leclerc
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

    def get_label(self, default=None):
        return lang(30156)

    def fetch(self, Dir, lvl, whiteFlag, blackFlag):
        return api.get('/artist/getSimilarArtists', artist_id=self.nid,
                       offset=self.offset, limit=self.limit)

    def populate(self, Dir, lvl, whiteflag, blackFlag):
        for data in self.data['artists']['items']:
            artist = getNode(Flag.ARTIST, data=data)
            self.add_child(artist)
        return True
