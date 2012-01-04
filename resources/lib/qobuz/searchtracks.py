import sys
import xbmcgui
import xbmcplugin
from utils import _sc
from constants import *
from mydebug import log, info, warn

###############################################################################
# Class QobuzSearchTracks 
###############################################################################
class QobuzSearchTracks():

    def __init__(self, qob,):
        self.Qob = qob
        self._raw_data = {}
        
    def search(self, query, limit = 100):
        self._raw_data = self.Qob.Api.search_tracks(query, limit)
        #pprint.pprint(self._raw_data)
        return self
        
    def length(self):
        if not self._raw_data['results']:
            return 0
        return len(self._raw_data['results']['tracks'])
    
    def add_to_directory(self):
        n = self.length()
        h = int(sys.argv[1])
        for t in self._raw_data['results']['tracks']:
            title = _sc(t['title'])
            if t['streaming_type'] != 'full':
                warn(self, "Skipping sample " + title.encode("utf8","ignore"))
                continue
            interpreter = _sc(t['interpreter']['name'])
            #print "Interpreter: " + interpreter + "\n"
            #print "Title: " + t['title']
            year = int(t['album']['release_date'].split('-')[0]) if t['album']['release_date'] else 0
            u = sys.argv[0] + "?mode=" + str(MODE_SONG) + "&id=" + str(t['id'])
            (sh,sm,ss) = t['duration'].split(':')
            duration = (int(sh) * 3600 + int(sm) * 60 + int(ss))
            item = xbmcgui.ListItem('test')
            item.setLabel(interpreter + ' - ' + _sc(t['album']['title']) + ' - ' + _sc(t['track_number']) + ' - ' + _sc(t['title']))
            item.setInfo(type="Music",infoLabels={
                                                   #"count":+,
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

