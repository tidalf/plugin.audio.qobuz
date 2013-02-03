from xbmcpy.plugin import Plugin
from node import url2dict
from qobuz.node import getNode, Flag
from qobuz.cache import cache
from qobuz.api import api
from qobuz.xbmc import makeItem, settings
from xbmcpy.directory import Directory

directory = None
def route_one(plugin, makeItem):
    global directory
    directory = Directory(handle=plugin.handle(), makeItem=makeItem, 
                      pluginId=plugin.plugin_id)
    root = plugin.route(Flag, getNode)
    root.populating(directory, depth=1, whiteFlag=Flag.ALL)
    directory.end()

"""Main
"""
import os
plugin = Plugin('plugin.audio.qobuztest')
profile = plugin.profile()
cache.base_path = os.path.join(profile, 
                               plugin.plugin_id, 'cache')
api.login(settings.get('username'), 
          settings.get('password'))    
directory = Directory(handle=plugin.handle(), makeItem=makeItem, 
                      pluginId=plugin.plugin_id)
alive = True
if directory.console:
    console = directory.console
    while alive:
        route_one(plugin, makeItem)
        command, arg1 = console.get_command()
        if command == 'view' and arg1 < len(directory):
            try:
                plugin._parameters = url2dict(directory[arg1].url())
            except:
                console.write('Invalid view command\n')
      
else:
    route_one(plugin, makeItem)

