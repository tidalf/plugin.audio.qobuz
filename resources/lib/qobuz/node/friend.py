#     Copyright 2011 Joachim Basmaison, Cyril Leclerc
#
#     This file is part of xbmc-qobuz.
#
#     xbmc-qobuz is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     xbmc-qobuz is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.   See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with xbmc-qobuz.   If not, see <http://www.gnu.org/licenses/>.
import sys
import pprint

import xbmcgui, xbmc
import json

import qobuz
from constants import Mode
from flag import NodeFlag
from node import Node
from playlist import Node_playlist
from debug import info, warn, error
from gui.util import color

'''
    NODE FRIEND
'''
from track import Node_track

class Node_friend(Node):

    def __init__(self, parent = None, parameters = None, progress = None):
        super(Node_friend, self).__init__(parent, parameters)
        self.type = NodeFlag.TYPE_NODE | NodeFlag.TYPE_FRIEND
        self.name = ''
        self.set_name(self.get_parameter('name'))
        self.set_label(self.name)
        self.label2 = self.label
        self.url = None
        self.set_is_folder(True)
   
    def set_label(self, label):
        colorItem = qobuz.addon.getSetting('color_item')
        self.label = 'friend / ' + color(colorItem, label)
    
    def set_name(self, name):
        self.name = name or ''
        self.set_label(self.name)
        return self
        
    def make_url(self,mode=Mode.VIEW):
        url = sys.argv[0] + '?mode=' + str(mode) + "&nt=" + str(self.type) + "&name=" + self.name
        return url
    
    def _change_appid(self):
        self._bak_appid = qobuz.api.appid
        qobuz.api.appid = "477478368"
        qobuz.registry.delete(name='user')
        qobuz.registry.login(
                           username=qobuz.addon.getSetting('username'), 
                           password=qobuz.addon.getSetting('password'))
        
    def _restore_appid(self):
        qobuz.api.appid = self._bak_appid
        qobuz.registry.delete(name='user')
        qobuz.registry.login(
                           username=qobuz.addon.getSetting('username'), 
                           password=qobuz.addon.getSetting('password'))
        
    def create(self, name = None):
        if not name:
            from gui.util import Keyboard
            kb = Keyboard('', 'Add Friend (i8n)')
            kb.doModal()
            name = ''
            if not kb.isConfirmed():
                warn(self, 'Nothing to do')
                return False
            name = kb.getText()
        friendpl = qobuz.api.playlist_getUserPlaylists(username=name)
        if not friendpl: return False
        user = qobuz.registry.get(name='user')
        if not user:
            return False
        friends = user['data']['user']['player_settings']
        if not 'friends' in friends:
            friends = []
        else: friends = friends['friends']
        if name in friends:
            return False
        friends.append(name)
        newdata = { 'friends': friends }
        self._change_appid()
        if not qobuz.api.user_update(player_settings=json.dumps(newdata)):
            self._restore_appid()
            return False
        self._restore_appid()
        return True
    
    def remove(self, name):
        if not name: return False
        user = qobuz.registry.get(name='user')
        if not user: return False
        friends = user['data']['user']['player_settings']
        if not 'friends' in friends: return False
        friends = friends['friends']
        if not name in friends: return False
        del friends[friends.index(name)]
        #dict((k, v) for (k, v) in somedict.iteritems() if not k.startswith('someprefix'))
        newdata = { 'friends': friends }
        self._change_appid()
        if not qobuz.api.user_update(player_settings=json.dumps(newdata)):
            self._restore_appid()
            return False
        self._restore_appid()
        return True
            
    def _build_down(self, xbmc_directory, lvl, flag = None):
        data = qobuz.api.playlist_getUserPlaylists(username=self.name)
        if not data:
            warn(self, "No friend data")
            return False
        for pl in data['playlists']['items']:
            node = Node_playlist()
            node.data = pl
            if node.get_owner() == self.label:
                print "GOT OWNER ID"
                self.id = node.get_owner_id()
            self.add_child(node)
        return True
    
    def hook_attach_context_menu(self, item, menuItems):
        colorItem = qobuz.addon.getSetting('color_item')
        colorWarn = qobuz.addon.getSetting('color_item_caution')
        
        ''' Delete friend'''
        url = self.make_url(Mode.FRIEND_REMOVE)
        menuItems.append((color(colorItem, 'Remove friend (i8n)' + ': ') + self.name, "XBMC.RunPlugin("+url+")"))
