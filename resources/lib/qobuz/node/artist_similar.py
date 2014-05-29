'''
    qobuz.node.similar_artist
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    This file is part of qobuz-xbmc

    :copyright: (c) 2012 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
from inode import INode
from qobuz.node import getNode, Flag
from qobuz.api import api
from qobuz.i8n import _


class Node_artist_similar(INode):

    def __init__(self, parameters={}):
        super(Node_artist_similar, self).__init__(parameters)
        self.kind = Flag.ARTIST_SIMILAR
        self.label = _('Similar artists')
        self.content_type = 'artists'
        self.items_path = 'artists'

    def fetch(self, renderer=None):
        data = api.get('/artist/getSimilarArtists', artist_id=self.nid,
                           offset=self.offset, limit=api.pagination_limit)
        print "GOT DATA %s" % data
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
