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
        self.depth = 2
        self.filter = 0


        
    def _add_to_directory(self, list):
        size = len(list)
        xbmcplugin.addDirectoryItems(handle = qobuz.boot.handle, items = list, totalItems = size)

    def display(self):
        if not self.set_root_node():
            print "Cannot set root node (" + str(self.node_type) + ", " + str(self.node_id) + ")"
            return False
        self.root.build_down(self.depth, self.filter)
        list = []
        #info(self, self.to_s())
        print "DEPTH: " + str(self.depth)
        print "FILTER: " + str(self.filter)
        ret = self.root.get_xbmc_items(list, self.depth, self.filter)
        #if not ret: return False
        size = len(list)
        print "Number of item: " + str(size)
        #xbmcplugin.setContent(handle = qobuz.boot.handle, content = self.root.content_type)
        self._add_to_directory(list)
        #xbmcplugin.addDirectoryItems(handle=qobuz.boot.handle, items=list, totalItems=size)
        xbmcplugin.endOfDirectory(handle = qobuz.boot.handle, succeeded = True, updateListing = False, cacheToDisc = True)
        return True

    def all_tracks(self):
        print "ALL TRACKS"
        if not self.set_root_node():
            print "Cannot set root node (" + str(self.node_type) + ", " + str(self.node_id) + ")"
            return False
        depth = -1
        self.root.build_down(depth, 0)
        list = []
        ret = self.root.get_xbmc_items(list, depth, NodeFlag.TYPE_TRACK)
        size = len(list)
        print "Number of tracks: " + str(size)
        self._add_to_directory(list)
        xbmcplugin.endOfDirectory(handle = qobuz.boot.handle, succeeded = True, updateListing = False, cacheToDisc = True)
        return True