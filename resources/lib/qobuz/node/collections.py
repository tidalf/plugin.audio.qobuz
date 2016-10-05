'''
    qobuz.node.collections
    ~~~~~~~~~~~~~~~~~~~~

    :part_of: xbmc-qobuz
    :copyright: (c) 2012-2016 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
from qobuz.node.inode import INode
from qobuz.gui.util import lang, getImage
from qobuz.node import getNode, Flag


class Node_collections(INode):

    def __init__(self, parent=None, parameters={}, data=None):
        super(Node_collections, self).__init__(parent=parent,
                                               parameters=parameters,
                                               data=data)
        self.nt = Flag.COLLECTIONS
        self.label = lang(30194)
        self.content_type = 'albums'
        self.image = getImage('album')

    def populate(self, Dir, lvl, whiteFlag, blackFlag):
        for kind in ['artists', 'albums', 'tracks']:
            self.add_child(getNode(Flag.COLLECTION, {'search-type': kind}))
        return True
