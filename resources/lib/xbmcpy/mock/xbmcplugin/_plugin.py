from collections import deque

class Plugin(deque):

    def addDirectoryItem(self, handle, url, listitem, isFolder=False,  
                             totalItems=False):
        pass

    def endOfDirectory(self, handle, succeeded=True, updateListing=True,
                                     cacheToDisc=True):
        pass

plugin = Plugin()
