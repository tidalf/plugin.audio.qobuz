'''
    qobuz.node.collection
    ~~~~~~~~~~~~~~~~~~~~~

    :part_of: xbmc-qobuz
    :copyright: (c) 2012 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
from inode import INode
from node import Flag
from api import api
from debug import info
from gui.util import getImage, getSetting


dialogHeading = 'Qobuz collection'


class Node_collection(INode):
    '''
    @class Node_collection:
    '''

    def __init__(self, parent=None, parameters=None):
        super(Node_collection, self).__init__(parent, parameters)
        self.nt = Flag.COLLECTION
        self.url = None
        self.is_folder = True
        self.image = getImage('songs')
        self.search_type = self.get_parameter('search-type')
        if self.search_type is None:
            self.search_type = 'artists'
        self.query = self.get_parameter('query', unQuote=True)
        self.offset = self.get_parameter('offset') or 0
        self.source = self.get_parameter('source')
        self.seen_artist = {}
        self.seen_album = {}
        self.seen_track = {}
        self.data = None

    def make_url(self, **ka):
        url = super(Node_collection, self).make_url(**ka)
        if self.search_type:
            url += '&search-type=' + str(self.search_type)
        return url

    def fetch(self, Dir, lvl, whiteFlag, blackFlag):
        limit = getSetting('pagination_limit', isInt=True)
        self.data = None
        query = self.query
        if not query:
            from gui.util import Keyboard
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
        self.data = data
        if self.search_type == 'albums':
            data = api.get('/collection/getAlbums', **kwargs)
        elif self.search_type == 'artists':
            data = api.get('/collection/getArtists', **kwargs)
        elif self.search_type == 'tracks':
            data = api.get('/collection/getTracks', **kwargs)
#         try:
#             self.data = data['items']
#             return True
#         except Exception as e:
#             warn(self, 'Exception: %s' % e)
        self.data = data
        return False

    def populate(self, Dir, lvl, whiteFlag, blackFlag):
        import pprint
        if self.data is None:
            return False
        for item in self.data:
            print "Item: %s" % item
#             node = None
#             if self.search_type == 'artists':
#                 for subdata in self.data[]
#                 node = getNode(Flag.ARTIST)
#                 node.data = item['artist']
# #                 if node.nid in self.seen_artist:
# #                     node = None
# #                 else:
# #                     self.seen_artist[node.nid] = True
#             elif self.search_type == 'albums':
#                 node = getNode(Flag.ALBUM)
#                 node.data = item['album']
# #                 if node.nid in self.seen_album:
# #                     node = None
# #                 else:
# #                     self.seen_album[node.nid] = True
#             elif self.search_type == 'tracks':
#                 node = getNode(Flag.TRACK)
#                 node.data = item['track']
# #                 if node.nid in self.seen_track:
# #                     node = None
# #                 else:
# #                     self.seen_track[node.nid] = True
#             if node is None:
#                 continue
# #             node.set_parameter('search-type', self.search_type)
# #             node.set_parameter('query', self.query)
#             self.add_child(node)
        return True
