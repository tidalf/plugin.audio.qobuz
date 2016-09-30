'''
    qobuz.node.public_playlists
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :part_of: xbmc-qobuz
    :copyright: (c) 2012 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
from qobuz.node import Flag, getNode
from qobuz.node.inode import INode
from qobuz.gui.util import lang, getImage, getSetting
from qobuz.api import api
from qobuz import debug

class Node_public_playlists(INode):
    '''@class Node_public_playlists
    '''

    def __init__(self, parent=None, parameters={}, data=None):
        super(Node_public_playlists, self).__init__(parent=parent,
                                                    parameters=parameters,
                                                    data=data)
        self.nt = Flag.PUBLIC_PLAYLISTS
        self.set_label(lang(30190))
        self.image = getImage('userplaylists')

    def fetch(self, Dir, lvl, whiteFlag, blackFlag):
        debug.info(self, 'FETCH offset: {}, limit: {}', self.offset, self.limit)
        data = api.get('/playlist/getPublicPlaylists', offset=self.offset,
                       limit=self.limit, type='last-created')
        if data is None:
            return False
        # import pprint
        # debug.info(self, 'PUBLIC PL DATA {}', pprint.pformat(data))
        self.data = data
        return True

    def populate(self, Dir, lvl, whiteFlag, blackFlag):
        for item in self.data['playlists']['items']:
            node = getNode(Flag.PLAYLIST, data=item)
            self.add_child(node)
        return True
