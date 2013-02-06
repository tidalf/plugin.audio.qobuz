'''
    qobuz.node.genre
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    This file is part of qobuz-xbmc

    :copyright: (c) 2012 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
from inode import INode
from qobuz.api import api
from qobuz.node import Flag, getNode
from qobuz.node.recommendation import RECOS_TYPE_IDS
from qobuz.i8n import _

class Node_genre(INode):
    '''
    @class Node_genre:
    '''
    def __init__(self, parameters={}):
        super(Node_genre, self).__init__(parameters)
        self.kind = Flag.GENRE
        self.label = _('Genre')
        self.image = ''
        self.offset = self.get_parameter('offset') or 0

    def url(self, **ka):
        url = super(Node_genre, self).url(**ka)
        if self.parent and self.parent.nid:
            url += "&parent-id=" + self.parent.nid
        return url

    def get_name(self):
        return self.get_property('name')

    def populate_reco(self, directory, ID):
        for gtype in RECOS_TYPE_IDS:
            node = getNode(
                Flag.RECOMMENDATION, {'parent': self, 'genre-id': ID, 'genre-type': gtype})
            node.populating(directory, 1, Flag.ALBUM, Flag.NONE)
        return True

    def fetch(self, directory=None):
        data = api.get('/genre/list', parent_id=self.nid, offset=self.offset, 
                       limit=api.pagination_limit)
        if not data: 
            self.data = None
            return True # Nothing return trigger reco build in build_down
        self.data = data
        g = self.data['genres']
        if 'parent' in g and int(g['parent']['level']) > 1:
            self.populate_reco(directory, g['parent']['id'])
        return True

    def populate(self, directory=None, depth=None):
        if not self.data or len(self.data['genres']['items']) == 0:
            return self.populate_reco(directory, self.nid)
        for genre in self.data['genres']['items']:
            node = getNode(Flag.GENRE, self.parameters)
            node.data = genre
            self.append(node)
        return True
