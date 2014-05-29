'''
    boot
    ~~~~

    This file is part of qobuz-xbmc

    :copyright: (c) 2012 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
from xbmcpy.plugin import Plugin
from pyobuz.node import getNode, Flag
from pyobuz.cache import cache
from pyobuz.api import api
from qobuz import settings, ItemFactory
"""Main
"""
import os
plugin = Plugin('plugin.audio.qobuz')
profile = plugin.profile()
cache.base_path = os.path.join(profile,
                               plugin.plugin_id, 'cache')
api.pagination_limit = int(settings['pagination_limit'])
api.login(settings['username'],
          settings['password'])

import xbmc  # @UnresolvedImport @UnusedImport
from qobuz.renderer import XbmcRenderer
from qobuz.commander import QobuzXbmcCommander
from qobuz.player import Player
renderer = XbmcRenderer(plugin,
                        QobuzXbmcCommander(Flag, getNode),
                        ItemFactory(),
                        Player(plugin=plugin))
renderer.render(plugin.route(Flag, getNode))
cache.delete_old()
