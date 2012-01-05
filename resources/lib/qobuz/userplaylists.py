import os
import sys
import xbmcplugin
import xbmcgui

from icacheable import ICacheable
from mydebug import log, info, warn
from constants import *
from easytag import EasyMediaTag, EasyMediaTag_UserPlaylists
###############################################################################
# Class QobuzUserPLaylists
###############################################################################
class QobuzUserPlaylists(ICacheable):

    def __init__(self,qob):
        self.Qob = qob
        self._raw_data = []
        self.cache_path = os.path.join(self.Qob.cacheDir,'userplaylists.dat')
        self.cache_refresh = 600
        self.fetch_data()

    def _fetch_data(self):
        raw_data = self.Qob.Api.get_user_playlists()
        data = []
        for p in raw_data:
            data.append(p['playlist'])
        return data

    def length(self):
        return len(self._raw_data)

    def add_to_directory(self):
        n = self.length()
        log(self,"Found " + str(n) + " playlist(s)")
        h = int(sys.argv[1])
        u = dir = None
        et = EasyMediaTag_UserPlaylists(self._raw_data)
        et.parse()
        for t in et.get_list():
            item = xbmcgui.ListItem()
            item.setLabel(t.getValue('title'))
            item.setLabel2(t.getValue('owner_name'))
            item.setInfo(type="Music",infoLabels={ "title": t.getName() })
            item.setProperty('duration', str(t.getCreatedAt()[0]))
            xbmcplugin.addDirectoryItem(handle=h,url=t.getValue('_url'),listitem=item,isFolder=True,totalItems=n)
        xbmcplugin.setContent(h,'songs')
        xbmcplugin.addSortMethod(h,xbmcplugin.SORT_METHOD_LABEL)
        xbmcplugin.setPluginFanart(h,self.Qob.fanImg)
#        for p in self._raw_data:
#            u = sys.argv[0] + "?mode=" + str(MODE_PLAYLIST) + "&id=" + str(p['id'])
#            item = xbmcgui.ListItem()
#            item.setLabel(p['name'])
#            item.setLabel2(p['owner']['name'])
#            item.setInfo(type="Music",infoLabels={ "title": p['name'] })
#            xbmcplugin.addDirectoryItem(handle=h,url=u,listitem=item,isFolder=True,totalItems=n)
#        xbmcplugin.setContent(h,'songs')
#        xbmcplugin.addSortMethod(h,xbmcplugin.SORT_METHOD_LABEL)
#        xbmcplugin.setPluginFanart(h,self.Qob.fanImg)