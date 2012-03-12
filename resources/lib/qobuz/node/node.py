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
        #print "Get property: " + repr(path)
#        print "type: " + str(type(path))
        if not self._data:
            return ''

        if isinstance(path, basestring):
         #   print "Got a string not tuple"
            if path in self._data and self._data[path] and self._data[path] != 'None':
                return self._data[path].encode('utf8', 'ignore')
            return ''

        root = self._data
        for i in range(0, len(path)):
#            print "root: " + repr(root)
#            print "PAth: " + path[i]
            if not path[i] in root:
                return ''
            root = root[path[i]]

        if root and root != 'None':
#            print "Return: " + repr(root)
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
        return url
    
    def make_XbmcListItem(self):
        import xbmcgui
        item = xbmcgui.ListItem(
                                    self.get_label(),
                                    self.get_label2(),
                                    self.get_image(),
                                    self.get_image(),
                                    self.get_url()
                                    )
        id = self.get_id()
        if id: id = str(id)
        else: id = ''
        item.setProperty('node_id', id)
        item.setProperty('IsFolder', 'true' if self.is_folder() else 'false')
        item.setIconImage(self.get_icon())
        item.setThumbnailImage(self.get_thumbnail())
        return item
    
    def set_url(self, url):
      self.url = url
      return self.url
    
    def get_url(self, mode = Mode.VIEW):
        return self.set_url(self.make_url(mode))

    def set_id(self, id):
        self.id = id

    def get_id(self):
        if self._data and 'id' in self._data and self._data:
            return self._data['id']
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

    def set_label(self, label):
        self.label = label
    
    def set_image(self, image):
        self.thumb = self.icon = image
    
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


    def filter(self, flag):
        if not flag: 
            #print "No flag: accept item"
            return False
        if flag & self.get_type(): 
            #print "FLAG is ok: accept item"
            return False
        #print "FLAG fail: removing item"
        return True

    '''
        build_down:
        This method fetch data from cache recursively and build our tree
        Node without cached data don't need to overload this method
    '''

    def build_down(self, lvl, flag = NodeFlag.TYPE_NODE, progress = None):
        #info(self, lvl*'#' + ' build_down (' + str(NodeFlag.TYPE_NODE) + ')')
        if lvl != -1 and lvl < 1:
            return True
        #info(self, " - build down hook (pre)")
        if progress: 
            progress.inc_buildcount()
            progress.update(50, "2/4 Discover trees: " + str(progress.buildcount))
        self._build_down(lvl, flag)
        if lvl != -1: lvl -= 1
        for c in self.childs:
            c.build_down(lvl, flag, progress)

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
            return False
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


    def attach_context_menu(self, item, node):
        import urllib
        color = qobuz.addon.getSetting('color_ctxitem')
        menuItems = []
        
        ''' ERASE CACHE '''
        erasecache=sys.argv[0]+"?mode="+str(Mode.ERASE_CACHE)
        menuItems.append((qobuz.utils.color(color, qobuz.lang(31009)), "XBMC.RunPlugin("+erasecache+")"))
        
        ''' SCAN '''
        node_url = urllib.quote(node.make_url(Mode.VIEW))
        url = sys.argv[0] + "?mode="+str(Mode.LIBRARY_SCAN) + "&url=" + node_url
        menuItems.append((qobuz.utils.color(color, "Scan"), "XBMC.RunPlugin("+url+")"))                                                             
        
        ''' SCAN DIR '''
        node_url = urllib.quote(self.make_url(Mode.VIEW))
        url = sys.argv[0] + "?mode="+str(Mode.LIBRARY_SCAN) + "&url=" + node_url
        menuItems.append((qobuz.utils.color(color, "Scan dir"), "XBMC.RunPlugin("+url+")"))                                                             
        
        if 1: #node.type & NodeFlag.TYPE_PLAYLIST: 
            '''
                This album 
            '''
            id = node.get_property(('album', 'id'))
            args = sys.argv[0] + '?mode=%i&nt=%i&nid=%s' % (Mode.VIEW, 
                                         NodeFlag.TYPE_PRODUCT, 
                                         id
                                         )
            cmd = "XBMC.Container.Update(%s)" % (args)  
            menuItems.append((qobuz.utils.color(color, qobuz.lang(39000)), cmd))
            
        if node.type & (NodeFlag.TYPE_PRODUCT | NodeFlag.TYPE_TRACK | NodeFlag.TYPE_ARTIST): 
            '''
                All album
            '''
            id = node.get_artist_id()
            args = sys.argv[0] + '?mode=%i&nt=%i&nid=%s' % (Mode.VIEW, 
                                         NodeFlag.TYPE_ARTIST, 
                                         id
                                         )
            cmd = "XBMC.Container.Update(%s)" % (args)  
            menuItems.append((qobuz.utils.color(color, qobuz.lang(39001)), cmd))
            
            '''
                Similar artist
            '''
            id = node.get_artist_id()
            query = urllib.quote(node.get_artist())
            args = sys.argv[0] + '?mode=%i&nt=%i&nid=%s&query=%s' % (Mode.VIEW, 
                                         NodeFlag.TYPE_SIMILAR_ARTIST, 
                                         id, query
                                         )
            cmd = "XBMC.Container.Update(%s)" % (args)
            menuItems.append((qobuz.utils.color(color, "Similar artist"), cmd))
        
        args = sys.argv[0] + "?mode=" + str(Mode.ADD_TO_CURRENT_PLAYLIST) + "&nt=" + str(node.get_type())
        if node.get_id(): args += "&nid=" + str(node.get_id())
        genre_type = node.get_parameter('genre-type')
        genre_id = node.get_parameter('genre-id')
        if genre_type: cmd += "&genre-type=" + genre_type
        if genre_id: cmd += "&genre-id=" + genre_id
        cmd = "XBMC.Container.Update(%s)" % (args)
        menuItems.append((qobuz.utils.color(color, 'Add to current playlist'), cmd))
        
        ''' Show playlist '''
        showplaylist=sys.argv[0]+"?mode="+str(Mode.VIEW)+'&nt='+str(NodeFlag.TYPE_USERPLAYLISTS) 
        menuItems.append((qobuz.utils.color(color, 'Show Playlist'), "XBMC.Container.Update("+showplaylist+")"))
        
#        ''' 
#        Give a chance to our siblings to attach their items
#        '''
        self.hook_attach_context_menu(item, node, menuItems, color)
        '''
        Add our items to the context menu
        '''
        if len(menuItems) > 0:
            item.addContextMenuItems(menuItems, replaceItems = False)

    def hook_attach_context_menu(self, item, node, menuItems, color):
        pass
  
    def _get_keyboard(self, default = "", heading = "", hidden = False):
        import xbmc
        kb = xbmc.Keyboard(default, heading, hidden)
        kb.doModal()
        if (kb.isConfirmed()):
            return unicode(kb.getText(), "utf-8")
        return ''
