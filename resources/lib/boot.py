'''
    boot
    ~~~~

    This file is part of qobuz-xbmc

    :copyright: (c) 2012 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
from xbmcpy.plugin import Plugin
from qobuz.node import getNode, Flag
from qobuz.cache import cache
from qobuz.api import api
from qobuz.xbmc import settings, ItemFactory
from qobuz.xbmc.player import Player
"""Main
"""
import os
plugin = Plugin('plugin.audio.qobuztest')
profile = plugin.profile()
cache.base_path = os.path.join(profile, 
                               plugin.plugin_id, 'cache')
api.pagination_limit = int(settings.get('pagination_limit'))
api.login(settings.get('username'), 
          settings.get('password'))    

renderer = None
#try:
if 1:
    import xbmc
    from node.renderer.xbmc import XbmcRenderer
    renderer = XbmcRenderer()
    renderer.itemFactory = ItemFactory()
    renderer.handle = plugin.handle()
    renderer.plugin_id = plugin.plugin_id
    renderer.whiteFlag = Flag.ALL
    renderer.player = Player(plugin=plugin)
#except Exception as e:
#    print "Outside of Xbmc: %s" % (e)
#    from node.renderer.console import ConsoleRenderer, ItemFactory
#    renderer = ConsoleRenderer()
#    renderer.itemFactory = ItemFactory()
#    renderer.whiteFlag = Flag.ALL

while renderer.alive:
        renderer.render(plugin.route(Flag, getNode), plugin)
        renderer.ask()


