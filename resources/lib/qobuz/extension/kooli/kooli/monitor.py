'''
    qobuz.extension.kooli.monitor
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :part_of: kodi-qobuz
    :copyright: (c) 2012-2016 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
import time
from kodi_six import xbmc  # pylint:disable=E0401

from qobuz.cache import cache_util
from qobuz.debug import getLogger

logger = getLogger(__name__)


class ServiceItem(object):
    def __init__(self, service, on_idle=False):
        self.service = service
        self.on_idle = on_idle

    def __getattr__(self, name, *a, **ka):
        return getattr(self.service, name, *a, **ka)


class Monitor(xbmc.Monitor):
    def __init__(self):
        super(Monitor, self).__init__()
        self.abortRequested = False
        self.garbage_refresh = 60
        self.last_garbage_on = time.time() - (self.garbage_refresh + 1)
        self.service = {}

    @staticmethod
    def onSettingsChanged():
        logger.info('Setting changed: %s')  # @todo Do Something

    def onAbortRequested(self):
        self.abortRequested = True

    def add_service(self, service, on_idle=False):
        self.service[service.name] = ServiceItem(service, on_idle=on_idle)

    def is_garbage_time(self):
        if time.time() > (self.last_garbage_on + self.garbage_refresh):
            return True
        return False

    @classmethod
    def isIdle(cls, since=1):
        try:
            if xbmc.getGlobalIdleTime() >= since:
                return True
            return False
        except Exception as e:
            logger.warn('getGlobalIdleTimeException %s', e)
            return False

    def cache_remove_old(self, **ka):
        self.last_garbage_on = time.time()
        cache_util.clean_old(self)

    def start_all_service(self):
        _ = [s.start() for s in self.service.values()]

    def stop_all_service(self):
        _ = [s.stop() for s in self.service.values()]

    def step(self):
        if self.isIdle():
            _ = [s.step() for s in self.service.values() if s.on_idle]
        else:
            _ = [s.step() for s in self.service.values() if not s.on_idle]
