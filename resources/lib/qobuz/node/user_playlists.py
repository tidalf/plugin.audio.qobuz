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
from playlist import Node_playlist
from tag.user_playlists import Tag_user_playlists

class Node_user_playlists(Node):
    
    def __init__(self, parent = None, parameters = None):
        super(Node_user_playlists, self).__init__(parent, parameters)
        self.label  = qobuz.utils.lang(30019)
        self.icon = self.thumb = qobuz.image.access.get('userplaylists')
        self.label2 = 'Keep your current playlist'
        self.type = NodeFlag.TYPE_NODE | NodeFlag.TYPE_USERPLAYLISTS
        self.set_content_type('files')
        display_by = self.get_parameter('display-by')
        if not display_by: display_by = 'songs'
        self.set_display_by(display_by)
        self.set_url()
        self.tag = Tag_user_playlists()
        
    def set_display_by(self, type):
        vtype = ('product', 'songs')
        if not type in vtype:
            error(self, "Invalid display by: " + type)
        self.display_by = type
    
    def get_url(self):
        print "URL - User playlist: " + self.url
        return self.url
    
    def get_display_by(self):
        return self.display_by
    
    def _build_down(self, lvl, flag = None):
        if not self.tag.fetch():
            error(self, "Cannot fetch data for user playlist")
        for p in self.tag.get_json()['playlist']:
            node = Node_playlist()
            node.tag.set_json(p)
#        print "user_playlist: " + build_down
#        return True
#        o = Cache_user_playlists(qobuz.api, qobuz.path.cache, -1)
#        self.set_json(o.get_data())
#        current_playlist_id = Cache_current_playlist().get_id()
#        print "Current ID: " + str(current_playlist_id)
#        for playlist in self.get_json():
#
#            c = Node_playlist()
#            c.set_id(playlist['id'])
#            if current_playlist_id and int(playlist['id']) == current_playlist_id:
#                c.set_is_current(True)
#            c.set_label(playlist['name'])
#            c.set_json(playlist)
#            c.set_url()
#            self.add_child(c)

    def _get_xbmc_items(self, list, lvl, flag):
        username = qobuz.addon.getSetting('username')
        color = qobuz.addon.getSetting('color_notowner')
        for c in self.childs:
            tag = TagPlaylist(c.get_json())
            item = tag.getXbmcItem()
            if tag.getOwner() != username:
                item.setLabel(''.join([qobuz.utils.color(color, tag.getOwner()), ' - ', tag.getName()]))
            else:
                self.attach_context_menu(item, NodeFlag.TYPE_PLAYLIST, tag.id)
            if c.is_current():
                label = item.getLabel()
                item.setLabel(qobuz.utils.color(color, '-> ') + label + qobuz.utils.color(color, ' <-'))
            url = c.get_url()

            item.setPath(url)
            list.append((url, item, True))
        return True
            
    def hook_attach_context_menu(self, item, type, id, menuItems, color):
        import sys
        ''' RENAME '''
        url=sys.argv[0]+"?mode="+str(MODE_RENAME_PLAYLIST)+'&nt='+str(type)
        if id: url+='&nid='+id
        menuItems.append((qobuz.utils.color(qobuz.addon.getSetting('color_ctxitem'), 'Rename'), "XBMC.RunPlugin("+url+")"))
        
        ''' DELETE '''
        url=sys.argv[0]+"?mode="+str(MODE_REMOVE_PLAYLIST)+'&nt='+str(type)
        if id: url+='&nid='+id
        menuItems.append((qobuz.utils.color(qobuz.addon.getSetting('color_ctxitem'), 'Delete'), "XBMC.RunPlugin("+url+")"))
        
        ''' SET AS CURRENT '''
        url=sys.argv[0]+"?mode="+str(MODE_SELECT_CURRENT_PLAYLIST)+'&nt='+str(type)
        if id: url+='&nid='+id
        menuItems.append((qobuz.utils.color(color, 'Set as current: ' + item.getLabel()), "XBMC.RunPlugin("+url+")"))
        
        ''' CREATE '''
        url=sys.argv[0]+"?mode="+str(MODE_CREATE_PLAYLIST)+'&nt='+str(type)
        if id: url+='&nid='+id
        menuItems.append((qobuz.utils.color(color, 'Create'), "XBMC.RunPlugin("+url+")"))
        
        ''' Display by '''
#        display_by = 'songs'
#        if self.display_by == 'songs':
#            display_by = 'product'
#        url=sys.argv[0]+"?mode="+str(MODE_NODE)+'&nt='+str(self.type)+'&display-by='+display_by
#        menuItems.append((qobuz.utils.color(qobuz.addon.getSetting('color_ctxitem'), 'Display by: ' + display_by), "XBMC.RunPlugin("+url+")"))
    

        
    
