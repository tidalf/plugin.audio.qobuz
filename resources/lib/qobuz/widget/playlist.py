import os
import sys
import time
import pprint
import xbmc, xbmcgui, xbmcplugin
from constants import *

from view.userplaylists import QobuzUserPlaylistsXbmc

__pluginpath__ = 'plugin://plugin.audio.qobuz/'

ACTION_SELECT = 7
ACTION_FOCUS = 0
ACTION_PREVIOUS_MENU = 10
ACTION_CONTEXT = 117
ACTION_BACK = 92

ACTION_MOUSE_FOCUS = 107
ACTION_MOUSE_SELECT = 100

class QobuzGui_Context(xbmcgui.WindowXMLDialog):
    def __init__(self,strXMLname, strFallbackPath, strDefaultName, forceFallback):
        # Changing the three varibles passed won't change, anything
        # Doing strXMLname = "bah.xml" will not change anything.
        # don't put GUI sensitive stuff here (as the xml hasn't been read yet
        # Idea to initialize your variables here
        self.xmlName = strXMLname
        self.fallbackPath = strFallbackPath
        self.defaultName = strDefaultName
        pass
    
    def onInit(self):
        ctl = self.getControl(1000)
        button = xbmcgui.ControlButton(100, 250, 200, 50, 'Status', font='font14')
        ctl.addItem('plop')
        pass
    
    def addButton(self):
        pass
    
class QobuzGui_Playlist(xbmcgui.WindowXML):
    def __init__(self,strXMLname, strFallbackPath, strDefaultName, forceFallback):
        # Changing the three varibles passed won't change, anything
        # Doing strXMLname = "bah.xml" will not change anything.
        # don't put GUI sensitive stuff here (as the xml hasn't been read yet
        # Idea to initialize your variables here
        pass
 
    def calculateResolution(self):
        w = self.getWidth()
        reso = self.getResolution()
        print "Resolution: " + str(reso)
        try:
            #self.setCoordinateResolution(reso)
            pass
        except:
            pass
        #self.clearProperties()
    
    def onInit(self):
        # Put your List Populating code/ and GUI startup stuff here
        print 'Loaded...'
        try:
            self.calculateResolution()
        except: pass
        #self.clearProperties()
        self.control_playlist = None
        try:
            self.control_playlist = self.getControl(301)
        except: pass
        print "Control: " + str(self.control_playlist)
        self.control_playlist = self
        if not self.control_playlist:
            self.close()
            return 
        self.add_userplaylists_items()
        
    
    def onClick(self, controlID):
        """
            Notice: onClick not onControl
            Notice: it gives the ID of the control not the control object
        """
        super(QobuzGui_Playlist, self).onClick(controlID)
        pass
 
    def onFocus(self, controlID):
        super(QobuzGui_Playlist, self).onFocus(controlID)
        pass
    
    
    def set_core(self, Core):
        self.Core = Core
    
    
    def add_userplaylist_item_contextmenu(self, item):
        __language__ = self.Core.Bootstrap.__language__
        menuItems = []
        remove=sys.argv[0]+"?mode="+str(MODE_PLAYLIST_REMOVE)
        menuItems.append((__language__(31010), "XBMC.RunPlugin("+remove+")"))
        item.addContextMenuItems(menuItems, replaceItems=False)
    
    def add_userplaylists_items(self):
        pl = QobuzUserPlaylistsXbmc(self.Core)
        list = pl.get_items()
        for l in list:
                item = l[1]
                path = l[0]
                item.setPath(path)
                item.setProperty('path', path)
                item.setIconImage(self.Core.Bootstrap.baseDir + '/default.tbn')
                print "Path: " + item.getProperty('path')
                self.control_playlist.addItem(item)
    
    def onKey(self, key):
        print "On key: " + str(key)
        super(QobuzGui_Playlist, self).onKey(action)
    
    def onControl(self, control):
        print "Control: " + str(control)
        if control == self.list_plugin:
            item = self.list_plugin.getSelectedItem()
            self.message('You selected : ' + item.getLabel())  
        super(QobuzGui_Playlist, self).onKey(action)
    
             
    def onAction(self, action):
        print 'Action Id: ' + str(action.getId())
        if action == ACTION_PREVIOUS_MENU:
            self.close()
        if action == ACTION_BACK:
            self.close()
        if action == ACTION_CONTEXT:
            print "Context menu wanted!"
            self.showContextMenu('item')


    def showContextMenu(self, item):
        d = QobuzGui_Context('Qobuz_DialogContextMenu.xml', self.Core.Bootstrap.baseDir, 'Default', True)
        d.doModal()
        