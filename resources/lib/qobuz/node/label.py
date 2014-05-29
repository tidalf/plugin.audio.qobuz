'''
    qobuz.node.label
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    This file is part of qobuz-xbmc

    :copyright: (c) 2012 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
from inode import INode
from qobuz.debug import warn
from qobuz.node import Flag
from qobuz.api import api
from qobuz.i8n import _


class Node_label(INode):
    '''
    @class Node_label:
    '''
    def __init__(self, parameters={}):
        super(Node_label, self).__init__(parameters)
        self.kind = Flag.LABEL
        self.label = _('Label')

    def populate(self, xbmc_directory, lvl, whiteFlag, blackFlag):
        """
        @bug: Qobuz service seam do don't return total so pagination is broken
        """
        data = api.get('/label/list', limit=api.pagination_limit,
                       offset=self.offset)
        if not data:
            warn(self, "No label data")
            return False
        for item in data['labels']['items']:
            node = Node_label()
            node.data = item
            self.append(node)
        return True
