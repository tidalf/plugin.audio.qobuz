'''
    qobuz.node.user_playlists
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    This file is part of qobuz-xbmc

    :copyright: (c) 2012 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
from qobuz.node import Flag, getNode
from qobuz.debug import warn
from qobuz.api import api
from qobuz.cache import cache
from qobuz.i8n import _
from inode import INode


class Node_user_playlists(INode):
    """User playlists node
        This node list playlist made by user and saved on Qobuz server
    """
    def __init__(self, parameters={}):
        super(Node_user_playlists, self).__init__(parameters)
        self.kind = Flag.USERPLAYLISTS
        self.label = _('User playlists')
        self.content_type = 'files'
        self.items_path = 'playlists'
        self.add_action('new', label=_('New playlist'), target=Flag.PLAYLIST)

    def fetch(self, renderer=None):
        data = api.get('/playlist/getUserPlaylists',
                       limit=api.pagination_limit, offset=self.offset,
                       user_id=api.user_id)
        if not data:
            warn(self, "Build-down: Cannot fetch user playlists data")
            return False
        self.data = data
        return True

    def populate(self, renderer=None):
        for playlist in self.data[self.items_path]['items']:
            node = getNode(Flag.PLAYLIST, self.parameters)
            node.data = playlist
            self.append(node)
        return True

    def delete_cache(self):
        key = cache.make_key('/playlist/getUserPlaylists',
                       limit=api.pagination_limit, offset=self.offset,
                       user_id=api.user_id)
        return cache.delete(key)
