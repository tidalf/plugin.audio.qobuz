
import xbmcplugin
import xbmcgui

from node.flag import NodeFlag
from constants import Mode
import qobuz
import time

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
        self.Progress.update(0, "Fetching Data (cache / network)")
        self.total_put = 0
        self.given_total = 0
        self.started_on = time.time()
        

    def elapsed(self):
        return time.time() - self.started_on
    
    def add_node(self, node):
        if not self.ALL_AT_ONCE: 
            return self.put_item(node)
        self.nodes.append(node)
        return True
    
    def set_given_total(self, total):
        self.given_total = total
        
    def get_given_total(self):
        return self.given_total
    
    def update(self, percent, line1, line2 = ''):
        et = str(int(self.elapsed())) + 's'
        line1 = ''.join(('[', str(self.total_put), ' / ', et, '] ', line1))
        self.Progress.update(percent, line1, line2)
    
    def is_canceled(self):
        return self.Progress.iscanceled()
    
    def put_item(self, node):
        self.total_put += 1
#        perc = self.total_put * (1 + (self.given_total / 100))
#        print "PERCENT: " + str(perc)
#        print "HANDLE: " + str(self.handle)
        mode = Mode.VIEW
        item = node.make_XbmcListItem()
        if not item:
            return False
        ret = xbmcplugin.addDirectoryItem(self.handle,
                                    node.make_url(),
                                    item,
                                    node.is_folder(),                       
                                    len(self.nodes))
        if not ret: self.put_item_ok = False
        if not (node.type & NodeFlag.TYPE_TRACK):
            self.update(50, "Add Item", node.get_label())
        return ret
    
    def close(self):
        if self.Progress: 
            self.Progress.close()
            self.Progress = None
        
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
        self.update(100, "Done", "Displaying " + str(self.total_put).encode('ascii', 'replace'))
        self.close()
        return success
        
    def set_content(self, content):
        xbmcplugin.setContent(handle = self.handle, content = content)