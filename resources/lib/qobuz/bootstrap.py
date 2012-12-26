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
from node.flag import NodeFlag

from exception import QobuzXbmcError
import json
import pprint

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


class XbmcRPC:
    def __init__(self):
        pass
    
    def send(self, request):
        if not request: raise QobuzXbmcError(who=self, what='missing_parameter', additional='request')
        request['jsonrpc'] = '2.0'
        request['method'] = 'JSONRPC.' + request['method']
        if not 'id' in request: request['id'] = 1
        rjson = json.dumps(request)
        print 'REQUEST: ' + rjson
        ret = xbmc.executeJSONRPC(rjson)
        return ret

    def ping(self):
        request = {
                   'method': 'Ping',
        }
        return self.send(request)
        
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
        self.bootstrap_lang()
        self.bootstrap_utils()
        self.bootstrap_gui()
        self.bootstrap_registry()
        self.bootstrap_sys_args()
        

    def bootstrap_lang(self):
        qobuz.lang = qobuz.addon.getLocalizedString

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
            qobuz.gui.show_login_failure()
            #@TODO sys.exit killing XBMC? FRODO BUG ?
            #sys.exit(1)
            raise QobuzXbmcError(who=self, what='invalid_login', additional=None)
            
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
                s.profile = os.path.join(xbmc.translatePath('special://profile/'), 'addon_data', qobuz.addon.getAddonInfo('id'))
                s.cache = os.path.join(s.profile, 'cache')
                s.resources = xbmc.translatePath(os.path.join(qobuz.path.base, 'resources'))
                s.image = xbmc.translatePath(os.path.join(qobuz.path.resources, 'img'))
            def to_s(s):
                out = 'profile : ' + s.profile + "\n"
                out += 'cache   : ' + s.cache + "\n"
                out += 'resources: ' + s.resources + "\n"
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

    def bootstrap_gui(self):
        from gui.utils import Utils
        qobuz.gui = Utils()

    def bootstrap_player(self):
        from player import QobuzPlayer
        qobuz.player = QobuzPlayer()


    '''
        Parse system parameters
    '''
    def bootstrap_sys_args(self):
        self.MODE = None
        self.params = get_params()
        if not 'nt' in self.params:
            self.params['nt'] = NodeFlag.TYPE_ROOT
            self.MODE = Mode.VIEW
        self.NT = int(self.params['nt'])
        ''' 
        set mode 
        '''
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
        from utils.cache_manager import cache_manager
        cm = cache_manager()
        cm.delete_all_data()


    '''
        Execute methode based on MODE
    '''
    def dispatch(self):
        import pprint, xbmc
        import time
        ret = False

        debug(self, "Mode: %s, Node: %s" % (Mode.to_s(self.MODE), NodeFlag.to_s(int(self.params['nt']))))

        ''' PLAY '''
        if self.MODE == Mode.PLAY:
            debug(self, "Playing song")
            self.bootstrap_player()
#            if qobuz.addon.getSetting('notification_playingsong') == 'true':
#                qobuz.gui.notify(34000, 34001)
            try:
                context_type = urllib.unquote(self.params["context_type"])
            except:
                context_type = "playlist"
            if qobuz.player.play(self.NID):
                return True
            return False

        # ERASE CACHE
        elif self.MODE == Mode.ERASE_CACHE:
            import xbmcgui
            ok = xbmcgui.Dialog().yesno('Remove cached data',
                          'Do you really want to erase all cached data')
            if not ok:
                info(self, "Deleting cached data aborted")
                return False
            self.erase_cache()
            qobuz.gui.notifyH("Qobuz cache", "All cached data removed")
            return True

        from renderer.xbmc import Xbmc_renderer as renderer
        ''' SET Node type '''
        nt = None
        try: nt = int(self.params['nt'])
        except:
            warn(self, "No node type...abort")
            return False
        debug(self, "Node type: " + str(nt))
        ''' SET Node id '''
        id = None
        try: id = self.params['nid']
        except: pass

        ''' UGLY MODE DISPATCH '''
        if self.MODE == Mode.VIEW:
            r = renderer(nt, id)
            r.set_depth(1)
            r.set_filter(NodeFlag.TYPE_NODE | NodeFlag.DONTFETCHTRACK)
            return r.display()

        elif self.MODE == Mode.VIEW_BIG_DIR:
            r = renderer(nt, id)
            r.set_depth(-1)
            r.set_filter(NodeFlag.TYPE_TRACK | NodeFlag.DONTFETCHTRACK)
            return r.display()

        elif self.MODE == Mode.SCAN:
            r = renderer(nt, id)
            r.set_depth(-1)
            r.set_filter(NodeFlag.DONTFETCHTRACK)
            return r.scan()

        elif self.MODE == Mode.PLAYLIST_SELECT_CURRENT:
            from  node.user_playlists import Node_user_playlists
            node = Node_user_playlists()
            if node.set_current_playlist(self.params['nid']):
                return False
            xbmc.executebuiltin('Container.Refresh')
            return True

        elif self.MODE == Mode.PLAYLIST_CREATE:
            from  node.user_playlists import Node_user_playlists
            node = Node_user_playlists()
            if not node.create_playlist():
                qobuz.gui.notify(30078, 30046)
                return False
            xbmc.executebuiltin('Container.Refresh')
            return True

        elif self.MODE == Mode.PLAYLIST_ADD_TO_CURRENT:
            from  node.playlist import Node_playlist
            node = Node_playlist(None, self.params)
            if not node.add_to_current_playlist():
                return False
            return True

        elif self.MODE == Mode.FAVORITES_ADD_TO_CURRENT:
            from  node.favorites import Node_favorites
            node = Node_favorites(None, self.params)
            if not node.add_to_favorites():
                return False
            return True

        elif self.MODE == Mode.PLAYLIST_ADD_AS_NEW:
            from  node.playlist import Node_playlist
            node = Node_playlist(None, self.params)
            if not node.add_as_new_playlist():
                return False
            return True
        
        elif self.MODE == Mode.PLAYLIST_RENAME:
            from  node.user_playlists import Node_user_playlists
            node = Node_user_playlists()
            if not node.rename_playlist(self.NID):
                return False
            xbmc.executebuiltin('Container.Refresh')
            return True

        elif self.MODE == Mode.PLAYLIST_REMOVE:
            from node.user_playlists import Node_user_playlists
            node = Node_user_playlists()
            if not node.remove_playlist(self.NID):
                return False
            xbmc.executebuiltin('Container.Refresh')
            return True

        elif self.MODE == Mode.PLAYLIST_REMOVE_TRACK:
            from node.playlist import Node_playlist
            node = Node_playlist(None, self.params)
            node.set_id(self.NID)
            node.set_data(qobuz.registry.get(name='user-playlist',id=self.NID))
            if not node.remove_tracks(self.params['track-id']):
                return False
            xbmc.executebuiltin('Container.Refresh')
            return True

        elif self.MODE == Mode.LIBRARY_SCAN:
            import urllib
            s = 'UpdateLibrary("music", "' + urllib.unquote(self.params['url']) + '&action=scan")'
            xbmc.executebuiltin(s)
            return False

        else:
            error(self, "Unknow mode: " + str(self.MODE))
            return False

        return True
