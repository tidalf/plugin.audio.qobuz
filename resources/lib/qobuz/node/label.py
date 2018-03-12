'''
    qobuz.node.label
    ~~~~~~~~~~~~~~~~

    :part_of: kodi-qobuz
    :copyright: (c) 2012-2018 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
from qobuz.api import api
from qobuz.gui.util import getImage, lang
from qobuz.node import Flag, helper
from qobuz.node.inode import INode, getNode


class Node_label(INode):
    def __init__(self, parent=None, parameters=None, data=None):
        parameters = {} if parameters is None else parameters
        super(Node_label, self).__init__(
            parent=parent, parameters=parameters, data=data)
        self.nt = Flag.LABEL
        self.image = getImage('album')
        self.content_type = 'albums'

    def get_label(self, default=None):
        if self.nid is None:
            return lang(30188)
        return self.get_property('name')

    def get_label2(self):
        if self.nid is None:
            return None
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

    def fetch(self, options=None):
        if self.nid is None:
            return api.get('/label/list', limit=self.limit, offset=self.offset)
        return api.get('/label/get', label_id=self.nid)

    def populate(self, options=None):
        options = helper.get_tree_traverse_opts(options)
        if self.nid is None:
            for item in self.data['labels']['items']:
                self.add_child(getNode(Flag.LABEL, data=item))
        else:
            options.xdir.add_node(self)
            supplier_id = self.get_property('supplier_id', default=None)
            if supplier_id is not None:
                options.xdir.add_node(
                    getNode(
                        Flag.LABEL,
                        parameters={'nid': supplier_id},
                        data={'name': '[Supplier]'}))
        return True
