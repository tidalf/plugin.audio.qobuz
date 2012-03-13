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

import qobuz
from constants import Mode
from flag import NodeFlag
from node import Node
from product import Node_product
from debug import info, warn, error
'''
    NODE PLAYLIST
'''
from cache.playlist import Cache_playlist
from track import Node_track

class Node_playlist(Node):

    def __init__(self, parent = None, parameters = None, progress = None):
        super(Node_playlist, self).__init__(parent, parameters)
        self.type = NodeFlag.TYPE_NODE | NodeFlag.TYPE_PLAYLIST
        self.current_playlist_id = None
        self.b_is_current = False
        self.set_content_type('songs')
#        self.tag = Tag_playlist()
        self.label = ""
        self.label2 = ""
        self.url = None
        self.thumb = ''
        self.icon = ''
        self.set_is_folder(True)
        self.cache = None
        self.packby = 'album'

    def get_label(self):
        return self.get_property('name')
        
    def set_is_current(self, b):
        self.b_is_current = b

    def is_current(self):
        return self.b_is_current

    def _set_cache(self):
        id = self.get_id()
        if not id:
            try: id = self.get_parameter('nid')
            except: pass
        if not id:
            error(self, "Cannot set cache without id")
            return False
        self.cache = Cache_playlist(id)
        self.set_id(id)
        return True

    def _build_down(self, lvl, flag = None):
        info(self, "Build-down playlist")
        if not self._set_cache():
            error(self, "Cannot set cache!")
            return False
        data = self.cache.fetch_data()
        if not data:
            warn(self, "Build-down: Cannot fetch playlist data")
            return False
        self.set_data(data)
        albumseen = {}
        for jtrack in data['tracks']:
            node = None
            if self.packby == 'album':
                jalbum = jtrack['album']
                if jalbum['id'] in albumseen: continue
                keys = [ 'artist', 'interpreter', 'composer']
                for k in keys:
                    if k in jtrack: jalbum[k] = jtrack[k]
                if 'image' in jtrack: jalbum['image'] = jtrack['image']
              
                node = Node_product()
                node.set_data(jalbum)
                
            else:
                node = Node_track()
                node.set_data(jtrack)
            albumseen[jalbum['id']] = node
            self.add_child(node)

    def _get_xbmc_items(self, list, lvl, flag, progress = None):
        if len(self.childs) < 1:
            qobuz.gui.notify(36000, 36001)
            return False
        for child in self.childs:
            item = child.make_XbmcListItem()
            self.attach_context_menu(item, child)
            mode = Mode.PLAY
            if self.packby == 'album': mode = Mode.VIEW
            url = child.get_url(mode)
            list.append((url, item, child.is_folder()))
        return True

    def hook_attach_context_menu(self, item, node, menuItems, color):
        pass
    
    def getLabel(self):
        return self.tag.get_name()

    def get_name(self):
        if self._data and 'name' in self._data:
            return self._data['name']
        return ''

    def get_owner(self):
        if self._data and 'owner' in self._data:
            return self._data['owner']['name']
    
    def get_description(self):
        return self.get_property('description')
    
    def make_XbmcListItem(self):
        import xbmcgui
        item = xbmcgui.ListItem(self.get_name(),
                                self.get_owner(),
                                self.get_icon(),
                                self.get_thumbnail(),
                                self.get_url())
        item.setProperty('node_id', str(self.get_id()))
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


    def add_to_current_playlist(self, ):
            from cache.current_playlist import Cache_current_playlist
            from renderer.xbmc import GuiProgress
            
            current_playlist = Cache_current_playlist()
            print "Current playlist id: " + str(current_playlist.get_id())
            print '-'*80 + "\n"
            print "Adding node to new playlist"
            print '-'*80 + "\n"
            from renderer.xbmc import Xbmc_renderer as renderer
            nt = None
            try: nt = int(self.get_parameter('nt'))
            except:
                print "No node type...abort"
                return False
            print "Node type: " + str(nt)
            
            id = None
            try: id = self.get_parameter('nid')        
            except: pass
            
            depth = -1
            try: depth = int(self.get_parameter('depth'))
            except: pass
            
            view_filter = 0
            try: view_filter = int(self.get_parameter('view-filter'))
            except: pass
            
            print "############################"
            r = renderer(nt, id)
            r.set_depth(depth)
            r.set_filter(view_filter)
            r.set_root_node()
            progress = GuiProgress()
            progress.create("Add to current playlist", r.root.get_label())
            r.root.build_down(depth, NodeFlag.DONTFETCHTRACK, progress)
            list = []
            ret = r.root.get_xbmc_items(list, depth, NodeFlag.TYPE_TRACK, progress)
            if not ret: return False
            trackids = []
            if len(list) < 1:
                warn(self, "No track to add to current playlist")
                return False
            for item in list:
                node_id =  item[1].getProperty('node_id')
                print "ADD: " + node_id
                trackids.append(node_id)
            strtracks = ','.join(trackids)
            ret = qobuz.api.playlist_add_track(str(current_playlist.get_id()), strtracks)
            
            from utils.cache import cache_manager
            from cache.playlist import Cache_playlist
            cm = cache_manager()
            pl = Cache_playlist(current_playlist.get_id())
            cm.delete(pl.get_cache_path())
            
            print "RET: " + pprint.pformat(ret)
            