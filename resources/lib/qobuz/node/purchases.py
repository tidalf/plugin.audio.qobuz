'''
    qobuz.node.purchases
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    This file is part of qobuz-xbmc

    :copyright: (c) 2012 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
from inode import INode
from qobuz.debug import warn
from qobuz.api import api
from qobuz.node import Flag, getNode
from xbmcpy.util import lang, getImage

class Node_purchases(INode):
    '''Displaying product purchased by user (track and album)
    '''
    def __init__(self, properties = {}):
        super(Node_purchases, self).__init__(properties)
        self.kind = Flag.PURCHASES
        self.label = lang(30002)
        self.content_type = 'albums'
        self.image = getImage('album')
        self.offset = self.get_property('offset') or 0

    def fetch(self, renderer=None):
        data = api.get('/purchase/getUserPurchases', 
                       limit=api.pagination_limit, offset=self.offset, 
                       user_id=api.user_id)
        if not data:
            warn(self, "Cannot fetch purchases data")
            return False
        self.data = data
        return True

    def populate(self, renderer=None):
        if 'albums' in self.data:
            self.__populate_albums()
        elif 'tracks' in self.data:
            self.__populate_tracks()

    def __populate_albums(self):
        for album in self.data['albums']['items']:
            node = getNode(Flag.ALBUM, self.parameters)
            node.data = album
            self.append(node)
        return list

    def __populate_tracks(self):
        for track in self.data['tracks']['items']:
            node = getNode(Flag.TRACK, self.parameters)
            node.data = track
            self.append(node)
        return True
