from collections import deque
from mock.xbmcplugin import xbmcplugin

__in_xbmc__ = False
console = None
try:
    import xbmc
    __in_xbmc__ = True
except:
    from xbmcpy.console import console


class Directory(deque):

    def __init__(self, **ka):
        self.handle = ka['handle'] if 'handle' in ka else 0
        self.makeItem = ka['makeItem'] if 'makeItem' in ka else None
        self.pluginId = ka['pluginId'] if 'pluginId' in ka else ''
        self.console = console
        super(Directory, self).__init__()

    def append(self, node):
        if self.makeItem:
            item = self.makeItem(node)
            if __in_xbmc__:
                if not item:
                    return False
                url = 'plugin://%s/%s' % (self.pluginId, node.url())
                xbmcplugin.addDirectoryItem(self.handle, url, item, 
                                            node.is_folder, 1)
            else:
                console.write("[%s] %s (%s)\n" % (str(len(self)), 
                                                  node.get_label(), node.url()))
        super(Directory, self).append(node)

    def end(self, success=True, updateListing=False, cacheToDisc=True):
        if __in_xbmc__:
            xbmcplugin.endOfDirectory(self.handle, success, updateListing, 
                                      cacheToDisc)
        else:
            console.write('Total item: %s\n' % (len(self)))
