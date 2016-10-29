'''
    qobuz.gui.directory
    ~~~~~~~~~~~~~~~~~~~

    :part_of: xbmc-qobuz
    :copyright: (c) 2012-2016 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
import xbmcplugin  # @UnresolvedImport
import xbmcgui  # @UnresolvedImport

from qobuz.gui.progress import Progress
import time
from qobuz.gui.util import lang
from qobuz import exception
from qobuz import debug
from qobuz import config


class Directory(object):
    """This class permit to add item to Xbmc directory or store nodes
        that we retrieve while building our tree

        Parameters:
        root: node, The root node
        nodeList: list, list of node (empty list by default)

        Named parameters:
            withProgress: bool, if set to false no Xbmc progress is displayed

        Note: After init you can set some optional parameters:
            asList: Don't put item to Xbmc Directory
            replaceItem: When attaching context menu to item, control if
                we are replacing Xbmc Default menu
    """

    def __init__(self, root=None, nodes=[], handle=None,
                 asList=False, asLocalUrl=False, withProgress=False, **ka):
        self.nodes = nodes
        self.label = 'Qobuz'
        if root is not None:
            self.label = '%s / %s' % (self.label, root.label)
        self.root = root
        self.asList = asList
        self.handle = handle
        self.put_item_ok = True
        self.Progress = Progress(enable=withProgress)
        self.total_put = 0
        self.started_on = time.time()
        #self.Progress.create(self.label)
        #self.update({'count': 0, 'total': 100}, lang(30169))
        self.line1 = ''
        self.line2 = ''
        self.line3 = ''
        self.percent = 0
        self.content_type = 'files'
        self.replaceItems = False
        self.asLocalUrl = asLocalUrl

    def __del__(self):
        """Cleaning our tree on delete
            @attention: may be useless
        """
        try:
            if self.nodes is not None:
                for node in self.nodes:
                    node.delete_tree()
            self.nodes = None
            if self.root is not None:
                self.root.delete_tree()
                self.root = None
        except Exception as e:
            import traceback
            traceback.print_exc()
            debug.warn("Something went wrong while deleting tree: {}", e)

    def elapsed(self):
        """Return elapsed time since directory has been created
        """
        return time.time() - self.started_on

    def add_node(self, node):
        """Adding node to node list if asList=True or putting item
        into Xbmc directory
        * @attention: broken, Raise exception if user has canceled progress
        """
        if self.Progress.iscanceled():
            raise exception.BuildCanceled('down')
        if self.asList:
            self.nodes.append(node)
            self.total_put += 1
            return True
        return self.__add_node(node)

    def __add_node(self, node):
        """Helper: Add node to xbmc.Directory
            Parameter:
            node: node, node to add
        """
        if self.is_canceled():
            return False
        item = node.makeListItem(replaceItems=self.replaceItems)
        if item is None:
            return False
        url = node.make_url(asLocalUrl=self.asLocalUrl)
        if not self.add_to_xbmc_directory(url=url,
                                          item=item,
                                          is_folder=node.is_folder):
            self.put_item_ok = False
            return False
        return True

    def is_canceled(self):
        """Return is_canceled value from our progress dialog
        """
        return self.Progress.iscanceled()

    def _xbmc_item(self, **ka):
        """Make xbmc item
            Named parameters:
                label: string, label for this item
                image: string, image for this item
                url  : string, url for this item
        """
        return xbmcgui.ListItem(
            ka['label'],
            ka['label'],
            ka['image'],
            ka['image'],
            ka['url'])

    def add_to_xbmc_directory(self, is_folder=False, **ka):
        """Add item to Xbmc Directory
            Named parameters:
                url: string
                item: xbmc.ListItem
                is_folder: bool
        """
        if not xbmcplugin.addDirectoryItem(self.handle, ka['url'], ka['item'],
                                           is_folder,
                                           self.total_put):
            return False
        self.total_put += 1
        return True

    def close(self):
        """Close our directory
            * close progress dialog ...
        """
        if self.Progress:
            self.Progress.close()
            self.Progress = None

    def end_of_directory(self, forceStatus=None):
        """This will tell xbmc that our plugin has finished, and that
        he can display our items
        """
        success = True
        if forceStatus != None:
            success = forceStatus
        if not self.put_item_ok or (self.total_put == 0):
            success = False
        if not self.asList:
            xbmcplugin.setContent(
                handle=self.handle,
                content=self.content_type)
            xbmcplugin.endOfDirectory(handle=self.handle,
                                      succeeded=success,
                                      updateListing=False,
                                      cacheToDisc=success)
        self.close()
        return self.total_put

    def set_content(self, content):
        """Set Xbmc directory content
        """
        self.content_type = content
