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
'''
    NODE RECOS
'''
from cache.recommendation import Cache_recommendation

class Node_recommendation(Node):

    def __init__(self, parent = None, parameters = None):
        super(Node_recommendation, self).__init__(parent, parameters)
        self.type = NodeFlag.TYPE_NODE | NodeFlag.TYPE_RECOMMANDATION
        genre_id = self.get_parameter('genre-id')
        if genre_id != None: self.genre_id = int(genre_id)
        else: self.genre_id = None
        self.genre_type = self.get_parameter('genre-type')
        self.set_url()
        self.set_label("Recommendation")

    def set_url(self):
        url = sys.argv[0] + '?mode=' + str(Mode.VIEW) + '&nt=' + str(NodeFlag.TYPE_RECOMMANDATION)
        if self.genre_type:
            url += '&genre-type=' + self.genre_type
        if self.genre_id:
            url += '&genre-id=' + str(self.genre_id)
        self.url = url

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
            self.add_child(node)
            node.setGenreType(t[0])
            node.set_label(t[1])
            node.set_url()


    def _get_xbmc_items_type(self, list, lvl, flag):
        for t in self.get_childs():
            item = xbmcgui.ListItem(t.get_label(), '', '', '', t.get_url())
            self.attach_context_menu(item, self.type, None)
            list.append((t.get_url(), item, True))
        return True

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
        for t in types:
            node = Node_recommendation()
            node.setGenreType(self.getGenreType())
            node.setGenreId(t[0])
            node.set_label(t[1])
            node.set_url()
            self.add_child(node)

    def _get_xbmc_items_genre(self, list, lvl, flag):
        color = qobuz.addon.getSetting('color_recospath')
        for t in self.get_childs():
            item = xbmcgui.ListItem(qobuz.utils.color(color, self.genre_type) + ' / ' + t.get_label(), '', '', '', t.get_url())
            self.attach_context_menu(item, self.type, None)
            list.append((t.get_url(), item, True))
        return True


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

    def _get_xbmc_items_type_genre(self, list , lvl, flag):
        print "TypeGenre xbmc item"
        for product in self.get_childs():
            item = product.make_XbmcListItem()
            self.attach_context_menu(item, self.type, None)
            list.append((product.get_url(), item, product.is_folder()))
        return True

# DISPATCH
    def _build_down(self, lvl, flag = None):
        if not self.genre_type:
            print "Build node type"
            return self._build_recos_type(lvl, flag)
        elif not self.genre_id:
            return self._build_recos_genre(lvl, flag)
        self.set_content_type('albums')
        return self._build_down_type_genre(lvl, flag)


    def _get_xbmc_items(self, list, lvl, flag):
        if not self.genre_type:
            print "Displaying type"
            return self._get_xbmc_items_type(list, lvl, flag)
        elif not self.genre_id:
            print "Displaying genre"
            return self._get_xbmc_items_genre(list, lvl, flag)
        return self._get_xbmc_items_type_genre(list, lvl, flag)

    def hook_attach_context_menu(self, item, type, id, menuItems, color):
        pass
#        import sys
#        ''' Add to current playlist '''
#        url = sys.argv[0] + "?mode=" + str(MODE_ADD_TO_CURRENT_PLAYLIST) + '&nt=' + str(NodeFlag.TYPE_PRODUCT)
#        if self.genre_id:
#            url += '&genre-id=' + str(self.genre_id)
#        if self.genre_type:
#            url += '&genre-type=' + str(self.genre_type)
#        url += "&nid=" + str(id)
#        print "URL add current: " + url
#        menuItems.append((qobuz.utils.color(qobuz.addon.getSetting('color_ctxitem'), 'Add to current playlist'), "XBMC.RunPlugin(" + url + ")"))
#
#        ''' Creating new playlist with current node '''
#        ''' Add to current playlist '''
#        url = sys.argv[0] + "?mode=" + str(MODE_ADD_AS_NEW_PLAYLIST) + '&nt=' + str(NodeFlag.TYPE_PRODUCT)
#        url += "&nid=" + str(id)
#        print "URL: " + url
#        menuItems.append((qobuz.utils.color(qobuz.addon.getSetting('color_ctxitem'), 'Add as new playlist'), "XBMC.RunPlugin(" + url + ")"))
#        addtopl=sys.argv[0]+"?mode="+str(MODE_ADD_TO_NEW_PLAYLIST)+'&nt='+str(type)
#        if id: addtopl+='&nid='+id
#        menuItems.append((qobuz.utils.color(color, 'Create as new playlist'), "XBMC.RunPlugin("+addtopl+")"))
#        ''' Add current node to playlist '''
#        addtopl=sys.argv[0]+"?mode="+str(MODE_ADD_TO_PLAYLIST)+'&nt='+str(type)
#        if id: addtopl+='&nid='+id
#        menuItems.append((qobuz.utils.color(color, 'Add to current playlist'), "XBMC.RunPlugin("+addtopl+")"))    


