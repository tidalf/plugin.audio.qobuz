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
import os
import sys

import xbmcaddon
import xbmc

import tempfile

from icacheable import ICacheable
from api import QobuzApi
from mydebug import log, info, warn
from utils import _sc
from track import QobuzTrack
from icacheable import ICacheable
from getrecommandation import QobuzGetRecommandation
from product import QobuzProduct
from userplaylists import QobuzUserPlaylists
from playlist import QobuzPlaylist
from searchtracks import QobuzSearchTracks
from searchalbums import QobuzSearchAlbums
from searchartists import QobuzSearchArtists

"""
 Class QobuzXbmc
"""
class QobuzXbmc:
    fanImg = xbmc.translatePath(os.path.join('resources/img/','playlist.png'))
    def __init__(self, baseDir):
        self.data = ""
        self.conn = ""
        self.Api = QobuzApi(self)
        self.__playlists = {}
        self._handle = int(sys.argv[1])
        self.baseDir = baseDir
        self.cacheDir = os.path.join(xbmc.translatePath('special://temp/'), os.path.basename(self.baseDir))
        info(self, "cacheDir: " + self.cacheDir)
        if os.path.isdir(self.cacheDir) == False:
            os.makedirs(self.cacheDir)
            info(self, "Make cache directory: " + self.cacheDir)

    def login(self,user,password):
        info(self, "Try to login as user: " + user)
        return self.Api.login(user,password)

    def is_logged(self):
        return self.Api.userid

    def getPlaylist(self,id):
        return QobuzPlaylist(self, id)

    def getProduct(self,id):
        return QobuzProduct(self, id)

    def getUserPlaylists(self):
        return QobuzUserPlaylists(self)

    def getQobuzAlbum(self, id):
        return QobuzAlbum(self, id)

    def getTrack(self,id):
        return QobuzTrack(self,id)
    
    def getEncounteredAlbum(self):
        return QobuzEncounteredAlbum(self)
    
    def getQobuzSearchTracks(self):
        return QobuzSearchTracks(self)

    def getQobuzSearchAlbums(self):
        return QobuzSearchAlbums(self)
    
    def getQobuzSearchArtists(self):
        return QobuzSearchArtists(self)

    def getProductsFromArtist(self):
        return QobuzSearchAlbums(self)

    def watchPlayback( self ):
        if not self.player.isPlayingAudio():
            self.Timer.stop()
            exit(0)
        info(self, "Watching player: " + self.player.getPlayingFile())
        self.Timer = threading.Timer( 6, self.watchPlayback, () )
        self.Timer.start()

    def getRecommandation(self,genre_id):
        return QobuzGetRecommandation(self, genre_id)

    def getRecommandation(self, genre_id,type):
        return QobuzGetRecommandation(self, genre_id, type)


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
#
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