'''
    qobuz.node.genre
    ~~~~~~~~~~~~~~~~

    :part_of: kodi-qobuz
    :copyright: (c) 2012-2016 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
from qobuz.api import api
from qobuz.gui.util import getImage, lang
from qobuz.node import Flag, getNode, helper
from qobuz.node.inode import INode
from qobuz.node.recommendation import RECOS_TYPE_IDS


class Node_genre(INode):
    def __init__(self, parent=None, parameters=None, data=None):
        parameters = {} if parameters is None else parameters
        super(Node_genre, self).__init__(
            parent=parent, parameters=parameters, data=data)
        self.nt = Flag.GENRE
        self.image = getImage('album')
        self.content_type = 'albums'

    def get_label(self, default=None):
        label = self.get_property('name', default=None)
        if label is not None:
            return label
        return lang(30189)

    def get_label2(self):
        return self.get_label()

    @classmethod
    def populate_reco(cls, options, genre_id):
        for genre_type in RECOS_TYPE_IDS:
            node = getNode(Flag.RECOMMENDATION,
                           {'genre-id': genre_id,
                            'genre-type': genre_type})
            node.populating(options.xdir, 1, Flag.ALBUM,
                            Flag.TRACK & Flag.STOPBUILD)
        return True

    def fetch(self, options=None):
        if self.nid is None:
            return api.get('/genre/list', offset=self.offset, limit=self.limit)
        return api.get('/genre/list',
                       parent_id=self.nid,
                       offset=self.offset,
                       limit=self.limit)

    def populate(self, options=None):
        options = options if options is None else helper.TreeTraverseOpts()
        if not self.data and len(self.data['genres']['items']) == 0:
            return self.populate_reco(options, self.nid)
        if self.nid is not None and self.data and len(self.data['genres'][
                'items']) == 0:
            for genre_type in RECOS_TYPE_IDS:
                node = getNode(Flag.RECOMMENDATION, {
                    'genre-id': self.nid,
                    'genre-type': genre_type
                })
                node.populating(helper.TraverseTreeOpts(
                    xdir=options.xdir,
                    lvl=1,
                    whiteFlag=Flag.ALBUM,
                    blackFlag=Flag.TRACK & Flag.STOPBUILD))
        else:
            for genre in self.data['genres']['items']:
                self.add_child(
                    Node_genre(
                        parameters={'nid': genre['id']}, data=genre))
        return True
