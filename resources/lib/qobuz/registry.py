from os import path as P
from qobuz import base_path, data_path
from qobuz.util.converter import converter
from qobuz import debug

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
        self.paths = [
            P.join(data_path, 'qobuz.conf'),
            P.expanduser('/etc/qobuz/qobuz.conf'),
            P.expanduser('~/.config/qobuz/qobuz.conf'),
            P.expanduser('~/.qobuz/qobuz.conf')
        ]
        self.conf.read(self.paths)

    def get(self, key):
        return self.conf.get('main', key)

class XbmcRegistryBackend(IRegistryBackend):

    def __init__(self, application):
        super(XbmcRegistryBackend, self).__init__(application)

    def get(self, key):
        return self.application.addon.getSetting(key)

    def set(self, key, value):
        self.application.addon.setSetting(key, str(value))

class Registry(object):

    def __init__(self, application):
        self.application = application
        try:
            import xbmc
            self.backend = XbmcRegistryBackend(application)
        except ImportError:
            self.backend = RegistryBackend(application)

    def get(self, key, to='raw', default=None):
        return getattr(converter, to)(self.backend.get(key), default=default)

    def set(self, key, value):
        self.backend.set(key, value)

    def __getitem__(self, key):
        return self.backend.get(key)
