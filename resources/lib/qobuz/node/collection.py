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
        self.set_label('Collection')
        self.url = None
        self.is_folder = True
        self.image = getImage('songs')
        self.search_type = self.get_parameter('search-type') or 'albums'
        self.query = self.get_parameter('query', unQuote=True)
        self.offset = self.get_parameter('offset') or 0

    def fetch(self, Dir, lvl, whiteFlag, blackFlag):
        limit = getSetting('pagination_limit', isInt=True)
        data = None
        query = self.get_parameter('query', unQuote=True)
        query = 'e'
        if not query:
            from gui.util import Keyboard
            k = Keyboard('', 'My %s' % self.search_type)
            k.doModal()
            if not k.isConfirmed():
                return False
            query = k.getText()
        query.strip()
        info(self, 'search_type: %s, query: %s' % (self.search_type, query))
        if self.search_type == 'albums':
            data = api.get('/collection/getAlbums', limit=limit)
        elif self.search_type == 'artists':
            data = api.get('/collection/getArtists', query=query, limit=limit)
        elif self.search_type == 'tracks':
            data = api.get('/collection/getTracks', query=query, limit=limit)
        self.data = data
        return True

    def populate(self, Dir, lvl, whiteFlag, blackFlag):
        import pprint
        info(self, 'RESULT: %s' % pprint.pformat(self.data))
        print pprint.pformat(self.data)
#         if self.collection_type == 'albums':
#             node = getNode(Flag.ALBUMS)
#             node.data = self.data['album']
#             self.add_child(node)
        return True
