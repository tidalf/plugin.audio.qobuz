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
import pprint

import qobuz
from constants import Mode
from flag import NodeFlag
from node import Node
from debug import info, warn, error
'''
    NODE PLAYLIST
'''
from cache.playlist import Cache_playlist
from track import Node_track

class Node_playlist(Node):

    def __init__(self, parent = None, parameters = None):
        super(Node_playlist, self).__init__(parent, parameters)
        self.type = NodeFlag.TYPE_NODE | NodeFlag.TYPE_PLAYLIST
        self.current_playlist_id = None
        self.b_is_current = False
        self.set_content_type('songs')
#        self.tag = Tag_playlist()
        self.label = ""
        self.label2 = ""
        self.url = None
        self.thumb = ''
        self.icon = ''
        self.set_is_folder(True)
        self.cache = None

    def set_is_current(self, b):
        self.b_is_current = b

    def is_current(self):
        return self.b_is_current

    def _set_cache(self):
        id = self.get_id()
        if not id:
            try: id = self.get_parameter('nid')
            except: pass
        if not id:
            error(self, "Cannot set cache without id")
            return False
        self.cache = Cache_playlist(id)
        self.set_id(id)
        return True

    def _build_down(self, lvl, flag = None):
        info(self, "Build-down playlist")
        if not self._set_cache():
            error(self, "Cannot set cache!")
            return False
        data = self.cache.fetch_data()
        if not data:
            warn(self, "Build-down: Cannot fetch playlist data")
            return False
        self.set_data(data)
        for track in data['tracks']:
            node = Node_track()
            node.set_data(track)
            self.add_child(node)

    def _get_xbmc_items(self, list, lvl, flag):
        if len(self.childs) < 1:
            qobuz.gui.notify(36000, 36001)
            return False
        for track in self.childs:
            item = track.make_XbmcListItem()#tag.getXbmcItem()
            #print "LABEL: " + item.getLabel()
            self.attach_context_menu(item, track)
            url = track.get_url(Mode.PLAY)
            list.append((url, item, False))
        return True

    def hook_attach_context_menu(self, item, type, id, menuItems, color):
        import sys
        ''' DELETE '''
#        print "removing track id: " + str(id)
#        url = sys.argv[0] + "?mode=" + str(MODE_PLAYLIST_REMOVE_TRACK) + '&nt=' + str(type) + '&tracks_id=' + str(id)
#        if self.id: url += '&nid=' + str(self.id)
#        menuItems.append((qobuz.utils.color(qobuz.addon.getSetting('color_ctxitem'), 'Remove track from playlist'), "XBMC.RunPlugin(" + url + ")"))


    def getLabel(self):
        return self.tag.get_name()

    def get_name(self):
        if self._data and 'name' in self._data:
            return self._data['name']
        return ''

    def get_owner(self):
        if self._data and 'owner' in self._data:
            return self._data['owner']['name']
    
    def get_description(self):
        return self.get_property('description')
    
    def make_XbmcListItem(self):
        import xbmcgui
        item = xbmcgui.ListItem(self.get_name(),
                                self.get_owner(),
                                self.get_icon(),
                                self.get_thumbnail(),
                                self.get_url())
        #item.setPath(self.get_url())
        #item.setProperty('Path', self.get_url())
        return item


    def remove_tracks(self, tracks_id):
        import qobuz
        info(self, "Removing tracks: " + tracks_id)
        if not qobuz.api.playlist_remove_track(self.id, tracks_id):
            warn(self, "Cannot remove tracks from playlist: " + str(self.id))
            return False
        info(self, "Tracks removed from playlist: " + str(self.id))
        return True


