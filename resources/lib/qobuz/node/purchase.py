'''
    qobuz.node.purchase
    ~~~~~~~~~~~~~~~~~~~

    :part_of: xbmc-qobuz
    :copyright: (c) 2012-2016 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
from qobuz.node.inode import INode
from qobuz import debug
from qobuz.api import api
from qobuz.node import Flag, getNode
from qobuz.gui.util import lang, getImage
from qobuz.api.user import current as user

class Node_purchase(INode):
    '''Displaying product purchased by user (track and album)
    '''

    def __init__(self, parent=None, parameters={}, data=None):
        super(Node_purchase, self).__init__(parent=parent,
                                            parameters=parameters,
                                            data=data)
        self.nt = Flag.PURCHASE
        self.image = getImage('album')
        self.content_type = 'albums'
        self.search_type = self.get_parameter('search-type')

    def get_label(self):
        if self.search_type is None:
            return lang(30101)
        elif self.search_type == 'all':
            return  '%s - %s' % (lang(30101), lang(30098))
        return '%s - %s' % (lang(30101),
                                  self.search_type.capitalize())

    def make_url(self, **ka):
        if self.search_type:
            ka['search-type'] = str(self.search_type)
            ka['purchased'] = 1
        return super(Node_purchase, self).make_url(**ka)

    def fetch(self, Dir, lvl, whiteFlag, blackFlag):
        if self.search_type is None:
            return {}
        return api.get('/purchase/getUserPurchases', limit=self.limit,
                       offset=self.offset, user_id=user.get_id())

    def populate(self, Dir, lvl, whiteFlag, blackFlag):
        if self.search_type is None:
            for search_type in ['all', 'albums', 'tracks']:
                self.add_child(getNode(Flag.PURCHASE,
                                       parameters={'search-type': search_type}))
            return True
        wanted = ['albums', 'tracks']
        if self.search_type != 'all':
            wanted = [self.search_type]
        ret = False
        for kind in wanted:
            method = '_populate_%s' % kind
            if not hasattr(self, method):
                debug.warn(self, 'No method named %s' % method)
                continue
            if getattr(self, method)(Dir, lvl, whiteFlag, blackFlag):
                ret = True
        return ret

    def _populate_albums(self, Dir, lvl, whiteFlag, blackFlag):
        self.content_type = 'albums'
        for album in self.data['albums']['items']:
            node = getNode(Flag.ALBUM, data=album)
            cache = node.fetch(noRemote=True)
            if cache is not None:
                node.data = cache
            node.data['purchased'] = True
            self.add_child(node)
        return True if len(self.data['albums']['items']) > 0 else False

    def _populate_tracks(self, Dir, lvl, whiteFlag, blackFlag):
        self.content_type = 'albums'
        for track in self.data['tracks']['items']:
            node = getNode(Flag.TRACK, data=track)
            node.data['purchased'] = True
            self.add_child(node)
            ret = True
        return True if len(self.data['tracks']['items']) > 0 else False
