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
import xbmcgui, xbmc

import qobuz
from flag import NodeFlag
from node import Node
from recommendation import Node_recommendation, RECOS_TYPE_IDS
from gui.util import getImage

'''
    NODE GENRE
'''

class Node_genre(Node):

    def __init__(self, parent = None, parameters = None, progress = None):
        super(Node_genre, self).__init__(parent, parameters)
        self.type = NodeFlag.TYPE_NODE | NodeFlag.TYPE_GENRE
        self.set_label('Genre (i8n)')
        if self.parent: self.label = self.parent.label + ' / ' + self.label
        self.id = 1
        self.label2 = self.label
        self.url = None
        self.set_is_folder(True)
        self.image = getImage('album')
    
    def make_url(self, **ka):
        url = super(Node_genre, self).make_url(**ka)
        if self.parent and self.parent.id: url+="&parent-id=" + self.parent.id
        return url
    
    def hook_post_data(self):
        self.id = self.get_property('id')
        self.label = self.get_property('name')
    
    def get_name(self):
        return self.get_property('name')
    
    def _build_down_reco(self, dir, lvl, whiteFlag, id):
        for gtype in RECOS_TYPE_IDS:
            print "GTYPE " + repr(gtype)
            node = Node_recommendation(self, {'genre-id': id, 'genre-type': gtype })
            node.build_down(dir, lvl, whiteFlag)
#        node = Node_recommendation(None, {'genre-id': id, 'genre-type': 'press-awards' })
#        node.build_down(dir, lvl, whiteFlag)
#        node = Node_recommendation(None, {'genre-id': id, 'genre-type': 'best-sellers' })
#        node.build_down(dir, lvl, whiteFlag)
#        node = Node_recommendation(None, {'genre-id': id, 'genre-type': 'editor-picks' })
#        node.build_down(dir, lvl, whiteFlag)
#        node = Node_recommendation(None, {'genre-id': id, 'genre-type': 'most-featured' })
#        node.build_down(dir, lvl, whiteFlag)
        return True
        
    def _build_down(self, dir, lvl, flag = None):
        offset = self.get_parameter('offset') or 0
        limit = qobuz.addon.getSetting('pagination_limit')
        data = qobuz.registry.get(name='genre-list', id=self.id, offset=offset, limit=limit)
        if not data or len(data['data']['genres']['items']) == 0:
            return self._build_down_reco(dir, lvl, flag, self.id)
        for genre in data['data']['genres']['items']:
            node = Node_genre()
            node.data = genre
            if 'parent' in genre and genre['parent']['level'] > 2:
                self._build_down_reco(dir, lvl, flag, genre['id'])
            self.add_child(node)
        return True
