import os
from kodi_six import xbmc  # pylint:disable= E0401

from .base import BaseBootstrap
from qobuz import exception
from qobuz.constants import Mode
from qobuz.debug import getLogger
from qobuz.node import Flag
from qobuz.renderer import renderer
import qobuz.config as config

logger = getLogger(__name__)


class KodiBootstrap(BaseBootstrap):
    '''Set some boot properties
    and route query based on parameters
    '''

    def __init__(self, application):
        super(KodiBootstrap, self).__init__(application)

    def init_app(self):
        '''General bootstrap'''
        super(KodiBootstrap, self).init_app()
        self.bootstrap_registry()
        self.bootstrap_sys_args()

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
