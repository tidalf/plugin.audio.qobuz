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
import xbmc

class QobuzPlayer(xbmc.Player):
    def __init__(self, type):
        super(QobuzPlayer, self).__init__(type)
        self.id = None
        self.last_id = None
        self.Qob = None

    def setApi (self, qob):
        self.Qob = qob
        
    def onPlayBackEnded(self):
        self.Qob.Api.report_streaming_stop(self.id)

    def set_track_id(self, id):
        if self.id:
            self.last_id = self.id
        self.id = id

    def watchPlayback( self ):
        while(self.isPlayingAudio()):
            info (self,"Watching Playback...")
            xbmc.sleep(6000)
        info (self,"End of Playback detected")
        exit(0)