'''
    qobuz.node.collection
    ~~~~~~~~~~~~~~~~~~~~~

    :part_of: xbmc-qobuz
    :copyright: (c) 2012 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
from qobuz.node.inode import INode
from qobuz.node import Flag, getNode
from qobuz.api import api
from qobuz.debug import info
from qobuz.gui.util import getImage, getSetting, lang


dialogHeading = 'Qobuz collection'


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
        return super(Node_collection, self).make_url(**ka)


    def fetch(self, Dir, lvl, whiteFlag, blackFlag):
        limit = getSetting('pagination_limit', asInt=True)
        self.data = None
        query = self.query
        if not query:
            from qobuz.gui.util import Keyboard
            k = Keyboard('', 'My %s' % self.search_type)
            k.doModal()
            if not k.isConfirmed():
                return False
            query = k.getText()
        query.strip()
        info(self, 'search_type: %s, query: %s' % (self.search_type, query))
        source = self.source
        kwargs = {'query': query,
                  'limit': limit,
                  }
        if source is not None:
            kwargs['source'] = source
        data = None
        if self.search_type == 'albums':
            data = api.get('/collection/getAlbums', **kwargs)
        elif self.search_type == 'artists':
            data = api.get('/collection/getArtists', **kwargs)
        elif self.search_type == 'tracks':
            data = api.get('/collection/getTracks', **kwargs)
        if data is None:
            return False
        self.data = data
        return True

    def get_description(self):
        return None

    def _populate_albums(self, data):
        '''helper'''
        node = getNode(Flag.ALBUM, data=data)
        self.add_child(node)
        return True

    def _populate_tracks(self, data):
        '''helper'''
        node = getNode(Flag.TRACK, data=data)
        self.add_child(node)
        return True

    def _populate_artists(self, data):
        '''helper'''
        node = getNode(Flag.ARTIST, data=data)
        self.add_child(node)
        return True

    def populate(self, Dir, lvl, whiteFlag, blackFlag):
        if self.data is None:
            return False
        method = getattr(self, '_populate_%s' % self.search_type)
        for item in self.data['items']:
            method(item)
        return True
