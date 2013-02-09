'''
    qobuz.node.inode
    ~~~~~~~~~~~~~~~~

    This file is part of qobuz-xbmc

    :copyright: (c) 2012 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
from node import BaseNode, url2dict
from qobuz.node import Flag, getNode
from qobuz.settings import settings
from qobuz.i8n import _

class INode(BaseNode):

    def __init__(self, parameters = {}):
        self.data = None
        super(INode, self).__init__(parameters)
        self.content_type = "files"
        self.items_path = None
        self.offset = self.get_parameter('offset', delete=True) or 0
        self.add_action('add_tracks', 
                        label=_('Add track(s) to favorite'),
                        target=Flag.FAVORITE)
        self.add_action('add_albums', 
                        label=_('Add album(s) to favorite'),
                        target=Flag.FAVORITE)
        self.add_action('add_artists', 
                        label=_('Add artist(s) to favorite'),
                        target=Flag.FAVORITE)
    @property
    def offset(self):
        return self._offset
    @offset.getter
    def offset(self):
        return self._offset
    @offset.setter
    def offset(self, value):
        if value is None:
            self._offset = None
        else:
            try:
                self._offset = int(value)
            except:
                self._offset = None

    def url(self, **ka):
        if self.offset is not None and not 'offset' in ka:
            ka['offset'] = self.offset
        return super(INode, self).url(**ka)

    def add_pagination_node(self, renderer):
        '''We are looking into data and set next node in renderer's list
            
            ::note:: each node who implement collection must have 
                items_path property so we can lookup to our pagination
                (we can change data in each node to be consistant here...)
        '''
        if not self.items_path:
            return False
        data = self.data[self.items_path]
        if not 'limit' in data:
            return False
        next_offset = data['offset'] + data['limit']
        if next_offset > data['total']:
            return False
        parameters = url2dict(self.url(offset=next_offset))
        node = getNode(self.kind, parameters)
        node.label = '[%s/%s] %s' % (parameters['offset'], 
                                     data['total'],
                                     self.get_label())
        self.append(node)
        return True

    def populating_hook_before_traversal(self, renderer=None):
        if self.data and settings['auto_pagination']:
            return self.add_pagination_node(renderer)
        return True
