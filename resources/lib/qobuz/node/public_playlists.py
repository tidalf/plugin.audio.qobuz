'''
    qobuz.node.public_playlists
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :part_of: xbmc-qobuz
    :copyright: (c) 2012-2016 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
from qobuz.node import Flag, getNode
from qobuz.node.inode import INode
from qobuz.gui.util import lang, getImage
from qobuz.api import api
from qobuz import debug

featured_type = ['editor-picks', 'last-created']
limit_max = 100

class Node_public_playlists(INode):

    def __init__(self, parent=None, parameters={}, data=None):
        super(Node_public_playlists, self).__init__(parent=parent,
                                                    parameters=parameters,
                                                    data=data)
        self.nt = Flag.PUBLIC_PLAYLISTS
        self.image = getImage('userplaylists')
        self.content_type = 'albums'
        self.type = self.get_parameter('type', default='last-created')
        if self.type not in featured_type:
            raise RuntimeError('InvalidFeaturedType: {}'.format(self.type))
        self.label = '%s (%s)' % (lang(30190), self.type)

    def fetch(self, *a, **ka):
        limit = self.limit if self.limit < limit_max else limit_max
        return api.get('/playlist/getFeatured',
                       offset=self.offset,
                       limit=limit,
                       type=self.type)

    def populate(self, *a, **ka):
        for item in self.data['playlists']['items']:
            self.add_child(getNode(Flag.PLAYLIST, data=item))
        return True if len(self.data['playlists']['items']) > 0 else False
