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
import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin
from icacheable import ICacheable
from mydebug import log, info, warn
from utils import _sc
from easytag import QobuzTagTrack
import pprint
'''
 Class QobuzTrack 

 @summary: Manage one qobuz track
 @param qob: parent
 @param id: track id
 @return: New QobuzTrack 
'''
class QobuzTrack(ICacheable):
    # Constructor
    def __init__(self, Core, id, context_type='playlist'):
        self.Core = Core
        self.id = id
        self.context_type = context_type
        self._raw_data = []
        self.cache_path = os.path.join(self.Core.Bootstrap.cacheDir,
                                        'track-' + str(self.id) + '.dat')
        self.cache_refresh = self.Core.Bootstrap.__addon__.getSetting('cache_duration_track')
        info(self, "Cache duration: " + str(self.cache_refresh))
        self.format_id = 6
        if self.Core.Bootstrap.__addon__.getSetting('streamtype') == 'mp3':
            self.format_id = 5
        self.fetch_data()

    # Methode called by parent class ICacheable when fresh data is needed
    def _fetch_data(self):
        data = {}
        data['info'] = self.Core.Api.get_track(self.id)
        return data
        
    # Return track duration
    def get_duration(self):
        (sh,sm,ss) = self._raw_data['info']['duration'].split(':')
        return (int(sh) * 3600 + int(sm) * 60 + int(ss))

    # Build an XbmcItem based on json data
    def getItem(self):
        '''
            This hack work but we must stick with the real API and pass
            album_id and context?
        '''
        album_id = ''
        #pprint.pprint(self._raw_data)
        t = QobuzTagTrack(self.Core, self._raw_data)
        item = t.getXbmcItem()
#        stream = self.Core.Api.get_track_url(self.id,
#                                                    self.context_type,
#                                                    album_id,
#                                                    self.format_id)
#        mimetype = 'audio/flac'
#        if self.format_id == 5:
#            mimetype = 'audio/mpeg'
#        item.setProperty('mimetype', mimetype)
        #item.setProperty('stream', str(stream['streaming_url']))
        pos = None
        try: 
            pos = str(self.Core.Bootstrap.params['pos'])
        except:
            pos = 0
        path = sys.argv[0] + "?mode=" + str(self.Core.Bootstrap.MODE) + "&id=" + self.Core.Bootstrap.ID + "&pos=" + pos
        item.setProperty('path', path)
        item.setPath(path)
        return item
    
    def stop(self, id):
        self.Core.Api.report_streaming_stop(self.id)
    
    
    
    # Play this track
    def play(self):
        #global player
        player = self.Core.Bootstrap.Player
        player.set_track_id(self.id)
        player.setApi(self.Core)
        print "Size: " + str(player.Playlist.size())
        item = self.getItem()
        if not item.getProperty('stream'):
            warn(self, "Player can't play track: " + item.getLabel())
            return False
        player.play( item)
        #item.setPath(item.getProperty('stream'))
        #xbmcplugin.setResolvedUrl(handle=self.Core.Bootstrap.__handle__,succeeded=True,listitem=item)
        return True
