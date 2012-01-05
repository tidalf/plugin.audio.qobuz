import os
import xbmcaddon
import xbmcplugin
import xbmcgui
import xbmc
import os,sys
import pprint

from icacheable import ICacheable
from logging import *
from utils import _sc
from constants import *

###############################################################################
# Class QobuzProduct
###############################################################################
class QobuzProduct(ICacheable):

    def __init__(self,qob,id):
        self.Qob = qob
        self.id = id
        self._raw_data = []
        self.cache_path = os.path.join(
                                        self.Qob.cacheDir,
                                        'product-' + str(self.id) + '.dat'
        )
        self.cache_refresh = 600
        self.fetch_data()

    def _fetch_data(self):
        #ea = self.Qob.getEncounteredAlbum()
        data = self.Qob.Api.get_product(str(self.id))['product']
        pprint.pprint(data)
        #for a in data['tracks']:
        #    ea.add(a)
        return data

    def length(self):
        return len(self._raw_data['tracks'])

    def add_to_directory(self):
        pprint.pprint(self._raw_data)
        n = self.length()
        h = int(sys.argv[1])
        p = self._raw_data
        for t in self._raw_data['tracks']:
            title = _sc(t['title'])
#            if t['streaming_type'] != 'full':
#                warn(self, "Skipping sample " + title.encode("utf8","ignore"))
#                continue
            interpreter = _sc(t['interpreter']['name'])
            year = int(p['release_date'].split('-')[0]) if p['release_date'] else 0
            u = sys.argv[0] + "?mode=" + str(MODE_SONG) + "&id=" + str(t['id'])
            (sh,sm,ss) = t['duration'].split(':')
            duration = (int(sh) * 3600 + int(sm) * 60 + int(ss))
            item = xbmcgui.ListItem('test')
#            item.setLabel(interpreter + ' - ' + p['title'] + ' - ' + t['track_number'] + ' - ' + t['title'])
            item.setLabel( t['track_number'] + ' - ' + t['title'])

            item.setInfo(type="Music",infoLabels={
#                                                   "count":  self.id,
                                                   "title":  title,
                                                   "artist": p['artist']['name'],
                                                   "album": title,
                                                   "tracknumber": int(t['track_number']),
                                                   "genre": _sc(p['genre']['name']),
                                                   "comment": "Qobuz Stream",
                                                   "duration": duration,
                                                   "year": year
                                                   })
            item.setPath(u)
            item.setProperty('Music','true')
            item.setProperty('IsPlayable','true');
            item.setProperty('mimetype','audio/flac')
            item.setThumbnailImage(p['image']['large'])
            xbmcplugin.addDirectoryItem(handle=h ,url=u ,listitem=item,isFolder=False,totalItems=n)
        xbmcplugin.setContent(h,'songs')
        #xbmcplugin.setPluginFanart(int(sys.argv[1]), self.Qob.fanImg)
