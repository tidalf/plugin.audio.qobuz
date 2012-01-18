import sys
import pprint

import xbmcplugin

import qobuz
from flag import NodeFlag
from debug import info

class renderer():
    
    def __init__(self, node_type, node_id = None, flag = 0):
        self.node_type = node_type
        self.node_id = node_id
        self.flag = flag
        self.root = None
    
    def to_s(self):
        s = "Node type: " + str(self.node_type) + "\n"
        s+= "Node id  : " + str(self.node_id) + "\n"
        s+= "Flag     : " + str(self.flag) + "\n"
        if self.root:
            s+= self.root.to_s()
        return s
    
    def set_root_node(self):
        if self.node_type & NodeFlag.TYPE_USERPLAYLISTS:
            from node_userplaylists import node_userplaylists
            self.root = node_userplaylists()
        elif self.node_type & NodeFlag.TYPE_PLAYLIST:
            from node_playlist import node_playlist
            self.root = node_playlist()
        else:
            return False
        self.root.setId(self.node_id)
        return True
    
    def display(self):
        if not self.set_root_node():
            print "Cannot set root node (" + str(self.node_type) + ", " + str(self.node_id) + ")"
            return False
        self.root.build_down(1, 0)
        list = []
        info(self, self.to_s())
        self.root.get_xbmc_item(list)
        size = len(list)
        xbmcplugin.addDirectoryItems(handle=int(sys.argv[1]), items=list, totalItems=size)
        xbmcplugin.endOfDirectory(handle=qobuz.boot.handle, succeeded=True, updateListing=False, cacheToDisc=True)
        