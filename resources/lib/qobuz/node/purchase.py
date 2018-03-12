'''
    qobuz.node.purchase
    ~~~~~~~~~~~~~~~~~~~

    :part_of: kodi-qobuz
    :copyright: (c) 2012-2016 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
from qobuz.api import api
from qobuz.api.user import current as user
from qobuz.debug import getLogger
from qobuz.gui.util import lang, getImage
from qobuz.node import Flag, getNode, helper
from qobuz.node.inode import INode

logger = getLogger(__name__)


def populate_return_helper(array):
    if len(array) > 0:
        return True
    return False


class Node_purchase(INode):
    def __init__(self, parent=None, parameters=None, data=None):
        parameters = {} if parameters is None else parameters
        super(Node_purchase, self).__init__(
            parent=parent, parameters=parameters, data=data)
        self.nt = Flag.PURCHASE
        self.image = getImage('album')
        self.content_type = 'albums'
        self.search_type = self.get_parameter('search-type')

    def get_label(self, default=None):
        if self.search_type is None:
            return lang(30101)
        elif self.search_type == 'all':
            return lang(30098)
        return self.search_type.capitalize()

    def make_url(self, **ka):
        if self.search_type:
            ka['search-type'] = str(self.search_type)
        return super(Node_purchase, self).make_url(**ka)

    def fetch(self, options=None):
        if self.search_type is None:
            return {}
        return api.get('/purchase/getUserPurchases',
                       limit=self.limit,
                       offset=self.offset,
                       user_id=user.get_id())

    def populate(self, options=None):
        if self.search_type is None:
            for search_type in ['albums']:  # 'all' , 'tracks']:
                self.add_child(
                    getNode(
                        Flag.PURCHASE, parameters={'search-type': search_type
                                                   }))
            return True
        wanted = ['albums', 'tracks']
        if self.search_type != 'all':
            wanted = [self.search_type]
        ret = False
        for kind in wanted:
            method = '_populate_%s' % kind
            if not hasattr(self, method):
                logger.warn('No method named %s', method)
                continue
            if getattr(self, method)(options):
                ret = True
        return ret

    def _populate_albums(self, options=None):
        options = helper.get_tree_traverse_opts(options)
        for album in self.data['albums']['items']:
            node = helper.get_node_album(album)
            self.add_child(node)
        return populate_return_helper(self.data['albums']['items'])

    def _populate_tracks(self, options=None):
        for track in self.data['tracks']['items']:
            self.add_child(getNode(Flag.TRACK, data=track))
        return populate_return_helper(self.data['tracks']['items'])
