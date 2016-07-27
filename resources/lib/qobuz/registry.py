from os import path as P
from qobuz import base_path, data_path
from qobuz.debug import log

class IRegistryBackend(object):

    def __init__(self, application):
        self.application = application

    def get(self, key):
        raise NotImplementedError('get')

class RegistryBackend(IRegistryBackend):

    def __init__(self, application):
        super(RegistryBackend, self).__init__(application)
        self._init()

    def _get_setting_path(self):
        return P.abspath(P.join(base_path, P.pardir, 'settings.xml'))

    def _init(self):
        import ConfigParser
        self.conf = ConfigParser.ConfigParser()
        self.paths = [P.join(data_path, 'qobuz.conf')]
        self.conf.read(self.paths)

    def get(self, key):
        return self.conf.get('main', key)

class XbmcRegistryBackend(IRegistryBackend):

    def __init__(self, application):
        super(XbmcRegistryBackend, self).__init__(application)

    def get(self, key):
        return self.application.addon.getSetting(key)

class Registry(object):

    def __init__(self, application):
        self.application = application
        try:
            import xbmc
            self.backend = XbmcRegistryBackend(application)
        except ImportError:
            self.backend = RegistryBackend(application)

    def get(self, key):
        return self.backend.get(key)

    def __getitem__(self, key):
        return self.backend.get(key)
