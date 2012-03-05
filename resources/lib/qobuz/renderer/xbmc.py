# -*- coding: UTF-8 -*- 
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

import xbmcplugin

import qobuz
from node.flag import NodeFlag
from debug import info, warn

class Xbmc_renderer():
    
    def __init__(self, node_type, node_id = None, flag = 0):
        self.node_type = node_type
        self.node_id = node_id
        self.flag = flag
        self.root = None
    
    def to_s(self):
        s = "Node type: " + str(self.node_type) + "\n"
        s+= "Node id  : " + str(self.node_id) + "\n"
        s+= "Flag     : " + str(self.flag) + "\n"
        if self.root:
            s+= self.root.to_s()
        return s
    
    def set_root_node(self):
        root = None
        if self.node_type & NodeFlag.TYPE_ROOT:
            from node.root import Node_root
            root = Node_root(None, qobuz.boot.params)
        elif self.node_type & NodeFlag.TYPE_TRACK:
            from node_track import node_track
            root = node_track(None, qobuz.boot.params)
        elif self.node_type & NodeFlag.TYPE_USERPLAYLISTS:
            print "SET ROOT NODE: USER PLAYLISTS"
            from node.user_playlists import Node_user_playlists
            root = Node_user_playlists(None, qobuz.boot.params)
        elif self.node_type & NodeFlag.TYPE_PLAYLIST:
            print "SET ROOT NODE: PLAYLIST"
            from node.playlist import Node_playlist
            root = Node_playlist(None, qobuz.boot.params)
        elif self.node_type & NodeFlag.TYPE_RECOMMANDATION:
            from node_recos import node_recos
            root = node_recos(None, qobuz.boot.params)
        elif self.node_type & NodeFlag.TYPE_PRODUCT:
            print "Render product"
            from node_product import node_product
            root = node_product(None, qobuz.boot.params)
        elif self.node_type & NodeFlag.TYPE_VIRTUAL_PLAYLIST:
            from node_virtual_playlist import node_virtual_playlist
            root = node_virtual_playlist(None, qobuz.boot.params)
        elif self.node_type & NodeFlag.TYPE_PURCHASES:
            from node_purchases import node_purchases
            root = node_purchases(None, qobuz.boot.params)
        elif self.node_type & NodeFlag.TYPE_SEARCH:
            from node_search import node_search
            root = node_search(None, qobuz.boot.params)
        else:
            print "Nothing to display"
            return False
        root.set_id(self.node_id)
        root.set_url()
        self.root = root
        return True

    '''
    add_to_playlist 

    '''

    def add_to_virtual_playlist(self):
        from data.virtual_playlist import cache_virtual_playlist
        self.set_root_node()
        list = []
        depth = -1
        if self.node_type == NodeFlag.TYPE_TRACK:
            self.root.build_down(depth, 0)
        else:
            self.root.build_down(depth, NodeFlag.DONTFETCHTRACK)
        self.root.get_tag_items(list, depth, NodeFlag.DONTFETCHTRACK)
        if len(list) < 1: 
            print "Nothing to add to virtual playlist"
            return 0
        print "Add to playlist: " + str(len(list))
        playlist = cache_virtual_playlist()
        for track in list:
            playlist.add_track(track)
        playlist.save()
        print "Virtual playlist updated!"
        return True
    
    def add_to_current_playlist(self):
        print "add to current playlist"
        from data.current_playlist import Cache_current_playlist
        cp = Cache_current_playlist()
        if not cp.data or not cp.data['id']:
            print "Cannot add track without current playlist"
            return False
        print "Current playlist: " + cp.data['name'] 
        self.set_root_node()
        list = []
        depth = -1
        if self.node_type == NodeFlag.TYPE_TRACK:
            self.root.build_down(depth, 0)
        else:
            self.root.build_down(depth, NodeFlag.DONTFETCHTRACK)
        self.root.get_tag_items(list, depth, NodeFlag.DONTFETCHTRACK)
        print "importing tracks from " + repr(self.root.get_label())
        if len(list) < 1: 
            print "No tracks to add to current playlist"
            return 0
        print "Add tracks to playlist: " + str(len(list))
        tracks_id = []
        for t in list:
            tracks_id.append(t['id'])
            
        print ', '.join(tracks_id)
        res = qobuz.api.playlist_add_track(','.join(tracks_id), cp.data['id'])
        if not res:
            print "Can't add tracks to playlist"
            return False
        info(self, "Playlist updated with " + str(len(list)) + " tracks")
        #print "Res: " + repr(res)
        from utils.cache import cache_manager
        cm = cache_manager()
        if not cm.delete_file('playlist-'+str(cp.data['id'])):
            warn(self, "Cannot delete cached playlist data, id=" + str(cp.data['id']))
        return True
    
    def add_as_new_playlist(self):
        self.set_root_node()
        list = []
        depth = -1
        if self.node_type == NodeFlag.TYPE_TRACK:
            self.root.build_down(depth, 0)
        else:
            self.root.build_down(depth, NodeFlag.DONTFETCHTRACK)
        if not self.root.get_label():
            warn(self, "Can't create playlist without name... aborting!")
            return False
        print "add to new playlist: " + repr(self.root.get_label())
        self.root.get_tag_items(list, depth, NodeFlag.DONTFETCHTRACK)
        if len(list) < 1: 
            print "No track to add to this new playlist"
            return 0
        print "Add to playlist: " + str(len(list))
        tracks_id = []
        for t in list:
            tracks_id.append(t['id'])
        print ', '.join(tracks_id)
        res = qobuz.api.playlist_create(self.root.get_label(), ','.join(tracks_id), '', 'off', 'off' )
        if not res:
            print "Can't create playlist"
            return False
        print "Playlist created"
        from utils.cache import cache_manager
        cm = cache_manager()
        cm.delete_file('userplaylists-0')

        return True
    
    def display(self):
        if not self.set_root_node():
            print "Cannot set root node (" + str(self.node_type) + ", " + str(self.node_id) + ")"
            return False
        depth = 1
        self.root.build_down(depth, 0)
        list = []
        #info(self, self.to_s())
        ret = self.root.get_xbmc_items(list, depth, 0)
        if not ret:
            return False
        size = len(list)
        xbmcplugin.setContent(handle=qobuz.boot.handle, content=self.root.content_type)
        xbmcplugin.addDirectoryItems(handle=qobuz.boot.handle, items=list, totalItems=size)
        xbmcplugin.endOfDirectory(handle=qobuz.boot.handle, succeeded=True, updateListing=False, cacheToDisc=True)
        return True
