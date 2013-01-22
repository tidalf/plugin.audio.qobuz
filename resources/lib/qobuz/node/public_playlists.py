'''
    qobuz.node.public_playlists
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2012 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
from node import Flag, getNode
from inode import INode
from debug import warn, error
from gui.util import lang, getImage, getSetting
from api import api

class Node_public_playlists(INode):
    '''
    @class Node_genre:
    '''
    def __init__(self, parent=None, parameters=None):
        super(Node_public_playlists, self).__init__(parent, parameters)
        self.nt = Flag.PUB
        self.set_label(lang(42102))
        self.url = None
        self.is_folder = True
        self.image = getImage('userplaylists')

    def hook_post_data(self):
        self.label = self.get_property('name')
        self.nid = self.get_property('nid')

    def populate(self, xbmc_directory, lvl, whiteFlag, blackFlag):
        offset = self.get_parameter('offset') or 0
        # we use pagination_limit as limit for the search so we don't need offset... FIXME
        limit = getSetting('pagination_limit')
        data = api.get('/playlist/getPublicPlaylists', limit=limit, type='last-created') # ,offset=offset
        if not data:
            warn(self, "No pubs")
            return False
        for item in data['playlists']['items']:
            node = getNode(Flag.PLAYLIST)
            node.data = item
            self.add_child(node)
        return True

