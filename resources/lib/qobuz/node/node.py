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
import sys
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
        self._data = None
        self.id = None

        
    def set_data(self, data):
        self._data = data

    def get_data(self):
        return self._data
    
    def fetch_data(self):
        if not self.cache: return None
        return self.cache.fetch_data()
    
    def get_property(self, path):
        if not self._data:
            return ''
        if isinstance(path, basestring):
            if path in self._data and self._data[path] and self._data[path] != 'None':
                return self._data[path].encode('utf8', 'ignore')
            return ''
        root = self._data
        for i in range(0, len(path)):
            if not path[i] in root:
                return ''
            root = root[path[i]]
        if root and root != 'None':
            return root.encode('utf8', 'replace')
        return ''

    def set_is_folder(self, b):
        self.b_is_folder = True if b else False

    def set_content_type(self, ct):
        self.content_type = ct

    def get_content_type(self):
        return self.content_type

    def get_thumbnail(self):
        return self.thumb

    def get_image(self):
        if self.thumb: return self.thumb
        return self.icon
    
    def get_icon(self):
        return self.icon

    def is_folder(self):
        return self.b_is_folder

    def to_s(self):
        s = "[Node][" + str(self.type) + "\n"
        s += " id: " + str(self.id) + "\n"
        s += " Label : " + str(self.label) + "\n"
        s += " label2: " + str(self.label2) + "\n"
        data = self.get_data()
        if data:
            s+= 'data:' + pprint.pformat(data)
        return s

    def set_parent(self, parent):
        self.parent = parent
        
    def get_parent(self):
        return self.parent
    
    def set_parameters(self, params):
        self.parameters = params

    def set_parameter(self, name, value):
        self.parameters[name] = value
        
    def get_parameter(self, name):
        try:
            return self.parameters[name]
        except: pass
        return None

    def make_url(self, mode = Mode.VIEW):
        url = sys.argv[0] + '?mode=' + str(mode) + "&nt=" + str(self.type)
        id = self.get_id()
        if id and id != 'None': url += "&nid=" + str(id)
        action = self.get_parameter('action')
        if action == 'scan': 
            url += "&action=scan"
        return url
    
    def make_XbmcListItem(self):
        import xbmcgui
        item = xbmcgui.ListItem(
                                    self.get_label(),
                                    self.get_label2(),
                                    self.get_image(),
                                    self.get_image(),
                                    self.make_url()
                                    )
        id = self.get_id()
        if id: id = str(id)
        else: id = ''
        item.setProperty('node_id', id)
        item.setProperty('IsFolder', 'true' if self.is_folder() else 'false')
        item.setIconImage(self.get_icon())
        item.setThumbnailImage(self.get_thumbnail())
        self.attach_context_menu(item)
        return item
    
    def set_url(self, url):
        self.url = url
        return self
    
    def get_url(self, mode = Mode.VIEW):
        return self.url

    def set_id(self, id):
        self.id = id
        return self
    
    def get_id(self):
        if self._data and 'id' in self._data and self._data:
            return self._data['id']
        return self.id

    def add_child(self, child):
        child.set_parent(self)
        child.set_parameters(self.parameters)
        self.childs.append(child)
        return self
    
    def get_childs(self):
        return self.childs

    def get_siblings(self, type):
        list = []
        for c in self.childs:
            if c.getType() == type:
                list.append(c)
        return list

    def set_label(self, label):
        self.label = label.encode('utf8', 'replace')
        return self
    
    def set_image(self, image):
        self.thumb = self.icon = image
        return self
    
    def set_label2(self, label):
        self.label2 = label.encode('utf8', 'replace')
        return self
    
    def get_label(self):
        return self.label

    def get_label2(self):
        return self.label2

    def set_type(self, type):
        self.type = type

    def get_type(self):
        return self.type


    def filter(self, flag):
        if not flag: 
            return False
        if flag & self.get_type(): 
            return False
        return True
        
    '''
        build_down:
        This method fetch data from cache recursively and build our tree
        Node without cached data don't need to overload this method
    '''

    def build_down(self, xbmc_directory, lvl = 1, whiteFlag = NodeFlag.TYPE_NODE):
        if xbmc_directory.is_canceled():
            return False
        if lvl != -1 and lvl < 1:
            return False
        self._build_down(xbmc_directory, lvl, whiteFlag)
        if lvl != -1: lvl -= 1
        xbmc_directory.set_given_total(len(self.childs))
        for child in self.childs:
            if child.type & whiteFlag:
                xbmc_directory.add_node(child)
            if child.build_down(xbmc_directory, lvl, whiteFlag):
                xbmc_directory.update(50, "Fetching Data (cache / network)", child.get_label())    
        return True

    '''
        _build_down:
        This method is called by build_down method, each object who 
        inherit from node object can implement their own code. Lot of object
        simply fetch data from qobuz (cached data)
    '''
    def _build_down(self, xbmc_directory, lvl, flag):
        ''' Can be overloaded '''
        pass


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


    def attach_context_menu(self, item):
        import urllib
        color = qobuz.addon.getSetting('color_ctxitem')
        menuItems = []
        cmd = ''
        ''' VIEW BIG DIR '''
        
        path = self.make_url(Mode.VIEW_BIG_DIR)
        label = "View big dir"
        menuItems.append(( qobuz.utils.color(color, label), "XBMC.Container.Update(%s)" % (path) ))
        
        
        ''' SCAN '''
        path = xbmc.getInfoLabel('ListItem.Path')
        node_url = urllib.quote(self.make_url(Mode.SCAN))
        url = sys.argv[0] + "?mode="+str(Mode.LIBRARY_SCAN) + "&url=" + node_url
        label = "Scan"
        menuItems.append((qobuz.utils.color(color, label), "XBMC.RunPlugin("+url+")"))                                                             
        
        ''' SCAN DIR '''
