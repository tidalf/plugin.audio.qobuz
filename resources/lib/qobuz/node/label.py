'''
    qobuz.node.label
    ~~~~~~~~~~~~~~~~

    :part_of: xbmc-qobuz
    :copyright: (c) 2012-2016 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
from qobuz.node.inode import INode
from qobuz import debug
from qobuz.gui.util import getImage, getSetting, lang
from qobuz.node import Flag
from qobuz.api import api


class Node_label(INode):
    '''
    @class Node_label:
    '''

    def __init__(self, parent=None, parameters={}, data=None):
        super(Node_label, self).__init__(parent=parent,
                                         parameters=parameters,
                                         data=data)
        self.nt = Flag.LABEL
        self.set_label(lang(30188))
        self.url = None
        self.is_folder = True
        self.image = getImage('album')

    def fetch(self, *a, **ka):
        if self.nid is None:
            return api.get('/label/list', limit=self.limit, offset=self.offset)
        return api.get('/label/get', label_id=self.nid)

    def populate(self, xbmc_directory, lvl, whiteFlag, blackFlag):
        debug.info(self, 'DATA {}', self.data)
        if self.nid is None:
            for item in self.data['labels']['items']:
                node = Node_label()
                node.data = item
                self.add_child(node)
        else:
            debug.info(self, 'Click on label: {}', self.get_property('name'))
        return True
