'''
    xbmcpy.plugin
    ~~~~~~~~~~~~~

    This file is part of qobuz-xbmc

    :copyright: (c) 2012 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
from mock import xbmcaddon
from mock.xbmc import xbmc

import sys, os
import pprint

def parse_parameters():
    """Parse parameters passed to xbmc plugin as sys.argv
    """
    rparam = {}
    if len(sys.argv) <= 1:
        return rparam
    paramstring = sys.argv[2]
    if len(paramstring) >= 2:
        params = sys.argv[2]
        cleanedparams = params.replace('?', '')
        if (params[len(params) - 1] == '/'):
            params = params[0:len(params) - 2]
        pairsofparams = cleanedparams.split('&')

        for i in range(len(pairsofparams)):
            splitparams = {}
            splitparams = pairsofparams[i].split('=')
            if (len(splitparams)) == 2:
                rparam[splitparams[0]] = splitparams[1]
    return rparam

class Plugin(object):
    """
    """
    def __init__(self, plugin_id):
        self.plugin_id = plugin_id
        self.addon = xbmcaddon.Addon
        xbmcaddon._addon_id_ = self.plugin_id
        self._parameters = parse_parameters()
        self.base_url = 'plugin://%s/' % (self.plugin_id)

    def handle(self):
        print "Sys %s" % (pprint.pformat(sys.argv))
        if len(sys.argv) < 2:
            return -1
        return int(sys.argv[1])

    def route(self, Flag, getNode):
        kind = self.parameter('kind')
        if kind is None:
            kind = Flag.ROOT
        else:
            kind = int(kind)
        return getNode(kind, self._parameters)

    def parameter(self, key):
        if not key in self._parameters:
            return None
        return self._parameters[key]

    def special_path(self, name):
        return xbmc.translatePath('special://%s/' % (name))

    def profile(self):
        profile = os.path.join(self.special_path('profile'), 'addon_data')
        return profile
