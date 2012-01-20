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

import os
import sys
import time
import pprint
import xbmc, xbmcgui, xbmcplugin
from constants import *

import qobuz
from debug import warn, info
from data.userplaylists import QobuzUserPlaylistsXbmc
from data.playlist import QobuzPlaylist


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

'''
    Edit a playlist
'''
class playlist_edit(xbmcgui.WindowXMLDialog):
        def __init__(self, strXMLname, strFallbackPath, strDefaultName, forceFallback):
            pass        
        
        def set_item(self, item):
            self.item = item
            
        def onInit(self):
#            if not self.item:
#                print "Cannot edit playlist without item"
#                return False
#            return True
#            self.clearProperties()
            self.ctl_name = self.getControl(302)
            self.ctl_name.setText(self.item.getProperty('name'))
            self.ctl_description = self.getControl(303)
            self.ctl_description.setText(self.item.getProperty('description'))
            
            pass
        
        def onAction(self, action):
            if action == ACTION_PREVIOUS_MENU:
                self.close()
                
            
class QobuzGui_Playlist(xbmcgui.WindowXML):
    def __init__(self,strXMLname, strFallbackPath, strDefaultName, forceFallback):
        # Changing the three varibles passed won't change, anything
        # Doing strXMLname = "bah.xml" will not change anything.
        # don't put GUI sensitive stuff here (as the xml hasn't been read yet
        # Idea to initialize your variables here
        self.xmlName = strXMLname
        self.fallbackPath = strFallbackPath
        self.defaultName = strDefaultName
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
        #self.control_playlist = self
#        if not self.control_playlist:
#            self.close()
#            return 
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
        pl = QobuzUserPlaylistsXbmc()
        list = pl.get_items()
        #image = self.Core.Bootstrap.baseDir + '/default.tbn'
        for l in list:
                item = l[1]
                path = l[0]
                item.setPath(path)
                item.setProperty('path', path)
#                item.setIconImage(image)
#                item.setThumbnailImage(image)
                print "Path: " + item.getProperty('path')
                self.addItem(item)
    
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


    def action_edit(self, item, position):
        w = playlist_edit('DialogEditPlaylist.xml', self.fallbackPath, self.defaultName, True)
        w.set_item(item)
        w.doModal()
        del w
        
    def action_rename(self):
        position = self.getCurrentListPosition()
        item = self.getListItem(position)
        oldname = item.getProperty('name').strip()
        print "Renaming item with name: " + oldname
        id = int(item.getProperty('playlist_id'))
        if not id:
            warn(self, "Cannot rename playlist without id")
            return False
        heading = "Renaming playlist: " + item.getLabel()
        kb = xbmc.Keyboard(item.getLabel(), heading, False)
        kb.doModal()
        if not kb.isConfirmed():
            print "Renaming canceled"
            return False
        newname = kb.getText().strip()
        if oldname == newname:
            print "Same name"
            return True
        ret = qobuz.api.playlist_update(id, 
                                        newname, 
                                        item.getProperty('description'),
                                        '',
                                        item.getProperty('is_public'),
                                        item.getProperty('is_collaborative')
                                        )
        if not ret:
            qobuz.gui.showNotificationH('Playlist Manager', 'Cannot rename playlist')
            warn(self, "Cannot rename playlist")
            return False
        pl = QobuzUserPlaylistsXbmc()
        pl.delete_cache()
        item.setLabel(newname)
        self.removeItem(position)
        self.addItem(item, position)
        return True
    
    def action_create(self):
        kb = xbmc.Keyboard("", "Creating playlist", False)
        kb.doModal()
        if not kb.isConfirmed():
            print "Create canceled"
            return False
        name = kb.getText().strip()
        ret = qobuz.api.playlist_create()
        
    def showContextMenu(self, item):
        options = [('edit', 'Editer')] #('delete', 'Delete'), ('create', 'Create'), ]
        
        optionstring = []
        for l in options:
            optionstring.append(l[1])
        diag = xbmcgui.Dialog()
        isel = diag.select('Playlist Option', optionstring)
        del diag
        print "Item Selected: " + str(options[isel][0])
        if isel == -1:
            print "Nothing selected"
            return True
        position = self.getCurrentListPosition()
        litem = self.getListItem(position)
        action = options[isel][0]
        if action == 'edit':
            self.action_edit(litem, position)
        if action == 'create':
            self.action_create()
        
        