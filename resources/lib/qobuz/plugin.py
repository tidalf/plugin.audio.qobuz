'''
    qobuz.plugin
    ~~~~~~~~~~~~

    :part_of: xbmc-qobuz
    :copyright: (c) 2012-2016 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
import os
import sys

from kodi_six import xbmc, xbmcaddon


class Plugin(object):
    def __init__(self, plugin_id):
        self.plugin_id = plugin_id
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

    def __str__(self):
        return '<Plugin id={plugin_id} addon_id={addon_id} version={version}>'\
            .format(plugin_id=self.plugin_id,
                    addon_id=self.get_addon_id(),
                    version=self.get_version())
