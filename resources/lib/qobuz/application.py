'''
    qobuz.application
    ~~~~~~~~~~~~~~~~~

    :part_of: xbmc-qobuz
    :copyright: (c) 2012-2016 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
import sys
from qobuz import exception
from qobuz import debug
from qobuz.bootstrap import Bootstrap
from qobuz import config
from qobuz.registry import Registry

class Application(object):

    def __init__(self, plugin=None, bootstrapClass=Bootstrap):
        self.plugin = plugin
        self.registry = Registry(self)
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
        except exception.QobuzError as e:
            debug.warn('[' + self.plugin.plugin_id + ']',
                       'Exception while running plugin')
