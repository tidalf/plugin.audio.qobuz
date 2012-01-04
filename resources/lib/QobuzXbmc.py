import httplib,json,time,urllib2,urllib,hashlib,mutagen
import sys,os,shutil,re,pickle,time,tempfile,xbmcaddon,xbmcplugin,xbmcgui,xbmc
import threading
#from mutagen.flac import FLAC
import pprint

from qobuz.api import QobuzApi

__addon__ = xbmcaddon.Addon('plugin.audio.qobuz')
__addonname__ = __addon__.getAddonInfo('name')
__cwd__ = __addon__.getAddonInfo('path')
__author__ = __addon__.getAddonInfo('author')
__version__ = __addon__.getAddonInfo('version')
__language__ = __addon__.getLocalizedString
__debugging__ = __addon__.getSetting('debug')

MODE_SEARCH_SONGS = 1
MODE_SEARCH_ALBUMS = 2
MODE_SEARCH_ARTISTS = 3
MODE_SEARCH_ARTISTS_ALBUMS = 4
MODE_SEARCH_PLAYLISTS = 5
MODE_ARTIST_POPULAR = 6
MODE_POPULAR_SONGS = 7
MODE_FAVORITES = 8
MODE_PLAYLISTS = 9
MODE_ALBUM = 10
MODE_ARTIST = 11
MODE_PLAYLIST = 12
MODE_SONG_PAGE = 13
MODE_SIMILAR_ARTISTS = 14
MODE_SHOW_RECOS = 15

MODE_SONG = 30
MODE_FAVORITE = 31
MODE_UNFAVORITE = 32
MODE_MAKE_PLAYLIST = 33
MODE_REMOVE_PLAYLIST = 34
MODE_RENAME_PLAYLIST = 35
MODE_REMOVE_PLAYLIST_SONG = 36
MODE_ADD_PLAYLIST_SONG = 37

###############################################################################
# Loggin helper functions
###############################################################################
def log(obj,msg,lvl="LOG"):
    xbmc.log(_sc('[' + lvl + '] ' + str(type(obj)) + ": " + msg))

def warn(obj,msg):
    if __debugging__:
        log(obj,msg,'WARN')

def info(obj,msg):
    if __debugging__:
        log(obj,msg,'INFO')

def error(obj,msg,code):
    log(obj,msg,'ERROR')
    os.sys.exit(code)

###############################################################################
# 
###############################################################################
def _sc(str):
    if not str:
        return 'NA'
    else:
        return u'' + str

###############################################################################
# Class QobuzXbmc
###############################################################################
class QobuzXbmc:
    fanImg = xbmc.translatePath(os.path.join('resources/img/','playlist.png'))
    def __init__(self):
        self.data = ""
        self.conn = ""
        self.Api = QobuzApi(self)
        self.__playlists = {}
        self._handle = int(sys.argv[1])
        self.cacheDir = os.path.join(tempfile.gettempdir(),'qobuz_xbmc')
        info(self, "cacheDir: " + self.cacheDir)
        if os.path.isdir(self.cacheDir) == False:
            os.makedirs(self.cacheDir)
            info("Make cache directory: " + self.cacheDir)

    def login(self,user,password):
        info(self, "Try to login as user: " + user)
        return self.Api.login(user,password)

    def is_logged(self):
        return self.Api.userid

#    def download_track_withurl(self,file_name,url):
#        u = urllib2.urlopen(url)
#        f = open(file_name, 'wb')
#        meta = u.info()
#        file_size = int(meta.getheaders("Content-Length")[0])
#        print "Downloading: %s Bytes: %s" % (file_name, file_size)
#        file_size_dl = 0
#        block_sz = 8192
#        while True:
#            buffer = u.read(block_sz)
#            if not buffer:
#                break
#            file_size_dl += len(buffer)
#            f.write(buffer)
#            status = r"%10d  [%3.2f%%]" % (file_size_dl, file_size_dl * 100. / file_size)
#            status = status + chr(8)*(len(status)+1)
#            print status,
#        f.close()
#        u.close()

    def getPlaylist(self,id):
        return QobuzPlaylist(self,id)

    def getUserPlaylists(self):
        return QobuzUserPlaylists(self)

    def getAlbum(self,id):
        return Album(self,id)

    def getTrack(self,id):
        return QobuzTrack(self,id)
    
    def getEncounteredAlbum(self):
        return QobuzEncounteredAlbum(self)
    
    def getQobuzSearchTracks(self):
        return QobuzSearchTracks(self)

    def watchPlayback( self ):
        if not self.player.isPlayingAudio():
            self.Timer.stop()
            exit(0)
        print "Watching player: " + self.player.getPlayingFile() + "\n"
        self.Timer = threading.Timer( 6, self.watchPlayback, () )
        self.Timer.start()

    def getRecommandation(self,genre_id):
        return QobuzGetRecommandation(self)

