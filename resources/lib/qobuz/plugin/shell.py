'''
    qobuz.plugin.shell
    ~~~~~~~~~~~~~~~~~~

    :part_of: xbmc-qobuz
    :copyright: (c) 2012-2016 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
import os
from os import path as Path

from .base import PluginBase
from qobuz import base_path


class ShellPlugin(PluginBase):
    def __init__(self, plugin_id):
        super(ShellPlugin, self).__init__(plugin_id=plugin_id)

    def get_version(self):
        return '0.1'

    def get_addon_id(self):
        return 'qobuz-shell'

    def get_addon_path(self):
        return base_path

    def get_lib_path(self):
        return os.path.join(base_path, 'resources', 'lib')

    def get_qobuz_path(self):
        return os.path.join(self.get_lib_path(), 'qobuz')
