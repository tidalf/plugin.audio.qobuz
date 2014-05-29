'''
    qobuz.node.friend_list
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    This file is part of qobuz-xbmc

    :copyright: (c) 2012 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
from inode import INode
from qobuz.debug import log, warn
from qobuz.api import api
from qobuz.node import getNode, Flag
from qobuz.i8n import _


class Node_friend_list(INode):
    '''
    @class Node_friend_list:
    '''
    def __init__(self, parameters={}):
        super(Node_friend_list, self).__init__(parameters)
        self.kind = Flag.FRIEND_LIST
        self.name = self.get_parameter('name', delete=True)
        self.image = ''
        self.label = _("%s's friend" % self.name) if self.name else _('Friend')

        self.content_type = 'artists'

    def url(self, **ka):
        ka['name'] = self.name
        url = super(Node_friend_list, self).url(**ka)
        return url

    def fetch(self, renderer=None):
        node = getNode(Flag.FRIEND, self.parameters)
        node.create('qobuz.com')
        return True

    def populate(self, renderer=None):
        username = api.username
        password = api.password
        user_id = api.user_id
        user_data = api.get('/user/login', username=username,
                                password=password)
        friend_data = user_data['user']['player_settings']['friends']
        log(self, "Build-down friends list " + repr(self.name))
        if self.name:
            data = api.get('/playlist/getUserPlaylists',
                               username=self.name, limit=0)
        else:
            data = api.get('/playlist/getUserPlaylists',
                               user_id=user_id, limit=0)
        if not data:
            warn(self, "No friend data")
            return False
        # extract all owner names from the list
        friend_list = []
        for item in data['playlists']['items']:
            if item['owner']['name'] == user_data['user']['login']:
                continue
            friend_list.append(item['owner']['name'])
        # add previously stored
        if (not self.name):
            for name in friend_data:
                friend_list.append(str(name))
        # remove duplicates
        keys = {}
        for e in friend_list:
            keys[e] = 1
        friend_list = keys.keys()
        # and add them to the directory
        for name in friend_list:
            node = getNode(Flag.FRIEND, self.parameters)
            if name == self.name:
                continue
            if name in friend_data:
                node.label = _('Friend / %s' % (node.label))
            self.append(node)
        return True
#    def attach_context_menu(self, item, menu):
#        label = self.get_label()
#        url = self.make_url()
#        menu.add(path='friend', label=label, cmd=containerUpdate(url))
#        url = self.make_url(nt=Flag.FRIEND, nm='gui_create', nid=self.nid)
#        menu.add(path='friend/add', label='Add', cmd=runPlugin(url))
#
#        ''' Calling base class '''
#        super(Node_friend_list, self).attach_context_menu(item, menu)
