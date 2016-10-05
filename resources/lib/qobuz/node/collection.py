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
from qobuz.gui.util import getImage, getSetting, lang


dialogHeading = 'Collection'


class Node_collection(INode):
    '''@class Node_collection:
    '''

    def __init__(self, parent=None, parameters={}, data=None):
        super(Node_collection, self).__init__(parent=parent,
                                              parameters=parameters,
                                              data=data)
        self.nt = Flag.COLLECTION
        self.url = None
        self.is_folder = True
        self.image = getImage('songs')
        self.search_type = self.get_parameter('search-type', default='tracks')
        self.query = self.get_parameter('query', unQuote=True)
        self.source = self.get_parameter('source')
        self.seen_artist = {}
        self.seen_album = {}
        self.seen_track = {}
        self.label = '%s - %s' % (lang(30194),  self.search_type.capitalize())

    def make_url(self, **ka):
        if self.search_type is not None:
            ka['search-type'] = self.search_type
        query = self.get_parameter('query')
        if self.query is not None:
            ka['query'] = query
        return super(Node_collection, self).make_url(**ka)


    def fetch(self, Dir, lvl, whiteFlag, blackFlag):
        query = self.get_parameter('query', unQuote=True)
        if not query:
            from qobuz.gui.util import Keyboard
            k = Keyboard('', 'My %s' % self.search_type)
            k.doModal()
            if not k.isConfirmed():
                return None
            query = k.getText().strip()
        source = self.source
        kwargs = {
            'query': query,
            'limit': self.limit,
        }
        if source is not None:
            kwargs['source'] = source
        if self.search_type == 'albums':
            return api.get('/collection/getAlbums', **kwargs)
        elif self.search_type == 'artists':
            return api.get('/collection/getArtists', **kwargs)
        elif self.search_type == 'tracks':
            return api.get('/collection/getTracks', **kwargs)
        return None

    def get_description(self):
        return None

    def _populate_albums(self, data):
        return getNode(Flag.ALBUM, data=data)

    def _populate_tracks(self, data):
        return getNode(Flag.TRACK, data=data)

    def _populate_artists(self, data):
        return getNode(Flag.ARTIST, data=data)

    def populate(self, Dir, lvl, whiteFlag, blackFlag):
        if self.data is None:
            return False
        method = getattr(self, '_populate_%s' % self.search_type)
        for item in self.data['items']:
            node = method(item)
            node.set_parameter('query', self.get_parameter('query'))
            self.add_child(node)
        return True
