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