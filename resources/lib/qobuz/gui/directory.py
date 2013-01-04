
import xbmcplugin
import xbmcgui


from progress import Progress
import time
from debug import warn, log
from gui.util import lang
from exception import QobuzXbmcError as Qerror


class Directory():

    def __init__(self, root, handle, AS_LIST=False, nodeList = []):
        self.nodes = []
        self.label = "Qobuz / "
        self.root = root
        self.AS_LIST = AS_LIST
        self.handle = handle
        self.put_item_ok = True
        self.Progress = Progress(True)
        self.total_put = 0
        self.started_on = time.time()
        self.Progress.create(self.label + root.get_label())
        self.update(0, 100, lang(40000))
        self.line1 = ''
        self.line2 = ''
        self.line3 = ''
        self.percent = 0
        self.content_type = 'files'
        self.nodes = nodeList
        log(self, "Handle: " + repr(self.handle))

    def __del__(self):
        for node in self.nodes:
            node.delete_tree()
        self.root = None

    def elapsed(self):
        return time.time() - self.started_on

    def add_node(self, node):
        if self.Progress.iscanceled():
            raise Qerror(who=self, what="build_down_cancel")
            return False
        if self.AS_LIST:
            self.nodes.append(node)
            return True
        return self._put_item(node)
       

    def update(self, count, total, line1, line2='', line3=''):
        percent = 100
        if total and count:
            percent = count * (1 + 100 / total)
        else:
            percent = count
            if percent > 100:
                percent = 100
        labstat = '[%05i]' % (self.total_put)
        self.line1 = labstat
        #self.line1 = line1
        self.line2 = line2
        self.line3 = line3
        self.percent = percent
        self.Progress.update(percent, line1, line2, line3)
        return True

    def is_canceled(self):
        return self.Progress.iscanceled()

    def _xbmc_item(self, **ka):
        return xbmcgui.ListItem(
            ka['label'],
            ka['label'],
            ka['image'],
            ka['image'],
            ka['url'])

    def add_item(self, **ka):
        if not xbmcplugin.addDirectoryItem(self.handle,
                                    ka['url'],
                                    ka['item'],
                                    ka['is_folder'],
                                    self.total_put):
            return False
        self.total_put += 1    
        return True
    
    def _put_item(self, node):
        if self.is_canceled() : 
            return False
        item = node.makeListItem()
        ret = None
        if not item:
            return False
        if not self.add_item(url=node.make_url(),
                                item=item,
                                is_folder=node.is_folder):
            self.put_item_ok = False
            return False
        return True
        

    def close(self):
        if self.Progress:
            self.Progress.close()
            self.Progress = None

    def end_of_directory(self, forceStatus=None):
        success = True
        if forceStatus != None:
            success = forceStatus
        if not self.put_item_ok or (self.total_put == 0):
            success = False
        xbmcplugin.setContent(
            handle=self.handle, content=self.content_type)
        xbmcplugin.endOfDirectory(handle=self.handle,
                                  succeeded=success,
                                  updateListing=False,
                                  cacheToDisc=success)
        self.update(100, 100, lang(40003), 
                    "%s : %s items" % (lang(40002), str(self.total_put)))
        self.close()
        return self.total_put

    def set_content(self, content):
        log(self, "Set content: " + content)
        self.content_type = content
