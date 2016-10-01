'''
    qobuz.node.friend_list
    ~~~~~~~~~~~~~~~~~~~~~

    :part_of: xbmc-qobuz
    :copyright: (c) 2012 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
from qobuz.node.inode import INode
from qobuz import debug
from qobuz.gui.util import getImage, runPlugin, containerUpdate, lang
from qobuz.api import api
from qobuz.node import getNode, Flag


class Node_friends(INode):
    '''@class Node_friend_list:
    '''

    def __init__(self, parent=None, parameters={}, data=None):
        super(Node_friends, self).__init__(parent=parent,
                                           parameters=parameters,
                                           data=data)
        self.nt = Flag.FRIENDS
        self.name = self.get_parameter('query')
        self.image = getImage('artist')
        self.label = str(self.name) + lang(30179) if (self.name) else lang(30180)
        self.url = None
        self.content_type = 'artists'

    def make_url(self, **ka):
        if self.name:
            ka['query'] = self.name
        return super(Node_friends, self).make_url(**ka)

    def fetch(self, Dir, lvl, whiteFlag, blackFlag):
        node = getNode(Flag.FRIEND)
        node.create('qobuz.com')
        return {}

    def populate(self, xbmc_directory, lvl, whiteFlag, blackFlag):
        user_data = api.get('/user/login',
                            username=api.username,
                            password=api.password)
        if not 'user' in user_data:
            return False
        friend_data = user_data['user']['player_settings']['friends']
        if self.name is not None:
            data = api.get('/playlist/getUserPlaylists',
                           username=self.name,
                           limit=self.limit, offset=self.offset,
                           type='last-created')
            debug.info('Friend {} data {}', self.name, data)
        else:
            data = api.get('/playlist/getUserPlaylists',
                           user_id=api.user_id,
                           limit=self.limit, offset=self.offset,
                           type='last-created')
        if data is None:
            debug.warn(self, 'No friend data')
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
            node.label = 'Friend / %s' % (node.label)
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
