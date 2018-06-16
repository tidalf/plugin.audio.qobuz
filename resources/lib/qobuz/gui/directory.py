'''
    qobuz.gui.directory
    ~~~~~~~~~~~~~~~~~~~

    :part_of: kodi-qobuz
    :copyright: (c) 2012-2018 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
import time

from kodi_six import xbmcplugin  # pylint:disable=E0401

from qobuz.debug import getLogger
from qobuz.gui.bg_progress import Progress
from qobuz.node import Flag

logger = getLogger(__name__)


class Directory(object):
    '''This class permit to add item to Xbmc directory or store nodes
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
    '''

    def __init__(self,
                 root=None,
                 nodes=None,
                 handle=None,
                 asList=False,
                 asLocalUrl=False,
                 showProgress=False):
        self.nodes = [] if nodes is None else nodes
        self.label = '...'
        if root is not None:
            self.label = '%s' % root.get_label()
        self.root = root
        self.asList = asList
        self.handle = handle
        self.put_item_ok = True
        self.total_put = 0
        self.started_on = time.time()
        self.content_type = 'files'
        self.replaceItems = False
        self.asLocalUrl = asLocalUrl
        self.filter_double = Flag.TRACK | Flag.ALBUM
        self.seen_nodes = {}
        self.progress = Progress(
            heading='Qobuz', message=self.label, enable=showProgress)

    def __enter__(self, *a, **ka):
        return self

    def elapsed(self):
        return time.time() - self.started_on

    def add_node(self, node):
        if self.filter_double is not None:
            if self.filter_double & node.nt == node.nt:
                if node.nid in self.seen_nodes:
                    self.progress.update(
                        message='Skip node type: %s' % Flag.to_s(node.nt))
                    return True
                self.seen_nodes[node.nid] = 1
        try:
            self.progress.update(message=node.get_label())
        except Exception as e:
            logger.warn('ProgressUpdateError %s', e)
        self.nodes.append(node)
        self.total_put += 1
        return True

    def _add_all_items(self):
        self.put_item_ok = True
        if self.asList:
            return True
        if not xbmcplugin.addDirectoryItems(self.handle, [(
            node.make_url(),
            node.makeListItem(
                replaceItems=self.replaceItems),
            node.is_folder
        ) for node in self.nodes], False):
            return False
        return True

    def add_to_xbmc_directory(self, is_folder=False, item=None, url=None,
                              **ka):
        if not xbmcplugin.addDirectoryItem(self.handle, url, item, is_folder,
                                           self.total_put):
            return False
        self.total_put += 1
        self.put_item_ok = True
        return True

    def end_of_directory(self, forceStatus=None):
        self._add_all_items()
        if self.seen_nodes:
            self.seen_nodes = {}
        success = True
        if forceStatus is not None:
            success = forceStatus
        if not self.put_item_ok or self.total_put == 0:
            success = False
        if not self.asList:
            xbmcplugin.setContent(
                handle=self.handle, content=self.content_type)
            xbmcplugin.endOfDirectory(
                handle=self.handle,
                succeeded=success,
                updateListing=False,
                cacheToDisc=success)
        return self.total_put

    def __exit__(self, *a, **ka):
        self.progress.update(percent=100, message='finished')
        self.progress.close()

    def set_content(self, content):
        self.content_type = content
