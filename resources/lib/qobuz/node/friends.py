'''
    qobuz.node.friend_list
    ~~~~~~~~~~~~~~~~~~~~~

    :part_of: kodi-qobuz
    :copyright: (c) 2012-2016 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
from qobuz.api import api
from qobuz.api.user import current as user
from qobuz.debug import getLogger
from qobuz.gui.util import getImage, runPlugin, containerUpdate, lang
from qobuz.node import getNode, Flag
from qobuz.node.inode import INode

logger = getLogger(__name__)


class Node_friends(INode):
    def __init__(self, parent=None, parameters=None, data=None):
        parameters = {} if parameters is None else parameters
        super(Node_friends, self).__init__(
            parent=parent, parameters=parameters, data=data)
        self.nt = Flag.FRIENDS
        self.name = self.get_parameter('query')
        self.image = getImage('artist')
        self.label = str(self.name) + lang(30179) if (
            self.name) else lang(30180)
        self.url = None
        self.content_type = 'songs'

    def make_url(self, **ka):
        if self.name:
            ka['query'] = self.name
        return super(Node_friends, self).make_url(**ka)

    def fetch(self, options=None):
        node = getNode(Flag.FRIEND)
        node.create('qobuz.com')
        return {}

    def populate(self, options=None):
        user_data = api.get('/user/login',
                            username=user.username,
                            password=user.password)
        if 'user' not in user_data:
            return False
        friend_data = user_data['user']['player_settings']['friends']
        if self.name is not None:
            data = api.get('/playlist/getUserPlaylists',
                           username=self.name,
                           limit=self.limit,
                           offset=self.offset,
                           type='last-created')
        else:
            data = api.get('/playlist/getUserPlaylists',
                           user_id=user.get_id(),
                           limit=self.limit,
                           offset=self.offset,
                           type='last-created')
        if data is None:
            logger.warn('No friend data')
            return False
        friend_list = {}

        def add_name(name):
            if name in friend_list:
                return None
            if name == user_data['user']['login']:
                return None
            if name == self.name:
                return None
            friend_list[name] = 1
            node = getNode(Flag.FRIEND, {'query': str(name)})
            node.label = 'Friend / %s' % node.label
            self.add_child(node)
            return node

        for item in data['playlists']['items']:
            add_name(item['owner']['name'])
        for name in friend_data:
            add_name(name)
        return True

    def attach_context_menu(self, item, menu):
        label = self.get_label()
        url = self.make_url()
        menu.add(path='friend', label=label, cmd=containerUpdate(url))
        url = self.make_url(nt=Flag.FRIEND, nm='gui_create', nid=self.nid)
        menu.add(path='friend/add', label=lang(30181), cmd=runPlugin(url))
        super(Node_friends, self).attach_context_menu(item, menu)
