#     Copyright 2011 Joachim Basmaison, Cyril Leclerc
#
#     This file is part of xbmc-qobuz.
#
#     xbmc-qobuz is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     xbmc-qobuz is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.   See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with xbmc-qobuz.   If not, see <http://www.gnu.org/licenses/>.
import pprint
import qobuz

class __NodeFlag():
    def __init__(self): 
        self.DONTFETCHTRACK = 1
        self.TYPE_NODE = 512
        self.TYPE_TRACK = 1024
        self.TYPE_PLAYLIST = 2048
        self.TYPE_USERPLAYLISTS = 4096

NodeFlag = __NodeFlag()

'''
    NODE
'''
class Node(object):
    
    def __init__(self, parent = None):
        self.parent = parent
        self.childs = []
        self.label = ''
        self.label2 = ''
        self.type = NodeFlag.TYPE_NODE
        self.json = None
        self.id = None
    
    def setId(self, id):
        self.id = id
        
    def getId(self):
        return self.id
    
    def add_child(self, child):
        child.setParent(self)
        self.childs.append(child)
        
    def setParent(self, parent):
        self.parent = parent
        
    def setLabel(self, label):
        self.label = label
        
    def setLabel2(self, label):
        self.label2 = label

    def getLabel(self):
        return self.label
    
    def getLabel2(self):
        return self.label2
    
    def setJson(self, json):
        self.json = json
    
    def getJson(self):
        return self.json
    
    def setType(self, type):
        self.type = type
    
    def getType(self):
        return self.type
        
    def build_down(self, lvl, flag = NodeFlag.TYPE_NODE):
        if self.type & flag:
            log("Stop building on flag...")
        if lvl != -1 and lvl < 1:
            log("Stop building with " + self.getLabel())
            return True
        if lvl != -1:
            lvl -= 1
        log("Building node: " + self.getLabel())
        for c in self.childs:
            c.build_down(lvl, flag)
    
    def count_node(self, flag = NodeFlag.TYPE_NODE):
        total = 0
        if self.type & flag: 
            total = 1
        for c in self.childs:
            total += c.count_node(flag)
        return total

'''
    NODE TRACK
'''
from data.track import QobuzTrack
class Node_track(Node):
    
    def __init__(self, parent = None):
        super(Node_track, self).__init__(parent)
        self.type = NodeFlag.TYPE_NODE | NodeFlag.TYPE_TRACK
        
    def build_down(self, lvl, flag = None):
        self.setLabel("Track ID[" + self.getId() + "] " + self.getLabel())
        if not (flag & NodeFlag.DONTFETCHTRACK):
            o = QobuzTrack(self.id)
            self.setJson(o.get_data())
        super(Node_track, self).build_down(lvl, flag)

'''
    NODE PLAYLIST
'''
from view.playlist import QobuzPlaylist
class Node_playlist(Node):
    
    def __init__(self, parent = None):
        super(Node_playlist, self).__init__(parent)
        self.type = NodeFlag.TYPE_NODE | NodeFlag.TYPE_PLAYLIST
        
    def build_down(self, lvl, flag = None):
        self.setLabel("Playlist ID: " + self.getId())
        o = QobuzPlaylist(self.id)
        self.setJson(o.get_data())
        for track in self.getJson()['tracks']:
            c = Node_track()
            c.setId(track['id'])
            c.setLabel(track['title'])
            self.add_child(c)
        super(Node_playlist, self).build_down(lvl, flag)

'''
    NODE USER PLAYLISTS
'''
from view.userplaylists import QobuzUserPlaylists
class Node_userplaylists(Node):
    
    def __init__(self, parent = None):
        super(Node_userplaylists, self).__init__(parent)
        self.label  = 'User Playlists'
        self.label2 = 'Keep your current playlist'
        self.type = NodeFlag.TYPE_NODE | NodeFlag.TYPE_USERPLAYLISTS
    
    
    def build_down(self, lvl, flag = None):
        o = QobuzUserPlaylists(qobuz.api, qobuz.path.cache, -1)
        self.setJson(o.get_data())
        pprint.pprint(self.getJson())
        for playlist in self.getJson():
            pprint.pprint(playlist)
            c = Node_playlist()
            c.setId(playlist['id'])
            c.setLabel(playlist['name'])
            self.add_child(c)
        super(Node_userplaylists, self).build_down(lvl, flag)


def log(msg):
    print "TESTNODE: " + msg.encode('ascii', 'ignore') + "\n"
        
        
class test_node():
    
    def __init__(self):
        pass
    
    def run(self):
        log('-'*80+"\n")
        root = Node()
        root.setLabel('root')
        root.add_child(Node_userplaylists())
        root.build_down(-1, NodeFlag.TYPE_TRACK| NodeFlag.DONTFETCHTRACK)
        log("Total Node          : " + str(root.count_node(NodeFlag.TYPE_NODE)))
        log("Total User Playlists: " + str(root.count_node(NodeFlag.TYPE_USERPLAYLISTS)))
        log("Total PLaylist      : " + str(root.count_node(NodeFlag.TYPE_PLAYLIST)))
        log("Total Track         : " + str(root.count_node(NodeFlag.TYPE_TRACK)))
        log('-'*80+"\n")
        

    
    
    
    
    
    
    
    
    
    
    
    
    
    