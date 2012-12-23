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
#import hashlib
#import pickle
import pprint
from time import time
import math
import hashlib
#import qobuz
from debug import *
import socket

socket.timeout = 5

class QobuzApi:

    def __init__(self):
        print 'Init QobuzAPI'
        self.auth = None
        self.authtoken = None
        self.cookie = None
        self.user_id = None
        self.auf = None
        self.token_validity_time = 3600
        self.retry_time = [1, 3, 5, 10]
        self.retry_num = 0
        self.appid = "285473059"
        self.last_error = None
        self.user = None
        self.password = None
        self.version = '0.2'
        self.baseUrl = 'http://player.qobuz.com/api.json/' + self.version

    def set_logged(self, *args, **data):
        self.authtoken = data['data']['user_auth_token']
        self.user_id = data['data']['user']['id']
    
    def _api_request(self, params, uri, **opt):
        self.last_error = None
        url = self.baseUrl
        useToken = False if (opt and 'noToken' in opt) else True

        # Setting header
        qheaders = {}
        if useToken and self.authtoken:
            qheaders["X-USER-AUTH-TOKEN"] = self.authtoken
            params['x-api-auth-token'] = self.authtoken
        qheaders["X-APP-ID"] = self.appid
       
        # Sending our request
        r = None
        try:
            r = requests.post(url + uri, data = params, cookies = self.cookie, headers = qheaders)
        except:
            warn(self, "API Error: POST fail")
            return None
        # We have cookies
        if r.cookies:
                self.cookie = r.cookies
        if not r.content:
            warn(self, "No content return")
            return None
        try:  # try to get if connexion fail we try a second time 
            response_json = json.loads(r.content)
        except:
            warn(self, "Json loads failed to load... retrying!")
            try:  # please !
                response_json = json.loads(r.content)
            except: 
                self.last_error = "Cannot load: " + url + uri
                warn(self, "Json loads failed a second time")
                return 0
            
        error = None
        try:
            error = response_json['status']
        except: pass
        if error == 'error':
            warn(self, "Something went wrong with request: "
                     + uri + "\n" + pprint.pformat(params) + "\n" + pprint.pformat(response_json))

            '''
            When something wrong we are deleting our auth token
                '''
            if self.auth:
                self.auth.delete_cache()
            return None
        return response_json
    
    def login(self, user, password):
        print "Login with user " + user
        # from cache.authentication import Cache_authentication
        params = {
                  'password': hashlib.md5(password).hexdigest(),
                  'username': user,
                  'email': user+'@QobuzXbmc.beta',
                   }
        data = self._api_request(params, "/user/login", noToken=True)
        if not data: return None
        if not 'user' in data: return None
        if not 'id' in data['user']: return None
        if not data['user']['id']: return None
        data['cookie'] = self.cookie
        data['user']['email'] = ''
        data['user']['firstname'] = ''
        data['user']['lastname'] = ''
        return data

    def get_track_url(self, track_id, context_type, context_id , format_id ):
        tsrequest = time()
        import binascii 
        from itertools import izip,cycle
        # appid and associated secret is for this app usage only 
        # Any use of the API implies your full acceptance of the General Terms and Conditions (http://www.qobuz.com/apps/api/QobuzAPI-TermsofUse.pdf)
        s3b = "Bg8HAA5XAFBYV15UAlVVBAZYCw0MVwcKUVRaVlpWUQ8="
        s3s = binascii.a2b_base64(s3b)
        s4 = ''.join(chr(ord(x) ^ ord(y)) for (x,y) in izip(s3s, cycle(self.appid)))
        params = {
                                   'format_id': str(format_id),
                                   'intent':'stream',
                                   'request_ts':tsrequest ,                        
                                   'request_sig':str(hashlib.md5("trackgetFileUrlformat_id" + str(format_id) + "intentstream" + "track_id" 
                                                            + str(track_id)+ str(tsrequest) + s4).hexdigest()),
                                   'track_id': str(track_id)
                }
        data = self._api_request(params, "/track/getFileUrl")
        return data

    def get_track(self, trackid):
        params = { #'x-api-auth-token': self.authtoken,
                                   'track_id': trackid}
        data = self._api_request(params, "/track/get")
        return data

    def get_user_playlists(self):
        params = { #'x-api-auth-token': self.authtoken,
                                   'user_id': self.user_id }
        data = self._api_request(params, "/playlist/getUserPlaylists")
        return data

    def getPlaylistSongs(self, playlistID):
        result = self._callRemote('getPlaylistSongs',
                                  {'playlistID' : playlistID});
        if 'result' in result:
            return self._parseSongs(result)
        else:
            return []

    def get_playlist(self, playlist_id = 39837):
        params = { #'x-api-auth-token':self.authtoken,
                                   'playlist_id':playlist_id,
                                   'extra':'tracks'}
        return self._api_request(params, "/playlist/get")

    def get_album_tracks(self, album_id, context_type = 'plalist'):
        params = { #'x-api-auth-token':self.authtoken, 
                  'album_id':album_id, 'context_type':context_type}
        return self._api_request(params, "/album/get")

    def get_product(self, id, context_type = "playlist"):
        return self.get_album_tracks(id, context_type)

    def get_recommandations(self, genre_id, typer = "new-releases", limit = 100):
        limit = 1000
        if genre_id == 'null':
            params = {#'x-api-auth-token': self.authtoken,
                                       'type': typer, 'limit': limit}
        else:
            params = {#'x-api-auth-token':self.authtoken,
                                       'genre_id': genre_id,
                                       'type': typer,
                                       'limit': limit}

        return self._api_request(params, "/album/getFeatured")

    def get_purchases(self, limit = 100):
        params = {#'x-api-auth-token':self.authtoken,
                                   'user_id': self.user_id }
        return self._api_request(params, "/purchase/getUserPurchases")
    
    def get_favorites(self, limit = 100):
        params = {#'x-api-auth-token':self.authtoken,
                                   # 'type': "tracks",
                                   'user_id': self.user_id }
        return self._api_request(params, "/favorite/getUserFavorites")

    # SEARCH #
    def search_tracks(self, query, limit = 100):
        params = {#'x-api-auth-token':self.authtoken,
                                   'query': query.encode("utf8", "ignore"),
                                   'type': 'tracks',
                                   'limit': limit}
        return self._api_request(params, "/search/getResults")

    def search_albums(self, query, limit = 100):
        params = {#'x-api-auth-token':self.authtoken,
                                   'query': query.encode("utf8", "ignore"),
                                   'type': 'albums', 'limit': limit}
        return self._api_request(params, "/search/getResults")

    def search_artists(self, query, limit = 100):
        params = {#'x-api-auth-token':self.authtoken,
                                   'query': query.encode("utf8", "ignore"),
                                   'type': 'artists', 'limit': limit}
        return self._api_request(params, "/search/getResults")

    def get_albums_from_artist(self, id, limit = 100):
        params = {#'x-api-auth-token': self.authtoken,
                                   'artist_id': id, 'limit': limit,'extra':'albums'}
        data = self._api_request(params, "/artist/get")
        return data
    # REPORT #    
    def report_streaming_start(self, track_id):
        # Any use of the API implies your full acceptance of the General Terms and Conditions (http://www.qobuz.com/apps/api/QobuzAPI-TermsofUse.pdf)
        params = {#'x-api-auth-token':self.authtoken,
                                   'user_id': self.user_id,
                                   'track_id': track_id}
        return self._api_request(params, "/track/reportStreamingStart")

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
        params = {#'x-api-auth-token': token,
                                   'user_id': self.user_id,
                                   'track_id': track_id,
                                   'duration': duration}
        return self._api_request(params, "/track/reportStreamingEnd")

    def playlist_add_track (self, playlist_id, tracks_id):
        params = {#'x-api-auth-token': self.authtoken,
                                   'track_ids': tracks_id,
                                   'playlist_id': playlist_id}
        log("info", "adding " + tracks_id + " to playlist " + playlist_id)
        return self._api_request(params, "/playlist/addTracks")
   
    def favorites_add_track (self, tracks_id):
        params = {#'x-api-auth-token': self.authtoken,
                                   'track_ids': tracks_id}
        log("info", "adding " + tracks_id + " to favorites ")
        return self._api_request(params, "/favorite/create")    
    
    def playlist_remove_track (self, playlist_id, playlist_track_id,):
        params = {#'x-api-auth-token': self.authtoken,
                                   'playlist_id': playlist_id,
                                   'playlist_track_ids': playlist_track_id,
                                   }
        log("info", "deleting " + playlist_track_id + " from playlist " + playlist_id)
        return self._api_request(params, "/playlist/deleteTracks")

    def playlist_create (self, playlist_name, tracks_id = '', description = '', album_id = '', is_public = 'on', is_collaborative = 'off'):
        params = {#'x-api-auth-token': self.authtoken,
                                   'name': playlist_name,
                                   'is_public': is_public,
                                   'track_ids':tracks_id,
                                   'album_id':album_id,
                                   'is_collaborative': is_collaborative,
                                   'description': description,
                                   'spotify_track_uris':'',
                                   'deezer_playlist_url':''}

        log("info", "creating new playlist" + repr(playlist_name) + "with (or without) tracks :" + tracks_id + ")")
        return self._api_request(params, "/playlist/create")

    def playlist_delete (self, playlist_id):
        params = { #'x-api-auth-token': self.authtoken,
                                   'playlist_id': playlist_id}
        log("info", "deleting playlist: " + str(playlist_id))
        return self._api_request(params, "/playlist/delete")

    def playlist_update (self, playlist_id, name, description = '', album_id = '', is_public = 'on', is_collaborative = 'off'):
        params = { #'x-api-auth-token': self.authtoken,
                                   'name'               : name,
                                   'is_public'          : is_public,
                                   'is_collaborative'   : is_collaborative,
                                   'description'        : description,
                                   'spotify_track_uris' : '',
                                   'deezer_playlist_url': '',
                                   'playlist_id'        : playlist_id }
        log("info", "updating playlist " + str(playlist_id))
        res = self._api_request(params, "/playlist/update")
        return res

    def get_similar_artists (self, artist_id):
        params = { 'artist_id': artist_id }
        return self._api_request(params, "/artist/getSimilarArtists")
        
if __name__ == '__main__':
    pass
