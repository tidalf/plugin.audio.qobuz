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

__addon__ = xbmcaddon.Addon('plugin.audio.qobuz')

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
