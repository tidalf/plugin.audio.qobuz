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
import json
import pprint

import xbmc

from constants import Mode
from debug import info, debug, warn, error
from dog import dog
import qobuz
from node.flag import NodeFlag as Flag
from exception import QobuzXbmcError
from gui.util import notifyH, notify, dialogLoginFailure, getImage, yesno

''' Arguments parssing '''
def get_params():
    d = dog()
    rparam = {}
    if len(sys.argv) <= 1:
        return rparam
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
                debug('QobuzDog', "Checking script parameter: " + splitparams[0])
                if d.kv_is_ok(splitparams[0], splitparams[1]):
                    rparam[splitparams[0]] = splitparams[1]
                else:
                    warn('[DOG]', "--- Invalid key: %s / value: %s" % (splitparams[0], splitparams[1]))
    return rparam



        
'''
    QobuzBootstrap
'''
class QobuzBootstrap(object):

    def __init__(self, __addon__, __handle__):
        qobuz.addon = __addon__
        self.handle = __handle__
        qobuz.boot = self
    
    ''' BOTTSTRAP App '''
    def bootstrap_app(self):
        from xbmcrpc import XbmcRPC
        self.bootstrap_directories()
        self.bootstrap_registry()
        self.bootstrap_sys_args()
        qobuz.rpc = XbmcRPC()

    ''' BOTTSTRAP Registry '''
    def bootstrap_registry(self):
        from registry import QobuzRegistry
        streamFormat = 6 if qobuz.addon.getSetting('streamtype') == 'flac' else 5
        try:
            qobuz.registry = QobuzRegistry(
                                       cacheType='default', 
                                       username=qobuz.addon.getSetting('username'), 
                                       password=qobuz.addon.getSetting('password'), 
                                       basePath=qobuz.path.cache,
                                       streamFormat=streamFormat, hashKey=False)

            qobuz.registry.get(name='user')
            qobuz.api = qobuz.registry.get_api()
        except QobuzXbmcError:
            dialogLoginFailure()
            #@TODO sys.exit killing XBMC? FRODO BUG ?
            #sys.exit(1)
            raise QobuzXbmcError(who=self, what='invalid_login', additional=None)
            
    ''' BOTTSTRAP Directories '''
    def bootstrap_directories(self):
        class PathObject ():
            def __init__(self):
                self.base = qobuz.addon.getAddonInfo('path')

            def _set_dir(self):
                self.profile = os.path.join(xbmc.translatePath('special://profile/'), 'addon_data', qobuz.addon.getAddonInfo('id'))
                self.cache = os.path.join(self.profile, 'cache')
                self.resources = xbmc.translatePath(os.path.join(qobuz.path.base, 'resources'))
                self.image = xbmc.translatePath(os.path.join(qobuz.path.resources, 'img'))
            def to_s(self):
                out = 'profile : ' + self.profile + "\n"
                out += 'cache   : ' + self.cache + "\n"
                out += 'resources: ' + self.resources + "\n"
                out += 'image   : ' + self.image + "\n"
                return out
            '''
            Make dir
            '''
            def mkdir(self, dir):
                if os.path.isdir(dir) == False:
                    try:
                        os.makedirs(dir)
                    except:
                        warn("Cannot create directory: " + dir)
                        exit(2)
                    info(self, "Directory created: " + dir)
        qobuz.path = PathObject()
        qobuz.path._set_dir()
        qobuz.path.mkdir(qobuz.path.cache)

    ''' BOTTSTRAP Debug '''
    def bootstrap_debug(self):
        from debug import log, warn, error, info
        class DebugObject():
            def __init__(self):
                self.log = log
                self.warn = warn
                self.error = error
                self.info = info
        qobuz.debug = DebugObject()
        
    ''' BOTTSTRAP Player '''
    def bootstrap_player(self):
        from player import QobuzPlayer
        qobuz.player = QobuzPlayer()

    ''' BOOTSTRAP Parse system parameters '''
    def bootstrap_sys_args(self):
        self.MODE = None
        self.params = get_params()
        if not 'nt' in self.params:
            self.params['nt'] = Flag.ROOT
            self.MODE = Mode.VIEW
        self.NT = int(self.params['nt'])
        try:
            self.MODE = int(self.params['mode'])
        except:
            warn(self, "No 'mode' parameter")
        for p in self.params:
            debug(self, "Param: " + p + ' = ' + str(self.params[p]))

        self.NID = ''
        if 'nid' in self.params: self.NID = self.params['nid']

        debug(self, "NT: " + str(self.NT) + " / NID: " + self.NID)

    def erase_cache(self):
        qobuz.registry.delete_by_name('^.*\.dat$')

    '''
       Dispatch
    '''
    def dispatch(self):
        debug(self, "Mode: %s, Node: %s" % (Mode.to_s(self.MODE), Flag.to_s(int(self.params['nt']))))
        ''' PLAY '''
        
        if self.MODE == Mode.PLAY:
            debug(self, "Playing song")
            self.bootstrap_player()
            if qobuz.player.play(self.NID):
                return True
            return False

        from renderer.xbmc import Xbmc_renderer as renderer

        ''' UGLY MODE DISPATCH '''
        if self.MODE == Mode.VIEW:
            r = renderer(self.NT, self.NID)
            r.set_depth(1)
            r.set_filter(Flag.NODE | Flag.DONTFETCHTRACK)
            return r.display()

        elif self.MODE == Mode.VIEW_BIG_DIR:
            r = renderer(self.NT, self.NID)
            r.set_depth(-1)
            r.set_filter(Flag.TRACK | Flag.DONTFETCHTRACK)
            return r.display()

        elif self.MODE == Mode.SCAN:
            r = renderer(self.NT, self.NID)
            r.set_depth(-1)
            r.set_filter(Flag.DONTFETCHTRACK)
            return r.scan()
        
