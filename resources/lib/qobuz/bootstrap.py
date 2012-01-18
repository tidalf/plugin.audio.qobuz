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

import pprint

import xbmc
    
from constants import *
import constants
from debug import *
import qobuz

''' Arguments parssing '''
def get_params():
    param=[]
    paramstring=sys.argv[2]
    if constants.__debugging__ :
        xbmc.log(paramstring)
        pass
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

'''
    QobuzBootstrap
'''
class QobuzBootstrap(object):
    
    def __init__(self, __addon__, __handle__):
        qobuz.addon = __addon__
        self.handle = __handle__
        #qobuz.lang = qobuz.addon.getLocalizedString

        qobuz.boot = self
    
    def bootstrap_app(self):
        self.bootstrap_directories()
        self.bootstrap_lang()
        self.bootstrap_api()
        self.bootstrap_core()
        self.bootstrap_image()
        self.bootstrap_gui()
        self.bootstrap_player()
        #self.bootstrap_db()
        self.bootstrap_sys_args()
        
        if not qobuz.core.login():
            qobuz.gui.showLoginFailure()
            exit(1)
        self.mode_dispatch()
    
    def bootstrap_lang(self):
        qobuz.lang = qobuz.addon.getLocalizedString
         
    def bootstrap_directories(self):
        class path ():
            def __init__(s):
                s.base = qobuz.addon.getAddonInfo('path')
                
            def _set_dir(s):
                s.temp = xbmc.translatePath('special://temp/')
                s.cache = os.path.join(s.temp, 'plugin.audio.qobuz')
                s.resources = xbmc.translatePath(os.path.join(qobuz.path.base, 'resources'))
                s.image = xbmc.translatePath(os.path.join(qobuz.path.resources, 'img'))

            '''
            Make dir
            '''
            def mkdir(s, dir):
                info(self, "Creating directoy: " +  dir)
                if os.path.isdir(dir) == False:
                    try:
                        os.makedirs(dir)
                    except:
                        warn("Cannot create directory: " + dir)
                        exit(2)
                    info(self, "Directory created: " + dir)
        qobuz.path = path()
        qobuz.path._set_dir()
        qobuz.path.mkdir(qobuz.path.cache)

    def bootstrap_debug(self):
        from debug import log, warn, error, info
        class d():
            def __init__(s):
                s.log = log
                s.warn = warn
                s.error = error
                s.info = info
        qobuz.debug = d()
        
    def bootstrap_api(self):
        from api import QobuzApi
        qobuz.api = QobuzApi()
        
    def bootstrap_core(self):
        from core import QobuzCore
        qobuz.core = QobuzCore()
    
    def bootstrap_image(self):
        from images import QobuzImage
        qobuz.image = QobuzImage()
        
    def bootstrap_gui(self):
        from gui import QobuzGUI
        qobuz.gui = QobuzGUI()
        
    def bootstrap_player(self):
        from player import QobuzPlayer
        qobuz.player = QobuzPlayer()
    
    def bootstrap_db(self):
        try:
            from utils.db import QobuzDb
            qobuz.db = QobuzDb(qobuz.path.cache, 'qobuz.db3')
        except:
            qobuz.db = None
        if not qobuz.db.open():
            warn(self, "Cannot open sql database")
            exit(0)

    '''
        Parse system parameters
    '''
    def bootstrap_sys_args(self):
        self.MODE = None
        self.ID = None
        self.META = None
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
        cache = qobuz.path.cache
        if not cache:
            warn(self, "Cache directory not set")
            return False
        if not os.path.exists(cache):
            warn(self, "Cache directory doesn't seem to exist")
            return False
        list = os.listdir(cache)
        for f in list:
            if not f.endswith('.dat'): 
                continue
            path = os.path.join(cache, str(f))
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
            qobuz.gui.showCategories()
        
        elif self.MODE == MODE_SONG:
            info(self, "PLaying song")
            qobuz.gui.showNotification(34000, 34001)
            try:
                context_type=urllib.unquote_plus(self.params["context_type"])
            except: 
                context_type="playlist"
            pos = None
            if qobuz.player.play(self.ID):      
                return True
        
        elif self.MODE == MODE_ARTIST:
            info(self, "Displaying artist")
            qobuz.gui.showArtist(str(self.ID))

        elif self.MODE == MODE_ALBUM:
            info(self, "Displaying album")
            try:
                context_type=urllib.unquote_plus(self.params["context_type"])
            except: 
                context_type="playlist"            
            qobuz.gui.showProduct(str(self.ID),context_type)
            
        elif self.MODE == MODE_USERPLAYLISTS:
            info(self, 'Displaying userplaylist')
            qobuz.gui.showUserPlaylists()
    
        elif self.MODE == MODE_SEARCH_SONGS:
            if qobuz.addon.getSetting('search_enabled') == 'false':
                info(self, "Search is disabled!")
                return False
            info(self, 'Searching songs')
            qobuz.gui.searchSongs()    
        
        elif self.MODE == MODE_SEARCH_ALBUMS:
            if qobuz.addon.getSetting('search_enabled') == 'false':
                info(self, "Search is disabled!")
                return False
            info(self, "Search albums")
            qobuz.gui.searchAlbums()
            
        elif self.MODE == MODE_SEARCH_ARTISTS:
            if qobuz.addon.getSetting('search_enabled') == 'false':
                info(self, "Search is disabled!")
                return False
            info(self, "Search artists")
            qobuz.gui.searchArtists()
     
        elif self.MODE == MODE_PLAYLIST:
            info(self, 'Displaying playlist')
            qobuz.gui.showPlaylist(str(self.ID))
            
        elif self.MODE == MODE_SHOW_RECOS:
            info(self, "Displaying recommendations")
            qobuz.gui.showRecommendationsTypes()

        elif self.MODE == MODE_SHOW_PURCHASES:
            info(self, "Displaying purchases")
            qobuz.gui.showPurchases()
        
        elif self.MODE == MODE_SHOW_RECO_T_G:
            info(self, "Displaying recommendations T/G")
            type = genre = ''
            try:
                type=urllib.unquote_plus(self.params["type"])
                genre=urllib.unquote_plus(self.params["genre"])
            except: pass
            qobuz.gui.showRecommendations(type, genre)
        
        elif self.MODE == MODE_SHOW_RECO_T:
            info(self, "Displaying recommendations T")
            type = ''
            try:
                type=urllib.unquote_plus(self.params["type"])
            except: pass
            qobuz.gui.showRecommendationsGenres(type)

        elif self.MODE == MODE_CURRENT_PLAYLIST:
            info(self, "Displaying current playlist")
            qobuz.gui.showCurrentPlaylist()
            
        elif self.MODE == MODE_ERASE_CACHE:
            info(self, "Erasing cache...")
            self.erase_cache()
            
        elif self.MODE == MODE_MANAGE_PLAYLIST:
            from widget.playlist import QobuzGui_Playlist
            p = QobuzGui_Playlist('Qobuz_MyMusicPlaylist.xml', self.baseDir, 'Default', True)
            p.set_core(self.Core)
            p.doModal()
            exit(0)
        
        elif self.MODE == MODE_TEST:
            from tree.node import test_node
            t = test_node()
            t.run()
        '''
            Directory Ending
        '''
        if self.MODE < MODE_SONG:
            qobuz.gui.endOfDirectory()

