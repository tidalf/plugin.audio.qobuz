'''
    qobuz.application
    ~~~~~~~~~~~~~~~~~

    :part_of: xbmc-qobuz
    :copyright: (c) 2012 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
import sys
from qobuz.exception import QobuzXbmcError
from qobuz.debug import warn
from qobuz.bootstrap import Bootstrap
from qobuz import config
from qobuz.registry import Registry

class Application(object):

    def __init__(self, plugin=None, bootstrapClass=Bootstrap):
        self.plugin = plugin
        self.registry = Registry(self)
        print('username %s' % self.registry.get('username'))
        config.app = self
        self.handle = 0
        if len(sys.argv) > 1:
            self.handle = int(sys.argv[1])
        self.bootstrap = bootstrapClass(self)

    def get_addon(self):
        if self.plugin is not None:
            return self.plugin.addon
        return None

    addon = property(get_addon)

    def start(self):
        try:
            self.bootstrap.init_app()
            self.bootstrap.dispatch()
        except QobuzXbmcError as e:
            warn('[' + pluginId + ']', "Exception while running plugin")
