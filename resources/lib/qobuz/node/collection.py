'''
    qobuz.node.collection
    ~~~~~~~~~~~~~~~~~~~~~

    :part_of: xbmc-qobuz
    :copyright: (c) 2012 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
import xbmcgui  # @UnresolvedImport
import qobuz  # @UnresolvedImport

from inode import INode
from node import getNode, Flag
from api import api
from cache import cache
from track import Node_track
from debug import warn, info
from renderer import renderer
from gui.util import notifyH, color, lang, getImage, runPlugin, \
    containerRefresh, containerUpdate, executeBuiltin, getSetting
from gui.contextmenu import contextMenu
from constants import Mode

dialogHeading = 'Qobuz collection'


class Node_collection(INode):
    '''
    @class Node_collection:
    '''

    def __init__(self, parent=None, parameters=None):
        super(Node_collection, self).__init__(parent, parameters)
        self.nt = Flag.COLLECTION
#         self.set_label('Collection')
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
        if not source:
            source = 'all'
#         source = 'favorited'
        data = None
        self.data = data
        if self.search_type == 'albums':
            data = api.get('/collection/getAlbums', query=query,
                           limit=limit, source=source)
        elif self.search_type == 'artists':
            data = api.get('/collection/getArtists', query=query,
                           limit=limit, source=source)
        elif self.search_type == 'tracks':
            data = api.get('/collection/getTracks', query=query,
                           limit=limit, source=source)
        try:
            self.data = data['items']
            return True
        except Exception as e:
            warn(self, 'Exception: %s' % e)
        return False

    def populate(self, Dir, lvl, whiteFlag, blackFlag):
        import pprint
        info(self, 'RESULT: %s' % pprint.pformat(self.data))
        print pprint.pformat(self.data)
        if self.data is None:
            return False
        for item in self.data:
            print "Item: %s" % item
            node = None
            if self.search_type == 'artists':
                node = getNode(Flag.ARTIST)
                node.data = item['artist']
#                 if node.nid in self.seen_artist:
#                     node = None
#                 else:
#                     self.seen_artist[node.nid] = True
            elif self.search_type == 'albums':
                node = getNode(Flag.ALBUM)
                node.data = item['album']
#                 if node.nid in self.seen_album:
#                     node = None
#                 else:
#                     self.seen_album[node.nid] = True
            elif self.search_type == 'tracks':
                node = getNode(Flag.TRACK)
                node.data = item['tracks']
#                 if node.nid in self.seen_track:
#                     node = None
#                 else:
#                     self.seen_track[node.nid] = True
            if node is None:
                continue
#             node.set_parameter('search-type', self.search_type)
#             node.set_parameter('query', self.query)
            self.add_child(node)
        return True
