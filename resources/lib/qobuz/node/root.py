#     Copyright 2011 Joachim Basmaison, Cyril Leclerc
#
#     This file is part of xbmc-qobuz.
#
#     xbmc-qobuz is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     xbmc-qobuz is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.   See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with xbmc-qobuz.   If not, see <http://www.gnu.org/licenses/>.

from inode import INode
from qobuz.cache import cache
from qobuz.cache.cacheutil import clean_all
from qobuz.node import getNode, Flag

class Node_root(INode):
    '''Our root node, we are displaying all qobuz nodes from here
    '''
    def __init__(self, parameters={}):
        super(Node_root, self).__init__(parameters)
        self.kind = Flag.ROOT
        self.label = 'Qobuz'
        self.content_type = 'files'
        self.display_recommendation = True

    def populate(self):
        self.append(getNode(Flag.USERPLAYLISTS, self.parameters))
        if self.display_recommendation:
            self.append(getNode(Flag.RECOMMENDATION, self.parameters))
#        self.append(getNode(Flag.PURCHASES, self.properties))
#        self.add_child(getNode(Flag.FAVORITES))
#        if getSetting('search_enabled', isBool=True):
#            search = getNode(Flag.SEARCH)
#            search.search_type = 'albums'
#            self.add_child(search)
#            search = getNode(Flag.SEARCH)
#            search.search_type = 'tracks'
#            self.add_child(search)
#            search = getNode(Flag.SEARCH)
#            search.search_type = 'artists'
#            self.add_child(search)
#        self.add_child(getNode(Flag.FRIEND_LIST))
#        self.add_child(getNode(Flag.GENRE))
#        self.add_child(getNode(Flag.PUBLIC_PLAYLISTS))
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
