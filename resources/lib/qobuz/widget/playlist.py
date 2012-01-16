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

ACTION_MOUSE_FOCUS = 107
ACTION_MOUSE_SELECT = 100
class QobuzGui_PlaylistItem():
    pass
    
class QobuzGui_Playlist(xbmcgui.WindowXMLDialog):
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
        self.setFocus(self)
    
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
                item.setIconImage(self.Core.Bootstrap.baseDir + 'default.tbn')
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
#        pl = self.control_playlist
#        item = pl.getSelectedItem()
#        if action == ACTION_FOCUS or action == ACTION_MOUSE_FOCUS:
#            item.select(True)
#        elif action == ACTION_SELECT or action == ACTION_MOUSE_SELECT:
#            print "Item selected: " + item.getLabel() + "\n"
        
        super(QobuzGui_Playlist, self).onAction(action)
#            print "Select\n"
#            i = self.list_plugin.getSelectedItem()
#            print('You selected: ' + i.getLabel() + ' / ' + i.getProperty('path'))
#            xbmc.executebuiltin("XBMC.RunPlugin("+os.sys.argv[1]+'/'+i.getProperty('path')+")")
