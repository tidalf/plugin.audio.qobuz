import sys
import os
import xbmcgui
import xbmcplugin

import pprint

from mydebug import log, info, warn
from constants import *

class QobuzGetRecommandation():

    def __init__(self,qob,genre_id,type='new-releases'):
        self.Qob = qob
        self._raw_data = []
        self.cache_path = os.path.join(self.Qob.cacheDir,'recommandations.dat')
        self.cache_refresh = 600
        self._raw_data = self._fetch_data(genre_id,type)

    def _fetch_data(self,genre_id, type, limit=100):
        return self.Qob.Api.get_recommandations(genre_id, type,limit)
    
    def length(self):
        return len(self._raw_data)

    def add_to_directory(self):
        n = self.length()
        log(self,"Found " + str(n) + " albums(s)")
        h = int(sys.argv[1])
        u = dir = None

        for p in self._raw_data:
            pprint.pprint(p)
            u = sys.argv[0] + "?mode=" + str(MODE_ALBUM) + "&id=" + str(p['id'])
            item = xbmcgui.ListItem()
            year = int(p['released_at'].split('-')[0]) if p['released_at'] else 0
            artist =  p['subtitle'] + ' - ' if p['subtitle'] else ''
            item.setLabel(artist +p['title'] + " (" + str(year) + ")")
            item.setLabel2(p['title'])
            item.setInfo(type="Music",infoLabels={ "title": p['title'] })
            item.setThumbnailImage(p['image']['large'])
            xbmcplugin.addDirectoryItem(handle=h,url=u,listitem=item,isFolder=True,totalItems=n)
        xbmcplugin.setContent(h,'songs')
        xbmcplugin.addSortMethod(h,xbmcplugin.SORT_METHOD_LABEL)
        xbmcplugin.setPluginFanart(h,self.Qob.fanImg)