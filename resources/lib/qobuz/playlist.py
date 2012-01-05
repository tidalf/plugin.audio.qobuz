import os
import sys
import xbmc
import xbmcgui
import xbmcplugin

from icacheable import ICacheable
from utils import _sc
from constants import *
from mydebug import * 

###############################################################################
# Class QobuzPLaylist
###############################################################################
class QobuzPlaylist(ICacheable):

    def __init__(self,qob,id):
        self.Qob = qob
        self.id = id
        self._raw_data = []
        self.cache_path = os.path.join(
                                        self.Qob.cacheDir,
                                        'playlist-' + str(self.id) + '.dat'
        )
        self.cache_refresh = 600
        self.fetch_data()

    def _fetch_data(self):
        #ea = self.Qob.getEncounteredAlbum()
        data = self.Qob.Api.get_playlist(self.id)['playlist']
        #for a in data['tracks']:
        #    ea.add(a)
        return data

    def length(self):
        return len(self._raw_data['tracks'])

    def add_to_directory(self):
        n = self.length()
        h = int(sys.argv[1])
        for t in self._raw_data['tracks']:
            title = _sc(t['title'])
            if t['streaming_type'] != 'full':
                warn(self, "Skipping sample " + title.encode("utf8","ignore"))
                continue
            interpreter = _sc(t['interpreter']['name'])
            year = int(t['album']['release_date'].split('-')[0]) if t['album']['release_date'] else 0
            u = sys.argv[0] + "?mode=" + str(MODE_SONG) + "&id=" + str(t['id'])
            (sh,sm,ss) = t['duration'].split(':')
            duration = (int(sh) * 3600 + int(sm) * 60 + int(ss))
            item = xbmcgui.ListItem('test')
            item.setLabel(interpreter + ' - ' + _sc(t['album']['title']) + ' - ' + _sc(t['track_number']) + ' - ' + _sc(t['title']))
            item.setInfo(type="Music",infoLabels={
                                                    "count": int(self.id),
                                                   "title":  title,
                                                   "artist": interpreter,
                                                   "album": _sc(t['album']['title']),
                                                   "tracknumber": int(t['track_number']),
                                                   "genre": _sc(t['album']['genre']['name']),
                                                   "comment": "Qobuz Stream",
                                                   "duration": duration,
                                                   "year": year
                                                   })
            item.setPath(u)
            item.setProperty('Music','true')
            item.setProperty('IsPlayable','true');
            item.setProperty('mimetype','audio/flac')
            item.setThumbnailImage(t['album']['image']['large'])
            xbmcplugin.addDirectoryItem(handle=h ,url=u ,listitem=item,isFolder=False,totalItems=n)
        xbmcplugin.setContent(h,'songs')
        #xbmcplugin.setPluginFanart(int(sys.argv[1]), self.Qob.fanImg)
