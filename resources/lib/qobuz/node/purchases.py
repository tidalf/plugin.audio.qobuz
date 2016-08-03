'''
    qobuz.node.purchases
    ~~~~~~~~~~~~~~~~~~~~

    :part_of: xbmc-qobuz
    :copyright: (c) 2012 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
from qobuz.node.inode import INode
from qobuz.gui.util import lang, getImage
from qobuz.node import getNode, Flag


class Node_purchases(INode):
    '''Our root node, we are displaying all qobuz nodes from here
    '''

    def __init__(self, parent=None, parameters={}, data=None):
        super(Node_purchases, self).__init__(parent=parent,
                                             parameters=parameters,
                                             data=data)
        self.nt = Flag.PURCHASES
        self.label = lang(30101)
        self.content_type = 'files'
        self.image = getImage('album')

    def populate(self, Dir, lvl, whiteFlag, blackFlag):
        for kind in ['all', 'albums', 'tracks']:
            self.add_child(getNode(Flag.PURCHASE, {'search-type': kind}))
        return True
