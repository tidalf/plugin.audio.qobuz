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
from qobuz.gui.util import lang, getImage, getSetting
from qobuz.api import api
from qobuz.node import getNode, Flag

data_search_type = {
    'artists': {
        'label': lang(30017),
        'content_type' : 'files',
        'image' : getImage('artist'),
    },
    'albums': {
        'label' : lang(30016),
        'content_type' : 'albums',
        'image' : getImage('album'),
    },
    'tracks': {
        'label' : lang(30015),
        'content_type' : 'songs',
        'image' : getImage('song'),
    },
    'collection': {
        'label' : lang(30018),
        'content_type' : 'files',
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

    def get_description(self):
        return self.get_label()

    def set_search_type(self, search_type):
        search_type = self.get_parameter('search-type')
        if search_type is None:
            self.set_parameter('search-type', 'albums')
            search_type = self.get_parameter('search-type')
        if search_type in data_search_type:
            self.label = data_search_type[search_type]['label']
            self.content_type = data_search_type[search_type]['content_type']
            self.image = data_search_type[search_type]['image']
        else:
            raise exception.InvalidSearchType(search_type)

    def fetch(self, Dir, lvl, whiteFlag, blackFlag):
        query = self.get_parameter('query', unQuote=True)
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


    def _populate_albums(self, Dir, lvl, whiteFlag, blackFlag):
        for album in self.data['albums']['items']:
            node = getNode(Flag.ALBUM, data=album)
            self.add_child(node)
        return True

    def _populate_tracks(self, Dir, lvl, whiteFlag, blackFlag):
        for track in self.data['tracks']['items']:
            node = getNode(Flag.TRACK, data=track)
            self.add_child(node)
        return True

    def _populate_artists(self, Dir, lvl, whiteFlag, blackFlag):
        for artist in self.data['artists']['items']:
            node = getNode(Flag.ARTIST, data=artist)
            self.add_child(node)
        return True

    def populate(self, Dir, lvl, whiteFlag, blackFlag):
        return getattr(self, '_populate_%s' % self.get_parameter('search-type'))(Dir, lvl, whiteFlag, blackFlag)
