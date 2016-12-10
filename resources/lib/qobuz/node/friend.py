'''
    qobuz.node.friend
    ~~~~~~~~~~~~~~~~~

    :part_of: xbmc-qobuz
    :copyright: (c) 2012-2016 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
import json
from qobuz.node.inode import INode
from qobuz import debug
from qobuz.gui.util import getImage, runPlugin, containerRefresh, \
    containerUpdate, notifyH, executeBuiltin, lang
from qobuz.api import api
from qobuz.api.user import current as user
from qobuz.cache import cache
from qobuz.node import Flag, getNode
from qobuz.theme import theme, color

class Node_friend(INode):

    def __init__(self, parent=None, parameters={}, data=None):
        super(Node_friend, self).__init__(parent=parent,
                                          parameters=parameters,
                                          data=data)
        self.nt = Flag.FRIEND
        self.image = getImage('artist')
        self.set_name(self.get_parameter('query'))
        self.content_type = 'files'

    def set_label(self, label):
        self.label = color(theme.get('item/default/color'), label)

    def set_name(self, name):
        self.name = name or ''
        self.set_label(self.name)
        return self

    def make_url(self, **ka):
        if self.name:
            ka['query'] = self.name
        return super(Node_friend, self).make_url(**ka)

    def gui_create(self):
        name = self.get_parameter('query')
        if not name:
            from qobuz.gui.util import Keyboard
            kb = Keyboard('',
                          str(lang(30181)))
            kb.doModal()
            name = ''
            if not kb.isConfirmed():
                return False
            name = kb.getText().strip()
        if not name:
            return False
        if not self.create(name):
            notifyH('Qobuz', 'Cannot add friend %s' % (name))
            return False
        notifyH('Qobuz', 'Friend %s added' % (name))
        return True

    def create(self, name=None):
        friendpl = api.get('/playlist/getUserPlaylists',
                           username=name,
                           type='last-created')
        if not friendpl:
            return False
        data = api.get('/user/login', username=user.username,
                       password=user.password)
        if not data:
            return False
        if data['user']['login'] == name:
            return False
        friends = data['user']['player_settings']
        if not 'friends' in friends:
            friends = []
        else:
            friends = friends['friends']
        if name in friends:
            return False
        friends.append(name)
        newdata = {'friends': friends}
        if not api.user_update(player_settings=json.dumps(newdata)):
            return False
        self.delete_cache()
        executeBuiltin(containerRefresh())
        return True

    def delete_cache(self):
        key = cache.make_key('/user/login', username=api.username,
                             password=api.password)
        cache.delete(key)

    def remove(self):
        name = self.get_parameter('query')
        if name == 'qobuz.com':
            return False
        if not name:
            return False
        user = self.get_user_data()
        if not user:
            return False
        friends = user['player_settings']
        if not 'friends' in friends:
            notifyH('Qobuz', 'You don\'t have friend',
                    'icon-error-256')
            debug.warn(self, 'No friends in user/player_settings')
            return False
        friends = friends['friends']
        if not name in friends:
            notifyH('Qobuz', 'You\'re not friend with %s' % (name),
                    'icon-error-256')
            debug.warn(self, 'Friend ' + repr(name) + ' not in friends data')
            return False
        del friends[friends.index(name)]
        newdata = {'friends': friends}
        if not api.user_update(player_settings=json.dumps(newdata)):
            notifyH('Qobuz', 'Friend %s added' % (name))
            notifyH('Qobuz', 'Cannot updata friend\'s list...',
                    'icon-error-256')
            return False
        notifyH('Qobuz', 'Friend %s removed' % (name))
        self.delete_cache()
        executeBuiltin(containerRefresh())
        return True

    def fetch(self, Dir, lvl, whiteFlag, blackFlag):
        node = getNode(Flag.FRIEND)
        node.create('qobuz.com')
        return api.get('/playlist/getUserPlaylists',
                       type='last-created',
                       username=self.name)

    def populate(self, Dir, lvl, whiteFlag, blackFlag):
        result = False
        if lvl != -1:
            self.add_child(getNode(Flag.FRIENDS, parameters=self.parameters))
        for playlist in self.data['playlists']['items']:
            node = getNode(Flag.PLAYLIST, data=playlist)
            if node.get_owner() == self.label:
                self.nid = node.get_owner_id()
            self.add_child(node)
            result = True
        return result

    def attach_context_menu(self, item, menu):
        colorWarn = theme.get('item/caution/color')
        url = self.make_url()
        menu.add(path='friend', label=self.name, cmd=containerUpdate(url))
        cmd = runPlugin(self.make_url(nt=Flag.FRIEND, nm='remove'))
        menu.add(path='friend/remove', label='Remove', cmd=cmd,
                 color=colorWarn)
        super(Node_friend, self).attach_context_menu(item, menu)
