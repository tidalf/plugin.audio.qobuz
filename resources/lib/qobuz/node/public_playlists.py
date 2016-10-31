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

class Node_public_playlists(INode):

    def __init__(self, parent=None, parameters={}, data=None):
        super(Node_public_playlists, self).__init__(parent=parent,
                                                    parameters=parameters,
                                                    data=data)
        self.nt = Flag.PUBLIC_PLAYLISTS
        self.set_label(lang(30190))
        self.image = getImage('userplaylists')
        self.content_type = 'albums'

    def fetch(self, Dir, lvl, whiteFlag, blackFlag):
        return api.get('/playlist/getPublicPlaylists',
                       offset=self.offset,
                       limit=self.limit,
                       type='last-created')

    def populate(self, Dir, lvl, whiteFlag, blackFlag):
        for item in self.data['playlists']['items']:
            self.add_child(getNode(Flag.PLAYLIST, data=item))
        return True if len(self.data['playlists']['items']) > 0 else False
