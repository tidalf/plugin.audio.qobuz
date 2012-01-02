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
    def __init__(self):
        self.data = ""
        self.conn = ""
        self.Api = QobuzApi(self) 
        self.__playlists = {}
        self._handle = int(sys.argv[1])

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
        return QobuzXbmcPlaylist(self, id)
    
    def getUserPlaylists(self):
        return QobuzXbmcUserPlaylists(self)
    
    def getAlbum(self, id):
        return Album(self, id)
     
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
                mkplaylst=sys.argv[0]+"?mode="+str(MODE_MAKE_PLAYLIST)+"&name="+name+"&id="+str(id)
                menuItems.append((__language__(30076), "XBMC.RunPlugin("+mkplaylst+")"))
          if mode == MODE_PLAYLIST:
                rmplaylst=sys.argv[0]+"?mode="+str(MODE_REMOVE_PLAYLIST)+"&name="+urllib.quote_plus(name)+"&id="+str(id)
                menuItems.append((__language__(30077), "XBMC.RunPlugin("+rmplaylst+")"))
                mvplaylst=sys.argv[0]+"?mode="+str(MODE_RENAME_PLAYLIST)+"&name="+urllib.quote_plus(name)+"&id="+str(id)
                menuItems.append((__language__(30078), "XBMC.RunPlugin("+mvplaylst+")"))

          dir.addContextMenuItems(menuItems, replaceItems=False)
          
          return xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=dir,isFolder=True, totalItems=items)
     
class QobuzUserPlaylists(object):
    def __init__(self, qob):
        self.Qob = qob
        self._raw_data = []
        self.__fetch_data()
    
    def __fetch_data(self):
        data = self.Qob.Api.get_user_playlists()
        self._raw_data = []
        for p in data:
            self._raw_data.append(p['playlist'])
        return self._raw_data
            

class QobuzXbmcUserPlaylists(QobuzUserPlaylists):
    def __init__(self, qob):
        super(QobuzXbmcUserPlaylists, self).__init__(qob)
        
    def length(self):
        return len(self._raw_data)
    
    def add_to_directory(self):
        n = self.length()
        xbmc.log("Found " + repr(self.length()) + " playlists...")
        for p in self._raw_data:

            playlistImg = None
            dir = self.Qob._add_dir(p['name'].encode('utf8', 'ignore'),'',MODE_PLAYLIST,playlistImg,p['id'], n)
        xbmcplugin.setContent(self.Qob._handle,'files')
        xbmcplugin.addSortMethod(self.Qob._handle,xbmcplugin.SORT_METHOD_LABEL)
        #xbmcplugin.setPluginFanart(int(sys.argv[1]),self.fanImg)
   

class QobuzPlaylist(object):
    def __init__(self,qob,playlist_id):
        self.qob = qob
        self.id = playlist_id
        self.data = None
        self.__tracks = []
        self.__fetch_data()


#    def download_all(self):
#        for track in self.pdata['playlist']['tracks']:
#            self.qob.download_track(track,'playlist',self.playlist_id)
#        #   print "\nsleeping 5s"
#            time.sleep(5)
#
#    def print_tracks (self):
#        for track in self.pdata['playlist']['tracks']:
#            print track['interpreter']['name'] +" - "+ track['album']['title'] + " - "+track['track_number'] +" - " + track['title']
    def __fetch_data(self):
         self._raw_data = self.qob.Api.get_playlist(self.id)['playlist']

    def get_tracks(self):
        return self._raw_data['tracks']
    
    def get_info(self):
        return self.data

class QobuzTrack(object):
    
    def __init__(self):
        self.data = None
    
    def load_json(self, json):
        self.data = json
    
class QobuzXbmcTrack(QobuzTrack):
    def __init__(self):
        super(QobuzXbmcTrack, self).__init__()

    def add_to_directory(self):
        pass
        

