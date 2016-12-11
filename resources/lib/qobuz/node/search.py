'''
    qobuz.node.search
    ~~~~~~~~~~~~~~~~~

    :part_of: xbmc-qobuz
    :copyright: (c) 2012-2016 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
from qobuz import debug
from qobuz.node.inode import INode
from qobuz import exception
from qobuz.gui.util import lang, getImage
from qobuz.api import api
from qobuz.node import getNode, Flag

data_search_type = {
    'artists': {
        'label': lang(30017),
        'content_type': 'artists',
        'image': getImage('artist'),
    },
    'albums': {
        'label': lang(30016),
        'content_type': 'albums',
        'image': getImage('album'),
    },
    'tracks': {
        'label': lang(30015),
        'content_type': 'albums',
        'image': getImage('song'),
    },
}


class Node_search(INode):
    def __init__(self, parent=None, parameters={}, data=None):
        super(Node_search, self).__init__(
            parent=parent, parameters=parameters, data=data)
        self.nt = Flag.SEARCH
        self.content_type = 'albums'
        self.search_type = self.get_parameter('search-type', default=None)

    def make_url(self, *a, **ka):
        ka['search-type'] = self.search_type
        return super(Node_search, self).make_url(*a, **ka)

    def get_label(self):
        if self.search_type is None:
            return lang(30022)
        query = self.get_parameter('query', to='unquote')
        if query is not None:
            return 'search %s: %s [%s/%s]' % (self.search_type,
                                              self.get_parameter('query'),
                                              self.offset, self.limit)
        return data_search_type[self.search_type]['label']

    def get_image(self):
        if self.search_type is None:
            return getImage('song')
        return data_search_type[self.search_type]['image']

    def fetch(self, *a, **ka):
        if self.search_type is None:
            return {}
        query = self.get_parameter('query', to='unquote')
        if query is None:
            from qobuz.gui.util import Keyboard
            k = Keyboard('', self.search_type)
            k.doModal()
            if not k.isConfirmed():
                return None
            query = k.getText().strip()
            if query is None or query == '':
                return None
            self.set_parameter('query', query, quote=True)
        return api.get('/search/getResults',
                       query=query,
                       type=self.search_type,
                       limit=self.limit,
                       offset=self.offset)

    def _get_parameters(self):
        return {
            'query': self.get_parameter('query'),
            'search-type': self.search_type
        }

    def _populate_albums(self, *a, **ka):
        for album in self.data[self.search_type]['items']:
            self.add_child(
                getNode(
                    Flag.ALBUM, parameters=self._get_parameters(), data=album))
        return True if len(self.data[self.search_type]['items']) > 0 else False

    def _populate_tracks(self, *a, **ka):
        for track in self.data[self.search_type]['items']:
            self.add_child(
                getNode(
                    Flag.TRACK, parameters=self._get_parameters(), data=track))
        return True if len(self.data[self.search_type]['items']) > 0 else False

    def _populate_artists(self, *a, **ka):
        for artist in self.data[self.search_type]['items']:
            self.add_child(
                getNode(
                    Flag.ARTIST,
                    parameters=self._get_parameters(),
                    data=artist))
        return True if len(self.data[self.search_type]['items']) > 0 else False

    def populate(self, *a, **ka):
        if self.search_type is None:
            for search_type in data_search_type.keys():
                self.add_child(
                    getNode(
                        Flag.SEARCH, parameters={'search-type': search_type}))
            return True
        self.content_type = data_search_type[self.search_type]['content_type']
        return getattr(self, '_populate_%s' % self.search_type)(*a, **ka)
