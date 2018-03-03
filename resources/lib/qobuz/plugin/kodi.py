'''
    qobuz.plugin.kodi
    ~~~~~~~~~~~~~~~~~

    :part_of: xbmc-qobuz
    :copyright: (c) 2012-2016 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
from kodi_six import xbmc, xbmcaddon
import os

from .base import PluginBase


class KodiPlugin(PluginBase):
    def __init__(self, plugin_id):
        super(KodiPlugin, self).__init__(plugin_id=plugin_id)
        self.addon = xbmcaddon.Addon(id=self.plugin_id)

    def get_version(self):
        return self.addon.getAddonInfo('version')

    def get_addon_id(self):
        return self.addon.getAddonInfo('id')

    def get_addon_path(self):
        return self.addon.getAddonInfo('path')

    def get_lib_path(self):
        return xbmc.translatePath(
            os.path.join(self.get_addon_path(), 'resources', 'lib'))

    def get_qobuz_path(self):
        return xbmc.translatePath(os.path.join(self.get_lib_path(), 'qobuz'))
