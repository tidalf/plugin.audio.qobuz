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
from gui.util import notifyH, getImage, color


class XbmcWindow_musicfiles(xbmcgui.Window):

    def __init__(self, **ka):
        # 10501 / WINDOW_MUSIC_FILES
        # (http://wiki.xbmc.org/index.php?title=Window_IDs)
        xbmcgui.Window(10501)

    def onAction(self, action):
        print 'Action: ' + repr(action.getId())


class Xbmc_renderer(IRenderer):

    def __init__(self, node_type, node_id=None):
        super(Xbmc_renderer, self).__init__(node_type, node_id)

    def add_directory_item(self, **ka):
        if not 'is_folder' in ka:
            ka['is_folder'] = 1
        if not 'image' in ka:
            ka['image'] = ''
        item = ka['dir']._xbmc_item(**ka)
        ka['dir'].add_item(url=ka['url'], item=item, is_folder=ka['is_folder'])

    def display(self):
        from gui.directory import Directory
        if not self.set_root_node():
            warn(
                self, ("Cannot set root node (%s, %s)") % (str(self.node_type),
                                                           str(self.node_id)))
            return False
        if 'nm' in qobuz.boot.params:
            methodName = qobuz.boot.params['nm']
            log(self, "Executing method on node: " + repr(methodName))
            getattr(self.root, methodName)()
            return True
        if not self.root.pre_build_down():
            return False
        Dir = Directory(self.root, qobuz.boot.handle, False)
        self.root.build_down(Dir, self.depth, self.filter)
        if self.root.pagination_next:
            colorItem = qobuz.addon.getSetting('color_item')
            nextString = (
                '[ %s  %s / %s ]') % (color(colorItem, self.root.get_label()),
                                      self.root.pagination_next_offset,
                                      self.root.pagination_total)
            print "NextString set: " + nextString
            self.add_directory_item(dir=Dir,
                                    label=nextString,
                                    url=self.root.pagination_next,
                                    image=getImage('next'))
        Dir.set_content(self.root.content_type)
        methods = [
            xbmcplugin.SORT_METHOD_UNSORTED,
            xbmcplugin.SORT_METHOD_LABEL,
            xbmcplugin.SORT_METHOD_DATE,
            xbmcplugin.SORT_METHOD_TITLE,
            xbmcplugin.SORT_METHOD_VIDEO_YEAR,
            xbmcplugin.SORT_METHOD_GENRE,
            xbmcplugin.SORT_METHOD_ARTIST,
            xbmcplugin.SORT_METHOD_ALBUM,
            xbmcplugin.SORT_METHOD_PLAYLIST_ORDER,
            xbmcplugin.SORT_METHOD_TRACKNUM, ]
        [xbmcplugin.addSortMethod(handle=qobuz.boot.handle,
                                  sortMethod=method) for method in methods]
        Dir.end_of_directory()
        return True

    def scan(self):
        from gui.directory import Directory
        if not self.set_root_node():
            warn(self, "Cannot set root node (" + str(
                self.node_type) + ", " + str(self.node_id) + ")")
            return False
        Dir = Directory(self.root, qobuz.boot.handle, False)
        self.root.build_down(Dir, -1, NodeFlag.TRACK | NodeFlag.DONTFETCHTRACK)
        Dir.set_content(self.root.content_type)
        Dir.end_of_directory()
        notifyH('Scanning results', str(Dir.total_put) +
                ' items where scanned', 3000)
        return True
