'''
    qobuz.bootstrap
    ~~~~~~~~~~~~~~~

    :part_of: xbmc-qobuz
    :copyright: (c) 2012-2016 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
import os
import sys
from kodi_six import xbmc

from qobuz import exception
from qobuz.cache import cache
from qobuz.constants import Mode
from qobuz.debug import getLogger
from qobuz.dog import dog
from qobuz.gui.util import dialogLoginFailure, containerRefresh
from qobuz.gui.util import dialogServiceTemporarilyUnavailable
from qobuz.node import Flag
from qobuz.renderer import renderer
import qobuz.config as config

logger = getLogger(__name__)


def get_checked_parameters():
    '''Parse parameters passed to xbmc plugin as sys.argv
    '''
    d = dog()
    rparam = {}
    if len(sys.argv) <= 1:
        return rparam
    paramstring = sys.argv[2]
    if len(paramstring) >= 2:
        params = sys.argv[2]
        cleanedparams = params.replace('?', '')
        pairsofparams = cleanedparams.split('&')

        for i, _item in enumerate(pairsofparams):
            splitparams = pairsofparams[i].split('=')
            if (len(splitparams)) == 2:
                if d.kv_is_ok(splitparams[0], splitparams[1]):
                    rparam[splitparams[0]] = splitparams[1]
                else:
                    logger.warn('--- Invalid key: %s / value: %s' %
                                (splitparams[0], splitparams[1]))
    return rparam


class MinimalBootstrap(object):
    def __init__(self, application):
        config.addon = application.addon
        self.application = application
        self.handle = application.handle
        config.boot = self
        logger.info('---')

    def init_app(self):
        self.bootstrap_directories()
        self.init_cache()

    @classmethod
    def init_cache(cls):
        cache.base_path = config.path.cache

    @classmethod
    def bootstrap_registry(cls):
        from qobuz.api import api
        if not api.login(
                config.app.registry.get('username'),
                config.app.registry.get('password')):
            if api.status_code == 503:
                dialogServiceTemporarilyUnavailable()
            else:
                dialogLoginFailure()
            containerRefresh()
            raise exception.InvalidLogin(None)

    @classmethod
    def bootstrap_directories(cls):
        class PathObject:
            def __init__(self):
                self.base = config.addon.getAddonInfo('path')

            def _set_dir(self):
                profile = xbmc.translatePath('special://profile/')
                self.profile = os.path.join(profile, 'addon_data',
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

            @classmethod
            def mkdir(cls, path):
                if not os.path.isdir(path):
                    try:
                        os.makedirs(path)
                    except:
                        logger.warn('Cannot create directory: %s', path)
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
            logger.warn('No \"mode\" parameter')
        if config.app.registry.get('debug', to='bool'):
            for name in self.params:
                logger.info('Param: %s = %s (%s)', name, str(
                    self.params[name]), Flag.to_s(self.params['nt']))

    def dispatch(self):
        '''Routing'''
        if self.MODE == Mode.PLAY:
            from qobuz.player import QobuzPlayer
            player = QobuzPlayer()
            if player.play(self.params['nid'], self.params):
                return True
            return False
        elif self.MODE == Mode.VIEW:
            r = renderer(self.nodeType, self.params)
            return r.run()
        elif self.MODE == Mode.VIEW_BIG_DIR:
            r = renderer(
                self.nodeType,
                parameters=self.params,
                whiteFlag=Flag.TRACK | Flag.ALBUM,
                depth=-1)
            return r.run()
        elif self.MODE == Mode.SCAN:
            r = renderer(
                self.nodeType,
                parameters=self.params,
                mode=self.MODE,
                whiteFlag=Flag.TRACK,
                depth=-1)
            return r.scan()
        else:
            raise exception.UnknownMode(self.MODE)


class Bootstrap(MinimalBootstrap):
    '''Set some boot properties
    and route query based on parameters
    '''

    def __init__(self, application):
        super(Bootstrap, self).__init__(application)

    def init_app(self):
        '''General bootstrap'''
        super(Bootstrap, self).init_app()
        self.bootstrap_registry()
        self.bootstrap_sys_args()
