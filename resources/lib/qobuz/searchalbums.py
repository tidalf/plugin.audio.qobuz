import sys
import xbmcgui
import xbmcplugin
from utils import _sc
from constants import *
from mydebug import log, info, warn

import pprint

###############################################################################
# Class QobuzSearchAlbums
###############################################################################
class QobuzSearchAlbums():

    def __init__(self, qob,):
        self.Qob = qob
        self._raw_data = []
        
    def search(self, query, limit = 100):
        self._raw_data = self.Qob.Api.search_albums(query, limit)
        #pprint.pprint(self._raw_data)
        return self
        
    def length(self):
        return len(self._raw_data)
    
    def add_to_directory(self):
        h = int(sys.argv[1])
        xbmc_directory_products(self._raw_data, self.length())
        #xbmcplugin.addDirectoryItem(handle=h ,url=u ,listitem=item,isFolder=False,totalItems=n)
        xbmcplugin.setContent(h,'songs')
 
 
def xbmc_directory_products(json, len):
    h = int(sys.argv[1])
    for p in json:
        a      = p['product']
        title  = _sc(a['title'])
        artist = _sc(a['artist'])
        genre  = _sc(a['genre'])
        image  = a['image']['large']
        year   = int(a['release_date'].split('-')[0]) if a['release_date'] else 0
        u = sys.argv[0] + "?mode=" + str(MODE_ALBUM) + "&id=" + str(a['id'])
        #(sh,sm,ss) = a['duration'].split(':')
        item   = xbmcgui.ListItem()
        item.setLabel(genre + ' / ' + artist + ' - ' + title)
        item.setInfo(type="Music",infoLabels={
                                                   #"count"  : long(a['id']),
                                                   "artist" : artist,
#                                                   "album"  : title,
#                                                   "genre"  : genre,
#                                                   "comment": "Qobuz Stream",
#                                                   "year"   : year
        })
        print "U:" + u + "\n"
        #item.setPath(u)
        #item.setProperty('Music','true')
        #item.setProperty('IsPlayable','false');
        item.setThumbnailImage(image)
        xbmcplugin.addDirectoryItem(handle=h , url=u,listitem=item,isFolder=True,totalItems=len)