class QobuzXbmcPlaylist(QobuzPlaylist):

    def __init__(self, qob, id):
        super(QobuzXbmcPlaylist, self).__init__(qob, id)

    def get_tracks1(self):
        data = super(QobuzXbmcPlaylist, self).get_tracks()
        list = []
        for track in data:
            coverart = track['album']['image']['large']
            # Trop space ce if :p
            if track['interpreter']['name']:
                artist=track['interpreter']['name'].encode('utf8', 'ignore')
            else:
                artist=track['interpreter']['name']
            list.append([track['title'].encode('utf8', 'ignore'),track['id'],track['album']['title'].encode('utf8', 'ignore') ,track['album']['id'],artist,track['interpreter']['id'],coverart])
        return list
    
    def add_to_directory(self):
    #def _add_songs_directory(self, songs, trackLabelFormat=ARTIST_ALBUM_NAME_LABEL, offset=0, playlistid=0, playlistname='', isFavorites=False):
          tracks =  super(QobuzXbmcPlaylist, self).get_tracks()
          totalSongs = len(tracks)
          offset = 0
          offset = int(offset)
          start = 0
          end = totalSongs

          # No pages needed
          if offset == 0 and totalSongs <= self.songspagelimit:
                if __debugging__ :
                     xbmc.log("Found " + str(totalSongs) + " songs...")
          # Pages
          else:
                # Cache all next pages songs
                if offset == 0:
                     self._setSavedSongs(songs)
                else:
                     songs = self._getSavedSongs()
                     totalSongs = len(songs)
                     
                if totalSongs > 0:
                     start = offset
                     end = min(start + self.songspagelimit,totalSongs)
          
          id = 0
          n = start
          items = end - start
          while n < end:
                song = songs[n]
                songid = song[1]
                albumid = song[3]
                duration = self._getSongDuration(songid,albumid)
                if duration != -1:  
                     item = self._get_song_item(song, trackLabelFormat)
                     coverart = item.getProperty('coverart')
                     songname = song[0]
                     songalbum = song[2] or "none"
                     songalbumid = song[3] or "none"
                     songartist = song[4] or "none"
                     coverart = "none"
                     u=sys.argv[0]+"?mode="+str(MODE_SONG)+"&name="+urllib.quote_plus(songname)+"&id="+str(songid) \
                     +"&album="+urllib.quote_plus(songalbum) \
                     +"&albumid="+urllib.quote_plus(songalbumid) \
                     +"&artist="+urllib.quote_plus(songartist) \
                     +"&coverart="+urllib.quote_plus(coverart)
                     fav=sys.argv[0]+"?mode="+str(MODE_FAVORITE)+"&name="+urllib.quote_plus(songname)+"&id="+str(songid)
                     unfav=sys.argv[0]+"?mode="+str(MODE_UNFAVORITE)+"&name="+urllib.quote_plus(songname)+"&id="+str(songid)+"&prevmode="
                     menuItems = []
                     if isFavorites == True:
                          unfav = unfav +str(MODE_FAVORITES)
                     else:
                          menuItems.append((__language__(30071), "XBMC.RunPlugin("+fav+")"))
                     menuItems.append((__language__(30072), "XBMC.RunPlugin("+unfav+")"))
                     if playlistid > 0:
                          rmplaylstsong=sys.argv[0]+"?playlistid="+str(playlistid)+"&id="+str(songid)+"&mode="+str(MODE_REMOVE_PLAYLIST_SONG)+"&name="+playlistname
                          menuItems.append((__language__(30073), "XBMC.RunPlugin("+rmplaylstsong+")"))
                     else:
                          addplaylstsong=sys.argv[0]+"?id="+str(songid)+"&mode="+str(MODE_ADD_PLAYLIST_SONG)
                          menuItems.append((__language__(30074), "XBMC.RunPlugin("+addplaylstsong+")"))
                     item.addContextMenuItems(menuItems, replaceItems=False)
                     xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=item,isFolder=False, totalItems=items)
                     id = id + 1
                else:
                     end = min(end + 1,totalSongs)
                     if __debugging__ :
                          xbmc.log(song[0] + " does not exist.")
                n = n + 1

          if totalSongs > end:
                u=sys.argv[0]+"?mode="+str(MODE_SONG_PAGE)+"&id=playlistid"+"&offset="+str(end)+"&label="+str(trackLabelFormat)+"&name="+playlistname
                self._add_dir(__language__(30075) + '...', u, MODE_SONG_PAGE, self.songImg, 0, totalSongs - end)

          xbmcplugin.setContent(self.Qob._handle, 'songs')
          #xbmcplugin.setPluginFanart(int(sys.argv[1]), self.fanImg)
    
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
