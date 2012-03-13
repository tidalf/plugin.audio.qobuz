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

import xbmcgui

import qobuz
from constants import Mode
from flag import NodeFlag
from node import Node
from product import Node_product
from debug import info, warn, error
'''
    NODE RECOS
'''
from cache.recommendation import Cache_recommendation

class Node_recommendation(Node):

    def __init__(self, parent = None, parameters = None):
        super(Node_recommendation, self).__init__(parent, parameters)
        self.type = NodeFlag.TYPE_NODE | NodeFlag.TYPE_RECOMMENDATION
        genre_id = self.get_parameter('genre-id')
        if genre_id != None: self.genre_id = int(genre_id)
        else: self.genre_id = None
        self.genre_type = self.get_parameter('genre-type')
        self.set_label(qobuz.lang(30082))
        self.thumb = self.icon = qobuz.image.access.get('album')

    def make_url(self, mode = Mode.VIEW):
        url = sys.argv[0] + '?mode=' + str(mode) + '&nt=' + str(self.get_type())
        if self.genre_type:
            url += '&genre-type=' + self.genre_type
        if self.genre_id:
            url += '&genre-id=' + str(self.genre_id)
        if 'action' in self.parameters and self.parameters['action'] == 'scan': 
            url += "&action=scan"
        return url

    def setGenreType(self, type):
        self.genre_type = type

    def setGenreId(self, id):
        self.genre_id = id

    def getGenreType(self):
        return self.genre_type

    def getGenreId(self):
        return self.genre_id

# TYPE
    def _build_recos_type(self, lvl, flag):
        types = []
        types.append(('new-releases', qobuz.lang(30084)))
        types.append(('press-awards', qobuz.lang(30083)))
        types.append(('best-sellers', qobuz.lang(30085)))
        types.append(('editor-picks', qobuz.lang(30086)))
        for t in types:
            node = Node_recommendation()
            node.setGenreType(t[0])
            node.set_label(t[1])
            self.add_child(node)

# GENRE
    def _build_recos_genre(self, lvl, flag):
        types = []
        types.append((2, qobuz.lang(30093)))
        types.append((10, qobuz.lang(30095)))
        types.append((6, qobuz.lang(30090)))
        types.append((59, qobuz.lang(30098)))
        types.append((73, qobuz.lang(30201)))
        types.append((80, qobuz.lang(30089)))
        types.append((64, qobuz.lang(30202)))
        types.append((91, qobuz.lang(30094)))
        types.append((94, qobuz.lang(30092)))
        types.append((112, qobuz.lang(30087)))
        types.append((127, qobuz.lang(30200)))
        types.append((123, qobuz.lang(30203)))
        color = qobuz.addon.getSetting('color_ctxitem')
        for t in types:
            node = Node_recommendation()
            node.setGenreType(self.getGenreType())
            node.setGenreId(t[0])
            node.set_label(qobuz.utils.color(color, self.genre_type + ' / ') + t[1])
            self.add_child(node)


# TYPE GENRE
    def _build_down_type_genre(self, lvl, flag):
        self.cache = Cache_recommendation(self.genre_id, self.genre_type)
        data = self.cache.fetch_data()
        if not data: 
            warn(self, "Cannot fetch data for recommendation")
            return False
        self.set_data(data)
        for product in data:
            node = Node_product()
            node.set_data(product)
            self.add_child(node)
        return True

    def cache_image(self, product):
        id = 'recos-'+self.genre_type
        image = qobuz.image.cache.get(id)
        if not image: 
            qobuz.image.cache.set(id, product.get_image())
        id = 'recos-'+self.genre_type + '-' + str(self.genre_id)
        image = qobuz.image.cache.get(id)
        if not image: 
            qobuz.image.cache.set(id, product.get_image())
        

# DISPATCH
    def _build_down(self, lvl, flag = None, progress = None):
        if not self.genre_type:
            print "Build node type"
            return self._build_recos_type(lvl, flag)
        elif not self.genre_id:
            return self._build_recos_genre(lvl, flag)
        self.set_content_type('albums')
        return self._build_down_type_genre(lvl, flag)


    def hook_attach_context_menu(self, item, node, menuItems, color):
        pass

