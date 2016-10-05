'''
    qobuz.bootstrap
    ~~~~~~~~~~~~~~~

    :part_of: xbmc-qobuz
    :copyright: (c) 2012-2016 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
import sys
import os

from qobuz.constants import Mode
from qobuz import debug
from qobuz.dog import dog
from qobuz.node import Flag
from qobuz import exception
from qobuz.gui.util import dialogLoginFailure, getSetting, containerRefresh
from qobuz.gui.util import dialogServiceTemporarilyUnavailable
import qobuz.config as config
from qobuz.cache import cache
from qobuz.renderer import renderer

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
                    debug.warn('[DOG]', "--- Invalid key: %s / value: %s" %
                         (splitparams[0], splitparams[1]))
    return rparam


class MinimalBootstrap(object):

    def __init__(self, application):
        config.addon = application.addon
        self.application = application
        self.handle = application.handle
        config.boot = self

    def init_app(self):
        self.bootstrap_directories()
        self.init_cache()

    def init_cache(self):
        cache.base_path = config.path.cache

    def bootstrap_registry(self):
        from qobuz.api import api
        api.stream_format = 6 if getSetting('streamtype') == 'flac' else 5
        if not api.login(getSetting('username'), getSetting('password')):
            if api.status_code == 503:
                dialogServiceTemporarilyUnavailable()
            else:
                dialogLoginFailure()
            #@TODO sys.exit killing XBMC? FRODO BUG ?
            # sys.exit(1)
            containerRefresh()
            raise exception.InvalidLogin(None)

    def bootstrap_directories(self):
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
                    os.path.join(config.path.resources, 'img', 'theme',
                                 'default'))

            def to_s(self):
                out = 'profile : ' + self.profile + "\n"
                out += 'cache   : ' + self.cache + "\n"
                out += 'resources: ' + self.resources + "\n"
                out += 'image   : ' + self.image + "\n"
                return out

            def mkdir(self, path):
                if not os.path.isdir(path):
                    try:
                        os.makedirs(path)
                    except:
                        debug.warn(self, "Cannot create directory: " + path)
                        exit(2)
        config.path = PathObject()
        config.path._set_dir()
        config.path.mkdir(config.path.cache)

    def bootstrap_sys_args(self):
        '''Store sys arguments'''
        self.MODE = None
        self.params = get_checked_parameters()
        if 'nt' not in self.params:
            self.params['nt'] = Flag.ROOT
            self.MODE = Mode.VIEW
        self.nodeType = int(self.params['nt'])
        try:
            self.MODE = int(self.params['mode'])
        except:
            debug.warn(self, "No 'mode' parameter")
        if getSetting('debug', asBool=True):
            for name in self.params:
                debug.info(self, "Param: %s = %s (%s)" % (name,
                                str(self.params[name]),
                                Flag.to_s(self.params['nt'])))

    def dispatch(self):
        '''Routing'''
        if self.MODE == Mode.PLAY:
            from qobuz.player import QobuzPlayer
            player = QobuzPlayer()
            if player.play(self.params['nid'],self.params):
                return True
            return False
        elif self.MODE == Mode.VIEW:
            r = renderer(self.nodeType, self.params)
            return r.run()
        elif self.MODE == Mode.VIEW_BIG_DIR:
            r = renderer(self.nodeType, self.params)
            r.whiteFlag = Flag.TRACK | Flag.ALBUM
            r.depth = -1
            return r.run()
        elif self.MODE == Mode.SCAN:
            r = renderer(self.nodeType, self.params, self.MODE)
            r.enable_progress = False
            r.whiteFlag = Flag.TRACK
            r.depth = -1
            return r.scan()
        else:
            raise exception.UnknownMode(self.MODE)
        return True


class Bootstrap(MinimalBootstrap):
    """Set some boot properties
    and route query based on parameters
    """

    def __init__(self, application):
        super(Bootstrap, self).__init__(application)

    def init_app(self):
        """General bootstrap
        """
        super(Bootstrap, self).init_app()
        self.bootstrap_registry()
        self.bootstrap_sys_args()
