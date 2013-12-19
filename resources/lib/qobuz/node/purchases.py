'''
    qobuz.node.purchases
    ~~~~~~~~~~~~~~~~~~~~

    :part_of: xbmc-qobuz
    :copyright: (c) 2012 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
from inode import INode
from debug import warn
from api import api
from node import Flag, getNode
from gui.util import lang, getImage, getSetting


class Node_purchases(INode):
    '''Displaying product purchased by user (track and album)
    '''
    def __init__(self, parent=None, parameters=None):
        super(Node_purchases, self).__init__(parent, parameters)
        self.label = lang(30101)
        self.nt = Flag.PURCHASES
        self.content_type = 'albums'
        self.image = getImage('album')
        self.offset = self.get_parameter('offset') or 0

    def fetch(self, Dir, lvl, whiteFlag, blackFlag):
        limit = getSetting('pagination_limit')
        data = api.get('/purchase/getUserPurchases', limit=limit,
                           offset=self.offset, user_id=api.user_id)
        if not data:
            warn(self, "Cannot fetch purchases data")
            return False
        self.data = data
        return True

    def populate(self, Dir, lvl, whiteFlag, blackFlag):
        if 'albums' in self.data:
            self.__populate_albums(Dir, lvl, whiteFlag, blackFlag)
        elif 'tracks' in self.data:
            self.__populate_tracks(Dir, lvl, whiteFlag, blackFlag)

    def __populate_albums(self, Dir, lvl, whiteFlag, blackFlag):
        for album in self.data['albums']['items']:
            node = getNode(Flag.ALBUM)
            node.data = album
            self.add_child(node)
        return list

    def __populate_tracks(self, Dir, lvl, whiteFlag, blackFlag):
        for track in self.data['tracks']['items']:
            node = getNode(Flag.TRACK)
            node.data = track
            self.add_child(node)
        return list
