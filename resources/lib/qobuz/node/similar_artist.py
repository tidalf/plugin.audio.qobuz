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
#import xbmcgui

import qobuz

from flag import NodeFlag
from node import Node
from product_by_artist import Node_product_by_artist
from artist import Node_artist
from gui.util import lang

import pprint
'''
    NODE ARTIST
'''


class Node_similar_artist(Node):

    def __init__(self, parent=None, parameters=None):
        super(Node_similar_artist, self).__init__(parent, parameters)
        self.type = NodeFlag.NODE | NodeFlag.SIMILAR_ARTIST
        self.content_type = 'artist'

    '''
        Getter
    '''
    def get_label(self):
        return lang(39000)

    def get_label2(self):
        return self.get_label()
    
    '''
        Build Down
    '''
    def _build_down(self, xbmc_directory, lvl, flag=None):
        print "Build down similar artist"
        offset = self.get_parameter('offset') or 0
        limit = qobuz.addon.getSetting('pagination_limit')
        data = qobuz.registry.get(name='artist-similar', id=self.id,
            artist_id=self.id, offset=offset, limit=limit)
        if not data:
            return 0
        for aData in data['data']['artists']['items']:
            #pprint.pprint(aData)
            artist = Node_artist(self)
            artist.data = aData
            #print 'Name: ' + repr(artist.get_name())
            self.add_child(artist)
        self.add_pagination(data)
        return len(data['data']['artists']['items'])
