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
import xbmcgui

import qobuz

from flag import NodeFlag
from node import Node
from product_by_artist import Node_product_by_artist

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
        query = self.get_parameter('query')
        data = qobuz.api.artist_getSimilarArtists(artist_id=query)
        if not data: return False
        total = len(data['artists']['items'])
        
        for jartist in data['artists']['items']:
                artist = Node_product_by_artist()
                artist.set_data(jartist)
                self.add_child(artist)
        return total

