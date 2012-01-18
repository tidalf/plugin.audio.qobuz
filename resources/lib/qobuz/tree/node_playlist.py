import pprint

import qobuz
from constants import *
from flag import NodeFlag
from node import node
from debug import info
'''
    NODE PLAYLIST
'''
from data.playlist import QobuzPlaylist
from utils.tag import QobuzTagPlaylist
from node_track import node_track

class node_playlist(node):
    
    def __init__(self, parent = None):
        super(node_playlist, self).__init__(parent)
        self.type = NodeFlag.TYPE_NODE | NodeFlag.TYPE_PLAYLIST
        
    def _build_down(self, lvl, flag = None):
        self.setLabel("Playlist ID: " + str(self.getId()))
        o = QobuzPlaylist(self.id)
        self.setJson(o.get_data())
        data = self.getJson()
        if not data:
            return False
        for track in self.getJson()['tracks']:
            c = node_track()
            c.setId(track['id'])
            c.setLabel(track['title'])
            self.add_child(c)
        return True
    def get_xbmc_item(self, list):
        t = QobuzTagPlaylist(self.getJson())
        self.setUrl()
        list.append((self.url, t.getXbmcItem(), True))
        for c in self.childs:
            c.get_xbmc_item(list)