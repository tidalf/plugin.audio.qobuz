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

import xbmcgui
        
import qobuz
from constants import Mode
from flag import NodeFlag
from debug import *
import weakref

'''
    NODE
'''
class Node(object):

    def __init__(self,parent=None,parameters=None):
        self.parameters = parameters
        self.id = None
        self.parent = None
        self.set_parent(parent)
        self.type = NodeFlag.TYPE_NODE
        self.content_type = "files"
        self.image = None
        self.childs = []
        self.label = ""
        self.label2 = ""
        self.is_folder = True
        self._data = None
      
    def delete_tree(self):
        for child in self.childs:
            child.delete_tree()
        del self.childs
        del self.parent
        del self.parameters
      
    def set_data(self,data):
        self._data = data

    def get_data(self):
        return self._data

    def get_property(self,path):
        if not self._data:
            return ''
        if isinstance(path,basestring):
            if path in self._data and self._data[path] and self._data[path] != 'None':
                return self._data[path] 
            return ''
        root = self._data
        for i in range(0,len(path)):
            if not path[i] in root:
                return ''
            root = root[path[i]]
        if root and root != 'None':
            return root 
        return ''

    def set_is_folder(self,b):
        self.is_folder = True if b else False

    def set_content_type(self,ct):
        self.content_type = ct

    def get_content_type(self):
        return self.content_type

    def get_image(self):
        if self.image: return self.image
        if self.parent: return self.parent.get_image()
        return ''

    def to_s(self):
        s = "[Node][" + str(self.type) + "\n"
        s += " id: " + str(self.id) + "\n"
        s += " Label : " + str(self.label) + "\n"
        s += " label2: " + str(self.label2) + "\n"
        data = self.get_data()
        if data:
            s += 'data:' + pprint.pformat(data)
        return s

    def set_parent(self,parent):
        if not parent: return 
        self.parent = weakref.proxy(parent)

    def get_parent(self):
        return self.parent

    '''
        Parameters 
        A hash for storing script parameter, each node have a copy of them.
        TODO: each node don't need to copy parameter
    '''
    def set_parameters(self,params):
        self.parameters = params

    def set_parameter(self,name,value):
        self.parameters[name] = value

    def get_parameter(self,name):
        try:
            return self.parameters[name]
        except: pass
        return None

    '''
        Make url
        This function is responsible to create the link to this node.
        Class who implement custom parameter must overload this method
    '''
    def make_url(self,mode=Mode.VIEW):
        url = sys.argv[0] + '?mode=' + str(mode) + "&nt=" + str(self.type)
        id = self.get_id()
        if id and id != 'None': url += "&nid=" + str(id)
        action = self.get_parameter('action')
        if action == 'scan':
            url += "&action=scan"
        return url

    '''
        Make Xbmc List Item
        return  a xbml list item
        Class can overload this method
    '''
    def make_XbmcListItem(self):
        image = self.get_image()
        item = xbmcgui.ListItem(
                                    self.get_label(),
                                    self.get_label2(),
                                    image,
                                    image,
                                    self.make_url()
                                    )
        self.attach_context_menu(item)
        return item

    def get_url(self,mode=Mode.VIEW):
        return self.make_url(mode)

    def set_id(self,id):
        self.id = id
        return self

    '''
        WE don't convert id to int because qobuz store album id
        with with zero in front of them
        TODO: check id consistency
    '''
    def get_id(self):
        if self._data and 'id' in self._data:
            return self._data['id']
        return self.id

    def add_child(self,child):
        child.set_parent(self)
        child.set_parameters(self.parameters)
        self.childs.append(child)
        return self

    def get_childs(self):
        return self.childs

    def get_siblings(self,type):
        list = []
        for c in self.childs:
            if c.getType() == type:
                list.append(c)
        return list

    def set_label(self,label):
        self.label = label.encode('utf8','replace')
        return self

    def set_image(self,image):
        self.image = image
        return self

    def set_label2(self,label):
        self.label2 = label.encode('utf8','replace')
        return self

    def get_label(self):
        return self.label

    def get_label2(self):
        return self.label2

    def set_type(self,type):
        self.type = type

    def get_type(self):
        return self.type


    def filter(self,flag):
        if not flag:
            return False
        if flag & self.get_type():
            return False
        return True

    # When returning False we are not displaying directory content
    def pre_build_down(self):
        return True
    '''
        build_down:
        This method fetch data from cache recursively and build our tree
        Node without cached data don't need to overload this method
    '''

    def build_down(self,xbmc_directory,lvl=1,whiteFlag=NodeFlag.TYPE_NODE):
        if xbmc_directory.is_canceled():
            return False
        if lvl != -1 and lvl < 1:
            return False
        self._build_down(xbmc_directory,lvl,whiteFlag)
        if lvl != -1: lvl -= 1
        total = len(self.childs)
        count = 0
        label = self.get_label()
        for child in self.childs:
            if not (child.type & NodeFlag.TYPE_TRACK):
                xbmc_directory.update(count, total, "Working", label, child.get_label())
            if child.type & whiteFlag:
                xbmc_directory.add_node(child)
            child.build_down(xbmc_directory,lvl,whiteFlag)
            count += 1
        return True

    '''
        _build_down:
        This method is called by build_down method, each object who 
        inherit from node object can implement their own code. Lot of object
        simply fetch data from qobuz (cached data)
    '''
    def _build_down(self,xbmc_directory,lvl,flag):
        pass

    def help_make_url(self,mode,nt,nid):
        return '%s?mode=%i&nt=%i&nid=%s' % (sys.argv[0],mode,nt,nid)

    def attach_context_menu(self,item):
        color = qobuz.addon.getSetting('color_item')
        menuItems = []
        cmd = ''

        ''' VIEW BIG DIR '''
        path = self.make_url(Mode.VIEW_BIG_DIR)
        label = qobuz.lang(39002)
        menuItems.append((qobuz.utils.color(color,label),"XBMC.Container.Update(%s)" % (path)))


        if self.type & (NodeFlag.TYPE_PRODUCT | NodeFlag.TYPE_TRACK | NodeFlag.TYPE_ARTIST):
            ''' ALL ALBUM '''
            id = self.get_artist_id()
            url = self.help_make_url(Mode.VIEW,NodeFlag.TYPE_ARTIST,id)
            cmd = "XBMC.Container.Update(%s)" % (url)
            menuItems.append((qobuz.utils.color(color,qobuz.lang(39001)),cmd))

            ''' Similar artist '''
            id = self.get_artist_id()
            import urllib
            query = urllib.quote(self.get_artist().encode('utf-8'))
            args = sys.argv[0] + '?mode=%i&nt=%i&nid=%s&query=%s' % (Mode.VIEW,
                                         NodeFlag.TYPE_SIMILAR_ARTIST,
                                         id,id)
            cmd = "XBMC.Container.Update(%s)" % (args)
            menuItems.append((qobuz.utils.color(color, qobuz.lang(39004)),cmd))

        ''' ADD TO CURRENT PLAYLIST '''
        cmd = "XBMC.Container.Update(%s)" % (self.make_url(Mode.PLAYLIST_ADD_TO_CURRENT))
        menuItems.append((qobuz.utils.color(color,qobuz.lang(39005)),cmd))

        ''' ADD TO FAVORITES '''
        cmd = "XBMC.Container.Update(%s)" % (self.make_url(Mode.FAVORITES_ADD_TO_CURRENT))
        menuItems.append((qobuz.utils.color(color,qobuz.lang(39011)),cmd))

        ''' ADD AS NEW '''
        cmd = "XBMC.Container.Update(%s)" % (self.make_url(Mode.PLAYLIST_ADD_AS_NEW))
        menuItems.append((qobuz.utils.color(color, qobuz.lang(30080)),cmd))
        
        ''' Show playlist '''
        if not (self.type & NodeFlag.TYPE_PLAYLIST):
            showplaylist = sys.argv[0] + "?mode=" + str(Mode.VIEW) + '&nt=' + str(NodeFlag.TYPE_USERPLAYLISTS)
            menuItems.append((qobuz.utils.color(color, qobuz.lang(39006)),"XBMC.Container.Update(" + showplaylist + ")"))

        if self.type & NodeFlag.TYPE_USERPLAYLISTS:
            ''' CREATE '''
            url = self.make_url(Mode.PLAYLIST_CREATE)
            menuItems.append((qobuz.utils.color(color, qobuz.lang(39008)), "XBMC.RunPlugin("+url+")"))
        ''' 
        Give a chance to our siblings to attach their items
        '''
        self.hook_attach_context_menu(item,menuItems)

        ''' SCAN '''
        if qobuz.addon.getSetting('enable_scan_feature') == 'true':
            url = self.make_url(Mode.SCAN)
            try:
                label = qobuz.utils.color(color,qobuz.lang(39003) + ": ") + self.get_label().decode('utf8','replace')
            except: pass
            menuItems.append((label,'XBMC.UpdateLibrary("music", "%s")' % (url)))

        ''' ERASE CACHE '''
        color = qobuz.addon.getSetting('color_item_caution')
        erasecache = sys.argv[0] + "?mode=" + str(Mode.ERASE_CACHE)
        menuItems.append((qobuz.utils.color(color,qobuz.lang(31009)),"XBMC.RunPlugin(" + erasecache + ")"))
        '''
        Add our items to the context menu
        '''

        if len(menuItems) > 0:
            item.addContextMenuItems(menuItems,replaceItems=False)

    def hook_attach_context_menu(self,item,menuItems):
        pass

    def _get_keyboard(self,default="",heading="",hidden=False):
        import xbmc
        kb = xbmc.Keyboard(default,heading,hidden)
        kb.doModal()
        if (kb.isConfirmed()):
            return unicode(kb.getText(),"utf-8")
        return ''
