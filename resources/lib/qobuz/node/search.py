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
        'content_type' : 'artists',
        'image' : getImage('artist'),
    },
    'albums': {
        'label' : lang(30016),
        'content_type' : 'albums',
        'image' : getImage('album'),
    },
    'tracks': {
        'label' : lang(30015),
        'content_type' : 'albums',
        'image' : getImage('song'),
    },
    'collection': {
        'label' : lang(30018),
        'content_type' : 'albums',
        'image' : getImage('song')
    }
}

class Node_search(INode):

    def __init__(self, parent=None, parameters={}, data=None):
        super(Node_search, self).__init__(parent=parent,
                                          parameters=parameters,
                                          data=data)
        self.nt = Flag.SEARCH
        self.set_search_type(self.get_parameter('search-type'))
        self.content_type = 'albums'

    def get_description(self):
        return self.get_label()

    def get_label(self):
        query = self.get_parameter('query', to='unquote')
        if query is not None:
            return 'search %s: %s' % (self.get_parameter('search-type'),
                                      self.get_parameter('query'))
        return super(Node_search, self).get_label()

    def set_search_type(self, search_type):
        if search_type is None:
            self.set_parameter('search-type', 'albums')
            search_type = self.get_parameter('search-type')
        if search_type in data_search_type:
            self.label = data_search_type[search_type]['label']
            self.content_type = data_search_type[search_type]['content_type']
            self.image = data_search_type[search_type]['image']
        else:
            raise exception.InvalidSearchType(search_type)

    # def makeListItem(self, **ka):
    #     #query = self.get_parameter('query', to='unquote')
    #     #if query is not None:
    #     #    ka['query'] = query
    #     item = super(Node_search, self).makeListItem(**ka)
    #     return item

    def fetch(self, Dir, lvl, whiteFlag, blackFlag):
        query = self.get_parameter('query', to='unquote')
        if query is None:
            from qobuz.gui.util import Keyboard
            k = Keyboard('', self.get_parameter('search-type'))
            k.doModal()
            if not k.isConfirmed():
                return None
            query = k.getText().strip()
            if query is None or query == '':
                return None
        self.set_parameter('query', query, quote=True)
        return api.get('/search/getResults',
                       query=query,
                       type=self.get_parameter('search-type'),
                       limit=self.limit,
                       offset=self.offset)


    def _get_parameters(self):
        return {
            'query': self.get_parameter('query'),
            'search-type': self.get_parameter('search-type')
        }

    def _populate_albums(self, Dir, lvl, whiteFlag, blackFlag):
        for album in self.data['albums']['items']:
            self.add_child(getNode(Flag.ALBUM,
                                   parameters=self._get_parameters(),
                                   data=album))
        return True if len(self.data['albums']['items']) > 0 else False

    def _populate_tracks(self, Dir, lvl, whiteFlag, blackFlag):
        for track in self.data['tracks']['items']:
            self.add_child(getNode(Flag.TRACK,
                                   parameters=self._get_parameters(),
                                   data=track))
        return True if len(self.data['tracks']['items']) > 0 else False

    def _populate_artists(self, Dir, lvl, whiteFlag, blackFlag):
        for artist in self.data['artists']['items']:
            self.add_child(getNode(Flag.ARTIST,
                                   parameters=self._get_parameters(),
                                   data=artist))
        return True if len(self.data['artists']['items']) > 0 else False

    def populate(self, Dir, lvl, whiteFlag, blackFlag):
        return getattr(self, '_populate_%s' % self.get_parameter('search-type'))(Dir, lvl, whiteFlag, blackFlag)
