'''
    qobuz.node.root
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    This file is part of qobuz-xbmc

    :copyright: (c) 2012 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''

from inode import INode
from qobuz.node import getNode, Flag
from qobuz.settings import settings
from qobuz.i8n import _
from qobuz.cache import cache


class Node_root(INode):
    '''Our root node, we are displaying all qobuz nodes from here
    '''
    def __init__(self, parameters={}):
        super(Node_root, self).__init__(parameters)
        self.kind = Flag.ROOT
        self.label = 'Qobuz'
        self.content_type = 'files'

    def populate(self, renderer=None):
        self.append(getNode(Flag.USERPLAYLISTS, self.parameters))
        if settings['recommendation_enable']:
            self.append(getNode(Flag.RECOMMENDATION, self.parameters))
        self.append(getNode(Flag.PURCHASES, self.parameters))
        self.append(getNode(Flag.FAVORITES, self.parameters))
        if settings['search_enable']:
            search = getNode(Flag.SEARCH, self.parameters)
            search.search_type = 'albums'
            self.append(search)
            search = getNode(Flag.SEARCH, self.parameters)
            search.search_type = 'tracks'
            self.append(search)
            search = getNode(Flag.SEARCH, self.parameters)
            search.search_type = 'artists'
            self.append(search)
        self.append(getNode(Flag.FRIEND_LIST, self.parameters))
        self.append(getNode(Flag.GENRE, self.parameters))
        self.append(getNode(Flag.PUBLIC_PLAYLISTS, self.parameters))
        return True

    def append(self, item):
        item.add_action('cache_delete_all',
                        label=_('Erase all data from cache'), target=Flag.ROOT)
        item.add_action('cache_delete_old',
                        label=_('Erase old data from cache'), target=Flag.ROOT)
        super(Node_root, self).append(item)

    def cache_delete_all(self, **ka):
        return cache.delete_all(**ka)

    def cache_delete_old(self):
        return cache.delete_old()

#    def gui_scan(self):
#        '''Scanning directory specified in query parameter
#        '''
#        query = self.get_parameter('query', unQuote=True)
#        print "Scanning folder: %s" % (query)
#        executeBuiltin('XBMC.UpdateLibrary("music", "%s")' % (query))
