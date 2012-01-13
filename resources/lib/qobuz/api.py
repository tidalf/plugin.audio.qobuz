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
import json
import time
import requests
import hashlib
import pickle
import pprint
from time import time
import math

from debug import log, info, warn

class QobuzApi:

    def __init__(self, Core = None):
        self.Core = Core
        self.headers = {"Content-type": "application/x-www-form-urlencoded","Accept": "text/plain"}
        self.authtoken = None
        self.userid = None
        self.authtime = None
        self.token_validity_time = 3600
        self.cachePath = None
        if self.Core:
            self.set_cache_path(os.path.join(self.Core.Bootstrap.cacheDir,'auth.dat'))
            info(self, 'authCacheDir: ' + self.get_cache_path())
        self.retry_time = [1, 3, 5, 10]
        self.retry_num = 0

    def set_cache_path(self, path):
        self.cachePath = path
        
    def get_cache_path(self):
        return self.cachePath
    
    def save_auth(self):
        cachePath = self.get_cache_path()
        if not cachePath:
            warn(self, "Cache path not defined (cannot save auth token)")
            return False
        data = {}
        data['authtoken'] = self.authtoken
        data['authtime'] = self.authtime
        data['userid'] = self.userid
        f = None
        try:
            f = open(cachePath, 'wb')
        except:
            warn(self, "Cannot open authentification cache for writing!")
            return False
        try:
            pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)
            f.close()
        except:
            warn(self, 'Cannot save authentification')
            return False
        return True
    
    def load_auth(self):
        cachePath = self.get_cache_path()
        if not cachePath:
            warn(self, "Cache path not defined (need to login each time)")
            return False
        
        if not os.path.exists(cachePath):
            warn(self, "Caching directory doesn't exist: " + cachePath)
            return False
        mtime = None
        try:
            mtime = os.path.getmtime(cachePath)
        except:
            warn(self,"Cannot stat cache file: " + cachePath)
        if (time() - mtime) > self.token_validity_time:
            info(self,"Our authentification token must be invalid")
            return False
        f = None
        try:
            f = open(cachePath, 'rb')
        except:
            warn(self, "Cannot open authentification cache for reading!")
            return False
        data = None
        try:
            data = pickle.load(f)
        except:
            warn(self, "Cannot load serialized data")
            return False
        pprint.pprint(data)
        self.authtime = data['authtime']
        self.authtoken = data['authtoken']
        self.userid = data['userid']
        return True
    
    def delete_auth_cache(self):
        cachePath = self.get_cache_path()
        if not cachePath:
            return False
        try:
            os.remove(cachePath)
            return True
        except: warn(self, "Cannot delete auth cache")
        return False
    
    def _api_request(self, params, uri):      
        info(self, "Get " + uri + ' / ' + params)
        url = "http://player.qobuz.com"
        r = requests.post(url + uri, data = params)
        response_json = json.loads(r.content)
        try:
            if response_json['status'] == "error":
                warn(self, "Something went wrong with request: " 
                     + uri + ' / ' + params)
                pprint.pprint(response_json)
                '''
                    When something wrong we are deleting our auth token
                '''
                self.delete_auth_cache()
                return None
        except: pass
        return response_json
    
    def login(self, user, password):
        if self.load_auth():
            info(self, 'Using authentification token from cache')
            return self.userid
        params = {'x-api-auth-token':'null','email': user ,
                                   'hashed_password': hashlib.md5(password).hexdigest() }
        
        data = self._api_request(params,"/api.json/0.1/user/login")
        if not data: return None
        if not 'user' in data: return None
        self.authtoken = data['user']['session_id']
        self.userid = data['user']['id']
        self.authtime = time()
        self.save_auth()
        return self.userid
    
    def get_track_url(self,track_id,context_type,context_id ,format_id = 6):
        params = {
                                   'x-api-auth-token':self.authtoken,
                                   'track_id': track_id ,
                                   'format_id': format_id,
                                   'context_type':context_type,
                                   'context_id':context_id}
        data = self._api_request(params,"/api.json/0.1/track/getStreamingUrl") 
        return data
            

    def get_track(self,trackid):
        params = {'x-api-auth-token': self.authtoken,
                                   'track_id': trackid}
        data = self._api_request(params,"/api.json/0.1/track/get")
        return data

    def get_user_playlists(self):
        params = {'x-api-auth-token': self.authtoken,
                                   'user_id': self.userid }
        data = self._api_request(params,"/api.json/0.1/playlist/getUserPlaylists")
        return data

    def getPlaylistSongs(self,playlistID):
        result = self._callRemote('getPlaylistSongs', 
                                  {'playlistID' : playlistID});
        if 'result' in result:
            return self._parseSongs(result)
        else:
            return []

    def get_playlist(self,playlist_id=39837):
        params = {'x-api-auth-token':self.authtoken,
                                   'playlist_id':playlist_id,
                                   'extra':'tracks'}
        return self._api_request(params,"/api.json/0.1/playlist/get")

    def get_album_tracks(self,album_id,context_type='plalist'):
        params = {'x-api-auth-token':self.authtoken,'product_id':album_id,'context_type':context_type}
        return self._api_request(params,"/api.json/0.1/product/get")

    def get_product(self, id, context_type = "playlist"):
        return self.get_album_tracks(id,context_type)
    
    def get_recommandations(self, genre_id, typer = "new-releases", limit = 100):
        if genre_id == 'null':
            params = {'x-api-auth-token':self.authtoken, 
                                       'type': typer, 'limit': limit}
        else:
            params = {'x-api-auth-token':self.authtoken, 
                                       'genre_id': genre_id, 
                                       'type': typer, 
                                       'limit': limit}
        
        return self._api_request(params,"/api.json/0.1/product/getRecommendations")
    
    def get_purchases(self, limit = 100):
        params = {'x-api-auth-token':self.authtoken, 
                                   'user_id': self.userid }
        return self._api_request(params,"/api.json/0.1/purchase/getUserPurchases")
    
    # SEARCH #
    def search_tracks(self, query, limit = 100):
        params = {'x-api-auth-token':self.authtoken, 
                                   'query': query.encode("utf8","ignore"), 
                                   'type': 'tracks', 
                                   'limit': limit}
        return self._api_request(params,"/api.json/0.1/track/search")

    def search_albums(self, query, limit = 100):
        params = {'x-api-auth-token':self.authtoken, 
                                   'query': query.encode("utf8","ignore"), 
                                   'type': 'albums', 'limit': limit}
        return self._api_request(params,"/api.json/0.1/product/search")
    
    def search_artists(self, query, limit = 100):
        params = {'x-api-auth-token':self.authtoken, 
                                   'query': query.encode("utf8","ignore"), 
                                   'type': 'artists', 'limit': limit}
        return self._api_request(params,"/api.json/0.1/track/search")
    
    def get_albums_from_artist(self, id, limit = 100):
        params = {'x-api-auth-token':self.authtoken, 
                                   'artist_id': id, 'limit': limit}
        return self._api_request(params,"/api.json/0.1/artist/get")

    # REPORT #    
    def report_streaming_start(self, track_id):
        #info(self, "Report Streaming start for user: " + str(self.userid) + ", track: " + str(track_id))
        params = {'x-api-auth-token':self.authtoken, 
                                   'user_id': self.userid, 
                                   'track_id': track_id}
        return self._api_request(params,"/api.json/0.1/track/reportStreamingStart")        

    def report_streaming_stop(self, track_id, duration):
        duration = math.floor(int(duration))
        if duration < 5:
            info(self, "Duration lesser than 5s, abort reporting")
            return None
        token = ''
        try:
            token = self.authtoken
        except:
            warn(self, 'No authentification token')
            return None
        #info(self, "Report Streaming stop for user:  " + str(self.userid) + ", track: " + str(track_id))
        params = {'x-api-auth-token': token, 
                                   'user_id': self.userid, 
                                   'track_id': track_id,
                                   'duration': duration}
        return self._api_request(params,"/api.json/0.1/track/reportStreamingEnd")

if __name__ == '__main__':
    pass
