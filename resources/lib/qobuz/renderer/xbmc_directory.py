
import xbmcplugin
import xbmcgui

from node.flag import NodeFlag
from constants import Mode

class xbmc_progress(xbmcgui.DialogProgress):
    
    def __init__(self, heading = None, line1 = None, line2 = None, line3 = None):
        super(xbmc_progress, self).__init__()
    
    
class xbmc_directory():
    
    def __init__(self, handle, ALL_AT_ONCE = False):
        self.nodes = []
        self.ALL_AT_ONCE = ALL_AT_ONCE
        self.handle = handle
        self.put_item_ok = True
        self.Progress = xbmc_progress()
        self.Progress.create("Qobuz directory")
        
    def add_node(self, node):
        self.nodes.append(node)
        if not self.ALL_AT_ONCE: 
            return self.put_item(node)
        return True
    
    def update(self, percent, line1, line2 = None):
        self.Progress.update(percent, line1, line2)
        
    def put_item(self, node):
        self.update(50, 'Add node:' + node.get_label(), '')
        mode = Mode.VIEW
        if node.type & NodeFlag.TYPE_TRACK:
            mode = Mode.PLAY
        url = node.get_url(mode)
        print "PUT ITEM: " + node.get_label()
        item = node.make_XbmcListItem()


        ret = xbmcplugin.addDirectoryItem(self.handle,
                                    url,
                                    item,
                                    node.is_folder(),                       
                                    len(self.nodes))
        if not ret: self.put_item_ok = False
        self.Progress.update(0, "Add Item", node.get_label())
        return ret
        
    def end_of_directory(self):
        xbmcplugin.endOfDirectory(handle = self.handle, 
                                   succeeded = self.put_item_ok, 
                                   updateListing = False, 
                                   cacheToDisc = self.put_item_ok)
        self.Progress.close()
        self.Progress = None
        
    def set_content(self, content):
        xbmcplugin.setContent(handle = self.handle, content = content)