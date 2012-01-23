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
from constants import *
from flag import NodeFlag
from node import node
'''
    NODE TRACK
'''
from data.recommandation import QobuzGetRecommandation
from tag.product import TagProduct

class node_recos(node):
    
    def __init__(self, parent = None):
        super(node_recos, self).__init__(parent)
        self.type = NodeFlag.TYPE_NODE | NodeFlag.TYPE_RECOMMANDATION
        
    def _build_recos_type(self, lvl, flag):
        return False
    
    def _build_recos_genre(self, lvl, flag):
        return False
    
    def _build_down(self, lvl, flag = None):
        genre_id = self.getParameter('genre_id')
        genre_type = self.getParameter('genre_type')
        if not genre_id:
            return self._build_recos_type(lvl, flag)
        elif not genre_type:
            return self._build_recos_genre(lvl, flag)
        assert(False)
#        o = QobuzGetRecommandation(genre_id, genre_type)
#        data = o.get_data()
#        self.setJson(data)
#
    def _get_xbmc_items_genre(self, list, lvl, flag):
        types = []
        types.append((2, "Blues/Country/Folk"))
        types.append((10, "Classique"))
        types.append((64, "Techno"))
        types.append((73, "Enfants"))
        for t in types:
            url = sys.argv[0] + '/?mode=' + str(MODE_NODE) + '&nt=' + str(NodeFlag.TYPE_RECOMMANDATION)+'&genre_type='+self.getParameter('genre_type')+'&genre_id=' + str(t[0])
            item = xbmcgui.ListItem(t[1], '', '', '', url)
            list.append((url, item, True))
            
    def _get_xbmc_items_type(self, list, lvl, flag):
        types = []
        types.append(('news', "News"))
        types.append(('press-awards', "Press Awards"))
        types.append(('best-sellers', "Best Sellers"))
        types.append(('editors-picks', "Editor's picks"))
        for t in types:
            url = sys.argv[0] + '/?mode=' + str(MODE_NODE) + '&nt=' + str(NodeFlag.TYPE_RECOMMANDATION)+'&genre_type=' + t[0]
            item = xbmcgui.ListItem(t[1], '', '', '', url)
            list.append((url, item, True))
        
    def _get_xbmc_items(self, list, lvl, flag):
        genre_id = self.getParameter('genre_id')
        genre_type = self.getParameter('genre_type')
        if not genre_type:
            print "Displaying type"
            return self._get_xbmc_items_type(list, lvl, flag)
        elif not genre_id:
            print "Displaying genre"
            return self._get_xbmc_items_genre(list, lvl, flag)
        print "Displaying recos"
        assert(False)
#        t = TagTrack(self.getJson())
#        self.setUrl()
#        item =  t.getXbmcItem(context = 'album', pos = 0, fanArt = 'fanArt')
#        list.append((item.getProperty('path'),item , False))
        
        
        