import httplib, json,time,urllib2,urllib,hashlib,mutagen
import sys, os, shutil, re, pickle, time, tempfile, xbmcaddon, xbmcplugin, xbmcgui, xbmc

from mutagen.flac import FLAC
import pprint
from qobuz.api import QobuzApi
# import os,sys,re,string,array
# import playlist
__addon__     = xbmcaddon.Addon('plugin.audio.qobuz')
__addonname__ = __addon__.getAddonInfo('name')
__cwd__       = __addon__.getAddonInfo('path')
__author__    = __addon__.getAddonInfo('author')
__version__   = __addon__.getAddonInfo('version')
__language__  = __addon__.getLocalizedString
__debugging__    = __addon__.getSetting('debug')

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
MODE_SONG = 15
MODE_FAVORITE = 16
MODE_UNFAVORITE = 17
MODE_MAKE_PLAYLIST = 18
MODE_REMOVE_PLAYLIST = 19
MODE_RENAME_PLAYLIST = 20
MODE_REMOVE_PLAYLIST_SONG = 21
MODE_ADD_PLAYLIST_SONG = 22

class QobuzXbmc:
    fanImg = xbmc.translatePath(os.path.join('resources/img/', 'playlist.png'))
    def __init__(self):
        self.data = ""
        self.conn = ""
        self.Api = QobuzApi(self) 
        self.__playlists = {}
        self._handle = int(sys.argv[1])
        self.cacheDir = os.path.join(tempfile.gettempdir(), 'qobuz_xbmc')
        print "cacheDir: " + self.cacheDir + "\n"
        if os.path.isdir(self.cacheDir) == False:
            os.makedirs(self.cacheDir)
            if self._debugging:
                print "Made " + self.cacheDir

    def login(self, user, password):
        return self.Api.login(user,password)

    def is_logged(self):
        return self.Api.userid

    def download_track_withurl(self,file_name,url):
        u = urllib2.urlopen(url)
        f = open(file_name, 'wb')
        meta = u.info()
        file_size = int(meta.getheaders("Content-Length")[0])
        print "Downloading: %s Bytes: %s" % (file_name, file_size)
        file_size_dl = 0
        block_sz = 8192
        while True:
            buffer = u.read(block_sz)
            if not buffer:
                break
            file_size_dl += len(buffer)
            f.write(buffer)
            status = r"%10d  [%3.2f%%]" % (file_size_dl, file_size_dl * 100. / file_size)
            status = status + chr(8)*(len(status)+1)
            print status,
        f.close()
        u.close()

    def getPlaylist(self, id):
        return QobuzPlaylist(self, id)
    
    def getUserPlaylists(self):
        return QobuzUserPlaylists(self)
    
    def getAlbum(self, id):
        return Album(self, id)
     
    def getTrack(self, id):
        return QobuzTrack(self, id)
    
    def tag_track(self,track,file_name,album_title="null"):
        audio = FLAC(file_name)
        audio["title"] = track['title']
        
        if album_title == "null":
            audio["album"] = track['album']['title']
            audio["genre"] = track['album']['genre']['name']
            audio["date"] = track['album']['release_date']
        else:
            audio["album"] = album_title
        
        #audio["genre"] = self.pdata['product']['genre']['name']
        #audio["date"] = self.pdata['product']['release_date'] 
        
        audio["length"] = track['duration']
        audio["artist"] = track['interpreter']['name']
        audio["discnumber"] = track['media_number']
        audio["tracknumber"] = track['track_number']
        audio.pprint()
        audio.save()
     
     
    def download_track(self,track,context,context_id,album_title="null"):
        url=self.Api.get_track_url(track['id'],context,context_id) 
        if album_title == "null":
            track_album=track['album']['title']
        else:
            track_album=album_title 
        file_name = track['interpreter']['name'] +" - "+ track_album + " - "+track['track_number']+" - "+track['title']+".flac"
        self.download_track_withurl(file_name,url)
        if album_title != "null":
            self.tag_track(track,file_name,album_title)
        else:
            self.tag_track(track,file_name)
    
    def _add_dir(self, name, url, mode, iconimage, id, items=1):
          if url == '':
                u=sys.argv[0]+"?mode="+str(mode)+"&name="+urllib.quote_plus(name)+"&id="+str(id)
          else:
                u = url
          dir=xbmcgui.ListItem(name, iconImage=iconimage, thumbnailImage=iconimage)
          dir.setInfo( type="Music", infoLabels={ "title": name } )
          
          # Custom menu items
          menuItems = []
          if mode == MODE_ALBUM:
                mkplaylst=sys.argv[0]+"?mode="+str(MODE_MAKE_PLAYLIST)+"&id="+str(id)
                menuItems.append((__language__(30076), "XBMC.RunPlugin("+mkplaylst+")"))
          if mode == MODE_PLAYLIST:
                rmplaylst=sys.argv[0]+"?mode="+str(MODE_REMOVE_PLAYLIST)+"&name="+urllib.quote_plus(name)+"&id="+str(id)
                menuItems.append((__language__(30077), "XBMC.RunPlugin("+rmplaylst+")"))
                mvplaylst=sys.argv[0]+"?mode="+str(MODE_RENAME_PLAYLIST)+"&name="+urllib.quote_plus(name)+"&id="+str(id)
                menuItems.append((__language__(30078), "XBMC.RunPlugin("+mvplaylst+")"))

          dir.addContextMenuItems(menuItems, replaceItems=False)
          
          return xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=dir,isFolder=True, totalItems=items)
    
