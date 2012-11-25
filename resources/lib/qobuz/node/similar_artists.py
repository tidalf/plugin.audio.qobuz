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
from artist import Node_artist
from debug import info, warn, error, debug
from cache.search_artists import Cache_search_artists
import urllib
import re
from xml.dom.minidom import parse, parseString
'''
    NODE ARTIST
'''

class Node_similar_artist(Node):

    def __init__(self, parent = None, parameters = None):
        super(Node_similar_artist, self).__init__(parent, parameters)
        self.type = NodeFlag.TYPE_NODE | NodeFlag.TYPE_SIMILAR_ARTIST
        self.set_content_type('albums')
        

    '''
        Getter 
    '''
    def get_label(self):
        return qobuz.lang(39000)
    
    def get_label2(self):
        return ""
        
    '''
        Build Down
    '''
    def _build_down(self, xbmc_directory, lvl, flag = None):
        query = self.get_parameter('query') # .strip().lower()
        data = qobuz.api.get_similar_artists(query)
        debug (self, pprint.pformat(data))
        if not data: return False
        total = len(data['artists']['items'])
        
        for jartist in data['artists']['items']:
                artist = Node_artist()
                artist.set_data(jartist)
                self.add_child(artist)
        return total