#        elif self.MODE == Mode.PLAYLIST_SUBSCRIBE:
#            from  node.user_playlists import Node_user_playlists
#            node = Node_user_playlists()
#            if node.subscribe_playlist(self.params['nid']):
#                return False
#            # xbmc.executebuiltin('Container.Refresh')
#            return True
#
#
#        elif self.MODE == Mode.PLAYLIST_ADD_TO_CURRENT:
#            from  node.playlist import Node_playlist
#            node = Node_playlist(None, self.params)
#            if not node.add_to_current_playlist():
#                return False
#            return True
#
#        elif self.MODE == Mode.FAVORITES_ADD_TO_CURRENT:
#            from  node.favorites import Node_favorites
#            node = Node_favorites(None, self.params)
#            if not node.add():
#                return False
#            return True
#
#        elif self.MODE == Mode.PLAYLIST_ADD_AS_NEW:
#            from  node.playlist import Node_playlist
#            node = Node_playlist(None, self.params)
#            if not node.add_as_new_playlist():
#                return False
#                qobuz.registry.delete_as_name('^user-playlists.*')
#                xbmc.executebuiltin('Container.Refresh')
#            return False
#        
#
#        elif self.MODE == Mode.PLAYLIST_REMOVE_TRACK:
#            from node.playlist import Node_playlist
#            node = Node_playlist(None, self.params)
#            node.id = self.NID
#            node.data = qobuz.registry.get(name='user-playlist',id=self.NID)
#            if not node.remove_tracks(self.params['track-id']):
#                return False
#            xbmc.executebuiltin('Container.Refresh')
#            return True
#
#        elif self.MODE == Mode.LIBRARY_SCAN:
#            import urllib
#            s = 'UpdateLibrary("music", "' + urllib.unquote(self.params['url']) + '&action=scan")'
#            xbmc.executebuiltin(s)
#            return False
#        
#        
#        elif self.MODE == Mode.FAVORITE_DELETE:
#            from node.favorites import Node_favorites
#            node = Node_favorites(self, self.params)
#            if not node.remove():
#                notifyH('Qobuz Xbmc (i8n)', 'Cannot remove favorite')
#                return False
#            xbmc.executebuiltin('Container.Refresh')
#            return True
#        
#        elif self.MODE == Mode.TEST:
#            import xbmcgui

        else:
            raise QobuzXbmcError(who=self,what="unknow_mode", additional=self.MODE)
        return True
