'''
    qobuz.bootstrap
    ~~~~~~~~~~~~~~~

    :part_of: xbmc-qobuz
    :copyright: (c) 2012-2016 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
import os
import sys

from .utils import get_checked_parameters
from qobuz import exception
from qobuz.cache import cache
from qobuz.constants import Mode
from qobuz.debug import getLogger
from qobuz.gui.util import dialogLoginFailure, containerRefresh
from qobuz.gui.util import dialogServiceTemporarilyUnavailable
from qobuz.node import Flag
import qobuz.config as config

logger = getLogger(__name__)


class BaseBootstrap(object):
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
        raise NotImplementedError()

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
        raise NotImplementedError()
