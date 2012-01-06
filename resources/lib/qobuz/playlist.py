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

import os
import sys
import xbmc
import xbmcgui
import xbmcplugin

from icacheable import ICacheable
from utils import _sc
from constants import *
from constants import __addon__
from mydebug import * 
from easytag import QobuzTagPlaylist

'''
    Class QobuzPLaylist
'''
class QobuzPlaylist(ICacheable):

    def __init__(self,qob,id):
        self.Qob = qob
        self.id = id
        self._raw_data = []
        self.cache_path = os.path.join(
                                        self.Qob.cacheDir,
                                        'playlist-' + str(self.id) + '.dat')
        self.cache_refresh = __addon__.getSetting('cache_duration_userplaylist')
        info(self, "Cache duration: " + str(self.cache_refresh))
        self.fetch_data()

    def _fetch_data(self):
        data = self.Qob.Api.get_playlist(self.id)['playlist']
        return data

    def length(self):
        return len(self._raw_data['tracks'])

    def add_to_directory(self):
        n = self.length()
        h = int(sys.argv[1])
        xp = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
        p = QobuzTagPlaylist(self.get_data())
        for t in p.get_tracks():
            if t.streaming_type and t.streaming_type != "full":
                warn(self, "Skipping sample " + t.getTitle())
                continue
            u = sys.argv[0] + "?mode=" + str(MODE_SONG) + "&id=" + t.id
            label = t.get_album().getTitle() + ' - ' + t.getLabel()
            item = xbmcgui.ListItem(label)
            item.setLabel(label)
            item.setInfo(type="Music",infoLabels={
                                                   "count": int(self.id),
                                                   "title":  t.getTitle(),
                                                   "artist": t.getArtist(),
                                                   "album": t.get_album().getTitle(),
                                                   "tracknumber": int(t.track_number),
                                                   "genre": t.get_album().getGenre(),
                                                   "comment": "Qobuz Stream",
                                                   "duration": t.getDuration(),
                                                   "year": t.get_album().getYear()
                                                   })
            item.setPath(u)
            item.setProperty('Music','true')
            item.setProperty('IsPlayable','true');
            item.setProperty('mimetype','audio/flac')
            image = t.get_album().getImage()
            item.setIconImage(image)
            item.setThumbnailImage(image)
            
            xbmcplugin.addDirectoryItem(handle=h ,url=u ,listitem=item,isFolder=False,totalItems=n)
            xp.add(u, item)
        xbmcplugin.setContent(h,'songs')
