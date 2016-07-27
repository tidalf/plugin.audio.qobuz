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

class Application(object):

    def __init__(self, plugin):
        config.app = self
        self.plugin = plugin
        self.handle = int(sys.argv[1])
        self.bootstrap = Bootstrap(self.plugin.addon, self.handle)

    def get_addon(self):
        return self.plugin.addon

    addon = property(get_addon)

    def start(self):
        try:
            self.bootstrap.init_app()
            self.bootstrap.dispatch()
        except QobuzXbmcError as e:
            warn('[' + pluginId + ']', "Exception while running plugin")
