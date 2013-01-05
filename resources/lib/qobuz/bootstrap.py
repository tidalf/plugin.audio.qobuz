#     Copyright 2011 Joachim Basmaison, Cyril Leclerc
#
#     This file is part of xbmc-qobuz.
#
#     xbmc-qobuz is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     xbmc-qobuz is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.   See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with xbmc-qobuz.   If not, see <http://www.gnu.org/licenses/>.
import sys
import os

import urllib
import json
import pprint

import xbmc

from constants import Mode
from debug import info, debug, warn, error
from dog import dog
import qobuz
from node.flag import NodeFlag as Flag
from exception import QobuzXbmcError
from gui.util import notifyH, notify, dialogLoginFailure, getImage, yesno, containerRefresh

''' Arguments parssing '''


def get_params():
    d = dog()
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
                debug('QobuzDog',
                      "Checking script parameter: " + splitparams[0])
                if d.kv_is_ok(splitparams[0], splitparams[1]):
                    rparam[splitparams[0]] = splitparams[1]
                else:
                    warn('[DOG]', "--- Invalid key: %s / value: %s" %
                         (splitparams[0], splitparams[1]))
    return rparam


'''
    QobuzBootstrap
'''


class QobuzBootstrap(object):

    def __init__(self, __addon__, __handle__):
        qobuz.addon = __addon__
        self.handle = __handle__
        qobuz.boot = self

    ''' BOTTSTRAP App '''
    def bootstrap_app(self):
        from xbmcrpc import XbmcRPC
        self.bootstrap_directories()
        self.bootstrap_registry()
        self.bootstrap_sys_args()
        qobuz.rpc = XbmcRPC()

    ''' BOTTSTRAP Registry '''
    def bootstrap_registry(self):
        from registry import QobuzRegistry
        streamFormat = 6 if qobuz.addon.getSetting(
            'streamtype') == 'flac' else 5
        cacheDurationMiddle = int(
            qobuz.addon.getSetting('cache_duration_middle')) * 60
        cacheDurationLong = int(
            qobuz.addon.getSetting('cache_duration_long')) * 60
        try:
            qobuz.registry = QobuzRegistry(
                cacheType='default',
                username=qobuz.addon.getSetting(
                    'username'),
                password=qobuz.addon.getSetting(
                    'password'),
                basePath=qobuz.path.cache,
                streamFormat=streamFormat, 
                hashKey=True,
                cacheMiddle=cacheDurationMiddle,
                cacheLong=cacheDurationLong
            )
            qobuz.registry.get(name='user')
            qobuz.api = qobuz.registry.get_api()
        except QobuzXbmcError:
            dialogLoginFailure()
            #@TODO sys.exit killing XBMC? FRODO BUG ?
            # sys.exit(1)
            containerRefresh()
            raise QobuzXbmcError(
                who=self, what='invalid_login', additional=None)

    ''' BOTTSTRAP Directories '''
    def bootstrap_directories(self):
        class PathObject ():
            def __init__(self):
                self.base = qobuz.addon.getAddonInfo('path')

            def _set_dir(self):
                self.profile = os.path.join(xbmc.translatePath('special://profile/'),
                                            'addon_data',
                                            qobuz.addon.getAddonInfo('id'))
                self.cache = os.path.join(self.profile, 'cache')
                self.resources = xbmc.translatePath(
                    os.path.join(qobuz.path.base, 'resources'))
                self.image = xbmc.translatePath(
                    os.path.join(qobuz.path.resources, 'img'))

            def to_s(self):
                out = 'profile : ' + self.profile + "\n"
                out += 'cache   : ' + self.cache + "\n"
                out += 'resources: ' + self.resources + "\n"
                out += 'image   : ' + self.image + "\n"
                return out
            '''
            Make dir
            '''
            def mkdir(self, dir):
                if not os.path.isdir(dir):
                    try:
                        os.makedirs(dir)
                    except:
                        warn("Cannot create directory: " + dir)
                        exit(2)
                    info(self, "Directory created: " + dir)
        qobuz.path = PathObject()
        qobuz.path._set_dir()
        qobuz.path.mkdir(qobuz.path.cache)

    ''' BOTTSTRAP Debug '''
    def bootstrap_debug(self):
        from debug import log, warn, error, info

        class DebugObject():
            def __init__(self):
                self.log = log
                self.warn = warn
                self.error = error
                self.info = info
        qobuz.debug = DebugObject()

    ''' BOTTSTRAP Player '''
    def bootstrap_player(self):
        from player import QobuzPlayer
        qobuz.player = QobuzPlayer()

    ''' BOOTSTRAP Parse system parameters '''
    def bootstrap_sys_args(self):
        self.MODE = None
        self.params = get_params()
        if not 'nt' in self.params:
            self.params['nt'] = Flag.ROOT
            self.MODE = Mode.VIEW
        self.nodeType = int(self.params['nt'])
        try:
            self.MODE = int(self.params['mode'])
        except:
            warn(self, "No 'mode' parameter")
        for p in self.params:
            debug(self, "Param: " + p + ' = ' + str(self.params[p]))

    def erase_cache(self):
        qobuz.registry.delete_by_name('^.*\.dat$')

    '''
       Dispatch
    '''
    def dispatch(self):
        info(self, "Mode: %s, Node: %s" % (Mode.to_s(self.MODE),
              Flag.to_s(int(self.params['nt']))))
        info(self, "Parameters:\n %s" % (pprint.pformat(self.params) ))
         
        if self.MODE == Mode.PLAY:
            debug(self, "Playing song")
            self.bootstrap_player()
            if qobuz.player.play(self.params['nid']):
                return True
            return False

        from util import getRenderer

        if self.MODE == Mode.VIEW:
            r = getRenderer(self.nodeType, self.params)
            return r.run()
        elif self.MODE == Mode.VIEW_BIG_DIR:
            r = getRenderer(self.nodeType, self.params)
            r.whiteFlag = Flag.TRACK | Flag.PRODUCT
            r.depth = -1
            return r.run()
        elif self.MODE == Mode.SCAN:
            r = getRenderer(self.nodeType, self.params)
            r.depth = -1
            return r.scan()
        else:
            raise QobuzXbmcError(
                who=self, what="unknow_mode", additional=self.MODE)
        return True
