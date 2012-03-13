
import xbmcplugin
import xbmcgui

from node.flag import NodeFlag
from constants import Mode
import qobuz

class xbmc_progress(xbmcgui.DialogProgress):
    
    def __init__(self, heading = None, line1 = None, line2 = None, line3 = None):
        super(xbmc_progress, self).__init__()
    
    
class xbmc_directory():
    
    def __init__(self, root, handle, ALL_AT_ONCE = False):
        self.nodes = []
        self.root = root
        self.ALL_AT_ONCE = ALL_AT_ONCE
        self.handle = handle
        self.put_item_ok = True
        self.Progress = xbmc_progress()
        self.Progress.create("Qobuz directory")
        self.total_put = 0
        
    def add_node(self, node):
        if not self.ALL_AT_ONCE: 
            return self.put_item(node)
        self.nodes.append(node)
        return True
    
    def update(self, percent, line1, line2 = None):
        self.Progress.update(percent, line1, line2)
        
    def put_item(self, node):
        self.total_put += 1
        mode = Mode.VIEW
        item = node.make_XbmcListItem()
        ret = xbmcplugin.addDirectoryItem(self.handle,
                                    node.make_url(),
                                    item,
                                    node.is_folder(),                       
                                    len(self.nodes))
        if not ret: self.put_item_ok = False
        self.Progress.update(0, "Add Item", node.get_label())
        return ret
        
    def end_of_directory(self):
        success = True
        if not self.put_item_ok or (self.total_put == 0):
            success = False
        xbmcplugin.endOfDirectory(handle = self.handle, 
                                   succeeded = success, 
                                   updateListing = False, 
                                   cacheToDisc = success)
        if self.total_put == 0:
            qobuz.gui.notifyH('Empty directory', self.root.get_label())
        self.Progress.close()
        self.Progress = None
        return success
        
    def set_content(self, content):
        xbmcplugin.setContent(handle = self.handle, content = content)