#        path = xbmc.getInfoLabel('Container.FolderPath') 
#        node_url = urllib.quote(path)#self.make_url(Mode.VIEW))
#        url = sys.argv[0] + "?mode="+str(Mode.LIBRARY_SCAN) + "&url=" + node_url
#        label = "Scan dir: " + path 
#        menuItems.append(( qobuz.utils.color(color, label), 'XBMC.RunPlugin("%s")' % (url) ))                                                         
        if self.type & NodeFlag.TYPE_PLAYLIST: 
            '''
                This album 
            '''
            id = self.get_property(('album', 'id'))
            args = sys.argv[0] + '?mode=%i&nt=%i&nid=%s' % (Mode.VIEW, 
                                         NodeFlag.TYPE_PRODUCT, 
                                         id
                                         )
            cmd = "XBMC.Container.Update(%s)" % (args)  
            menuItems.append((qobuz.utils.color(color, qobuz.lang(39000)), cmd))
            
        if self.type & (NodeFlag.TYPE_PRODUCT | NodeFlag.TYPE_TRACK | NodeFlag.TYPE_ARTIST): 
            '''
                All album
            '''
            id = self.get_artist_id()
            args = sys.argv[0] + '?mode=%i&nt=%i&nid=%s' % (Mode.VIEW, 
                                         NodeFlag.TYPE_ARTIST, 
                                         id
                                         )
            cmd = "XBMC.Container.Update(%s)" % (args)  
            menuItems.append((qobuz.utils.color(color, qobuz.lang(39001)), cmd))
            
            '''
                Similar artist
            '''
            id = self.get_artist_id()
            query = urllib.quote(self.get_artist())
            args = sys.argv[0] + '?mode=%i&nt=%i&nid=%s&query=%s' % (Mode.VIEW, 
                                         NodeFlag.TYPE_SIMILAR_ARTIST, 
                                         id, query
                                         )
            cmd = "XBMC.Container.Update(%s)" % (args)
            menuItems.append((qobuz.utils.color(color, "Similar artist"), cmd))
        
        args = sys.argv[0] + "?mode=" + str(Mode.ADD_TO_CURRENT_PLAYLIST) + "&nt=" + str(self.get_type())
        if self.get_id(): args += "&nid=" + str(self.get_id())
        genre_type = self.get_parameter('genre-type')
        genre_id = self.get_parameter('genre-id')
        if genre_type: cmd += "&genre-type=" + genre_type
        if genre_id: cmd += "&genre-id=" + genre_id
        cmd = "XBMC.Container.Update(%s)" % (args)
        menuItems.append((qobuz.utils.color(color, 'Add to current playlist'), cmd))
        
        ''' Show playlist '''
        if not (self.get_type() & NodeFlag.TYPE_PLAYLIST):
            showplaylist=sys.argv[0]+"?mode="+str(Mode.VIEW)+'&nt='+str(NodeFlag.TYPE_USERPLAYLISTS) 
            menuItems.append((qobuz.utils.color(color, 'Show Playlist'), "XBMC.Container.Update("+showplaylist+")"))
        
        ''' ERASE CACHE '''
        color = qobuz.addon.getSetting('color_ctxitem_caution')
        erasecache=sys.argv[0]+"?mode="+str(Mode.ERASE_CACHE)
        menuItems.append((qobuz.utils.color(color, qobuz.lang(31009)), "XBMC.RunPlugin("+erasecache+")"))
#        ''' 
#        Give a chance to our siblings to attach their items
#        '''
        #self.hook_attach_context_menu(item, node, menuItems, color)
        '''
        Add our items to the context menu
        '''
        if len(menuItems) > 0:
            item.addContextMenuItems(menuItems, replaceItems = False)

    def hook_attach_context_menu(self, item, menuItems, color):
        pass
  
    def _get_keyboard(self, default = "", heading = "", hidden = False):
        import xbmc
        kb = xbmc.Keyboard(default, heading, hidden)
        kb.doModal()
        if (kb.isConfirmed()):
            return unicode(kb.getText(), "utf-8")
        return ''
