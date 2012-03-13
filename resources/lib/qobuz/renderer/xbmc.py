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
from debug import info, warn
from irenderer import IRenderer

class GuiProgress(xbmcgui.DialogProgress):
    def __init__(self, heading = None, line1 = None, line2 = None, line3 = None):
        super(GuiProgress, self).__init__()
        self.buildcount = 0
        self.itemcount = 0
        self.showDialog = True
        self.isopen = False
        
    def hide(self):
        self.showDialog = False
    
    def show(self):
        self.showDialog = True
        
    def update_buildcount(self):
        self.buildcount+=1
        self.update(50, "2/4 Discover node: " + str(self.buildcount))
        
    def update_itemcount(self):
        self.itemcount+=1
        self.update(75, "3/4 Retrieve node: " + str(self.itemcount))
    
    def update_addtodirectory(self, count, total):
        if total == 0:
            self.update(100, "Empty directory")
            return True
        perc = count * ( (100.0 / total))
        print "Perc: " + str(perc)
        import math
        perc = math.floor(perc)
        self.update(perc , "Add Item To directory: " + str(count) + " / " + str(total))
        return True
        
    def inc_buildcount(self):
        print "INC BUILD COUNT"
        self.buildcount += 1
        
    def inc_itemcount(self):
        self.itemcount += 1

    def update(self, p, t):
        p = int(p)
        if p < 0: p = 0
        if p > 100: p = 100
        if not self.showDialog: return False
        super(GuiProgress, self).update(p, t)
        return True

    def create(self, h, l1 = None):
        if not self.showDialog: return False
        super(GuiProgress, self).create(h, l1)
        self.isopen = True
        return True
    
    def iscanceled(self):
        if not self.showDialog: return False
        return super(GuiProgress, self).iscanceled()
    
    def close(self):
        if not self.isopen: return False
        return super(GuiProgress, self).close()

class Xbmc_renderer(IRenderer):

    def __init__(self, node_type, node_id = None, flag = 0):
        super(Xbmc_renderer, self).__init__(node_type, node_id, flag)
        self.depth = 2
        self.filter = 0

    def _add_to_directory(self, list, progress):
        step = 500
        size = len(list)
        start = 0
        print "SIZEEEEEEEEEEEEE: " + str(size)
        if size <= step:
            progress.update_addtodirectory(start, size)
            xbmcplugin.addDirectoryItems(handle = qobuz.boot.handle, items = list, totalItems = size)
            return True
        while start <= (size - step):
            print "BEGGGGGGGGGGGGGGGGGGGG: " + str(start)
            stop = start + step
            sublist = list[start:stop]
            progress.update_addtodirectory(start, size)
            xbmcplugin.addDirectoryItems(handle = qobuz.boot.handle, items = sublist, totalItems = len(sublist))
            start = stop
            time.sleep(1)
        if start <= size:
            print "COMPLETE LIST: " + str(start)
            progress.update_addtodirectory(start, size)
            xbmcplugin.addDirectoryItems(handle = qobuz.boot.handle, items = list[start:], totalItems = len(sublist))
        return True
    
    def display(self):
        #import xbmcgui
        progress = GuiProgress()#xbmcgui.DialogProgress()  
        action = ''
        bCacheToDisc = True
        if 'action' in qobuz.boot.params and qobuz.boot.params['action'] == 'scan':
            #progress.hide()
            action = 'scan'
            bCacheToDisc = False
        progress.create("Walking into the dark forest", "The beginning")
        progress.update(25, "1/4 One drop...")
        if not self.set_root_node():
            print "Cannot set root node (" + str(self.node_type) + ", " + str(self.node_id) + ")"
            return False
        if action == 'scan':
            self.depth = -1
            self.filter = NodeFlag.DONTFETCHTRACK
        progress.update_buildcount()
        self.root.build_down(self.depth, self.filter, progress)
        list = []

        #info(self, self.to_s())
        print "DEPTH: " + str(self.depth)
        print "FILTER: " + str(self.filter)
        progress.update_itemcount()
        ret = self.root.get_xbmc_items(list, self.depth, self.filter, progress)
        if progress.iscanceled():
            xbmcplugin.endOfDirectory(handle = qobuz.boot.handle, succeeded = False, updateListing = False, cacheToDisc = False)
            return False
        #if not ret: return False
        size = len(list)
        if size < 1: return False
        progress.update(100, "4/4 Add node to directory")
        print "Number of item: " + str(size)
        xbmcplugin.setContent(handle = qobuz.boot.handle, content = self.root.content_type)
        self._add_to_directory(list, progress)
        #xbmcplugin.addDirectoryItems(handle=qobuz.boot.handle, items=list, totalItems=size)
        xbmcplugin.endOfDirectory(handle = qobuz.boot.handle, succeeded = True, updateListing = False, cacheToDisc = bCacheToDisc)
        progress.close()
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