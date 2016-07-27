'''
    qobuz.bootstrap
    ~~~~~~~~~~~~~~~

    :part_of: xbmc-qobuz
    :copyright: (c) 2012 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
import sys
import os

from qobuz.constants import Mode
from qobuz.debug import info, debug, warn
from qobuz.dog import dog
from qobuz.node import Flag
from qobuz.exception import QobuzXbmcError
from qobuz.gui.util import dialogLoginFailure, getSetting, containerRefresh
from qobuz.gui.util import dialogServiceTemporarilyUnavailable
import qobuz.config as config
from qobuz.cache import cache


def get_checked_parameters():
    """Parse parameters passed to xbmc plugin as sys.argv
    """
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
                if d.kv_is_ok(splitparams[0], splitparams[1]):
                    rparam[splitparams[0]] = splitparams[1]
                else:
                    warn('[DOG]', "--- Invalid key: %s / value: %s" %
                         (splitparams[0], splitparams[1]))
    return rparam


class Bootstrap(object):
    """Set some boot properties
    and route query based on parameters
    """

    def __init__(self, __addon__, __handle__):
        config.addon = __addon__
        self.handle = __handle__
        config.boot = self

    def init_app(self):
        """General bootstrap
        """
        from xbmcrpc import XbmcRPC
        self.bootstrap_directories()
        self.bootstrap_registry()
        self.bootstrap_sys_args()
        config.rpc = XbmcRPC()

    def bootstrap_registry(self):
        from qobuz.api import api
        cache.base_path = config.path.cache
        api.stream_format = 6 if getSetting('streamtype') == 'flac' else 5
        if not api.login(getSetting('username'), getSetting('password')):
            if api.status_code == 503:
                dialogServiceTemporarilyUnavailable()
            else:
                dialogLoginFailure()
            #@TODO sys.exit killing XBMC? FRODO BUG ?
            # sys.exit(1)
            containerRefresh()
            raise QobuzXbmcError(
                who=self, what='invalid_login', additional=None)

    def bootstrap_directories(self):
        """Setting some common path used by our application
            cache, image...
        """
        import xbmc  # @UnresolvedImport

        class PathObject ():

            def __init__(self):
                self.base = config.addon.getAddonInfo('path')

            def _set_dir(self):
                profile = xbmc.translatePath('special://profile/')
                self.profile = os.path.join(profile,
                                            'addon_data',
                                            config.addon.getAddonInfo('id'))
                self.cache = os.path.join(self.profile, 'cache')
                self.resources = xbmc.translatePath(
                    os.path.join(config.path.base, 'resources'))
                self.image = xbmc.translatePath(
                    os.path.join(config.path.resources, 'img'))

            def to_s(self):
                out = 'profile : ' + self.profile + "\n"
                out += 'cache   : ' + self.cache + "\n"
                out += 'resources: ' + self.resources + "\n"
                out += 'image   : ' + self.image + "\n"
                return out
            '''
            Make dir
            '''

            def mkdir(self, path):
                if not os.path.isdir(path):
                    try:
                        os.makedirs(path)
                    except:
                        warn("Cannot create directory: " + path)
                        exit(2)
                    info(self, "Directory created: " + path)
        config.path = PathObject()
        config.path._set_dir()
        config.path.mkdir(config.path.cache)

    def bootstrap_sys_args(self):
        """Parsing sys arg parameters and store them
        """
        self.MODE = None
        self.params = get_checked_parameters()
        if 'nt' not in self.params:
            self.params['nt'] = Flag.ROOT
            self.MODE = Mode.VIEW
        self.nodeType = int(self.params['nt'])
        try:
            self.MODE = int(self.params['mode'])
        except:
            warn(self, "No 'mode' parameter")
        for name in self.params:
            info(self, "Param: %s = %s (%s)" % (name, str(self.params[name]),
                                                Flag.to_s(self.params['nt'])))

    def dispatch(self):
        """Routing based on parameters
        """
        if self.MODE == Mode.PLAY:
            from player import QobuzPlayer
            debug(self, "Playing song")
            player = QobuzPlayer()
            if player.play(self.params['nid'],self.params):
                return True
            return False

        from renderer import renderer

        if self.MODE == Mode.VIEW:
            r = renderer(self.nodeType, self.params)
            return r.run()
        elif self.MODE == Mode.VIEW_BIG_DIR:
            r = renderer(self.nodeType, self.params)
            r.whiteFlag = Flag.TRACK | Flag.ALBUM
            r.depth = -1
            return r.run()
        elif self.MODE == Mode.SCAN:
            r = renderer(self.nodeType, self.params)
            r.enable_progress = False
            r.whiteFlag = Flag.TRACK
            r.depth = -1
            return r.scan()
        else:
            raise QobuzXbmcError(
                who=self, what="unknow_mode", additional=self.MODE)
        return True
