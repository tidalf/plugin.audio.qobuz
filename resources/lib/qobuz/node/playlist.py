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

import xbmcgui

import qobuz
from constants import Mode
from flag import NodeFlag
from node import Node
from product import Node_product
from debug import info, warn, error
'''
    NODE PLAYLIST
'''
#from cache.playlist import Cache_playlist
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
        self.packby = ''#album'
#        self.image = qobuz.image.access.get('playlist')
        if self.packby == 'album':
            self.set_content_type('albums')
        else:
            self.set_content_type('songs')
#        self.set_auto_set_cache(True)

    def get_label(self):
        return self.get_name()

    def set_is_my_playlist(self, b):
        self.is_my_playlist = b
            
    def set_is_current(self, b):
        self.b_is_current = b

    def is_current(self):
        return self.b_is_current

    def _build_down(self, xbmc_directory, lvl, flag = None):
        nid = self.get_id() or self.get_parameter('nid')
        info(self, "Build-down playlist")
        data = qobuz.registry.get(name='user-playlist',id=nid)
        if not data:
            warn(self, "Build-down: Cannot fetch playlist data")
            return False
        albumseen = {}
        for jtrack in data['data']['tracks']['items']:
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
                albumseen[jalbum['id']] = node
            else:
                node = Node_track()
                node.set_data(jtrack)
            self.add_child(node)
        
    def get_name(self):
        name = self.get_property('name')
        return name
    
    def get_owner(self):
        return self.get_property(('owner', 'name'))
            
    def get_description(self):
        return self.get_property('description')
    
    def make_XbmcListItem(self):
        color_item = qobuz.addon.getSetting('color_item')
        color_pl = qobuz.addon.getSetting('color_item_playlist')
        label = self.get_name()
        image = self.get_image()
        owner = self.get_owner()
        url = self.make_url()
        if self.b_is_current:
            label = ''.join(('-o] ', qobuz.utils.color(color_item, label), ' [o-'))
        if not self.is_my_playlist: 
            label = qobuz.utils.color(color_item, owner) + ' - ' + self.get_name() 
        label = qobuz.utils.color(color_pl, label)
        item = xbmcgui.ListItem(label,
                                owner,
                                image,
                                image,
                                url)
        if not item:
            warn(self, "Error: Cannot make xbmc list item")
            return None
        item.setPath(url)
        self.attach_context_menu(item)
        return item

    def hook_attach_context_menu(self, item, menuItems):
        color = qobuz.addon.getSetting('color_item')
        color_warn = qobuz.addon.getSetting('color_item_caution')
        label = self.get_label()
        
        ''' SET AS CURRENT '''
        url = self.make_url(Mode.PLAYLIST_SELECT_CURRENT)
        menuItems.append((qobuz.utils.color(color, qobuz.lang(39007) + ': ') + label, "XBMC.RunPlugin("+url+")"))
                
        ''' CREATE '''
        url = self.make_url(Mode.PLAYLIST_CREATE)
        menuItems.append((qobuz.utils.color(color, qobuz.lang(39008)), "XBMC.RunPlugin("+url+")"))

        ''' RENAME '''
        url = self.make_url(Mode.PLAYLIST_RENAME)
        menuItems.append((qobuz.utils.color(color, qobuz.lang(39009) + ': ') + label, "XBMC.RunPlugin("+url+")"))

        ''' REMOVE '''
        url = self.make_url(Mode.PLAYLIST_REMOVE)
        menuItems.append((qobuz.utils.color(color_warn, qobuz.lang(39010) + ': ') + label, "XBMC.RunPlugin("+url+")"))
        
        
    def remove_tracks(self, tracks_id):
        import qobuz, xbmc
        info(self, "Removing tracks: " + tracks_id)
        result = qobuz.api.playlist_deleteTracks(playlist_id=self.id, playlist_track_ids=tracks_id)
        if not result:
            warn(self, "Cannot remove tracks from playlist: " + str(self.id))
            qobuz.gui.notifyH('Qobuz Playlist / Remove track', "Fail to remove track")
            return False
        info(self, "Tracks removed from playlist: " + str(self.id))
        qobuz.registry.delete(name='user-playlist', id=self.id)
        xbmc.executebuiltin('Container.Refresh')
        return True


    def add_to_current_playlist(self):
            from gui.directory import Directory
            from renderer.xbmc import Xbmc_renderer as renderer
            cid = qobuz.registry.get(name='user-current-playlist-id')
            if cid: cid = cid['data']
            if not cid:
                warn(self, 'no current playlist id')
                qobuz.gui.notify(29000, 29001)
                return False
            nt = None
            try: nt = int(self.get_parameter('nt'))
            except:
                warn(self, "No node type...abort")
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
            render = renderer(nt, id)
            render.set_depth(depth)
            render.set_filter(view_filter)
            render.set_root_node()
            dir = Directory(render.root, qobuz.boot.handle, True)
            flags = NodeFlag.TYPE_TRACK | NodeFlag.DONTFETCHTRACK
            if render.root.type & NodeFlag.TYPE_TRACK:
                flags = NodeFlag.TYPE_TRACK
            ret = render.root.build_down(dir, depth, flags)
            if not ret: 
                dir.end_of_directory()
                return False
            trackids = []
            if len(dir.nodes) < 1:
                warn(self, "No track to add to current playlist")
                dir.end_of_directory()
                return False
            for node in dir.nodes:
                trackids.append(str(node.get_id()))
            strtracks = ','.join(trackids)
            ret = qobuz.api.playlist_addTracks(playlist_id=str(cid), track_ids=strtracks)
            if ret:
                qobuz.registry.delete(name='user-playlist', id=cid)
            return True
            
    def add_as_new_playlist(self):
        from gui.directory import Directory
        from user_playlists import Node_user_playlists
        from renderer.xbmc import Xbmc_renderer as renderer
        nt = None
        try: nt = int(self.get_parameter('nt'))
        except:
            warn(self, "No node type...abort")
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
        render = renderer(nt, id)
        render.set_depth(depth)
        render.set_filter(view_filter)
        render.set_root_node()
        dir = Directory(render.root, qobuz.boot.handle, True)
        flags = NodeFlag.TYPE_TRACK | NodeFlag.DONTFETCHTRACK
        if render.root.type & NodeFlag.TYPE_TRACK:
            flags = NodeFlag.TYPE_TRACK
        ret = render.root.build_down(dir, depth, flags)
        if not ret:
            dir.end_of_directory()
            warn(self, "Nothing to add as new playlist")
            return False
        info(self, "CREATE PLAYLIST: " + repr(render.root.get_label()))
        userplaylists = Node_user_playlists()
        nid = userplaylists.create_playlist(render.root.get_label())
        if not nid: 
            warn(self, "Cannot create playlist...")
            dir.end_of_directory()
            return False
        trackids = []
        if len(dir.nodes) < 1:
            warn(self, "No track to add to current playlist")
            dir.end_of_directory()
            return False
        for node in dir.nodes:
            trackids.append(str(node.get_id()))
        strtracks = ','.join(trackids)
        ret = qobuz.api.playlist_addTracks(playlist_id=nid, track_ids=strtracks)
        if ret:
            qobuz.registry.set(name='user-current-playlist-id', id=0, value=nid, noRemote=True)
        dir.end_of_directory()
        return True
