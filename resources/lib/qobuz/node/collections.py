'''
    qobuz.node.collection
    ~~~~~~~~~~~~~~~~~~~~~

    :part_of: xbmc-qobuz
    :copyright: (c) 2012 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
from inode import INode
from node import getNode, Flag
from gui.util import getImage

dialogHeading = 'Qobuz collections'


class Node_collections(INode):
    '''
    @class Node_collections:
    '''

    def __init__(self, parent=None, parameters=None):
        super(Node_collections, self).__init__(parent, parameters)
        self.nt = Flag.COLLECTIONS
        self.set_label('Collections')
        self.url = None
        self.is_folder = True
        self.image = getImage('songs')

    def fetch(self, Dir, lvl, whiteFlag, blackFlag):
        return True

    def populate(self, Dir, lvl, whiteFlag, blackFlag):
        for kind in ['artists', 'albums', 'tracks']:
            node = getNode(Flag.COLLECTION, params={'search-type': kind},)
            node.set_parameter('search-type', kind)
            node.set_label('%s collection' % kind.capitalize())
            self.add_child(node)
        return True
