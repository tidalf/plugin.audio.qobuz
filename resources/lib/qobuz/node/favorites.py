'''
    qobuz.node.favorites
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    This file is part of qobuz-xbmc

    :copyright: (c) 2012 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''

from inode import INode
from qobuz.node import getNode, Flag
from qobuz.settings import settings
from qobuz.i8n import _

class Node_favorites(INode):

    def __init__(self, parameters={}):
        super(Node_favorites, self).__init__(parameters)
        self.kind = Flag.FAVORITES
        self.label = _('Favorites')
        self.content_type = 'files'

    def populate(self, renderer=None):
        for favorite in ['albums', 'tracks', 'artists']:
            parameters = self.parameters.copy()
            parameters['items_path'] = favorite
            node = getNode(Flag.FAVORITE, parameters)
            self.append(node)
        return True
