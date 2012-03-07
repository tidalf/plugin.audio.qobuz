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
import pprint

import qobuz
from constants import *
from flag import NodeFlag
from node import Node
from debug import *

'''
    NODE USER PLAYLISTS
'''

from cache.user_playlists import Cache_user_playlists
from playlist import Node_playlist

class Node_user_playlists(Node):

    def __init__(self, parent = None, parameters = None):
        super(Node_user_playlists, self).__init__(parent, parameters)
        self.label = qobuz.utils.lang(30019)
        self.icon = self.thumb = qobuz.image.access.get('userplaylists')
        self.label2 = 'Keep your current playlist'
        self.type = NodeFlag.TYPE_NODE | NodeFlag.TYPE_USERPLAYLISTS
        self.set_content_type('files')
        display_by = self.get_parameter('display-by')
        if not display_by: display_by = 'songs'
        self.set_display_by(display_by)
        self.set_url()
        self.cache = Cache_user_playlists()

    def set_display_by(self, type):
        vtype = ('product', 'songs')
        if not type in vtype:
            error(self, "Invalid display by: " + type)
        self.display_by = type

    def get_display_by(self):
        return self.display_by

    def _build_down(self, lvl, flag = None):
        info(self, "Build-down: user playlists")
        data = self.cache.fetch_data()
        if not data:
            warn(self, "Build-down: Cannot fetch user playlists data")
            return False
        self.set_data(data)
        print "DATA: " + repr(data)
        for playlist in data:
            node = Node_playlist()
            node.set_data(playlist)
            self.add_child(node)

    def _get_xbmc_items(self, list, lvl, flag):
        username = qobuz.addon.getSetting('username')
        color = qobuz.addon.getSetting('color_notowner')
        for playlist in self.childs:
            item = playlist.make_XbmcListItem()#tag.getXbmcItem()
            #print "URL: " + item.getProperty('Path')
            if playlist.get_owner() != username:
                item.setLabel(''.join([qobuz.utils.color(color, playlist.get_owner()), ' - ', playlist.get_name()]))
            else:
                self.attach_context_menu(item, NodeFlag.TYPE_PLAYLIST, playlist.get_id())
            #if playlist.is_current():
#                label = item.getLabel()
#                item.setLabel(qobuz.utils.color(color, '-> ') + label + qobuz.utils.color(color, ' <-')
#            print "plop"
#            print "append: " + item.getLabel()
#            print "url   ; " + item.getProperty('Path')
            #print "URL2: " + playlist.get_url()
            list.append((playlist.get_url(), item, playlist.is_folder()))
        return True

#    def hook_attach_context_menu(self, item, type, id, menuItems, color):
#        import sys
#        ''' RENAME '''
#        url=sys.argv[0]+"?mode="+str(MODE_RENAME_PLAYLIST)+'&nt='+str(type)
#        if id: url+='&nid='+id
#        menuItems.append((qobuz.utils.color(qobuz.addon.getSetting('color_ctxitem'), 'Rename'), "XBMC.RunPlugin("+url+")"))
#        
#        ''' DELETE '''
#        url=sys.argv[0]+"?mode="+str(MODE_REMOVE_PLAYLIST)+'&nt='+str(type)
#        if id: url+='&nid='+id
#        menuItems.append((qobuz.utils.color(qobuz.addon.getSetting('color_ctxitem'), 'Delete'), "XBMC.RunPlugin("+url+")"))
#        
#        ''' SET AS CURRENT '''
#        url=sys.argv[0]+"?mode="+str(MODE_SELECT_CURRENT_PLAYLIST)+'&nt='+str(type)
#        if id: url+='&nid='+id
#        menuItems.append((qobuz.utils.color(color, 'Set as current: ' + item.getLabel()), "XBMC.RunPlugin("+url+")"))
#        
#        ''' CREATE '''
#        url=sys.argv[0]+"?mode="+str(MODE_CREATE_PLAYLIST)+'&nt='+str(type)
#        if id: url+='&nid='+id
#        menuItems.append((qobuz.utils.color(color, 'Create'), "XBMC.RunPlugin("+url+")"))

        ''' Display by '''
#        display_by = 'songs'
#        if self.display_by == 'songs':
#            display_by = 'product'
#        url=sys.argv[0]+"?mode="+str(MODE_NODE)+'&nt='+str(self.type)+'&display-by='+display_by
#        menuItems.append((qobuz.utils.color(qobuz.addon.getSetting('color_ctxitem'), 'Display by: ' + display_by), "XBMC.RunPlugin("+url+")"))




