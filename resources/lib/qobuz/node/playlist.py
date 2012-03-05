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
from debug import info, warn, error
'''
    NODE PLAYLIST
'''
from cache.playlist import Cache_playlist
from tag.playlist import Tag_playlist
from tag.track import Tag_track

class Node_playlist(Node):
    
    def __init__(self, parent = None, parameters = None):
        super(Node_playlist, self).__init__(parent, parameters)
        self.type = NodeFlag.TYPE_NODE | NodeFlag.TYPE_PLAYLIST
        self.current_playlist_id = None
        self.b_is_current = False
        self.set_content_type('songs')
        self.tag = Tag_playlist()
        self.label = ""
        self.label2 = ""
        self.url = None
        self.thumb = ''
        self.icon = ''
        self.set_is_folder(True)
        
    def set_is_current(self, b):
        self.b_is_current = b
        
    def is_current(self):
        return self.b_is_current
    
    def _build_down(self, lvl, flag = None):
        self.tag.set_id(self.id)
        if not self.tag.fetch():
            error(self, "Cannot fetch data for playlist id: " + self.id)
        o = Cache_playlist(self.id)
        data = o.fetch_data()
        if self.id != data['id']:
            error(self, "Playlist id mismatch ???? ABORT")
        #data = o.get_data()
        self.tag.set_json(data)
        if tag.id: self.set_id(tag.id)
    
        for track in data['tracks']:
            c = node_track()
            c.set_json(track)
            c.set_id(track['id'])
            c.set_label(track['title'])
            c.set_url()
            self.add_child(c)
        return True
    
    def _get_xbmc_items(self, list, lvl, flag):
        if len(self.childs) < 1:
            qobuz.gui.notification(36000, 36001)
            return False
        for c in self.childs:
            tag = TagTrack(c.get_json())
            item = tag.getXbmcItem()
            if self.is_current():
                label = item.getLabel()
                label = '-> ' + label + ' <-'
                qobuz.utils.color('FFFF0000', label)
                item.setLabel(label)
            self.attach_context_menu(item, NodeFlag.TYPE_TRACK, tag.id)
            list.append((item.getProperty('path'), item, False))
        return True

    def hook_attach_context_menu(self, item, type, id, menuItems, color):
        import sys
        ''' DELETE '''
        print "removing track id: " + str(id)
        url=sys.argv[0]+"?mode="+str(MODE_PLAYLIST_REMOVE_TRACK)+'&nt='+str(type)+'&tracks_id=' + str(id)
        if self.id: url+='&nid='+str(self.id)
        menuItems.append((qobuz.utils.color(qobuz.addon.getSetting('color_ctxitem'), 'Remove track from playlist'), "XBMC.RunPlugin("+url+")"))
            
    
    def getLabel(self):
        return self.tag.get_name()
    
    def make_XbmcListItem(self):
        import xbmcgui
        #print "url: " + self.get_url()
        item = xbmcgui.ListItem(self.tag.get_name(),
                                self.tag.owner.get_name(),
                                self.get_icon(),
                                self.get_thumbnail(),
                                self.get_url())
        #item.setPath(self.get_url())
        #item.setProperty('Path', self.get_url())
        return item
        
        
    def remove_tracks(self, tracks_id):
        import qobuz
        info(self, "Removing tracks: " + tracks_id)
        if not qobuz.api.playlist_remove_track(self.id, tracks_id):
            warn(self, "Cannot remove tracks from playlist: " + str(self.id))
            return False
        info(self, "Tracks removed from playlist: " + str(self.id))
        return True
    

