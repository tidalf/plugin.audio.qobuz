'''
    qobuz.node.collection
    ~~~~~~~~~~~~~~~~~~~~~

    :part_of: xbmc-qobuz
    :copyright: (c) 2012-2016 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
from qobuz.node.inode import INode
from qobuz.node import Flag, getNode
from qobuz.api import api
from qobuz import debug
from qobuz.gui.util import getImage, lang

from qobuz.util.converter import converter

dialogHeading = 'Collection'


class Node_collection(INode):
    def __init__(self, parent=None, parameters={}, data=None):
        super(Node_collection, self).__init__(
            parent=parent, parameters=parameters, data=data)
        self.nt = Flag.COLLECTION
        self.url = None
        self.image = getImage('songs')
        self.search_type = self.get_parameter('search-type')
        self.query = self.get_parameter('query', to='unquote')
        self.source = self.get_parameter('source')
        self.content_type = 'albums'

    def get_label(self):
        if self.search_type is None:
            return lang(30194)
        return '%s - %s' % (lang(30194), self.search_type.capitalize())

    def get_image(self):
        return getImage('album')

    def make_url(self, **ka):
        if self.search_type is not None:
            ka['search-type'] = self.search_type
        query = self.get_parameter('query')
        if self.query is not None:
            ka['query'] = query
        return super(Node_collection, self).make_url(**ka)

    def fetch(self, Dir, lvl, whiteFlag, blackFlag):
        if self.search_type is None:
            return {}
        query = self.get_parameter('query', to='unquote')
        if not query:
            from qobuz.gui.util import Keyboard
            k = Keyboard('', 'My %s' % self.search_type)
            k.doModal()
            if not k.isConfirmed():
                return None
            query = k.getText().strip()
        if query == '':
            return None
        kwargs = {'query': converter.quote(query)}
        if self.source is not None:
            kwargs['source'] = self.source
        debug.info(self, 'SEARCH {}', kwargs)
        if self.search_type == 'albums':
            return api.get('/collection/getAlbums', **kwargs)
        elif self.search_type == 'artists':
            return api.get('/collection/getArtists', **kwargs)
        elif self.search_type == 'tracks':
            return api.get('/collection/getTracks', **kwargs)
        return None

    def get_description(self):
        return None

    def _populate_albums(self, data=None, parameters={}):
        return getNode(Flag.ALBUM, data=data, parameters=parameters)

    def _populate_tracks(self, data=None, parameters={}):
        return getNode(Flag.TRACK, data=data, parameters=parameters)

    def _populate_artists(self, data=None, parameters={}):
        return getNode(Flag.ARTIST, data=data, parameters=parameters)

    def populate(self, Dir, lvl, whiteFlag, blackFlag):
        if self.search_type is None:
            for search_type in ['albums', 'tracks', 'artists']:
                self.add_child(
                    getNode(
                        Flag.COLLECTION,
                        parameters={'search-type': search_type}))
            return True
        if self.data is None:
            return False
        method = getattr(self, '_populate_%s' % self.search_type)
        for item in self.data['items']:
            self.add_child(
                method(
                    data=item,
                    parameters={'query': self.get_parameter('query')}))
        return True
