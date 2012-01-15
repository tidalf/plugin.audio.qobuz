import os
import sys
import xbmc, xbmcgui, xbmcplugin
import time

__pluginpath__ = 'plugin://plugin.audio.qobuz/'

ACTION_SELECT = 7
ACTION_PREVIOUS_MENU = 10

class QobuzGui_Playlist(xbmcgui.WindowXML):
    def __init__(self,strXMLname, strFallbackPath, strDefaultName, forceFallback):
        # Changing the three varibles passed won't change, anything
        # Doing strXMLname = "bah.xml" will not change anything.
        # don't put GUI sensitive stuff here (as the xml hasn't been read yet
        # Idea to initialize your variables here
        self.Run = True
        pass
 
    def onInit(self):
        # Put your List Populating code/ and GUI startup stuff here
        print 'Loaded...'
        self.getControl(101).setLabel('Playlist')
        self.list_plugin = self.getControl(20)
        
        irootplug = xbmcgui.ListItem('Qobuz', '[Qobuz]', 'default.tbn', 'default.tbn', path= __pluginpath__)
        #irootplug.setInfo('music')
        irootplug.setProperty('path', __pluginpath__)
        self.list_plugin.addItem(irootplug)
        #self.setControl(self.list_plugin)
        self.list_playlist = self.getControl(21)
        self.setFocus(self.list_plugin)
        self.Run = True
        pass 
    
    def onControl(self, control):
        print "Control: " + str(control)
        if control == self.list_plugin:
            item = self.list_plugin.getSelectedItem()
            self.message('You selected : ' + item.getLabel())  
            
    def onAction(self, action):
        print 'Action: ' + str(action)
        if action == ACTION_PREVIOUS_MENU:
            self.close()
        if action == ACTION_SELECT:
            print "Select\n"
            i = self.list_plugin.getSelectedItem()
            print('You selected: ' + i.getLabel() + ' / ' + i.getProperty('path'))
            xbmc.executebuiltin("XBMC.RunPlugin("+os.sys.argv[1]+'/'+i.getProperty('path')+")")
