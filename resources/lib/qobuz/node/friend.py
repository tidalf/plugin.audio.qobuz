'''
    qobuz.node.friend
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    This file is part of qobuz-xbmc

    :copyright: (c) 2012 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''

import json

from inode import INode
from qobuz.debug import warn
from qobuz.api import api
from qobuz.cache import cache
from qobuz.node import Flag, getNode
# from qobuz.settings import settings


class Node_friend(INode):
    '''
    @class Node_friend:
    '''

    def __init__(self, parameters={}):
        super(Node_friend, self).__init__(parameters)
        self.kind = Flag.FRIEND
        self.image = ''
        self.name = self.get_parameter('query', delete=True)

    def set_label(self, label):
        self.label = label

    @property
    def name(self):
        return self._name

    @name.getter
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name or ''
        self.label = self.name

    def url(self, **ka):
        ka['query'] = self.name
        return super(Node_friend, self).url(**ka)

#    def gui_create(self):
#        name = self.get_parameter('query')
#        if not name:
#            from gui.util import Keyboard
#            kb = Keyboard('',
#                          str(lang(41102)))
#            kb.doModal()
#            name = ''
#            if not kb.isConfirmed():
#                return False
#            name = kb.getText().strip()
#        if not name:
#            return False
#        if not self.create(name):
#            notifyH('Qobuz', 'Cannot add friend %s' % (name))
#            return False
#        notifyH('Qobuz', 'Friend %s added' % (name))
#        return True

    def create(self, name=None):
        username = api.username
        password = api.password
        friendpl = api.get('/playlist/getUserPlaylists', username=name)
        if not friendpl:
            return False
        user = api.get('/user/login', username=username, password=password)
        if user['user']['login'] == name:
            return False
        if not user:
            return False
        friends = user['user']['player_settings']
        if not 'friends' in friends:
            friends = []
        else:
            friends = friends['friends']
        if name in friends:
            return False
        friends.append(name)
        newdata = {'friends': friends}
        # easyapi.get(name='user')
        if not api.user_update(player_settings=json.dumps(newdata)):
            return False
#        qobuz.registry.delete(name='user')
#        executeBuiltin(containerRefresh())
        return True

    def delete_cache(self):
        key = cache.make_key('/user/login', username=api.username,
                             password=api.password)
        cache.delete(key)

#    def remove(self):
#        name = self.get_parameter('query')
#        if name == 'qobuz.com':
#            return False
#        if not name:
#            return False
#        user = self.get_user_data()
#        if not user:
#            return False
#        friends = user['player_settings']
#        if not 'friends' in friends:
#            notifyH('Qobuz', "You don't have friend",
#                    'icon-error-256')
#            warn(self, "No friends in user/player_settings")
#            return False
#        friends = friends['friends']
#        if not name in friends:
#            notifyH('Qobuz', "You're not friend with %s" % (name),
#                    'icon-error-256')
#            warn(self, "Friend " + repr(name) + " not in friends data")
#            return False
#        del friends[friends.index(name)]
#        newdata = {'friends': friends}
#        if not api.user_update(player_settings=json.dumps(newdata)):
#            notifyH('Qobuz', 'Friend %s added' % (name))
#            notifyH('Qobuz', "Cannot updata friend's list...",
#                    'icon-error-256')
#            return False
#        notifyH('Qobuz', 'Friend %s removed' % (name))
#        self.delete_cache()
#        executeBuiltin(containerRefresh())
#        return True

    def populate(self, renderer=None):
        data = api.get('/playlist/getUserPlaylists', username=self.name)
        if not data:
            warn(self, "No friend data")
            return False
        if depth != -1:
            self.append(getNode(Flag.FRIEND_LIST, self.parameters))
        for pl in data['playlists']['items']:
            node = getNode(Flag.PLAYLIST, self.parameters)
            node.data = pl
            if node.get_owner() == self.label:
                self.nid = node.get_owner_id()
            self.append(node)
        return True

#    def attach_context_menu(self, item, menu):
#        colorWarn = getSetting('item_caution_color')
#        url=self.make_url()
#        menu.add(path='friend', label=self.name, cmd=containerUpdate(url))
#        cmd = runPlugin(self.make_url(nt=Flag.FRIEND, nm="remove"))
#        menu.add(path='friend/remove', label='Remove', cmd=cmd,
#                 color=colorWarn)
#
#        ''' Calling base class '''
#        super(Node_friend, self).attach_context_menu(item, menu)