#    def tag_track(self,track,file_name,album_title="null"):
#        audio = FLAC(file_name)
#        audio["title"] = track['title']
#        
#        if album_title == "null":
#            audio["album"] = track['album']['title']
#            audio["genre"] = track['album']['genre']['name']
#            audio["date"] = track['album']['release_date']
#        else:
#            audio["album"] = album_title
#        
#        #audio["genre"] = self.pdata['product']['genre']['name']
#        #audio["date"] = self.pdata['product']['release_date'] 
#        
#        audio["length"] = track['duration']
#        audio["artist"] = track['interpreter']['name']
#        audio["discnumber"] = track['media_number']
#        audio["tracknumber"] = track['track_number']
#        audio.pprint()
#        audio.save()
#     
#     
#    def download_track(self,track,context,context_id,album_title="null"):
#        url=self.Api.get_track_url(track['id'],context,context_id) 
#        if album_title == "null":
#            track_album=track['album']['title']
#        else:
#            track_album=album_title 
#        file_name = track['interpreter']['name'] +" - "+ track_album + " - "+track['track_number']+" - "+track['title']+".flac"
#        self.download_track_withurl(file_name,url)
#        if album_title != "null":
#            self.tag_track(track,file_name,album_title)
#        else:
#            self.tag_track(track,file_name)


###############################################################################
# Interface ICacheable
###############################################################################
class ICacheable(object):

    def __init__(self):
        self._raw_data = None
        self.cache_refresh = 60
        self.cache_path = None

    def _load_cache_data(self):
        log(self,"Load: " + self.cache_path)
        if not os.path.exists(self.cache_path):
            return None
        mtime = None
        try:
            mtime = os.path.getmtime(self.cache_path)
        except:
            warn(self,"Cannot stat cache file: " + self.cache_path)
        if self.cache_refresh:
            if (time.time() - mtime) > self.cache_refresh:
                info(self,"Refreshing cache")
                return None
        f = None
        try:
            f = open(self.cache_path,'rb')
        except:
            warn(self,"Cannot open cache file: " + self.cache_path)
            return None
        return pickle.load(f)

    def _save_cache_data(self,data):
        f = open(self.cache_path,'wb')
        pickle.dump(data,f,protocol=pickle.HIGHEST_PROTOCOL)
        f.close()

    def fetch_data(self):
        self._raw_data = self._load_cache_data()
        if not self._raw_data:
            data = self._fetch_data()
            self._save_cache_data(data)
            self._raw_data = data
        return self._raw_data

    def _fetch_data(self):
        assert("Need to implement fetch_data!")

    def to_s(self):
        str = "Cache refresh: " + repr(self.cache_refresh) + "\n"
        str += "Cache path: " + self.cache_path + "\n"
        return str

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

        for p in self._raw_data:
            u = sys.argv[0] + "?mode=" + str(MODE_PLAYLIST) + "&id=" + str(p['id'])
            item = xbmcgui.ListItem()
            item.setLabel(p['name'])
            item.setLabel2(p['owner']['name'])
            item.setInfo(type="Music",infoLabels={ "title": p['name'] })
            xbmcplugin.addDirectoryItem(handle=h,url=u,listitem=item,isFolder=True,totalItems=n)
        xbmcplugin.setContent(h,'songs')
        xbmcplugin.addSortMethod(h,xbmcplugin.SORT_METHOD_LABEL)
        xbmcplugin.setPluginFanart(h,self.Qob.fanImg)

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

