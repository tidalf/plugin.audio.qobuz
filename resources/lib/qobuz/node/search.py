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
import qobuz
from debug import info, warn, error
from flag import NodeFlag
from node import Node
from product import Node_product
from track import Node_track
from artist import Node_artist
from constants import Mode
import pprint

#from search.artists import Search_artists
            
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

    def _get_xbmc_items(self, p_list, lvl, flag):
        stype = self.get_search_type()
        search = None
        limit = None
        if stype == 'songs':
            from qobuz.search.tracks import Search_tracks
            print "Searching songs"
            search = Search_tracks()
            limit = qobuz.addon.getSetting('songsearchlimit')
            heading = qobuz.lang(30013)
            self.set_content_type('songs')
        elif stype == 'albums':
            from qobuz.search.albums import Search_albums
            print "Searching albums"
            search = Search_albums()
            limit = qobuz.addon.getSetting('albumsearchlimit')
            heading = qobuz.lang(30014)
            self.set_content_type('albums')
        elif stype == 'artists':
            print "Searching artists"
            from qobuz.search.artists import Search_artists
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
        ret = search.search(query, limit)
        if not ret:
            warn(self, "Searching artists API call fail")
            return p_list
        data = search.get_data()
        #print pprint.pformat(data)
        self.notify_data_result(data)
        if self.search_type == 'albums':
            for json_product in data:
                json_product = json_product['product']
                artist = json_product['artist']
                json_product['artist'] = { }
                json_product['artist']['name'] = artist
                product = Node_product()
                product.set_data(json_product)
                item = product.make_XbmcListItem()
                self.attach_context_menu(item, product)
                p_list.append((product.get_url(), item, product.is_folder()))
        elif self.search_type == 'songs':
            #print "DATA: " + pprint.pformat(data)
            for jtrack in data['tracks']:
                track = Node_track()
                track.set_data(jtrack)
                print "Track"
                pprint.pprint(jtrack)
                item = track.make_XbmcListItem()
                self.attach_context_menu(item, track)
                p_list.append((track.get_url(Mode.PLAY), item, track.is_folder()))
                 
        elif self.search_type == 'artists':
            print "NOT IMPLEMENTED (search artists)"
            for jartist in data['results']['artists']:
                print "ARTIST JSON"
                pprint.pprint(jartist)
                artist = Node_artist()
                artist.set_data(jartist)
                item = artist.make_XbmcListItem()
                self.attach_context_menu(item, artist)
                p_list.append((artist.get_url(), item, artist.is_folder()))
        return p_list

    def notify_data_result(self, data):
        if not 'length' in data:
            warn(self, "Notify fail")
            return False
        qobuz.gui.notifyH("Qobuz Search - " + self.search_type,
                          'Artists: ' + str(data['length']['artists']) + " / "
                          'Products: ' + str(data['length']['products']) + " / "
                          'Songs: ' + str(data['length']['tracks']) + "\n"
                          , None, 5000)
        return True
    
    def _get_keyboard(self, default = "", heading = "", hidden = False):
        import xbmc
        kb = xbmc.Keyboard(default, heading, hidden)
        kb.doModal()
        if (kb.isConfirmed()):
            return unicode(kb.getText(), "utf-8")
        return ''
