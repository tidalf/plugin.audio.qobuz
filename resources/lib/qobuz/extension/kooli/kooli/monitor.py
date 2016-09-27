import time
import xbmc

class ServiceItem(object):
    def __init__(self, service, on_idle=False):
        self.service = service
        self.on_idle=on_idle

    def __getattr__(self, name, *a, **ka):
        return getattr(self.service, name, *a, **ka)

class Monitor(xbmc.Monitor):

    def __init__(self):
        super(Monitor, self).__init__()
        self.abortRequested = False
        self.garbage_refresh = 60
        self.last_garbage_on = time.time() - (self.garbage_refresh + 1)
        self.service = {}

    def onAbortRequested(self):
        self.abortRequested = True

    def add_service(self, service, on_idle=False):
        self.service[service.name] = ServiceItem(service, on_idle=on_idle)

    def is_garbage_time(self):
        if time.time() > (self.last_garbage_on + self.garbage_refresh):
            return True
        return False

    def isIdle(self, since=1):
        try:
            if xbmc.getGlobalIdleTime() >= since:
                return True
            return False
        except:
            return False

    def cache_remove_old(self, **ka):
        self.last_garbage_on = time.time()
        clean_old(cache)

    def onSettingsChanged(self):
        pass

    def start_all_service(self):
        [s.start() for s in self.service.values()]

    def stop_all_service(self):
        [s.stop() for s in self.service.values()]

    def step(self):
        if self.isIdle():
            [s.step() for s in self.service.values() if s.on_idle]
        else:
            [s.step() for s in self.service.values() if not s.on_idle]
