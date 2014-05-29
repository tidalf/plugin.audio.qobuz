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
from qobuz.i8n import _


class Node_purchases(INode):
    '''Displaying product purchased by user (track and album)
    '''
    def __init__(self, properties={}):
        super(Node_purchases, self).__init__(properties)
        self.kind = Flag.PURCHASES
        self.label = _('Purchases')
        self.content_type = 'albums'

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
        ret = False
        if 'albums' in self.data:
            if self.__populate_albums():
                ret = True
        if 'tracks' in self.data:
            if self.__populate_tracks():
                ret = True
        return ret

    def __populate_albums(self):
        for album in self.data['albums']['items']:
            node = getNode(Flag.ALBUM, self.parameters)
            node.data = album
            self.append(node)
        return True

    def __populate_tracks(self):
        for track in self.data['tracks']['items']:
            node = getNode(Flag.TRACK, self.parameters)
            node.data = track
            self.append(node)
        return True
