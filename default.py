#     Copyright 2011 Stephen Denham, Joachim Basmaison, Cyril Leclerc
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


#sys.exit(1)
'''
 Bootstrap
'''
import os
import sys
import xbmcaddon
import xbmc

__addon__        = xbmcaddon.Addon()
__addonversion__ = __addon__.getAddonInfo('version')
__addonid__      = __addon__.getAddonInfo('id')
__cwd__          = __addon__.getAddonInfo('path')

#Player = xbmc.Player()
#Playlist = xbmc.PlayList(0)
#__scriptid__ = "script.audio.qobuz"
#__scriptname__ = "Qobuz"
#__author__ = "Solver"
#__url__ = "http://code.google.com/p/grooveshark-for-xbmc/"
#__svn_url__ = ""
#__credits__ = ""
#__XBMC_Revision__ = "31000"
#
#try: #It's an XBOX/pre-dharma
#    __cwd__ = os.getcwd()
#    __settings__ = xbmc.Settings(path=__cwd__)
#    __language__ = xbmc.Language(__cwd__.replace( ";", "" )).getLocalizedString
#    __debugging__ = __settings__.getSetting("debug")
#    __isXbox__ = True
#    __version__ = "0.3.1"
#    BASE_RESOURCE_PATH = xbmc.translatePath(os.path.join(__cwd__, 'resources', 'lib' ))
#    print 'GrooveShark: Initialized as a XBOX plugin'
#
#except: #It's post-dharma
#    import xbmcaddon
#    __settings__ = xbmcaddon.Addon(id=__scriptid__)
#    __language__ = __settings__.getLocalizedString
#    __debugging__ = __settings__.getSetting("debug")
#    __isXbox__ = False
#    __version__ = __settings__.getAddonInfo('version')
#    BASE_RESOURCE_PATH = xbmc.translatePath(os.path.join(__settings__.getAddonInfo('path'), 'resources', 'lib' ))
#    __cwd__ = __settings__.getAddonInfo('path')
#    print 'GrooveShark: Initialized as a post-dharma plugin'
    #traceback.print_exc()
    

addonDir  = __addon__.getAddonInfo('path')
libDir = xbmc.translatePath(os.path.join(addonDir, 'resources', 'lib'))
sys.path.append(libDir)
from qobuz.bootstrap import *
Core = QobuzBootstrap(__addon__, int(sys.argv[1]))
Core.parse_sys_args()
Core.mode_dispatch()
print "Script ENDED"

## Mark song as playing or played
#def markSong(songid, duration, streamKey, streamServerID):
#     global songMarkTime
#     global playTimer
#     global player
#     if player.isPlayingAudio():
#          tNow = player.getTime()
#          if tNow >= STREAM_MARKING_TIME and songMarkTime == 0:
#                # SHO #
#                #groovesharkApi.markStreamKeyOver30Secs(streamKey, streamServerID)
#                # SHO #
#                songMarkTime = tNow
#          elif duration > tNow and duration - tNow < 2 and songMarkTime >= STREAM_MARKING_TIME:
#                playTimer.cancel()
#                songMarkTime = 0
#                # SHO #
#                #groovesharkApi.markSongComplete(songid, streamKey, streamServerID)
#                # SHO #
#     else:
#          playTimer.cancel()
#          songMarkTime = 0
#

#class _Info:
#     def __init__( self, *args, **kwargs ):
#          self.__dict__.update( kwargs )

#class PlayTimer(Thread):
#     # interval -- floating point number specifying the number of seconds to wait before executing function
#     # function -- the function (or callable object) to be executed
#
#     # iterations -- integer specifying the number of iterations to perform
#     # args -- list of positional arguments passed to function
#     # kwargs -- dictionary of keyword arguments passed to function
#
#     def __init__(self, interval, function, iterations=0, args=[], kwargs={}):
#          Thread.__init__(self)
#          self.interval = interval
#          self.function = function
#          self.iterations = iterations
#          self.args = args
#          self.kwargs = kwargs
#          self.finished = Event()
#
#     def run(self):
#          count = 0
#          while not self.finished.isSet() and (self.iterations <= 0 or count < self.iterations):
#                self.finished.wait(self.interval)
#                if not self.finished.isSet():
#                     self.function(*self.args, **self.kwargs)
#                     count += 1
#
#     def cancel(self):
#          self.finished.set()
#
#     def setIterations(self, iterations):
#          self.iterations = iterations
#
#
#     def getTime(self):
#          return self.iterations * self.interval
