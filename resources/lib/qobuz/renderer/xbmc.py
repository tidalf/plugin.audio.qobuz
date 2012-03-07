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
from irenderer import IRenderer


class Xbmc_renderer(IRenderer):

    def __init__(self, node_type, node_id = None, flag = 0):
        super(Xbmc_renderer, self).__init__(node_type, node_id, flag)

    def _add_to_directory(self, list):
        size = len(list)
        xbmcplugin.addDirectoryItems(handle = qobuz.boot.handle, items = list, totalItems = size)

    def display(self):
        if not self.set_root_node():
            print "Cannot set root node (" + str(self.node_type) + ", " + str(self.node_id) + ")"
            return False
        depth = 1
        self.root.build_down(depth, 0)
        list = []
        #info(self, self.to_s())
        ret = self.root.get_xbmc_items(list, depth, 0)
        if not ret: return False
        size = len(list)
        xbmcplugin.setContent(handle = qobuz.boot.handle, content = self.root.content_type)
        self._add_to_directory(list)
        #xbmcplugin.addDirectoryItems(handle=qobuz.boot.handle, items=list, totalItems=size)
        xbmcplugin.endOfDirectory(handle = qobuz.boot.handle, succeeded = True, updateListing = False, cacheToDisc = True)
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
        if not cm.delete_file('playlist-' + str(cp.data['id'])):
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
        res = qobuz.api.playlist_create(self.root.get_label(), ','.join(tracks_id), '', 'off', 'off')
        if not res:
            print "Can't create playlist"
            return False
        print "Playlist created"
        from utils.cache import cache_manager
        cm = cache_manager()
        cm.delete_file('userplaylists-0')

        return True


