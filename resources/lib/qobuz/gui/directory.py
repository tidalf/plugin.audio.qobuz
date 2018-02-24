'''
    qobuz.gui.directory
    ~~~~~~~~~~~~~~~~~~~

    :part_of: xbmc-qobuz
    :copyright: (c) 2012-2016 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
import time

import xbmcgui
import xbmcplugin

from qobuz import debug
from qobuz.gui.bg_progress import Progress
from qobuz.gui.util import lang
from qobuz.node import Flag


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
                 nodes=[],
                 handle=None,
                 asList=False,
                 asLocalUrl=False,
                 showProgress=False):
        self.nodes = nodes
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
        self.filter_double = Flag.TRACK
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
                    self.progress.update(message='Skip node type: %s' % Flag.to_s(node.nt) )
                    return True
                self.seen_nodes[node.nid] = 1
        try:
           self.progress.update(message=node.get_label().encode('ascii'))
        except:
           pass
        if self.asList is True:
            self.nodes.append(node)
            self.total_put += 1
            return True
        return self.__add_node(node)

    def __add_node(self, node):
        item = node.makeListItem(replaceItems=self.replaceItems)
        if item is None:
            return False
        url = node.make_url(asLocalUrl=self.asLocalUrl)
        if not self.add_to_xbmc_directory(
                url=url, item=item, is_folder=node.is_folder):
            self.put_item_ok = False
            return False
        return True

    def add_to_xbmc_directory(self, is_folder=False, item=None, url=None,
                              **ka):
        if not xbmcplugin.addDirectoryItem(self.handle, url, item, is_folder,
                                           self.total_put):
            return False
        self.total_put += 1
        return True

    def end_of_directory(self, forceStatus=None):
        if self.seen_nodes:
            self.seen_nodes = {}
        success = True
        if forceStatus != None:
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
