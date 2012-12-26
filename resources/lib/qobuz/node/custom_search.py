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
import qobuz
from debug import info, warn, error, debug
from flag import NodeFlag
from node import Node
from product import Node_product
from track import Node_track
from constants import Mode
import pprint


import xbmc, xbmcgui, xbmcplugin

class QobuzSearchKeyboard(xbmcgui.WindowXML):
    def __init__(self,*a,**ka):
        super(QobuzSearchKeyboard, self).__init__(*a, **ka)
    
    def onInit(self):
        self.btnClose = xbmcgui.ControlButton(100, 250, 200, 50, 'Status', font='font14')
        self.addControl(self.btnClose)
    
class Node_custom_search(Node):

    def __init__(self, parent = None, params = None):
        super(Node_custom_search, self).__init__(parent, params)
        self.type = NodeFlag.TYPE_NODE | NodeFlag.TYPE_CUSTOM_SEARCH
        self.label = "xSearch (beta)"


    def get_description(self):
        return self.get_label()

    def pre_build_down(self):
#        kb = QobuzSearchKeyboard()
#        kb.doModal()
        xbmcplugin.endOfDirectory(handle = 0,
                                   succeeded = False,
                                   updateListing = False,
                                   cacheToDisc = False)
        from gui.dialog.search import Dialog
        name = 'plugin.audio.qobuz-search.xml'
        print 'name: ' + name
        d = QobuzSearchKeyboard(name, qobuz.addon.getAddonInfo('path'), 'default')
        d.doModal()
        d.close()
        del d

        return False
    
    def _build_down(self, xbmc_directory, lvl, flag):
        pass
        


