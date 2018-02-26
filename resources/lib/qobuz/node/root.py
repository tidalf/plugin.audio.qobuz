'''
    qobuz.node.root
    ~~~~~~~~~~~~~~~

    :part_of: xbmc-qobuz
    :copyright: (c) 2012-2016 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
from qobuz import config
from qobuz.api.user import current as current_user
from qobuz.cache import cache
from qobuz.cache.cache_util import clean_all
from qobuz.debug import getLogger
from qobuz.gui.util import executeBuiltin, lang
from qobuz.gui.util import yesno, notifyH, getImage
from qobuz.node import getNode, Flag
from qobuz.node.inode import INode

logger = getLogger(__name__)

def makeSubscriptionNode():
    return getNode(
        Flag.TEXT,
        parameters={
            'label': '(Free Account / Subscribe on qobuz.com)',
            'image':
            'http://static-www.qobuz.com/img/sprite/sprite-plans-option-2015.png'
        })


class Node_root(INode):
    def __init__(self, parent=None, parameters=None, data=None):
        parameters = {} if parameters is None else parameters
        super(Node_root, self).__init__(
            parent=parent, parameters=parameters, data=data)
        self.nt = Flag.ROOT
        self.content_type = 'albums'
        self.label = 'Qobuz'

    def populate(self, *a, **ka):
        free = current_user.is_free_account()
        if free:
            self.add_child(makeSubscriptionNode())
        if not free:
            self.add_child(getNode(Flag.USER))
            self.add_child(getNode(Flag.USERPLAYLISTS))
        if config.app.registry.get('show_recommendations', to='bool'):
            self.add_child(getNode(Flag.RECOMMENDATION))
        if not free:
            self.add_child(getNode(Flag.PURCHASE))
            self.add_child(getNode(Flag.FAVORITE))
        if config.app.registry.get('search_enabled', to='bool'):
            self.add_child(getNode(Flag.SEARCH))
        if not free:
            self.add_child(getNode(Flag.FRIENDS))
        self.add_child(getNode(Flag.PUBLIC_PLAYLISTS))
        self.add_child(
            getNode(
                Flag.PUBLIC_PLAYLISTS, parameters={'type': 'editor-picks'}))
        if config.app.registry.get('show_experimental', to='bool'):
            self.add_child(getNode(Flag.LABEL))
            self.add_child(getNode(Flag.ARTICLE))
            self.add_child(getNode(Flag.GENRE))
            if not free:
                self.add_child(getNode(Flag.COLLECTION))
        if free:
            self.add_child(makeSubscriptionNode())
        return True

    @classmethod
    def cache_remove(cls):
        '''GUI/Removing all cached data
        '''
        if not yesno(lang(30121), lang(30122)):
            logger.warn('Deleting cached data aborted')
            return False
        if clean_all(cache):
            notifyH(lang(30119), lang(30123))
        else:
            notifyH(lang(30119), lang(30120), getImage('icon-error-256'))
        return True

    def gui_scan(self):
        '''Scanning directory specified in query parameter
        '''
        executeBuiltin('UpdateLibrary("music", "%s")' % (self.get_parameter(
            'query', to='unquote')))