def log(obj, msg, lvl = "LOG"):
    xbmc.log('[' + lvl + '] ' + str(type(obj)) + ": " + msg)
                 
def warn(obj, msg):
    if __debugging__:
        log(obj, msg, 'WARN')

def info(obj, msg):
    if __debugging__:
        log(obj, msg, 'INFO')

def error(obj, msg, code):
    log(obj, msg, 'ERROR')
    os.sys.exit(code)
    
class ICacheable(object):
    
    def __init__(self):
        self._raw_data = None
        self.cache_refresh = 60
        self.cache_path = None

    def _load_cache_data(self):
        log(self, "Load: " + self.cache_path)
        if not os.path.exists(self.cache_path):
            return None
        mtime = None
        try:
            mtime = os.path.getmtime(self.cache_path)
        except: 
            warn(self, "Cannot stat cache file: " + self.cache_path)
        
        if (time.time() - mtime) > self.cache_refresh:
            info(self, "Refreshing cache")
            return None

        f = None
        try:
            f = open(self.cache_path, 'rb')
        except:
            warn(self, "Cannot open cache file: " + self.cache_path)
            return None
        return pickle.load(f)

    def _save_cache_data(self, data):
        f = open(self.cache_path, 'wb')
        pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)
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

class QobuzUserPlaylists(ICacheable):
    
    def __init__(self, qob):
        self.Qob = qob
        self._raw_data = []
        self.cache_path =  os.path.join(self.Qob.cacheDir, 'userplaylists.dat')
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
        log(self, "Found " + str(n) + " playlist(s)")
        h = int(sys.argv[1])
        u = dir = None
        xbmcplugin.setContent(h, 'files')
        xbmcplugin.addSortMethod(h, xbmcplugin.SORT_METHOD_LABEL)
        xbmcplugin.setPluginFanart(int(sys.argv[1]), self.Qob.fanImg)
        for p in self._raw_data:
<<<<<<< HEAD
            u=sys.argv[0]+"?mode="+str(MODE_PLAYLIST)+"&id="+str(p['id'])
=======
>>>>>>> origin/boom
            item=xbmcgui.ListItem()
            item.setLabel(p['name'])
            item.setLabel2(p['owner']['name'])
            item.setInfo( type="Music", infoLabels={ "title": p['name'] } )
            xbmcplugin.addDirectoryItem(handle=h,url=u,listitem=item,isFolder=True, totalItems=n)
            #dir = self.Qob._add_dir(p['name'].encode('utf8', 'ignore'),'',MODE_PLAYLIST,playlistImg,p['id'], n)
        #xbmcplugin.setContent(h, 'Playlists')
        #xbmcplugin.addSortMethod(h, xbmcplugin.SORT_METHOD_LABEL)
        #xbmcplugin.setPluginFanart(int(sys.argv[1]),self.Qob.fanImg)
        #xbmcplugin.endOfDirectory(h, True, False, True)

class QobuzTrack(ICacheable):
    def __init__(self, qob, id):
        self.Qob = qob
        self.id = id
        self._raw_data = []
        self.cache_path =  os.path.join(
                                        self.Qob.cacheDir, 
                                        'track-'+repr(self.id)+'.dat'
        )
        self.cache_refresh = 1200
        self.format_id = 6       
        settings = xbmcaddon.Addon(id='plugin.audio.qobuz')
        # Todo : Due to caching, streaming url can be mixed if settings are 
        # changed
        if settings.getSetting('streamtype') == 'mp3':
            self.format_id = 5
        self.fetch_data()
        #pprint.pprint(self._raw_data)
        
    def _fetch_data(self):
        data = {}
        data['info'] = self.Qob.Api.get_track(self.id)
        data['stream'] = self.Qob.Api.get_track_url(self.id, 'playlist', data['info']['album']['id'], self.format_id)
        return data
    
    def get_duration(self):
        (sh, sm, ss) = self._raw_data['info']['duration'].split(':')
        return (int(sh)*3600 + int(sm)*60 + int(ss))
    
    def play(self):
        global player
        playlist = xbmc.PlayList(xbmc.PLAYLIST_MUSIC)
        listitem = xbmcgui.ListItem(self._raw_data['info']['title'])
        i = self._raw_data['info']
        a = i['album']
        mimetype = 'audio/flac'
        if self.format_id == 5:
            mimetype = 'audio/mpeg'
        listitem.setInfo('music', {
                                   'count': self.id,
                                   'title': i['title'], 
                                   'artist' : i['interpreter']['name'],
                                   'genre': a['genre']['name'],
                                   'tracknumber': int(i['track_number']),
                                   'duration': self.get_duration(),
                                   'mimetype': mimetype
                                   })
        listitem.setThumbnailImage(a['image']['large'])
        listitem.setPath(self._raw_data['stream']['streaming_url'])
        p = xbmc.Player()
        if p.isPlaying():
            p.stop()
            xbmc.sleep(250)
        p.play(str(self._raw_data['stream']['streaming_url']), listitem)
        #xbmc.executebuiltin('PlayMedia('+str(self._raw_data['stream']['streaming_url'])+')')
            
