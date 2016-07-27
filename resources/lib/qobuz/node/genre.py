'''
    qobuz.node.genre
    ~~~~~~~~~~~~~~~~

    :part_of: xbmc-qobuz
    :copyright: (c) 2012 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
from qobuz.node.inode import INode
from qobuz.gui.util import getImage, getSetting, lang
from qobuz.api import api
from qobuz.node import Flag, getNode
from qobuz.node.recommendation import RECOS_TYPE_IDS
from qobuz.debug import log

class Node_genre(INode):
    '''@class Node_genre:
    '''

    def __init__(self, parent=None, parameters=None):
        super(Node_genre, self).__init__(parent, parameters)
        self.nt = Flag.GENRE
        self.set_label(lang(30189))
        self.is_folder = True
        self.image = getImage('album')
        self.offset = self.get_parameter('offset') or 0

    def make_url(self, **ka):
        if self.parent is not None and self.parent.nid is not None:
            ka['parent-id'] = self.parent.nid
        return super(Node_genre, self).make_url(**ka)

    def hook_post_data(self):
        self.label = self.get_property('name')

    def get_name(self):
        return self.get_property('name')

    def populate_reco(self, Dir, lvl, whiteFlag, blackFlag, genre_id):
        for genre_type in RECOS_TYPE_IDS:
            node = getNode(Flag.RECOMMENDATION, {
                'parent': self,
                'genre-id': genre_id,
                'genre-type': genre_type
            })
            node.populating(Dir, 1, Flag.ALBUM, blackFlag)
        return True

    def fetch(self, Dir, lvl, whiteFlag, blackFlag):
        limit = getSetting('pagination_limit')
        data = api.get('/genre/list', parent_id=self.nid, offset=self.offset,
                       limit=limit)
        if not data:
            self.data = None
            return True  # Nothing returned trigger reco build in build_down
        self.data = data
        genres = self.data['genres']
        if 'parent' in genres and int(genres['parent']['level']) > 1:
            self.populate_reco(Dir, lvl, whiteFlag, blackFlag,
                               genres['parent']['id'])
        return True

    def populate(self, Dir, lvl, whiteFlag, blackFlag):
        if not self.data or len(self.data['genres']['items']) == 0:
            return self.populate_reco(Dir, lvl, whiteFlag, blackFlag, self.nid)
        for genre in self.data['genres']['items']:
            node = Node_genre(self, {'nid': genre['id']})
            node.data = genre
            self.add_child(node)
        return True
