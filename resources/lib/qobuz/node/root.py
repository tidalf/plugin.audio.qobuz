'''
    qobuz.node.root
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    This file is part of qobuz-xbmc

    :copyright: (c) 2012 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''

from inode import INode
from qobuz.node import getNode, Flag
from qobuz.xbmc import settings

class Node_root(INode):
    '''Our root node, we are displaying all qobuz nodes from here
    '''
    def __init__(self, parameters={}):
        super(Node_root, self).__init__(parameters)
        self.kind = Flag.ROOT
        self.label = 'Qobuz'
        self.content_type = 'files'
        self.display_recommendation = True

    def populate(self, renderer=None):
        self.append(getNode(Flag.USERPLAYLISTS, self.parameters))
        if self.display_recommendation:
            self.append(getNode(Flag.RECOMMENDATION, self.parameters))
        self.append(getNode(Flag.PURCHASES, self.parameters))
        self.append(getNode(Flag.FAVORITES, self.parameters))
        if settings.get('search_enabled') == 'true':
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

#    def cache_remove(self):
#        '''GUI/Removing all cached data
#        '''
#        from gui.util import yesno, notifyH, getImage
#        from debug import log
#        if not yesno(lang(31102), lang(31103)):
#            log(self, "Deleting cached data aborted")
#            return False
#        if clean_all(cache):
#            notifyH(lang(31100), lang(31104))
#        else:
#            notifyH(lang(31100), lang(31101),
#                    getImage('icon-error-256'))
#        return True
#
#    def gui_scan(self):
#        '''Scanning directory specified in query parameter
#        '''
#        query = self.get_parameter('query', unQuote=True)
#        print "Scanning folder: %s" % (query)
#        executeBuiltin('XBMC.UpdateLibrary("music", "%s")' % (query))
