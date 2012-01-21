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

import qobuz
from debug import *

class QobuzApi:

    def __init__(self):
        self.auth = None
        self.authtoken = None
        self.userid = None
        self.auf = None
        self.token_validity_time = 3600
        self.retry_time = [1, 3, 5, 10]
        self.retry_num = 0
    
    def _api_request(self, params, uri):      
        url = "http://player.qobuz.com"
        r = requests.post(url + uri, data = params)
        response_json = json.loads(r.content)
        error = None
        try:
            error = response_json['status']
        except: pass
        if error == 'error':
            warn(self, "Something went wrong with request: " 
                     + uri + "\n"  + pprint.pformat(params) + "\n" + pprint.pformat(response_json))
            
            '''
            When something wrong we are deleting our auth token
                '''
            self.auth.delete_cache()
            return None
        return response_json
    
    def login(self, user, password):
        from data.auth import QobuzAuth
        auth = QobuzAuth(user, password)
        data = auth.get_data()
        if not data:
            return False
        self.authtoken = data['user']['session_id']
        self.userid = data['user']['id']
        self.auth = auth
        self.auf = data['user']['credential']['allowed_audio_format_ids']
        return auth
    
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
            params = {'x-api-auth-token': self.authtoken, 
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
        data = self._api_request(params,"/api.json/0.1/artist/get")
        return data
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
    
    def playlist_add_track (self, track_ids, playlist_id):
        params = {'x-api-auth-token': token, 
                                   'track_ids': track_ids,
                                   'playlist_id': playlist_id}
        log("info","adding " + trackid + "to playlist" + playlist_id )
        return self._api_request(params,"/api.json/0.1/playlist/addTracks")
     
    # TOBECHECKED 
    def playlist_delete_track (self, playlist_track_id,playlist_id):
        params = {'x-api-auth-token': token, 
                                   'playlist_track_id': playlist_track_id,
                                   'playlist_id': playlist_id}
        log("info","deleting " + playlist_track_id + "from playlist" + playlist_id )
        return self._api_request(params,"/api.json/0.1/playlist/deleteTracks")
    
    def playlist_create (self, playlist_name, track_ids='', description='', album_id='', is_public='on', is_collaborative='off' ):
        params = {'x-api-auth-token': token, 
                                   'name': playlist_name,
                                   'is_public':on,
                                   'track_ids':track_ids,
                                   'album_id':album_id,
                                   'is_collaborative':is_collaborative,
                                   'description':description,
                                   'spotify_track_uris':'',
                                   'deezer_playlist_url':''}
                                          
        log("info","creating new playlist" + playlist_name + "with (or without) tracks :", tracks_ids )
        #&is_public=on&spotify_track_uris=&deezer_playlist_url=&track_ids=1068442%2C1068443%2C1068444&album_id=&is_collaborative=off
        return self._api_request(params,"/api.json/0.1/playlist/create")

    def playlist_delete (self, playlist_id):
        params = {'x-api-auth-token': token, 
                                   'playlist_id': playlist_id}
        log("info","deleting playlist: " + playlist_id )
        return self._api_request(params,"/api.json/0.1/playlist/delete")
  
    def playlist_update (self, playlist_id, name, description='', album_id='', is_public='on', is_collaborative='off' ):
        params = {'x-api-auth-token': self.authtoken, 
                                   'name'               : name,
                                   'is_public'          : is_public,
                                   'is_collaborative'   : is_collaborative,
                                   'description'        : description,
                                   'spotify_track_uris' : '',
                                   'deezer_playlist_url': '',
                                   'playlist_id'        : playlist_id }
        #name=John+Coltrane+Quartet&description=John+Coltrane+Quartet&is_public=on&spotify_track_uris=&deezer_playlist_url=&playlist_id=78237&is_collaborative=off

        log("info","updating playlist " + str(playlist_id) )
        res =  self._api_request(params,"/api.json/0.1/playlist/update")
        return res

if __name__ == '__main__':
    pass
