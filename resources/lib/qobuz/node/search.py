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
#import pprint

from debug import info, warn, error, debug
from flag import NodeFlag
from node import Node
from product import Node_product
from track import Node_track
from product_by_artist import Node_product_by_artist
from constants import Mode
from exception import QobuzXbmcError
from gui import notifyH

#from search.artists import Search_artists

class Node_search(Node):

    def __init__(self, parent = None, params = None):
        super(Node_search, self).__init__(parent, params)
        self.type = NodeFlag.TYPE_NODE | NodeFlag.TYPE_SEARCH
        self.search_type = 'albums'

    def get_label(self):
        return self.label

    def get_description(self):
        return self.get_label()

    ''' Property / search_type '''
    @property
    def search_type(self):
        return self._search_type
    
    @search_type.setter
    def search_type(self, st):
        if st == 'artists':
            self.label = qobuz.lang(30015)
            self.set_content_type('files')
        elif st == 'albums':
            self.label = qobuz.lang(30014)
            self.set_content_type('albums')
        elif st == 'tracks':
            self.label = qobuz.lang(30013)
            self.set_content_type('songs')
        else:
            raise QobuzXbmcError(who=self, what='invalid_type', additional=st)
        self._search_type = st
    @search_type.getter
    def search_type(self):
        return self._search_type


    def make_url(self, mode = Mode.VIEW):
        url = sys.argv[0] + '?mode=' + str(mode) + '&nt=' + str(self.get_type())
        url += '&search-type=' + self.search_type
        if 'action' in self.parameters and self.parameters['action'] == 'scan':
            url += "&action=scan"
        return url

    def _build_down(self, xbmc_directory, lvl, flag):
        stype = self.search_type
        search = None
        limit = None
        query = self.get_parameter('query')
        if not query:
            from qobuz.gui import Keyboard
            k = Keyboard('', stype)
            k.doModal()
            if not k.isConfirmed():
                return False
            query = k.getText()
        query.strip()
        data = qobuz.api.search_getResults(query=query, type=stype, limit=limit)
        if not data:
            warn(self, "Searching artists API call fail")
            return False
        if not data:
            warn(self, "Search return no data")
            return False
        self.notify_data_result(data)
        if self.search_type == 'albums':
            try:
                if data['albums']['items']: pass
            except: 
                return False
            for json_product in data['albums']['items']:
                artist = json_product['artist']['name']
                product = Node_product()
                product.set_data(json_product)
                self.add_child(product)
        elif self.search_type == 'tracks':
            try:
                if data['tracks']['items']: pass
            except: 
                return False
            for jtrack in data['tracks']['items']:
                track = Node_track()
                track.set_data(jtrack)
                self.add_child(track)
        elif self.search_type == 'artists':
            try:
                if data['artists']['items']: pass
            except: 
                return False
            for jartist in data['artists']['items']:
                artist = Node_product_by_artist()
                artist.set_data(jartist)
                self.add_child(artist)
        return True

    def notify_data_result(self, data):
        if not 'length' in data:
            warn(self, "Notify fail")
            return False
        notifyH("Qobuz Search - " + self.search_type,
                          'Artists: ' + str(data['length']['artists']) + " / "
                          'Products: ' + str(data['length']['products']) + " / "
                          'Songs: ' + str(data['length']['tracks']) + "\n"
                          , None, 5000)
        return True


