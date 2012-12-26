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

    def __init__(self, node_type, node_id = None):
        super(Xbmc_renderer, self).__init__(node_type, node_id)

    def display(self):
        from gui.directory import Directory
        if not self.set_root_node():
            warn(self, "Cannot set root node (" + str(self.node_type) + ", " + str(self.node_id) + ")")
            return False
        buildDown = self.root.pre_build_down()
        if buildDown:
            dir = Directory(self.root, qobuz.boot.handle, False)
            self.root.build_down(dir, self.depth, self.filter)
            dir.set_content(self.root.content_type)
#            xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_TITLE)
#            xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_LABEL)
#            xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_NONE)
            dir.end_of_directory()
        return True

    def scan(self):
        from gui.directory import Directory
        if not self.set_root_node():
            warn(self, "Cannot set root node (" + str(self.node_type) + ", " + str(self.node_id) + ")")
            return False
        dir = Directory(self.root, qobuz.boot.handle, False)
        self.root.build_down(dir, -1, NodeFlag.TYPE_TRACK | NodeFlag.DONTFETCHTRACK)
        dir.set_content(self.root.content_type)
        dir.end_of_directory()
        qobuz.gui.notifyH('Scanning results', str(dir.total_put) + ' items where scanned', 3000)
        return True
