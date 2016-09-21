'''
    qobuz.node.root
    ~~~~~~~~~~~~~~~

    :part_of: xbmc-qobuz
    :copyright: (c) 2012 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
from qobuz.node.inode import INode
from qobuz.gui.util import getSetting, executeBuiltin, lang
from qobuz.cache import cache
from qobuz.cache.cache_util import clean_all
from qobuz.node import getNode, Flag
from qobuz import debug

class Node_root(INode):
    '''Our root node, we are displaying all qobuz nodes from here
    '''

    def __init__(self, parent=None, parameters={}, data=None):
        super(Node_root, self).__init__(parent=parent, parameters=parameters,
                                        data=data)
        self.nt = Flag.ROOT
        self.content_type = 'files'
        self.label = 'Qobuz'

    def populate(self, Dir, lvl, whiteFlag, blackFlag):
        self.add_child(getNode(Flag.USERPLAYLISTS))
        if getSetting('show_recommendations', asBool=True):
            self.add_child(getNode(Flag.RECOMMENDATION))
        self.add_child(getNode(Flag.PURCHASES))
        self.add_child(getNode(Flag.FAVORITES))
        if getSetting('search_enabled', asBool=True):
            search = getNode(Flag.SEARCH)
            search.search_type = 'albums'
            self.add_child(search)
            search = getNode(Flag.SEARCH)
            search.search_type = 'tracks'
            self.add_child(search)
            search = getNode(Flag.SEARCH)
            search.search_type = 'artists'
            self.add_child(search)
            collections = getNode(Flag.COLLECTIONS)
            self.add_child(collections)
        self.add_child(getNode(Flag.FRIENDS))
        self.add_child(getNode(Flag.GENRE))
        self.add_child(getNode(Flag.PUBLIC_PLAYLISTS))
        return True

    def cache_remove(self):
        '''GUI/Removing all cached data
        '''
        from qobuz.gui.util import yesno, notifyH, getImage
        from qobuz.debug import log
        if not yesno(lang(30121), lang(30122)):
            log(self, 'Deleting cached data aborted')
            return False
        if clean_all(cache):
            notifyH(lang(30119), lang(30123))
        else:
            notifyH(lang(30119), lang(30120),
                    getImage('icon-error-256'))
        return True

    def gui_scan(self):
        '''Scanning directory specified in query parameter
        '''
        executeBuiltin('UpdateLibrary("music", "%s")' % (
            self.get_parameter('query', unQuote=True)))
