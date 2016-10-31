'''
    qobuz.node.user_playlist
    ~~~~~~~~~~~~~~~~~~~~~~~

    :part_of: xbmc-qobuz
    :copyright: (c) 2012-2016 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
import os
from qobuz.node import Flag, getNode
from qobuz.node.inode import INode
from qobuz import debug
from qobuz.gui.util import lang, getImage
from qobuz.api import api
from qobuz.api.user import current as user
from qobuz import config

class Node_user_playlists(INode):

    def __init__(self, parent=None, parameters={}, data=None):
        super(Node_user_playlists, self).__init__(parent=parent,
                                                  parameters=parameters,
                                                  data=data)
        self.nt = Flag.USERPLAYLISTS
        self.label = lang(30021)
        self.image = getImage('userplaylists')
        self.content_type = 'albums'
        self.display_product_cover = config.app.registry.get(
            'userplaylists_display_cover',
            to='bool')

    def set_display_by(self, dtype):
        vtype = ('product', 'songs')
        if not dtype in vtype:
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

    def fetch(self, *a, **ka):
        return api.get('/playlist/getUserPlaylists',
                       limit=self.limit,
                       offset=self.offset,
                       user_id=user.get_id(),
                       type='last-created')

    def populate(self, *a, **ka):
        login = config.app.registry.get('username')
        cid = self.get_current_playlist_id()
        for data in self.data['playlists']['items']:
            node = getNode(Flag.PLAYLIST, data=data)
            if cid and cid == node.nid:
                node.set_is_current(True)
            if node.get_owner() == user.username:
                node.set_is_my_playlist(True)
            self.add_child(node)
        return True if len(self.data['playlists']['items']) > 0 else False
