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
import qobuz

from debug import warn
from flag import NodeFlag
from inode import INode
from product import Node_product
from track import Node_track
from product_by_artist import Node_product_by_artist
from exception import QobuzXbmcError
from gui.util import notifyH, lang, getImage
import urllib

class Node_search(INode):

    def __init__(self, parent=None, params=None):
        super(Node_search, self).__init__(parent, params)
        self.type = NodeFlag.NODE | NodeFlag.SEARCH
        self.search_type = self.get_parameter('search-type') or 'albums'
        self.query = None

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
            self.label = lang(30015)
            self.content_type = 'files'
            self.image = getImage('artist')
        elif st == 'albums':
            self.label = lang(30014)
            self.content_type = 'albums'
            self.image = getImage('album')
        elif st == 'tracks':
            self.label = lang(30013)
            self.content_type = 'songs'
            self.image = getImage('song')
        else:
            raise QobuzXbmcError(who=self, what='invalid_type', additional=st)
        self._search_type = st

    @search_type.getter
    def search_type(self):
        return self._search_type

    def make_url(self, **ka):
        url = super(Node_search, self).make_url(**ka)
        url += '&search-type=' + self.search_type
        query = self.query or self.get_parameter('query')
        if query:
            url += '&query=' + query
        return url

    def pre_build_down(self, Dir, lvl, whiteFlag, blackFlag):
        offset = self.get_parameter('offset') or 0
        limit = qobuz.addon.getSetting('pagination_limit')
        stype = self.search_type
        search = None
        query = self.get_parameter('query')
        if not query:
            from gui.util import Keyboard
            k = Keyboard('', stype)
            k.doModal()
            if not k.isConfirmed():
                return False
            query = k.getText()
        query.strip()
        data = qobuz.api.search_getResults(
            query=query, type=stype, limit=limit, offset=offset)
        if not data:
            warn(self, "Search return no data")
            return False
        self.set_parameter('query', (urllib.quote_plus(query)) )
        self.data = data
        return True
    
    def _build_down(self, Dir, lvl, whiteFlag, blackFlag):
        if self.search_type == 'albums':
            try:
                if self.data['albums']['items']:
                    pass
            except:
                return False
            for json_product in self.data['albums']['items']:
                artist = json_product['artist']['name']
                product = Node_product()
                product.data = json_product
                self.add_child(product)
        elif self.search_type == 'tracks':
            try:
                if self.data['tracks']['items']:
                    pass
            except:
                return False
            for jtrack in self.data['tracks']['items']:
                track = Node_track()
                track.data = jtrack
                self.add_child(track)
        elif self.search_type == 'artists':
            try:
                if self.data['artists']['items']:
                    pass
            except:
                return False
            for jartist in self.data['artists']['items']:
                artist = Node_product_by_artist()
                artist.data = jartist
                self.add_child(artist)
        return True

    def notify_data_result(self, data):
        if not 'length' in data:
            warn(self, "Notify fail")
            return False
        notifyH("Qobuz Search - " + self.search_type,
                'Artists: ' + str(data['length']['artists']) + " / "
                'Products: ' + str(
                    data['length']['products']) + " / "
                'Songs: ' + str(data['length']['tracks']) + "\n",
                getImage('default'),
                2000)
        return True
