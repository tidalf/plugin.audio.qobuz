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
from debug import info, warn, error
from flag import NodeFlag
from node import Node
import qobuz
from constants import Mode
from search.albums import Search_albums
            
class Node_search(Node):

    def __init__(self, parent = None, params = None):
        super(Node_search, self).__init__(parent, params)
        self.type = NodeFlag.TYPE_NODE | NodeFlag.TYPE_SEARCH
        self.search_type = 'albums'

    def get_label(self):
        if self.search_type == 'artists':
            return "Searching artist"
        elif self.search_type == 'albums':
            return "Searching albums"
        elif self.search_type == 'songs':
            return "Searching for songs"
    
    def set_search_type(self, st):
        print "Set search type: " + st
        self.search_type = st
        
    def get_search_type(self):
        return self.search_type

    
    def make_url(self, mode = Mode.VIEW):
        url = sys.argv[0] + '?mode=' + str(mode) + '&nt=' + str(self.get_type())
        url += '&search-type=' + self.search_type
        return url
        
    def _get_xbmc_items(self, list, lvl, flag):
        stype = self.get_search_type()
        search = None
        limit = None
        if stype == 'songs':
            print "Searching songs"
            search = qobuz.core.getQobuzSearchTracks()
            limit = qobuz.addon.getSetting('songsearchlimit')
            heading = qobuz.lang(30013)
            self.set_content_type('songs')
        elif stype == 'albums':
            print "Searching albums"
            search = Search_albums()
            limit = qobuz.addon.getSetting('albumsearchlimit')
            heading = qobuz.lang(30014)
            self.set_content_type('albums')
        elif stype == 'artists':
            print "Searching artists"
            from search.artists import Search_artists
            search = Search_artists()
            limit = qobuz.addon.getSetting('artistsearchlimit')
            heading = qobuz.lang(30015)
            self.set_content_type('files')
        else:
            error(self, "Unknown search-type: " + stype)
        query = self.get_parameter('query')
        if not query:
            query = self._get_keyboard('', heading)
            if not query:
                return False
        query.strip()
        print "Query: " + query
        search.search(query, limit)
        slist = search.get_items()
        if len(slist) < 1:
            qobuz.gui.notification(36000, 35001)
            self._get_xbmc_items(list, lvl, flag)
            return False
        list.extend(slist)
        return True

    def _get_keyboard(self, default = "", heading = "", hidden = False):
        import xbmc
        kb = xbmc.Keyboard(default, heading, hidden)
        kb.doModal()
        if (kb.isConfirmed()):
            return unicode(kb.getText(), "utf-8")
        return ''
