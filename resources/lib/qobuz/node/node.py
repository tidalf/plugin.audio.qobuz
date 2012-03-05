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
from constants import Mode
from flag import NodeFlag
from debug import *

'''
    NODE
'''
class Node(object):
    
    def __init__(self, parent = None, parameters = None):
        self.id = None
        self.parameters = parameters
        self.parent = parent
        self.type = NodeFlag.TYPE_NODE
        self.content_type = "files"
        self.icon = ""
        self.thumb = "" 
        self.childs = []
        self.label = ""
        self.label2 = ""
        self.url = None
        self.b_is_folder = True
        self.tag = None
        #self.bfolder = True
       
    def set_is_folder(self, b):
        self.b_is_folder = True if b else False
    def get_cached_data(self):
        warn(self, "get_cached_data must be overloaded!")
        pass
    
    def set_content_type(self, ct):
        self.content_type = ct
        
    def get_content_type(self):
        return self.content_type
    
    def get_thumbnail(self):
        return self.thumb
    
    def get_icon(self):
        return self.icon
    
    def is_folder(self):
        return self.b_is_folder
    
    def to_s(self):
        s = "[Node][" + str(self.type) + "\n"
        s+= "     id: " + str(self.id) + "\n"
        s+= " Label : " + str(self.label) + "\n"
        s+= " label2: " + str(self.label2) + "\n"
        return s
    
    def set_parameters(self, params):
        self.parameters = params
        
    def get_parameter(self, name):
        try:
            return self.parameters[name]
        except: pass
        return None
    
    def set_url(self):
        url = 'plugin://plugin.audio.qobuz2/?mode='+str(Mode.VIEW)+"&nt="+str(self.type)
        if self.tag and self.tag.id != None:
            url += "&nid="+str(self.tag.id)
        self.url = url
    
    def get_url(self):
        if not self.url: self.set_url()
        return self.url
        
    def set_id(self, id):
        self.id = id    
        
    def get_id(self):
        return self.id
        
    def add_child(self, child):
        child.set_parent(self)
        child.set_parameters(self.parameters)
        self.childs.append(child)
    
    def get_childs(self):
        return self.childs

    def get_siblings(self, type):
        list = []
        for c in self.childs:
            if c.getType() == type:
                list.append(c)
        return list
    
    def set_parent(self, parent):
        self.parent = parent
        
    def set_label(self, label):
        self.label = label
        
    def set_label2(self, label):
        self.label2 = label

    def get_label(self):
        return self.label
    
    def get_label2(self):
        return self.label2
    
    def set_type(self, type):
        self.type = type
    
    def get_type(self):
        return self.type
    
    
    '''
        build_down:
        This method fetch data from cache recursively and build our tree
        Node without cached data don't need to overload this method
    '''
    
    def build_down(self, lvl, flag = NodeFlag.TYPE_NODE):
        #info(self, lvl*'#' + ' build_down (' + str(NodeFlag.TYPE_NODE) + ')')
        if lvl != -1 and lvl < 1:
            return True
        #info(self, " - build down hook (pre)")
        self._build_down(lvl, flag)
        if lvl != -1:
            lvl -= 1
        for c in self.childs:
            c.build_down(lvl, flag)

    '''
        _build_down:
        This method is called by build_down method, each object who 
        inherit from node object can implement their own code. Lot of object
        simply fetch data from qobuz (cached data)
    ''' 
    def _build_down(self, lvl, flag):
        ''' Can be overloaded '''
        pass
    
    '''
        get_xbmc_items:
        This method return all xbmc items needed by xbmc.* routines
        We can filter item with flag
    '''
    def get_xbmc_items(self, list, lvl, flag = NodeFlag.TYPE_NODE):
        if lvl != -1 and lvl < 1:
            return True
        if not self._get_xbmc_items(list, lvl, flag):
            return False
        if lvl != -1:
            lvl -= 1
        for c in self.childs:
            if not c.get_xbmc_items(list, lvl, flag):
                return False
        return True
    
    
    '''
        count_node:
        Just a helper function who scan a builded tree and count nodes
    '''
    def count_node(self, flag = NodeFlag.TYPE_NODE):
        total = 0
        if self.type & flag: 
            total = 1
        for c in self.childs:
            total += c.count_node(flag)
        return total
    
    def get_tag_items(self, list, lvl, flag = NodeFlag.TYPE_NODE):
        if lvl != -1 and lvl < 1:
            return True
        self._get_tag_items(list, lvl, flag)
        if lvl != -1:
            lvl -= 1
        for c in self.childs:
            c.get_tag_items(list, lvl, flag)
         
       
    def attach_context_menu(self, item, type, id = None):
        import sys
        color = qobuz.addon.getSetting('color_ctxitem')
        menuItems = []
        
        ''' Show playlist '''
        # addtopl=sys.argv[0]+"?mode="+str(MODE_NODE)+'&nt='+str(NodeFlag.TYPE_USERPLAYLISTS) # Do not work
        # if id: addtopl+='&nid='+id
        # menuItems.append((qobuz.utils.color(color, 'Show Playlist'), "XBMC.RunAddon("+addtopl+")"))
        
#        ''' 
#        Give a chance to our siblings to attach their items
#        '''
        self.hook_attach_context_menu(item, type, id, menuItems, color)
        '''
        Add our items to the context menu
        '''
        if len(menuItems) > 0:
            item.addContextMenuItems(menuItems, replaceItems=False)        
    
    def hook_attach_context_menu(self, item, type, id, menuItems, color):
        pass
    
    def log(msg):
        print "TESTNODE: " + msg.encode('ascii', 'ignore') + "\n"
        
        
#class test_node():
#    
#    def __init__(self):
#        pass
#    
#    def run(self):
#        from node_userplaylists import node_userplaylists
#        log('-'*80+"\n")
#        root = node()
#        root.set_label('root')
#        root.add_child(node_userplaylists())
#        root.build_down(-1, NodeFlag.TYPE_TRACK| NodeFlag.DONTFETCHTRACK)
#        log("Total Node          : " + str(root.count_node(NodeFlag.TYPE_NODE)))
#        log("Total User Playlists: " + str(root.count_node(NodeFlag.TYPE_USERPLAYLISTS)))
#        log("Total PLaylist      : " + str(root.count_node(NodeFlag.TYPE_PLAYLIST)))
#        log("Total Track         : " + str(root.count_node(NodeFlag.TYPE_TRACK)))
#        log('-'*80+"\n")
#        
