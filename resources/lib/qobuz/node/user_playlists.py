'''
    qobuz.node.user_playlist
    ~~~~~~~~~~~~~~~~~~~~~~~

    :part_of: xbmc-qobuz
    :copyright: (c) 2012-2016 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
import os

from qobuz import config
from qobuz import debug
from qobuz.api import api
from qobuz.api.user import current as user
from qobuz.cache import cache
from qobuz.gui.util import lang, getImage
from qobuz.node import Flag, getNode
from qobuz.node.inode import INode

limit_max = 100


class Node_user_playlists(INode):
    def __init__(self, parent=None, parameters=None, data=None):
        parameters = {} if parameters is None else parameters
        super(Node_user_playlists, self).__init__(
            parent=parent, parameters=parameters, data=data)
        self.nt = Flag.USERPLAYLISTS
        self.label = lang(30021)
        self.image = getImage('userplaylists')
        self.content_type = 'albums'
        self.display_product_cover = config.app.registry.get(
            'userplaylists_display_cover', to='bool')

    def set_display_by(self, dtype):
        vtype = ('product', 'songs')
        if dtype not in vtype:
            error(self, "Invalid display by: " + dtype)
        self.display_by = dtype

    def get_display_by(self):
        return self.display_by

    def set_current_playlist_id(self, playlist_id):
        userdata = self.get_user_storage()
        userdata['current_playlist'] = int(playlist_id)
        userdata.sync()

    def get_current_playlist_id(self):
        userdata = self.get_user_storage()
        if 'current_playlist' not in userdata:
            return None
        return int(userdata['current_playlist'])

    def _get_limit(self):
        return self.limit if self.limit < limit_max else limit_max

    def fetch(self, *a, **ka):
        return api.get('/playlist/getUserPlaylists',
                       limit=self._get_limit(),
                       offset=self.offset,
                       user_id=user.get_id(),
                       type='last-created')

    def populate(self, *a, **ka):
        cid = self.get_current_playlist_id()
        for data in self.data['playlists']['items']:
            node = getNode(
                Flag.PLAYLIST, data=data, parameters={'nt': self.nt})
            if cid and cid == node.nid:
                node.set_is_current(True)
            if node.get_owner() == user.username:
                node.set_is_my_playlist(True)
            self.add_child(node)
        return True if len(self.data['playlists']['items']) > 0 else False
