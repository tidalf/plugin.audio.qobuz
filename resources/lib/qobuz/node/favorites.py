'''
    qobuz.node.favoritess
    ~~~~~~~~~~~~~~~~~~~~

    :part_of: xbmc-qobuz
    :copyright: (c) 2012-2016 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
from qobuz.node.inode import INode
from qobuz.gui.util import lang, getImage
from qobuz.node import getNode, Flag


class Node_favorites(INode):

    def __init__(self, parent=None, parameters={}, data=None):
        super(Node_favorites, self).__init__(parent=parent,
                                             parameters=parameters,
                                             data=data)
        self.nt = Flag.FAVORITES
        self.label = lang(30081)
        self.image = getImage('album')
        self.content_type = 'albums'

    def populate(self, Dir, lvl, whiteFlag, blackFlag):
        for kind in ['all', 'albums', 'tracks', 'artists']:
            self.add_child(getNode(Flag.FAVORITE, parameters={'search-type': kind}))
        return True
