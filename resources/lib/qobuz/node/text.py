'''
    qobuz.node.collections
    ~~~~~~~~~~~~~~~~~~~~

    :part_of: xbmc-qobuz
    :copyright: (c) 2012 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
from qobuz.node.inode import INode
from qobuz.gui.util import lang, getImage
from qobuz.node import getNode, Flag


class Node_text(INode):

    def __init__(self, parent=None, parameters={}, data=None):
        super(Node_text, self).__init__(parent=parent,
                                               parameters=parameters,
                                               data=data)
        self.nt = Flag.TEXT
        self.label = self.get_parameter('label')
        self.is_folder = False
        self.content_type = 'files'
        #self.content_type = 'files'
        #self.image = getImage('album')

    #def populate(self, Dir, lvl, whiteFlag, blackFlag):
        # for kind in ['artists', 'albums', 'tracks']:
        #     self.add_child(getNode(Flag.COLLECTION, {'search-type': kind}))
        # return True
