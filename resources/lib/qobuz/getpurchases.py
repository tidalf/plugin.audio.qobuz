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
import sys
import os
import xbmcgui
import xbmcplugin

import pprint

from mydebug import log, info, warn
from constants import *
from icacheable import ICacheable
from easytag import QobuzTagArtist
from easytag import QobuzTagTrack
from easytag import  QobuzTagProduct

"""
    Class QobuzGetPurchases
"""
class QobuzGetPurchases(ICacheable):

    def __init__(self, Core, limit = 100):
        self.Core = Core
        self.limit = limit
        super(QobuzGetPurchases, self).__init__(self.Core.Bootstrap.cacheDir, 
                                       'purchases')
        self.set_cache_refresh(self.Core.Bootstrap.__addon__.getSetting('cache_duration_recommandation'))
        info(self, "Cache duration: " + str(self.cache_refresh))
        
    def _fetch_data(self):
        return self.Core.Api.get_purchases(self.limit)
    
    def length(self):
        if not self._raw_data:
            return 0
        return len(self._raw_data)

    def add_to_directory(self):
        n = self.length()
        print "Len: " +str(n)
        #i = 0
        albumseen = {}
        needsave = False
        for track in self._raw_data:    
            t = QobuzTagTrack(self.Core, track)
            if 'BLACK_ID' in track:
                continue
            pprint.pprint(t)
            albumid = t.getAlbumId()
            log ('warn',albumid)
            isseen = 'false'
            try:
                 isseen = albumseen[albumid]
            except: pass
            if isseen == 'false':
                   #if  albumseen[albumid] is false:
                log ('warn','album never seen try to add it')
                try:
                    print "Album ID " + str(albumid)
                    album = self.Core.getProduct(str(albumid))
                except:
                    track['BLACK_ID'] = 'true'
                    needsave = True
                    print "cannot get product"
                    continue
                if 1:
                    print "Plop1"
                    a = QobuzTagProduct(self.Core, album.get_raw_data())
#                except:
#                    print "Cannot tag product"
#                    continue
#                    print "plop"
                item = a.getXbmcItem()
                albumid = a.id     
                u = sys.argv[0] + "?mode=" + str(MODE_ALBUM) + "&id=" + str(albumid) + "&context_type=purchased"
                item.setPath(u)
                item.setProperty('path', u)
                    
                xbmcplugin.addDirectoryItem(handle=self.Core.Bootstrap.__handle__, 
                                                url=u, listitem=item, isFolder=True, 
                                                totalItems=n)          
                print "ADDED"           
            albumseen[albumid] = 'true'
            #except:                             
#                    #log ('warn', "album not found...")
#                    albumseen[albumid] = 'true'
                      
           #except:pass
           
            
           #item = t.getXbmcItem('songs')
           #u = sys.argv[0] + "?mode=" + str(MODE_SONG) + "&id=" + t.id + "&pos=" + str(i) + "&context_type=purchases" 
           #self.Core.Bootstrap.GUI.addDirectoryItem(u , item, False, n)
           #xp.add(u, item)
           #i = i + 1
        
        
        #for product in self.get_data():
        if needsave:
            self._save_cache_data(self._raw_data)
        return n

