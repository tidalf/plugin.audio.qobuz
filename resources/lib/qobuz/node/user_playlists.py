'''
    qobuz.node.user_playlist
    ~~~~~~~~~~~~~~~~~~~~~~~

    :part_of: xbmc-qobuz
    :copyright: (c) 2012-2016 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
from qobuz.node import Flag, getNode
from qobuz.node.inode import INode
from qobuz import debug
from qobuz.gui.util import lang, getImage, getSetting
from qobuz.api import api
import os

class Node_user_playlists(INode):

    def __init__(self, parent=None, parameters={}, data=None):
        super(Node_user_playlists, self).__init__(parent=parent,
                                                  parameters=parameters,
                                                  data=data)
        self.nt = Flag.USERPLAYLISTS
        self.label = lang(30021)
        self.image = getImage('userplaylists')
        self.content_type = 'albums'
        # display_by = self.get_parameter('display-by', default=None)
        # if display_by is None:
        #     display_by = 'songs'
        # self.set_display_by(display_by)
        display_cover = getSetting('userplaylists_display_cover', asBool=True)
        self.display_product_cover = display_cover

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

    def fetch(self, Dir, lvl, whiteFlag, blackFlag):
        return api.get('/playlist/getUserPlaylists',
                       limit=self.limit,
                       offset=self.offset,
                       user_id=api.user_id,
                       type='last-created')

    def populate(self, Dir, lvl, whiteFlag, blackFlag):
        login = getSetting('username')
        cid = self.get_current_playlist_id()
        for data in self.data['playlists']['items']:
            node = getNode(Flag.PLAYLIST, data=data)
            if cid and cid == node.nid:
                node.set_is_current(True)
            if node.get_owner() == login:
                node.set_is_my_playlist(True)
            self.add_child(node)
        return True
