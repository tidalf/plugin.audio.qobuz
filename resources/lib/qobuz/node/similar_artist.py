'''
    qobuz.node.similar_artist
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    This file is part of qobuz-xbmc

    :copyright: (c) 2012 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
from inode import INode
from qobuz.node import getNode, Flag
from xbmcpy.util import lang
from qobuz.api import api

'''
    NODE ARTIST
'''

class Node_similar_artist(INode):

    def __init__(self, parameters={}):
        super(Node_similar_artist, self).__init__(parameters)
        self.kind = Flag.SIMILAR_ARTIST
        self.content_type = 'artists'
        self.items_path = 'artists'

    def get_label(self):
        return lang(30010)

    def fetch(self, renderer=None):
        data = api.get('/artist/getSimilarArtists', artist_id=self.nid, 
                           offset=self.offset, limit=api.pagination_limit)
        if not data:
            return False
        self.data = data
        return True

    def populate(self, renderer=None):
        for data in self.data[self.items_path]['items']:
            artist = getNode(Flag.ARTIST, {'nid': data['id']})
            artist.data = data
            self.append(artist)
        return True