class QobuzGetRecommandation():

    def __init__(self, qob,):
        self.Qob = qob
        self._raw_data = {}
        
    def get(self, genre_id, limit = 100):
        self._raw_data = self.Qob.Api.get_recommandations(genre_id, limit)
        pprint.pprint(self._raw_data)
        return self
        
    def length(self):
        pprint.pprint(self._raw_data)
        return len(self._raw_data)
    
    def add_to_directory(self):
        n = self.length()
        h = int(sys.argv[1])
        for t in self._raw_data:
            title = _sc(t['title'])
            interpreter = _sc(t['subtitle'])
            #print "Interpreter: " + interpreter + "\n"
            #print "Title: " + t['title']
            year = int(t['released_at'].split('-')[0]) if t['released_at'] else 0
            u = sys.argv[0] + "?mode=" + str(MODE_SONG) + "&id=" + str(t['id'])
            #(sh,sm,ss) = t['duration'].split(':')
            #duration = (int(sh) * 3600 + int(sm) * 60 + int(ss))
            item = xbmcgui.ListItem('test')
            item.setLabel(interpreter + ' - ' + _sc(t['subtitle']) + ' - ' + _sc(t['title']))
            item.setInfo(type="Music",infoLabels={
                                                   #"count":+,
                                                   "title":  title,
                                                   "artist": interpreter,
                                                   "album": _sc(t['subtitle']),
                                                   # "tracknumber": '0',
                                                   "genre": 'unavailable',
                                                   "comment": "Qobuz Stream",
                                                   # "duration": duration,
                                                   "year": year
                                                   })
            item.setPath(u)
            item.setProperty('Music','true')
            item.setProperty('IsPlayable','true');
            item.setProperty('mimetype','audio/flac')
            item.setThumbnailImage(t['image']['large'])
            xbmcplugin.addDirectoryItem(handle=h ,url=u ,listitem=item,isFolder=False,totalItems=n)
        xbmcplugin.setContent(h,'songs')
        #xbmcplugin.setPluginFanart(int(sys.argv[1]), self.Qob.fanImg)       


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
                                        'playlist-' + repr(self.id) + '.dat'
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
            item.setLabel(interpreter + ' - ' + t['album']['title'] + ' - ' + t['track_number'] + ' - ' + t['title'])
            item.setInfo(type="Music",infoLabels={
                                                    "count":+self.id,
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



###############################################################################
# Class QobuzTrack 
#
# @summary: Manage one qobuz track
# @param qob: parent
# @param id: track id
# @return: New QobuzTrack 
###############################################################################
class QobuzTrack(ICacheable):
    # Constructor
    def __init__(self,qob,id):
        self.Qob = qob
        self.id = id
        self._raw_data = []
        self.cache_path = os.path.join(self.Qob.cacheDir,
                                        'track-' + repr(self.id) + '.dat')
        self.cache_refresh = 1200
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
        data['info'] = self.Qob.Api.get_track(self.id)
        data['stream'] = self.Qob.Api.get_track_url(self.id,
                                                    'playlist',
                                                    data['info']['album']['id'],
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
        while timeout > 0:
            if player.isPlayingAudio == True:
                return
            #print "Waiting for stream to start\n"
            xbmc.sleep(1)
            timeout-=1
        self.Qob.Api.report_streaming_start(self.id)
        
        player.onPlayBackEnded('stop_track('+str(self.id)+')')
        
        
class QobuzPlayer(xbmc.Player):
    def __init__(self, type):
        super(QobuzPlayer, self).__init__(type)
        self.id = None
        self.last_id = None
    
    def onPlayBackEnded(self, id):
        print "Stopping file with id" + str(self.last_id)
    
    def set_track_id(self, id):
        if self.id:
            self.last_id = self.id
        self.id = id
        
class QobuzEncounteredAlbum(ICacheable):
    # Constructor
    def __init__(self,qob):
        self.Qob = qob
        self._raw_data = {}
        self.cache_path = os.path.join(self.Qob.cacheDir,
                                        'encoutered_albums' + '.dat')
        self.cache_refresh = None

    # Methode called by parent class ICacheable when fresh data is needed
    def _fetch_data(self):
        return self._raw_data

    def add(self, album):
        id = str(album['id'])
        print "Id: " + id + "\n"
        if self._raw_data[id]:
            info(self, "AlbumID: " + id + ' already present')
        self._raw_data[id] = album
        self._save_cache_data(album)
    
    