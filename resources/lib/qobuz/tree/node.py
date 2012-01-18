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
from constants import *
from flag import NodeFlag

'''
    NODE
'''
class node(object):
    
    def __init__(self, parent = None):
        self.parent = parent
        self.childs = []
        self.label = ''
        self.label2 = ''
        self.type = NodeFlag.TYPE_NODE
        self.json = None
        self.id = None
        self.url = None
    
    def setUrl(self):
        url = 'plugin://plugin.audio.qobuz/?mode='+str(MODE_NODE)+"&nt="+str(self.type)
        if self.id != None:
            url += "&nid="+str(self.id)
        self.url = url
         
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
        self._build_down(lvl, flag)
        log("Building node: " + self.getLabel())
        for c in self.childs:
            c.build_down(lvl, flag)
            
    def _build_down(self, lvl, flag):
        pass
    
    def count_node(self, flag = NodeFlag.TYPE_NODE):
        total = 0
        if self.type & flag: 
            total = 1
        for c in self.childs:
            total += c.count_node(flag)
        return total

    def get_xbmc_item(self, list):
        for c in self.childs:
            c.get_xbmc_item(list)
        

def log(msg):
        print "TESTNODE: " + msg.encode('ascii', 'ignore') + "\n"
        
        
class test_node():
    
    def __init__(self):
        pass
    
    def run(self):
        from node_userplaylists import node_userplaylists
        log('-'*80+"\n")
        root = node()
        root.setLabel('root')
        root.add_child(node_userplaylists())
        root.build_down(-1, NodeFlag.TYPE_TRACK| NodeFlag.DONTFETCHTRACK)
        log("Total Node          : " + str(root.count_node(NodeFlag.TYPE_NODE)))
        log("Total User Playlists: " + str(root.count_node(NodeFlag.TYPE_USERPLAYLISTS)))
        log("Total PLaylist      : " + str(root.count_node(NodeFlag.TYPE_PLAYLIST)))
        log("Total Track         : " + str(root.count_node(NodeFlag.TYPE_TRACK)))
        log('-'*80+"\n")
        

    
    
    
    
    
    
    
    
    
    
    
    
    
    