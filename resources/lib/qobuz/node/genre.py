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
from node.renderer.list import ListRenderer
from qobuz.debug import log, warn


class Node_genre(INode):
    '''
    @class Node_genre:
    '''
    def __init__(self, parameters={}):
        super(Node_genre, self).__init__(parameters)
        self.kind = Flag.GENRE
        self.label = _('Genre')

    @property
    def label(self):
        return self._label

    @label.getter
    def label(self):
        name = self.get_name()
        return name or self._label

    @label.setter
    def label(self, label):
        self._label = label

    def url(self, **ka):
        url = super(Node_genre, self).url(**ka)
        if self.parent and self.parent.nid:
            url += "&parent-id=" + self.parent.nid
        return url

    def get_name(self):
        return self.get_property('name')

    def populate_reco(self, renderer, gid):
        album_ids = {}
        log(self, "Populate reco %s" % gid)
        for gtype in RECOS_TYPE_IDS:
            lr = ListRenderer()
            lr.depth = -1
            lr.whiteFlag = Flag.ALBUM | Flag.TRACK
            lr.blackFlag = Flag.TRACK | Flag.ALBUM
            node = getNode(
                Flag.RECOMMENDATION, {'genre-id': gid, 'genre-type': gtype})
            node.populating(lr)
            for album in lr:
                aid = album.nid
                if aid in album_ids:
                    continue
                album_ids[aid] = 1
                renderer.append(album)
            #renderer.extend([track for track in lr])
        return True

    def fetch(self, renderer=None):
        data = api.get('/genre/list', parent_id=self.nid, offset=self.offset,
                       limit=api.pagination_limit)
        if data is None:
            """Nothing return trigger reco build in build_down"""
            return True
        self.data = data
        g = self.data['genres']
        lvl = 0
        try:
            lvl = int(g['parent']['level'])
        except Exception as e:
            warn(self, "Exception: %s" % e)
        print "Level: %s" % lvl
        if 'parent' in g and lvl > 1:
            self.populate_reco(renderer, int(g['parent']['id']))
        return True

    def populate(self, renderer):
        if not self.data or len(self.data['genres']['items']) == 0:
            return self.populate_reco(renderer, self.nid)
        for genre in self.data['genres']['items']:
            node = getNode(Flag.GENRE, self.parameters)
            node.data = genre
            self.append(node)
        return True
