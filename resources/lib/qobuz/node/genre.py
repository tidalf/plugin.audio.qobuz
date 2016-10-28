'''
    qobuz.node.genre
    ~~~~~~~~~~~~~~~~

    :part_of: xbmc-qobuz
    :copyright: (c) 2012-2016 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
from qobuz.node.inode import INode
from qobuz.gui.util import getImage, getSetting, lang
from qobuz.api import api
from qobuz.node import Flag, getNode
from qobuz.node.recommendation import RECOS_TYPE_IDS
from qobuz import debug

class Node_genre(INode):
    '''@class Node_genre:
    '''

    def __init__(self, parent=None, parameters={}, data=None):
        super(Node_genre, self).__init__(parent=parent,
                                         parameters=parameters,
                                         data=data)
        self.nt = Flag.GENRE
        self.image = getImage('album')

    def get_label(self):
        label = self.get_property('name', default=None)
        if label is not None:
            return label
        return lang(30189)

    def get_label2(self):
        return self.get_label()

    def populate_reco(self, xdir, lvl, whiteFlag, blackFlag, genre_id):
        for genre_type in RECOS_TYPE_IDS:
            node = getNode(Flag.RECOMMENDATION, {
                'genre-id': genre_id,
                'genre-type': genre_type
            })
            node.populating(xdir, 1, Flag.ALBUM, Flag.TRACK & Flag.STOPBUILD)
        return True

    def fetch(self, xdir, lvl, whiteFlag, blackFlag):
        if self.nid is None:
            return api.get('/genre/list', offset=self.offset, limit=self.limit)
        return api.get('/genre/list', parent_id=self.nid, offset=self.offset,
                       limit=self.limit)

    def populate(self, xdir, lvl, whiteFlag, blackFlag):
        if not self.data and len(self.data['genres']['items']) == 0:
            return self.populate_reco(xdir, lvl, whiteFlag, blackFlag, self.nid)
        if self.nid is not None and self.data and len(self.data['genres']['items']) == 0:
            for genre_type in RECOS_TYPE_IDS:
                node = getNode(Flag.RECOMMENDATION, {
                    'genre-id': self.nid,
                    'genre-type': genre_type
                })
                node.populating(xdir, 1, Flag.ALBUM, Flag.TRACK & Flag.STOPBUILD)
        else:
            for genre in self.data['genres']['items']:
                self.add_child(Node_genre(parameters={'nid': genre['id']},
                                          data=genre))
        return True
