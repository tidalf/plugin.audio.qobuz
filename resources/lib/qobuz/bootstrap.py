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
import os

import urllib

import xbmc

from constants import Mode
from debug import info, debug, warn, error
from dog import dog
import qobuz

''' Arguments parssing '''
def get_params():
    d = dog()
    rparam = {}
    paramstring = sys.argv[2]
    if len(paramstring) >= 2:
        params = sys.argv[2]
        cleanedparams = params.replace('?', '')
        if (params[len(params) - 1] == '/'):
            params = params[0:len(params) - 2]
        pairsofparams = cleanedparams.split('&')

        for i in range(len(pairsofparams)):
            splitparams = {}
            splitparams = pairsofparams[i].split('=')
            if (len(splitparams)) == 2:
                info('QobuzDog', "Checking script parameter: " + splitparams[0])
                if d.kv_is_ok(splitparams[0], splitparams[1]):
                    rparam[splitparams[0]] = splitparams[1]
                else:
                    print "Invalid key/value (" + splitparams[0] + ", " + splitparams[1] + ")"
    return rparam

'''
    QobuzBootstrap
'''
class QobuzBootstrap(object):

    def __init__(self, __addon__, __handle__):
        qobuz.addon = __addon__
        self.handle = __handle__
        qobuz.boot = self

    def bootstrap_app(self):
        self.bootstrap_directories()
        debug(self, "Directories:\n" + qobuz.path.to_s())
        self.bootstrap_lang()
        self.bootstrap_utils()
        self.bootstrap_api()
        self.bootstrap_core()
        self.bootstrap_image()
        self.bootstrap_gui()
        #self.bootstrap_player()
        #self.bootstrap_db()
        self.bootstrap_sys_args()
        self.auth = qobuz.core.login()
        if not self.auth:
            qobuz.gui.show_login_failure()
            exit(1)
        self.dispatch()

    def bootstrap_lang(self):
        qobuz.lang = qobuz.addon.getLocalizedString

    def bootstrap_utils(self):
        import utils.string
        class Utils():
            def __init__(self):
                self.color = utils.string.color
                self.lang = qobuz.addon.getLocalizedString
        qobuz.utils = Utils()

    def bootstrap_directories(self):
        class path ():
            def __init__(s):
                s.base = qobuz.addon.getAddonInfo('path')

            def _set_dir(s):
                s.profile = os.path.join(xbmc.translatePath('special://profile/'), 'addon_data', 'plugin.audio.qobuz')
                s.cache = os.path.join(s.profile, 'cache')
                s.resources = xbmc.translatePath(os.path.join(qobuz.path.base, 'resources'))
                s.image = xbmc.translatePath(os.path.join(qobuz.path.resources, 'img'))
            def to_s(s):
                out = 'profile : ' + s.profile + "\n"
                out += 'cache   : ' + s.cache + "\n"
                out += 'resouces: ' + s.resources + "\n"
                out += 'image   : ' + s.image + "\n"
                return out
            '''
            Make dir
            '''
            def mkdir(s, dir):
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
        warn(self, "REWRITE! need to bootstrap player")
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
        self.params = get_params()
        print repr(self.params)
        if not 'nt' in self.params:
            self.params['nt'] = '16384'
            self.MODE = Mode.VIEW
        ''' 
        set mode 
        '''
        try:
            self.MODE = int(self.params['mode'])
        except:
            warn(self, "No 'mode' parameter")
        for p in self.params:
            debug(self, "Param: " + p + ' = ' + str(self.params[p]))

    '''
    
    '''
    def build_url(self, mode, id, pos = None):
        req = sys.argv[0] + "?&mode=" + str(mode) + "&id=" + str(id)
        return req

    def erase_cache(self):
        from utils.cache import cache_manager
        cm = cache_manager()
        cm.delete_all_data()

    '''
    
    '''
    def build_url_return(self):
        return sys.argv[2]
    '''
        Execute methode based on MODE
    '''
    def dispatch(self):
        ret = False
        if self.MODE == Mode.VIEW:
            info(self, "Displaying node")
            from renderer.xbmc import Xbmc_renderer as renderer
            nt = None
            try:
                nt = int(self.params['nt'])
            except:
                print "No node type...abort"
                return False
            print "Node type: " + str(nt)
            id = None
            try: id = self.params['nid']
            except: pass
            r = renderer(nt, id, 0)
            r.display()

        elif self.MODE == Mode.PLAY:
            info(self, "Playing song")
            self.bootstrap_player()
            if qobuz.addon.getSetting('notification_playingsong') == 'true':
                qobuz.gui.notification(34000, 34001)
            try:
                context_type = urllib.unquote(self.params["context_type"])
            except:
                context_type = "playlist"
            if qobuz.player.play(self.params['nid']):
                return True
