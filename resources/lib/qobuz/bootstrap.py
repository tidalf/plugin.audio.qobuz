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
import sys, os
import urllib
import xbmc

from constants import *
import constants
from core import QobuzCore
from gui import QobuzGUI
from debug import *
from player import QobuzPlayer
#from winmain import QobuzWindow
from images import QobuzImages

import xbmcgui

''' Arguments parssing '''
def get_params():
    param=[]
    paramstring=sys.argv[2]
    if constants.__debugging__ :
        xbmc.log(paramstring)
    if len(paramstring)>=2:
        params=sys.argv[2]
        cleanedparams=params.replace('?','')
        if (params[len(params)-1]=='/'):
            params=params[0:len(params)-2]
        pairsofparams=cleanedparams.split('&')
        param={}
        for i in range(len(pairsofparams)):
            splitparams={}
            splitparams=pairsofparams[i].split('=')
            if (len(splitparams))==2:
                param[splitparams[0]]=splitparams[1]
    return param

import threading
import time
class Watcher(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.Terminated = False
        self.name = "Watcher"
        self._stopevent = threading.Event( )
        
    def run(self, player, id, pos):
        if not player.play(id, pos):
            return False
        i = 0
        while not self._stopevent.isSet():
            try:
                if player.isPlayingAudio():
                    print "Player is playing: " + self.item.getLabel()
                    player.watchPlayback()
                    time.sleep()
                else:
                    self.stop()
            except:
                self.stop()
                print "Player stopped"
      
    def stop(self):  
        self._stopevent.set( )  

'''
    QobuzBoostrap
'''
class QobuzBootstrap(object):
    
    def __init__(self, __addon__, __handle__):
        #global Player
        self.__addon__ = __addon__
        self.__handle__ = __handle__
        info(self, "Handle: " + str(self.__handle__))
        self.__language__ = __addon__.getLocalizedString
        self.bootstrapDirectories()
        self.Core = QobuzCore(self)
        self.GUI = QobuzGUI(self)
        self.Player = QobuzPlayer()
        self.Player.setCore(self.Core)
        self.Images = QobuzImages(self.imgDir)
        self.MODE = None
        self.ID = None
        self.META = None
        self.parse_sys_args()
        '''
            NAME can be used to set icon for each folder i think :)
            XBMC maintain a cache path/icon 
            http://wiki.xbmc.org/index.php?title=Thumbnails
        '''
        self.NAME = None
        if not self.Core.login():
            self.GUI.showLoginFailure()
            exit(1)
        self.mode_dispatch()
    
    '''
        Initialize needed directories
    '''
    def bootstrapDirectories(self):
        self.baseDir = self.__addon__.getAddonInfo('path')
        self.cacheDir = os.path.join(xbmc.translatePath('special://temp/'),  os.path.basename(self.baseDir))
        self.resDir =  xbmc.translatePath(os.path.join(self.baseDir, 'resources'))
        self.imgDir = xbmc.translatePath(os.path.join(self.resDir, 'img'))
        self.mkdir('cache', self.cacheDir)
    
    '''
        Make dir
    '''
    def mkdir(self, name, dir):
        info(self, name + ': ' + dir)
        if os.path.isdir(dir) == False:
            try:
                os.makedirs(dir)
            except:
                warn("Cannot create directory: " + dir)
                exit(2)
            info(self, "Directory created: " + dir)
            
    '''
        Parse system parameters
    '''
    def parse_sys_args(self):
        self.params = get_params()
        ''' 
        set mode 
        '''
        try:
            self.MODE = int(self.params['mode'])
        except: 
            warn(self, "No 'mode' parameter")
        ''' 
        set id 
        '''
        try: 
            self.ID = str(self.params["id"])
        except: 
            warn(self, "No 'id' parameter")
        try: 
            self.META = str(self.params["meta"])
        except: pass
        for p in self.params:
            info(self, "Param: " + p + ' = ' + str(self.params[p]))
    
    '''
    
    '''
    def build_url(self, mode, id, pos = None):
        req = sys.argv[0] + "?&mode=" + str(mode)+"&id="+str(id)
        if self.META:
            req += "&meta=1"
        return req
    
    def erase_cache(self):
        import re
        if not self.cacheDir:
            warn(self, "Cache directory not set")
            return False
        if not os.path.exists(self.cacheDir):
            warn(self, "Cache directory doesn't seem to exist")
            return False
        list = os.listdir(self.cacheDir)
        for f in list:
            if not f.endswith('.dat'): 
                continue
            path = os.path.join(self.cacheDir, str(f))
            if os.unlink(path):
                info(self, "Cache file deleted: " + path)
            else:
                warn(self, "Cannot remove cache file: " + path)
    '''
    
    '''
    def build_url_return(self):
        return sys.argv[2]
    '''
        Execute methode based on MODE
    '''       
    def mode_dispatch(self):
        if not self.MODE:
            self.GUI.showCategories()
        
        elif self.MODE == MODE_SONG:
            info(self, "PLaying song")
            self.Core.Bootstrap.GUI.showNotificationH('Qobuz Player', 'Loading song...')
            try:
                context_type=urllib.unquote_plus(self.params["context_type"])
            except: 
                context_type="playlist"
            pos = None
            if self.Player.play(self.ID):      
                return True
        
        elif self.MODE == MODE_ARTIST:
            info(self, "Displaying artist")
            self.GUI.showArtist(str(self.ID))

        elif self.MODE == MODE_ALBUM:
            info(self, "Displaying album")
            try:
                context_type=urllib.unquote_plus(self.params["context_type"])
            except: 
                context_type="playlist"            
            self.GUI.showProduct(str(self.ID),context_type)
            
        elif self.MODE == MODE_USERPLAYLISTS:
            info(self, 'Displaying userplaylist')
            self.GUI.showUserPlaylists()
    
        elif self.MODE == MODE_SEARCH_SONGS:
            info(self, 'Searching songs')
            self.GUI.searchSongs()    
        
        elif self.MODE == MODE_SEARCH_ALBUMS:
            info(self, "Search albums")
            self.GUI.searchAlbums()
            
        elif self.MODE == MODE_SEARCH_ARTISTS:
            info(self, "Search artists")
            self.GUI.searchArtists()
     
        elif self.MODE == MODE_PLAYLIST:
            info(self, 'Displaying playlist')
            self.GUI.showPlaylist(str(self.ID))
            
        elif self.MODE == MODE_SHOW_RECOS:
            info(self, "Displaying recommendations")
            self.GUI.showRecommendationsTypes()

        elif self.MODE == MODE_SHOW_PURCHASES:
            info(self, "Displaying purchases")
            self.GUI.showPurchases()
        
        elif self.MODE == MODE_SHOW_RECO_T_G:
            info(self, "Displaying recommendations T/G")
            type = genre = ''
            try:
                type=urllib.unquote_plus(self.params["type"])
                genre=urllib.unquote_plus(self.params["genre"])
            except: pass
            self.GUI.showRecommendations(type, genre)
        
        elif self.MODE == MODE_SHOW_RECO_T:
            info(self, "Displaying recommendations T")
            type = ''
            try:
                type=urllib.unquote_plus(self.params["type"])
            except: pass
            self.GUI.showRecommendationsGenres(type)

        elif self.MODE == MODE_CURRENT_PLAYLIST:
            info(self, "Displaying current playlist")
            self.GUI.showCurrentPlaylist()
            
        elif self.MODE == MODE_ERASE_CACHE:
            info(self, "Erasing cache...")
            self.erase_cache()
            
        '''
            Directory Endin
        '''
        if self.MODE < MODE_SONG:
            self.GUI.endOfDirectory()
        