class QobuzPlaylist(ICacheable):

    def __init__(self, qob, id):
        self.Qob = qob
        self.id = id
        self._raw_data = []
        self.cache_path =  os.path.join(
                                        self.Qob.cacheDir, 
                                        'playlist-'+repr(self.id)+'.dat'
        )
        self.cache_refresh = 600
        self.fetch_data()

    def _fetch_data(self):
        return self.Qob.Api.get_playlist(self.id)['playlist']
    
    def length(self):
        return len(self._raw_data['tracks'])
    
    def get_tracks1(self):
        list = []
        for track in self._raw_data['tracks']:
            print "----\n"
            coverart = track['album']['image']['large']
            if track['interpreter']['name']:
                artist=track['interpreter']['name'].encode('utf8', 'ignore')
            else:
                artist= ""
            list.append([
                         track['title'].encode('utf8', 'ignore'),
                         track['id'],
                         track['album']['title'].encode('utf8', 'ignore') ,
                         track['album']['id'],
                         artist,
                         track['interpreter']['id'],
                         coverart
            ])
        return list
    
    def add_to_directory(self):
        n = self.length()
        h = int(sys.argv[1])
        #playlist.clear()
        #xbmc.executebuiltin("Playlist.Clear");
        playlist = xbmc.PlayList(xbmc.PLAYLIST_MUSIC)
        #playlist.clear()
        for t in self._raw_data['tracks']:
            #pprint.pprint(t)
            if not t['interpreter']['name']: 
                t['interpreter']['name']="unknown"

            interpreter = urllib.quote_plus(t['interpreter']['name'].encode('utf8', 'ignore')) 
            u=sys.argv[0]+"?mode="+str(MODE_SONG)+"&id="+str(t['id']) 
                     #+"&album="+urllib.quote_plus(t['album']['title']) \
                     #+"&albumid="+urllib.quote_plus(str(t['album']['id'])) \
                     #+"&artist="+interpreter \
                     #+"&coverart="+urllib.quote_plus(t['image']['large'].convert('ascii', 'ignore')) 
            item = xbmcgui.ListItem()
            pitem = xbmc.PlayListItem()
            
            if not t['interpreter']['name'] or t['interpreter']['name'] == "unknown":
                interpreter_name = ""
                t['interpreter']['name']='unknown'
            else: 
                 interpreter_name = t['interpreter']['name']+" - "

            (sh, sm, ss) = t['duration'].split(':')
            duration = (int(sh)*3600 + int(sm)*60 + int(ss))
            item.setLabel(interpreter_name + t['album']['title'] + ' - ' + t['track_number'] + ' - ' + t['title'])
            #item.setLabel2(t['title'])
            position = playlist.getposition()
            print "Position: " + repr(position) + "\n"
            item.setInfo( type="music", infoLabels= { 
                                                    "count": + self.id,
                                                    "size:": '10000',
                                                   "title": t['title'], 
                                                   "artist": t['interpreter']['name'],
                                                   "album": t['album']['title'],
                                                   "tracknumber": int(t['track_number']),
                                                   "genre": t['album']['genre']['name'],
                                                   "comment": "Qobuz Stream",
                                                   "duration": duration,
                                                   "year": int(t['album']['release_date'].split('-')[0])
                                                   })
            playlist.add(url=u, listitem=item)
            item.setThumbnailImage(t['album']['image']['large'])
            playlist.add(url=u, listitem=item)
            xbmcplugin.addDirectoryItem(handle=h,url=u,listitem=item,isFolder=False, totalItems=n)
        xbmcplugin.setContent(h, 'songs')
        xbmcplugin.setPluginFanart(int(sys.argv[1]), self.Qob.fanImg)
        #xbmc.executebuiltin('playlist.playoffset(music,0)')

class Album:
    def __init__(self,qob,album_id):
        self.qob = qob
        self.album_id = album_id
        self.conn = ""
        self.pdata = self.qob.Api.get_album_tracks(album_id)

    def download_all(self):
        for track in self.pdata['product']['tracks']:
            self.qob.download_track(track,'album',self.album_id,self.pdata['product']['title'])
            print "\nsleeping 5s"
            time.sleep(5)

    def print_tracks (self):
        for track in self.pdata['product']['tracks']:
        #       print json.dumps(track)
            print track['interpreter']['name'] +" - "+ self.pdata['product']['title'] + " - "+track['track_number'] +" - " + track['title']