#        
#        if not self.MODE:
#            ret = qobuz.gui.showCategories()
#        
#        elif self.MODE == MODE_SONG:
#            info(self, "Playing song")
#            if qobuz.addon.getSetting('notification_playingsong') == 'true':
#                qobuz.gui.showNotification(34000, 34001)
#            try:
#                context_type=urllib.unquote_plus(self.params["context_type"])
#            except: 
#                context_type="playlist"
#            pos = None
#            if qobuz.player.play(self.ID):      
#                return True
#        
#        elif self.MODE == MODE_ARTIST:
#            info(self, "Displaying artist")
#            ret = qobuz.gui.showArtist(str(self.ID))
#
#        elif self.MODE == MODE_ALBUM:
#            info(self, "Displaying album")
#            try:
#                context_type=urllib.unquote_plus(self.params["context_type"])
#            except: 
#                context_type="playlist"            
#            ret = qobuz.gui.showProduct(str(self.ID),context_type)
#            
#        elif self.MODE == MODE_USERPLAYLISTS:
#            info(self, 'Displaying userplaylist')
#            ret = qobuz.gui.showUserPlaylists()
#    
#        elif self.MODE == MODE_SEARCH_SONGS:
#            if qobuz.addon.getSetting('search_enabled') == 'false':
#                info(self, "Search is disabled!")
#                return False
#            info(self, 'Searching songs')
#            ret =qobuz.gui.searchSongs()    
#        
#        elif self.MODE == MODE_SEARCH_ALBUMS:
#            if qobuz.addon.getSetting('search_enabled') == 'false':
#                info(self, "Search is disabled!")
#                return False
#            info(self, "Search albums")
#            ret = qobuz.gui.searchAlbums()
#            
#        elif self.MODE == MODE_SEARCH_ARTISTS:
#            if qobuz.addon.getSetting('search_enabled') == 'false':
#                info(self, "Search is disabled!")
#                return False
#            info(self, "Search artists")
#            ret = qobuz.gui.searchArtists()
#     
#        elif self.MODE == MODE_PLAYLIST:
#            info(self, 'Displaying playlist')
#            ret = qobuz.gui.showPlaylist(str(self.ID))
#            
#        elif self.MODE == MODE_SHOW_RECOS:
#            info(self, "Displaying recommendations")
#            ret = qobuz.gui.showRecommendationsTypes()
#
#        elif self.MODE == MODE_SHOW_PURCHASES:
#            info(self, "Displaying purchases")
#            ret = qobuz.gui.showPurchases()
#        
#        elif self.MODE == MODE_SHOW_RECO_T_G:
#            import urllib
#            info(self, "Displaying recommendations T/G")
#            type = genre = ''
#            try:
#                type=urllib.unquote_plus(self.params["type"])
#                genre=urllib.unquote_plus(self.params["genre"])
#            except: pass
#            ret = qobuz.gui.showRecommendations(type, genre)
#        
#        elif self.MODE == MODE_SHOW_RECO_T:
#            import urllib
#            info(self, "Displaying recommendations T")
#            type = ''
#            try:
#                type=urllib.unquote_plus(self.params["type"])
#            except: pass
#            ret = qobuz.gui.showRecommendationsGenres(type)
#
#        elif self.MODE == MODE_CREATE_PLAYLIST:
#            info(self, "Creating new playlist")
#            ret = qobuz.gui.create_playlist()
#            
#        elif self.MODE == MODE_CURRENT_PLAYLIST:
#            info(self, "Displaying current playlist")
#            ret = qobuz.gui.show_current_playlist()
#            
#        elif self.MODE == MODE_ERASE_CACHE:
#            info(self, "Erasing cache...")
#            self.erase_cache()
#            
#        elif self.MODE == MODE_RENAME_PLAYLIST:
#            info(self, "Renaming playlist id: " + str(self.params['nid']))
#            qobuz.gui.rename_playlist(self.params['nid'])
#        
#        elif self.MODE == MODE_REMOVE_PLAYLIST:
#            id = int(self.params['nid'])
#            if not id:
#                print "Cannot delete playlist without id"
#                return False
#            info(self, "Deleting playlist: " + self.params['nid'])
#            res = qobuz.api.playlist_delete(id)
#            if not res:
#                print "Cannot delete playlist with id " + str(id)
#                return False
#            print "Playlist deleted: " + str(id)
#            from utils.cache import cache_manager
#            cm = cache_manager()
#            cm.delete_file('userplaylists-0')
#            xbmc.executebuiltin('Container.Refresh')
#            return True
#            
#        elif self.MODE == MODE_MANAGE_PLAYLIST:
#            from widget.playlist import QobuzGui_Playlist
#            p = QobuzGui_Playlist('Qobuz_MyMusicPlaylist.xml', qobuz.path.base, 'Default', True)
#            p.doModal()
#            del p
#            exit(0)
#        
#        elif self.MODE == MODE_TEST:
#            from tree.node import test_node
#            t = test_node()
#            t.run()
#        
#        elif self.MODE == MODE_NODE:
#            from tree.renderer import renderer
#            nt = None
#            try:
#                nt = int(self.params['nt'])
#            except:
#                print "No node type...abort"
#                return False
#            print "Node type: " + str(nt)
#            id = None
#            try: id = self.params['nid']
#            except: pass
#            r = renderer(nt, id, 0)
#            r.display()
#            
#        elif self.MODE == MODE_ADD_TO_CURRENT_PLAYLIST:
#            from data.current_playlist import Cache_current_playlist
#            current_playlist = Cache_current_playlist()
#            from tag.playlist import TagPlaylist
#            tag = TagPlaylist(current_playlist.get_data())
#            id = tag.id
#            print "Current playlist id: " + str(id)
#            print '-'*80 + "Adding node to new playlist"
#            from tree.renderer import renderer
#            nt = None
#            try: nt = int(self.params['nt'])
#            except:
#                print "No node type...abort"
#                return False
#            print "Node type: " + str(nt)
#            id = None
#            try: id = self.params['nid']
#            except: pass
#            r = renderer(nt, id, 0)
#            r.add_to_current_playlist()
#
#        elif self.MODE == MODE_ADD_AS_NEW_PLAYLIST:
#            print '-'*80 + "Adding node to new playlist"
#            from tree.renderer import renderer
#            nt = None
#            try: nt = int(self.params['nt'])
#            except:
#                print "No node type...abort"
#                return False
#            print "Node type: " + str(nt)
#            id = None
#            try: id = self.params['nid']
#            except: pass
#            r = renderer(nt, id, 0)
#            r.add_as_new_playlist()
#                        
#            
#        elif self.MODE == MODE_LIBRARY_SCAN:
#            import urllib
#            s = 'UpdateLibrary("music", "'+sys.argv[0] + urllib.unquote(self.params['url'])+'")'
#            log(self, s)
#            xbmc.executebuiltin(s)
#        
#        elif self.MODE == MODE_PLAYLIST_REMOVE_TRACK:
#            info(self, "Removing track from playlist " + self.params['nid'])
#            from tree.node_playlist import node_playlist
#            pl = node_playlist(self.params)
#            pl.set_id(self.params['nid'])
#            info(self, "Removing track from playlist " + str(pl.id))
#            pl.remove_tracks(self.params['tracks_id'])
#        
#        elif self.MODE == MODE_SELECT_CURRENT_PLAYLIST:
#            qobuz.gui.set_current_playlist(int(self.params['nid']))
#        
#        else:
#            warn(self, "Unknown mode: " + str(self.MODE) + "... exiting!")
#            ret = False
#        
#        '''
#            Directory Ending
#        '''
#        if ret: #self.MODE < MODE_SONG:
#            qobuz.gui.endOfDirectory()
