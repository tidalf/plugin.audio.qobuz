'''
    qobuz.node.search
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    This file is part of qobuz-xbmc

    :copyright: (c) 2012 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''

from qobuz.debug import warn
from qobuz.exception import InvalidType
from inode import INode
from qobuz.api import api
from qobuz.node import getNode, Flag
from qobuz.i8n import _


class Node_search(INode):

    def __init__(self, parameters=None):
        super(Node_search, self).__init__(parameters)
        self.kind = Flag.SEARCH
        self.search_type = self.get_parameter('search-type',
                                              delete=True) or 'albums'
        self.query = self.get_parameter('query',
                                        decode=True,
                                        delete=True)
        self.label = _('Search')

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
            self.label = _('Search artist')
            self.content_type = 'files'
        elif st == 'albums':
            self.label = _('Search album')
            self.content_type = 'albums'
        elif st == 'tracks':
            self.label = _('Search song')
            self.content_type = 'songs'
        else:
            raise InvalidType(st)
        self._search_type = st

    @search_type.getter
    def search_type(self):
        return self._search_type

    def url(self, **ka):
        ka['search_type'] = self.search_type
        if self.query and not 'query' in ka:
            ka['query'] = self.query
        return super(Node_search, self).url()

    def fetch(self, renderer=None):
        stype = self.search_type
        query = self.query
        if not query:
            from xbmcpy.keyboard import Keyboard
            k = Keyboard('', stype)
            k.doModal()
            if not k.isConfirmed():
                return False
            query = k.getText()
        query.strip()
        data = api.get('/search/getResults', query=query, type=stype,
                           limit=api.pagination_limit, offset=self.offset)
        if not data:
            warn(self, "Search return no data")
            return False
        if data[stype]['total'] == 0:
            return False
        if not 'items' in data[stype]:
            return False
        self.set_parameter('query', query, encode=True)
        self.data = data
        return True

    def populate(self, renderer=None):
        if self.search_type == 'albums':
            for album in self.data['albums']['items']:
                node = getNode(Flag.ALBUM, self.parameters)
                node.data = album
                self.append(node)
        elif self.search_type == 'tracks':
            for track in self.data['tracks']['items']:
                node = getNode(Flag.TRACK, self.parameters)
                node.data = track
                self.append(node)
        elif self.search_type == 'artists':
            for artist in self.data['artists']['items']:
                node = getNode(Flag.ARTIST, self.parameters)
                node.data = artist
                self.append(node)
        return True
