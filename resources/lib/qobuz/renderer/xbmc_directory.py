
import xbmcplugin
import xbmcgui

from node.flag import NodeFlag
from constants import Mode
from gui import Progress
import qobuz
import time
from debug import warn
    
class xbmc_directory():
    
    def __init__(self, root, handle, ALL_AT_ONCE = False):
        self.nodes = []
        self.label = "Qobuz / "
        self.root = root
        self.ALL_AT_ONCE = ALL_AT_ONCE
        self.handle = handle
        self.put_item_ok = True
        self.Progress = Progress(True)
        self.total_put = 0
        self.started_on = time.time()
        self.Progress.create(self.label + root.get_label())
        self.update(0, 100, qobuz.lang(40000))
        self.line1 = ''
        self.line2 = ''
        self.line3 = ''
        self.percent = 0

    def elapsed(self):
        return time.time() - self.started_on
    
    def add_node(self, node):
        if not self.ALL_AT_ONCE: 
            return self._put_item(node)
        self.nodes.append(node)
        return True
    
    def _pretty_time(self, time):
        hours = (time / 3600)
        minutes = (time / 60) - (hours * 60)
        seconds = time % 60
        return '%02i:%02i:%02i' % (hours, minutes, seconds)
    
    def update(self, count, total, line1, line2 = '', line3 = ''):
        percent = 100
        if total and count:
            percent = count * (1 + 100 / total)
        else:
            percent = count
            if percent > 100: percent = 100
        pet = self._pretty_time(int(self.elapsed()))
        line1 = '[%05i / %s] %s' % (self.total_put, pet, line1)
        self.line1 = line1
        self.line2 = line2
        self.line3 = line3
        self.percent = percent
        self.Progress.update(percent, line1, line2, line3)
        return True
    
    def is_canceled(self):
        return self.Progress.iscanceled()
    
    def _put_item(self, node):
        self.total_put += 1
        mode = Mode.VIEW
        item = node.make_XbmcListItem()
        if not item:
            return False
        try:
            ret = xbmcplugin.addDirectoryItem(self.handle,
                                    node.make_url(),
                                    item,
                                    node.is_folder,                       
                                    self.total_put)
        except: 
            warn(self, "Cannot add item")
        if not ret: self.put_item_ok = False
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
            qobuz.gui.notifyH(qobuz.lang(40001).encode('utf8', 'replace'), self.root.get_label().encode('utf8', 'replace'))
        self.update(100, 100,  qobuz.lang(40003), qobuz.lang(40002) + ': ' + str(self.total_put).encode('ascii', 'replace') + ' items')
        self.close()
        return success
        
    def set_content(self, content):
        xbmcplugin.setContent(handle = self.handle, content = content)
