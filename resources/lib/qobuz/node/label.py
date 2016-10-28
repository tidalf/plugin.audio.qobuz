'''
    qobuz.node.label
    ~~~~~~~~~~~~~~~~

    :part_of: xbmc-qobuz
    :copyright: (c) 2012-2016 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
from qobuz.node.inode import INode, getNode
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
        self.image = getImage('album')
        self.content_type = 'albums'

    def get_label(self):
        if self.nid is None:
            return lang(30188)
        return self.get_property('name')

    def get_label2(self, default=None):
        if self.nid is None:
            return default
        return self.get_property('albums_count')

    def get_image(self):
        if self.nid is None:
            return getImage('album')
        return self.get_property('image')

    def makeListItem(self, **ka):
        item = super(Node_label, self).makeListItem(**ka)
        if self.nid is not None:
            item.setIconImage(self.get_image())
            item.setThumbnailImage(self.get_image())
            item.setProperty('description', self.get_property('description'))
        return item

    def fetch(self, *a, **ka):
        if self.nid is None:
            return api.get('/label/list', limit=self.limit, offset=self.offset)
        return api.get('/label/get', label_id=self.nid)

    def populate(self, xdir, lvl, whiteFlag, blackFlag):
        if self.nid is None:
            for item in self.data['labels']['items']:
                node = Node_label()
                node.data = item
                self.add_child(node)
        else:
            xdir.add_node(self)
            xdir.add_node(getNode(Flag.LABEL,
                                  parameters={
                                      'nid': self.get_property('supplier_id')},
                                  data={'name': '-> supplier'}
            ))
        return True
