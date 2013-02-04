'''
    xbmcpy.mock._plugin
    ~~~~~~~~~~~~~~~~~~~

    This file is part of qobuz-xbmc

    :copyright: (c) 2012 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
from collections import deque

class Plugin(deque):

    def addDirectoryItem(self, handle, url, listitem, isFolder=False,  
                             totalItems=False):
        pass

    def endOfDirectory(self, handle, succeeded=True, updateListing=True,
                                     cacheToDisc=True):
        pass

plugin = Plugin()
