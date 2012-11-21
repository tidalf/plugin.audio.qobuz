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
    NODE PLAYLIST
'''
#from cache.playlist import Cache_playlist
from track import Node_track

class Node_favorites(Node):

    def __init__(self, parent = None, parameters = None, progress = None):
        super(Node_favorites, self).__init__(parent, parameters)
        self.type = NodeFlag.TYPE_NODE | NodeFlag.TYPE_FAVORITES
        self.set_label(qobuz.lang(30079))
        #self.set_is_folder(True)
        #self.cache = None
        self.packby = ''#album'
        self.image = qobuz.image.access.get('playlist')
        #if self.packby == 'album':
        #    self.set_content_type('albums')
        #else:
        
        self.name = qobuz.lang(30079)
        self.label = qobuz.lang(30079)
        
        self.set_content_type('songs')
        self.set_auto_set_cache(True)

    # def get_label(self):
    #    return self.get_name()

    def set_cache(self):
        id = "1348794"
        from cache.favorites import Cache_favorites
        if not id:
            try: id = self.get_parameter('nid')
            except: pass
        if not id:
            error(self, "Cannot set cache without id")
            return False
        self.cache = Cache_favorites(id)
        return True

    def _build_down(self, xbmc_directory, lvl, flag = None):
        info(self, "Build-down favorites")
        if not self.set_cache():
            error(self, "Cannot set cache!")
            return False
        data = self.cache.fetch_data(xbmc_directory.Progress)
        if not data:
            warn(self, "Build-down: Cannot fetch favorites data")
            return False
        self.set_data(data)
        albumseen = {}
        warn (self, pprint.pformat(data))
        for jtrack in data['tracks']['items']:
            node = None
            #if self.packby == 'album':
            node = Node_track()
            node.set_data(jtrack)
            self.add_child(node)
        for product in self.filter_products(self.cache.get_data()):
            self.add_child(product)
        return True
        
        
        del self._data['tracks']
        
    def get_name(self):
        name = self.get_property('name')
        return name
    
    def get_owner(self):
        return self.get_property(('owner', 'name'))
            
    def get_description(self):
        return self.get_property('description')
    
    def make_XbmcListItem(self):
        color_item = qobuz.addon.getSetting('color_item')
        color_pl = qobuz.addon.getSetting('color_item_playlist')
        # label = self.get_name() 
        image = self.get_image()
        owner = self.get_owner()
        url = self.make_url()
        #if not self.is_my_playlist: 
        #    label = qobuz.utils.color(color_item, owner) + ' - ' + self.get_name() 
        # label = qobuz.utils.color(color_pl, label)
        item = xbmcgui.ListItem(self.label,
                                owner,
                                image,
                                image,
                                url)
        if not item:
            warn(self, "Error: Cannot make xbmc list item")
            return None
        item.setPath(url)
        self.attach_context_menu(item)
        return item

    def hook_attach_context_menu(self, item, menuItems):
        color = qobuz.addon.getSetting('color_item')
        color_warn = qobuz.addon.getSetting('color_item_caution')
        label = self.get_label()
                        
#        ''' CREATE '''
#        url = self.make_url(Mode.PLAYLIST_CREATE)
#        menuItems.append((qobuz.utils.color(color, qobuz.lang(39008)), "XBMC.RunPlugin("+url+")"))

#        ''' REMOVE '''
#        url = self.make_url(Mode.FAVORITE_REMOVE)
#        menuItems.append((qobuz.utils.color(color_warn, qobuz.lang(39010).encode('utf8', 'replace') + ': ') + label, "XBMC.RunPlugin("+url+")"))
        

    
    def filter_products(self, data):
        list = []
        if not data: return list
        # Qobuz free tracks with invalid product id
        #blackid = ['0000020110926', '0000201011300', '0000020120220', '0000020120221']
        albumseen = {}
        for track in data['albums']['items']:
            json = track
            # json[u'composer'] = track['composer']
            json[u'interpreter'] = track['artist']['name']
            product = Node_product()
            product.set_data(json)
            id = product.get_id()
            #if id in blackid: product.is_special_purchase = True
            if id in albumseen: continue
            albumseen[id] = 1
            list.append(product)
        return list

