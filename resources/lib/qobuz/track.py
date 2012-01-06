import sys
import os
import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin
from icacheable import ICacheable
from mydebug import log, info, warn
from utils import _sc
from constants import __addon__

'''
 Class QobuzTrack 

 @summary: Manage one qobuz track
 @param qob: parent
 @param id: track id
 @return: New QobuzTrack 
'''
class QobuzTrack(ICacheable):
    # Constructor
    def __init__(self,qob,id):
        self.Qob = qob
        self.id = id
        self._raw_data = []
        self.cache_path = os.path.join(self.Qob.cacheDir,
                                        'track-' + str(self.id) + '.dat')
        self.cache_refresh = __addon__.getSetting('cache_duration_track')
        info(self, "Cache duration: " + str(self.cache_refresh))
        self.format_id = 6
        settings = xbmcaddon.Addon(id='plugin.audio.qobuz')
        # Todo : Due to caching, streaming url can be mixed if settings are 
        # changed
        if settings.getSetting('streamtype') == 'mp3':
            self.format_id = 5
        self.fetch_data()

    # Methode called by parent class ICacheable when fresh data is needed
    def _fetch_data(self):
        data = {}
        album_id = ''
        try:
            album_id = data['info']['album']['id']
        except: pass
        data['info'] = self.Qob.Api.get_track(self.id)
        #pprint.pprint(data['info'])
        data['stream'] = self.Qob.Api.get_track_url(self.id,
                                                    'playlist',
                                                    album_id,
                                                    self.format_id)
        return data

    # Return track duration
    def get_duration(self):
        (sh,sm,ss) = self._raw_data['info']['duration'].split(':')
        return (int(sh) * 3600 + int(sm) * 60 + int(ss))

    # Build an XbmcItem based on json data
    def getItem(self):
        item = xbmcgui.ListItem(label=repr(self._raw_data['info']['title']))
        i = self._raw_data['info']
        a = i['album']
        mimetype = 'audio/flac'
        if self.format_id == 5:
            mimetype = 'audio/mpeg'
        item.setInfo(type='music',infoLabels={
                                   'count': self.id,
                                   'title': _sc(i['title']),
                                   'artist' : _sc(i['interpreter']['name']),
                                   'genre': _sc(a['genre']['name']),
                                   'tracknumber': int(i['track_number']),
                                   'mimetype': mimetype,
                                                "title": i['title'],
                                                "album": a['title'],
                                                "artist": i['interpreter']['name'],
                                                "duration": self.get_duration()})
        item.setProperty('Music','true')
        item.setProperty('mimetype',mimetype)
        item.setProperty("IsPlayable",'true')
        item.setProperty('duration', str(self.get_duration()))
        #item.setProperty('songid', str(self.id))
        #item.setProperty('coverart', a['image']['large'])
        #item.setProperty('title', i['title'])
        #item.setProperty('album', a['title'])
        #item.setProperty('artist', i['interpreter']['name'])
        #item.setProperty('duration', str(self.get_duration()))
        #item.setThumbnailImage(a['image']['large'])
        #item.setProperty('path', self._raw_data['stream']['streaming_url'] )
        item.setPath(self._raw_data['stream']['streaming_url'])
        return item
    
    def stop(self, id):
        self.Qob.Api.report_streaming_stop(self.id)
        
    # Play this track
    def play(self):
        #global player
        player = xbmc.Player()
        #player.set_track_id(self.id)
        item = self.getItem()
        xbmcplugin.setResolvedUrl(handle=int(sys.argv[1]),succeeded=True,listitem=item)
        timeout = 30
        info(self, "Waiting song to start")
        while timeout > 0:
            if player.isPlayingAudio == False:
                time.sleep(.500)
                timeout-=.500
            else: timeout = 0
        info(self, "Song started")
        self.Qob.Api.report_streaming_start(self.id)
        #player.onPlayBackEnded('stop_track('+str(self.id)+')')
        