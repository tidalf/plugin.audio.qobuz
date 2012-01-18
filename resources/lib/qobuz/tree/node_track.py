import pprint

import qobuz
from constants import *
from flag import NodeFlag
from node import node
'''
    NODE TRACK
'''
from data.track import QobuzTrack
from utils.tag import QobuzTagTrack
class node_track(node):
    
    def __init__(self, parent = None):
        super(node_track, self).__init__(parent)
        self.type = NodeFlag.TYPE_NODE | NodeFlag.TYPE_TRACK
        
    def _build_down(self, lvl, flag = None):
        self.setLabel("Track ID[" + self.getId() + "] " + self.getLabel())
        if not (flag & NodeFlag.DONTFETCHTRACK):
            o = QobuzTrack(self.id)
            self.setJson(o.get_data())
    
    def get_xbmc_item(self, list):
        t = QobuzTagTrack(self.getJson())
        self.setUrl()
        list.append((self.url, t.getXbmcItem(), True))
        for c in self.childs:
            c.get_xbmc_item(list)