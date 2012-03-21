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
import random
import pprint

import xbmcgui

import qobuz
from constants import Mode
from flag import NodeFlag
from node import Node
from product import Node_product
from debug import info, warn, error

RECOS_TYPES = {
                     'new-releases': qobuz.lang(30084),
                      'press-awards': qobuz.lang(30083),
                      'best-sellers': qobuz.lang(30085),
                      'editor-picks': qobuz.lang(30086),
                      }

RECOS_GENRES = {
              2: qobuz.lang(30093),
              10: qobuz.lang(30095),
              6: qobuz.lang(30090),
              59: qobuz.lang(30098),
              73: qobuz.lang(30201),
              80: qobuz.lang(30089),
              64: qobuz.lang(30202),
              91: qobuz.lang(30094),
              94: qobuz.lang(30092),
              112: qobuz.lang(30087),
              127: qobuz.lang(30200),
              123: qobuz.lang(30203),
              'null': 'All',
              }
'''
    NODE RECOS
'''
from cache.recommendation import Cache_recommendation

class Node_recommendation(Node):

    def __init__(self, parent = None, parameters = None):
        super(Node_recommendation, self).__init__(parent, parameters)
        self.type = NodeFlag.TYPE_NODE | NodeFlag.TYPE_RECOMMENDATION
        genre_id = self.get_parameter('genre-id')
        if genre_id != None: self.genre_id = genre_id
        else: self.genre_id = None
        self.genre_type = self.get_parameter('genre-type')
        self.set_label(qobuz.lang(30082))
        self.image = qobuz.image.access.get('album')

    def make_url(self, mode = Mode.VIEW):
        url = sys.argv[0] + '?mode=' + str(mode) + '&nt=' + str(self.get_type())
        if self.genre_type:
            url += '&genre-type=' + self.genre_type
        if self.genre_id:
            url += '&genre-id=' + str(self.genre_id)
        if 'action' in self.parameters and self.parameters['action'] == 'scan':
            url += "&action=scan"
        return url

    def set_genre_type(self, type):
        self.genre_type = type

    def set_genre_id(self, id):
        self.genre_id = id

    def get_genre_type(self):
        return self.genre_type

    def get_genre_id(self):
        return self.genre_id

# TYPE
    def _build_recos_type(self, xbmc_directory, lvl, flag):
        types = []
        color = qobuz.addon.getSetting('color_item')
        for gtype in RECOS_TYPES:
            node = Node_recommendation()
            node.set_genre_type(gtype)
            node.set_label(self.label + ' / ' + qobuz.utils.color(color, RECOS_TYPES[gtype]))
            self.add_child(node)
        return True

# GENRE
    def _build_recos_genre(self, xbmc_directory, lvl, flag):
        types = []
        color = qobuz.addon.getSetting('color_item')
        for genreid in RECOS_GENRES:
            node = Node_recommendation()
            type = self.get_genre_type()
            node.set_genre_type(self.get_genre_type())
            node.set_genre_id(genreid)
            if qobuz.addon.getSetting('userplaylists_display_cover') == 'true':
                image_name = 'recos-%s-%s' % (type, genreid)
                image = qobuz.image.cache.get(image_name)
                if image: node.image = image
            node.set_label(self.label + ' / ' + qobuz.utils.color(color, RECOS_TYPES[self.genre_type]) + ' / ' + RECOS_GENRES[genreid])
            self.add_child(node)
        return True


# TYPE GENRE
    def _build_down_type_genre(self, xbmc_directory, lvl, flag):
        self.cache = Cache_recommendation(self.genre_id, self.genre_type)
        data = self.cache.fetch_data()
        if not data:
            warn(self, "Cannot fetch data for recommendation")
            return False
        self.set_data(data)
        if qobuz.addon.getSetting('userplaylists_display_cover') == 'true':
            genre_id = self.get_genre_id()
            if genre_id != 'null': genre_id = str(genre_id)
            image_name = 'recos-%s-%s' % (self.get_genre_type(), genre_id)
            image = qobuz.image.cache.get(image_name)
            if not image: self._get_random_image_type_genre(image_name, data)
        for product in data:
            node = Node_product()
            node.set_data(product)
            self.add_child(node)
        return True

    def _get_random_image_type_genre(self, image_name, data):
        if not data: return None
        size = len(data)
        if size < 1: return None
        r = random.randint(0, size - 1)
        image = ''
        try:
            image = data[r]['image']['large']
            image.replace("_230.", "_600.")
        except: pass
        if not image: return None
        qobuz.image.cache.set(image_name, image)
        return image

#    def cache_image(self, product):
#        id = 'recos-'+self.genre_type
#        image = qobuz.image.cache.get(id)
#        if not image: 
#            qobuz.image.cache.set(id, product.get_image())
#        id = 'recos-'+self.genre_type + '-' + str(self.genre_id)
#        image = qobuz.image.cache.get(id)
#        if not image: 
#            qobuz.image.cache.set(id, product.get_image())


# DISPATCH
    def _build_down(self, xbmc_directory, lvl, flag = None, progress = None):
        if not self.genre_type:
            return self._build_recos_type(xbmc_directory, lvl, flag)
        elif not self.genre_id:
            return self._build_recos_genre(xbmc_directory, lvl, flag)
        self.set_content_type('albums')
        return self._build_down_type_genre(xbmc_directory, lvl, flag)


