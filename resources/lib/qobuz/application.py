'''
    qobuz.application
    ~~~~~~~~~~~~~~~~~

    :part_of: xbmc-qobuz
    :copyright: (c) 2012-2016 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
import sys

from qobuz import config
from qobuz.bootstrap import Bootstrap
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

    def __enter__(self):
        return self

    def __exit__(self, *a, **ka):
        self.plugin = None

    def get_addon(self):
        if self.plugin is not None:
            return self.plugin.addon
        return None

    addon = property(get_addon)

    def start(self):
        self.bootstrap.init_app()
        self.bootstrap.dispatch()
