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
        self.is_my_playlist = False
        self.label = ""
        self.label2 = ""
        self.url = None
        self.set_is_folder(True)
        self.cache = None
        self.packby = 'album'
        self.image = qobuz.image.access.get('playlist')
        if self.packby == 'album':
            self.set_content_type('albums')
        else:
            self.set_content_type('songs')

    def get_label(self):
        return self.get_property('name')
    
    def set_is_my_playlist(self, b):
        self.is_my_playlist = b
            
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

    def _build_down(self, xbmc_directory, lvl, flag = None):
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
            
    def get_name(self):
        return self.get_property('name')

    def get_owner(self):
        return self.get_property(('owner', 'name'))
            
    def get_description(self):
        return self.get_property('description')
    
    def make_XbmcListItem(self):
        import xbmcgui
        color = qobuz.addon.getSetting('color_ctxitem')
        label = self.get_name()
        image = self.get_image()
        url = self.make_url()
        if self.b_is_current:
            label = qobuz.utils.color(color, label)
        if not self.is_my_playlist: 
            label = qobuz.utils.color(color, self.get_owner()) + ' - ' + self.get_name() 
        
        item = xbmcgui.ListItem(label,
                                self.get_owner(),
                                image,
                                image,
                                url)
        if not item:
            warn(self, "Error: Cannot make xbmc list item")
            return None
        id = self.get_id()
        if id: 
            item.setProperty('node_id', str(id))
        item.setPath(url)
        item.setThumbnailImage(image)
        item.setIconImage(image)
        self.attach_context_menu(item)
        return item

    def hook_attach_context_menu(self, item, menuItems):
        color = qobuz.addon.getSetting('color_ctxitem')
   
        ''' SET AS CURRENT '''
        url = self.make_url(Mode.SELECT_CURRENT_PLAYLIST)
        menuItems.append((qobuz.utils.color(color, 'Set as current: ')+ self.get_label(), "XBMC.RunPlugin("+url+")"))
                
        ''' CREATE '''
        url=sys.argv[0]+"?mode="+str(Mode.CREATE_PLAYLIST)+'&nt='+str(self.get_type())
        if self.get_id(): url+='&nid='+self.get_id()
        menuItems.append((qobuz.utils.color(color, 'Create'), "XBMC.RunPlugin("+url+")"))

        ''' RENAME '''
        url=sys.argv[0]+"?mode="+str(Mode.RENAME_PLAYLIST)+'&nt='+str(self.get_type())
        if self.get_id(): url+='&nid='+self.get_id()
        menuItems.append((qobuz.utils.color(color, 'Rename: ') + self.get_label(), "XBMC.RunPlugin("+url+")"))

        ''' REMOVE '''
        color = qobuz.addon.getSetting('color_ctxitem_caution')
        url=sys.argv[0]+"?mode="+str(Mode.REMOVE_PLAYLIST)+'&nt='+str(self.get_type())
        if self.get_id(): url+='&nid='+self.get_id()
        menuItems.append((qobuz.utils.color(color, 'Remove: ') + self.get_label(), "XBMC.RunPlugin("+url+")"))


    def remove_tracks(self, tracks_id):
        import qobuz
        info(self, "Removing tracks: " + tracks_id)
        if not qobuz.api.playlist_remove_track(self.id, tracks_id):
            warn(self, "Cannot remove tracks from playlist: " + str(self.id))
            return False
        info(self, "Tracks removed from playlist: " + str(self.id))
        return True


    def add_to_current_playlist(self, ):
            from renderer.xbmc_directory import xbmc_directory
            from cache.current_playlist import Cache_current_playlist
            current_playlist = Cache_current_playlist()
            from renderer.xbmc import Xbmc_renderer as renderer
            nt = None
            try: nt = int(self.get_parameter('nt'))
            except:
                print "No node type...abort"
                return False
            id = None
            try: id = self.get_parameter('nid')        
            except: pass 
            depth = -1
            try: depth = int(self.get_parameter('depth'))
            except: pass
            view_filter = 0
            try: view_filter = int(self.get_parameter('view-filter'))
            except: pass
            r = renderer(nt, id)
            r.set_depth(depth)
            r.set_filter(view_filter)
            r.set_root_node()
            dir = xbmc_directory(r.root, qobuz.boot.handle, True)
            ret = r.root.build_down(dir, depth, NodeFlag.TYPE_TRACK | NodeFlag.DONTFETCHTRACK)
            if not ret: return False
            trackids = []
            if len(dir.nodes) < 1:
                warn(self, "No track to add to current playlist")
                return False
            for node in dir.nodes:
                trackids.append(node.get_id())
            strtracks = ','.join(trackids)
            ret = qobuz.api.playlist_add_track(str(current_playlist.get_id()), strtracks)
            
            from utils.cache import cache_manager
            from cache.playlist import Cache_playlist
            cm = cache_manager()
            pl = Cache_playlist(current_playlist.get_id())
            cm.delete(pl.get_cache_path())
            dir.Progress.close()