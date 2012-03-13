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

import xbmc
import xbmcgui
import xbmcplugin
import time

import qobuz
from node.flag import NodeFlag
from debug import info, warn, log
from irenderer import IRenderer



class Xbmc_renderer(IRenderer):

    def __init__(self, node_type, node_id = None, flag = 0):
        super(Xbmc_renderer, self).__init__(node_type, node_id, flag)
        self.depth = 1
        self.filter = 0

    def _add_to_directory(self, list, progress):
        step = 500
        size = len(list)
        start = 0
        if size <= step:
            progress.update_addtodirectory(start, size)
            xbmcplugin.addDirectoryItems(handle = qobuz.boot.handle, items = list, totalItems = size)
            return True
        while start <= (size - step):
            stop = start + step
            sublist = list[start:stop]
            progress.update_addtodirectory(start, size)
            xbmcplugin.addDirectoryItems(handle = qobuz.boot.handle, items = sublist, totalItems = len(sublist))
            start = stop
            time.sleep(1)
        if start <= size:
            progress.update_addtodirectory(start, size)
            xbmcplugin.addDirectoryItems(handle = qobuz.boot.handle, items = list[start:], totalItems = len(sublist))
        return True
    
    def scan(self):
    
        progress = GuiProgress()
        #progress.hide()
        progress.create("Building tree / Scan", "The beginning")
        
        if not self.set_root_node():
            print "Cannot set root node (" + str(self.node_type) + ", " + str(self.node_id) + ")"
            return False
        self.root.build_down(self.depth, self.filter, progress)
        list = []
        self.depth = -1
        ret = self.root.get_xbmc_items(list, self.depth, self.filter, progress)
        if progress.iscanceled():
            xbmcplugin.endOfDirectory(handle = qobuz.boot.handle, succeeded = False, updateListing = False, cacheToDisc = False)
            return False
        size = len(list)
        if size < 1: return False
        xbmcplugin.setContent(handle = qobuz.boot.handle, content = self.root.content_type)
        self._add_to_directory(list, progress)
        xbmcplugin.endOfDirectory(handle = qobuz.boot.handle, succeeded = True, updateListing = True, cacheToDisc = False)
        progress.close()
        return True
        

    def display(self):
        log(self, "DISPLAY")
        from renderer.xbmc_directory import xbmc_directory
        dir = xbmc_directory(qobuz.boot.handle, False)
        if not self.set_root_node():
            print "Cannot set root node (" + str(self.node_type) + ", " + str(self.node_id) + ")"
            return False
        self.root.build_down(dir, 1, NodeFlag.TYPE_NODE) 
        dir.set_content(self.root.content_type)
        dir.end_of_directory()
        return True

    def all_tracks(self):
        print "ALL TRACKS"
        progress = GuiProgress()
        if not self.set_root_node():
            print "Cannot set root node (" + str(self.node_type) + ", " + str(self.node_id) + ")"
            return False
        depth = -1
        self.root.build_down(depth, 0, progress)
        list = []
        ret = self.root.get_xbmc_items(list, depth, NodeFlag.TYPE_TRACK, progress)
        size = len(list)
        print "Number of tracks: " + str(size)
        self._add_to_directory(list)
        xbmcplugin.endOfDirectory(handle = qobuz.boot.handle, succeeded = True, updateListing = False, cacheToDisc = True)
        return True