# Copyright 2011 Joachim Basmaison, Cyril Leclerc

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
import xbmcgui
import xbmcplugin
from utils import _sc
from constants import *
from mydebug import log, info, warn
from easytag import QobuzTagTrack

###############################################################################
# Class QobuzSearchTracks 
###############################################################################
class QobuzSearchTracks():

    def __init__(self, Core):
        self.Core = Core
        self._raw_data = {}
        
    def search(self, query, limit = 100):
        self._raw_data = self.Core.Api.search_tracks(query, limit)
        return self
        
    def length(self):
        if not self._raw_data['results']:
            return 0
        return len(self._raw_data['results']['tracks'])
    
    def add_to_directory(self):
        n = self.length()
        h = int(sys.argv[1])
        pprint.pprint(self._raw_data)
        for track in self._raw_data['results']['tracks']:
            t = QobuzTagTrack(track)
            if t.streaming_type != 'full':
                warn(self, "Skipping sample " + t.title)
                continue
            u = sys.argv[0] + "?mode=" + str(MODE_SONG) + "&id=" + t.id
            item = xbmcgui.ListItem('test')
            item.setLabel(t.getLabel())
            item.setInfo(type="Music",infoLabels={
                                                   #"count":+,
                                                   "title":  t.getTitle(),
                                                   "artist": t.getArtist(),
                                                   "album": t.get_album().getTitle(),
                                                   "tracknumber": int(t.track_number),
                                                   "genre": t.get_album().getGenre(),
                                                   "comment": "Qobuz Stream",
                                                   "duration": int(t.getDuration()),
                                                   "year": int(t.get_album().getYear())
                                                   })
            item.setPath(u)
            item.setProperty('Music','true')
            item.setProperty('IsPlayable','true');
            item.setProperty('mimetype','audio/flac')
            image = t.get_album().getImage()
            item.setThumbnailImage(image)
            item.setIconImage(image)
            xbmcplugin.addDirectoryItem(handle=h ,url=u ,listitem=item,isFolder=False,totalItems=n)


