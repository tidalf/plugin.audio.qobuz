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
#import os
import json
import requests
import pprint
from time import time
import math
import hashlib

from exception import QobuzXbmcError
from debug import warn, log

import socket

socket.timeout = 5

collectionLimit = 1000

class QobuzApi:

    def __init__(self):
        self.authtoken = None
        self.cookie = None
        self.user_id = None
        self.auf = None
        self.token_validity_time = 3600
        self.retry_time = [1,3,5,10]
        self.retry_num = 0
        self.appid = "285473059"
        self.last_error = None
        self.user = None
        self.password = None
        self.version = '0.2'
        self.baseUrl = 'http://player.qobuz.com/api.json/' + self.version
        self.stats = { 
                      'request': 0
        }
        self.__set_s4()

    def _check_ka(self, ka, mandatory, allowed = []):
        for label in mandatory:
            if not label in ka: raise QobuzXbmcError(who=self,what='missing_parameter', additional=label)
        for label in ka:
            if label not in mandatory and label not in allowed:
                raise QobuzXbmcError(who=self,what='invalid_parameter', additional=label)
    
    def set_logged(self,*args,**data):
        self.authtoken = data['data']['user_auth_token']
        self.user_id = data['data']['user']['id']
        self.logged_on = time()

    def __set_s4(self):
        import binascii
        from itertools import izip,cycle
        # appid and associated secret is for this app usage only 
        # Any use of the API implies your full acceptance of the General Terms and Conditions (http://www.qobuz.com/apps/api/QobuzAPI-TermsofUse.pdf)
        s3b = "Bg8HAA5XAFBYV15UAlVVBAZYCw0MVwcKUVRaVlpWUQ8="
        s3s = binascii.a2b_base64(s3b)
        self.s4 = ''.join(chr(ord(x) ^ ord(y)) for (x,y) in izip(s3s,cycle(self.appid)))

    def _api_request(self,params,uri,**opt):
        self.last_error = None
        self.stats['request'] += 1
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
            r = requests.post(url + uri,data=params,cookies=self.cookie,headers=qheaders)
        except:
            self.last_error = "Qobuz API POST fail"
            warn(self, self.last_error)
            return None
        # We have cookies
        if r.cookies:
                self.cookie = r.cookies
        if not r.content:
            warn(self,"No content return")
            return None
        try:  # try to get if connexion fail we try a second time 
            response_json = json.loads(r.content)
        except:
            warn(self,"Json loads failed to load... retrying!")
            try:  # please !
                response_json = json.loads(r.content)
            except:
                self.last_error = "Cannot load: " + url + uri
                warn(self,"Json loads failed a second time")
                return 0

        error = None
        try:
            error = response_json['status']
        except: pass
        if error == 'error':
            warn(self,"Something went wrong with request: "
                     + uri + "\n" + pprint.pformat(params) + "\n" + pprint.pformat(response_json))

            '''
            When something wrong we are deleting our auth token
                '''
            return None
        return response_json

    '''
    User
    '''
    def user_login(self, **ka):
        self._check_ka(ka, ['username', 'password'], ['email'])
        data = self._api_request(ka, "/user/login", noToken=True)
        if not data: return None
        if not 'user' in data: return None
        if not 'id' in data['user']: return None
        if not data['user']['id']: return None
        data['cookie'] = self.cookie
        data['user']['email'] = ''
        data['user']['firstname'] = ''
        data['user']['lastname'] = ''
        return data

    ''' 
    Track 
    '''
    def track_get(self, **ka):
        self._check_ka(ka, ['track_id'])
        data = self._api_request(ka,"/track/get")
        return data
    
    def track_getFileUrl(self, **ka):
        self._check_ka(ka, ['format_id', 'track_id'])
        ka['request_ts'] = time()
        params = {'format_id'  : str(ka['format_id']),
                  'intent'     : 'stream',
                  'request_ts' : ka['request_ts'] ,
                  'request_sig': str(hashlib.md5("trackgetFileUrlformat_id" + str(ka['format_id']) + "intentstream" + "track_id"
                                + str(ka['track_id']) + str(ka['request_ts']) + self.s4).hexdigest()), 'track_id': str(ka['track_id'])
        }
        return self._api_request(params,"/track/getFileUrl")
    
    # MAPI UNTESTED
    def track_search(self, **ka):
        self._check_ka(ka, ['query'], ['limit'])
        if not 'limit' in ka: ka['limit'] = collectionLimit
        data = self._api_request(ka,"/track/search")
        return data
    '''
    Artist
    '''
    def artist_get(self, **ka):
        self._check_ka(ka, ['artist_id'], ['extra'])
        data = self._api_request(ka,"/artist/get")
        return data
    '''
    Album
    '''
    def album_get(self, **ka):
        self._check_ka(ka, ['album_id'])
        return self._api_request(ka,"/album/get")

    def album_getFeatured(self, **ka):
        self._check_ka(ka, [], ['type', 'genre_id'])
        if not 'limit' in ka: ka['limit'] = collectionLimit
        return self._api_request(ka,"/album/getFeatured")

    '''
    Playlist
    '''
    def playlist_getUserPlaylists(self):
        params = { 'user_id': self.user_id }
        data = self._api_request(params,"/playlist/getUserPlaylists")
        return data

    def playlist_get(self,**ka):
        self._check_ka(ka, ['playlist_id'], ['extra'])
        return self._api_request(ka,"/playlist/get")
    
    def playlist_addTracks (self, **ka):
        self._check_ka(ka, ['playlist_id', 'track_ids'])
        return self._api_request(ka,"/playlist/addTracks")
    

    '''
    Purchase
    '''
    def purchase_getUserPurchases(self,**ka):
        self._check_ka(ka, [], ['order_id', 'order_line_id', 'flat', 'limit'])
        if not 'limit'in ka: ka['limit'] = collectionLimit
        return self._api_request(ka,"/purchase/getUserPurchases")

    def favorite_getUserFavorites(self, **ka):
        self._check_ka(ka, [], ['user_id', 'type', 'limit'])
        if not 'limit' in ka: ka['limit'] = collectionLimit
        return self._api_request(ka,"/favorite/getUserFavorites")

    # SEARCH #
    def search_getResults(self, **ka):
        self._check_ka(ka, ['query'], ['type', 'limit'])
        mandatory = ['query', 'type']
        for label in mandatory:
            if not label in ka: raise QobuzXbmcError(who=self, what='missing_parameter',additional=label)
        if not 'limit' in ka: ka['limit'] = collectionLimit
        return self._api_request(ka,"/search/getResults")


    # REPORT #    
    def report_streaming_start(self,track_id):
        # Any use of the API implies your full acceptance of the General Terms and Conditions (http://www.qobuz.com/apps/api/QobuzAPI-TermsofUse.pdf)
        params = {  'user_id': self.user_id,'track_id': track_id}
        return self._api_request(params,"/track/reportStreamingStart")

    def report_streaming_stop(self,track_id,duration):
        duration = math.floor(int(duration))
        if duration < 5:
            info(self,"Duration lesser than 5s, abort reporting")
            return None
        token = ''
        try:
            token = self.authtoken
        except:
            warn(self,'No authentification token')
            return None
        params = {  'user_id': self.user_id,
                    'track_id': track_id,
                    'duration': duration}
        return self._api_request(params,"/track/reportStreamingEnd")



    def favorites_create (self, **ka):
        mandatory = ['artist_ids', 'albums_ids', 'track_ids']
        found = None
        for label in mandatory:
            if label in ka: found = label
        if not found:
            raise QobuzXbmcError(who=self, what='missing_parameter',additional='artist_ids|albums_ids|track_ids')
        return self._api_request(ka,"/favorite/create")

    def playlist_deleteTracks (self, **ka):
        self._check_ka(ka, ['playlist_id'], ['playlist_track_ids'])
        return self._api_request(ka,"/playlist/deleteTracks")

    def playlist_create (self, **ka):
        self._check_ka(ka, ['name'], ['is_public', 'is_collaborative', 'tracks_id', 'album_id'])
        if not 'is_public' in ka: ka['is_public'] = True
        if not 'is_collaborative' in ka: ka['is_collaborative'] = False
        return self._api_request(ka,"/playlist/create")

    def playlist_delete (self, **ka):
        self._check_ka(ka, ['playlist_id'])
        if not 'playlist_id' in ka:  raise QobuzXbmcError(who=self, what='missing_parameter',additional='playlist_id')
        return self._api_request(ka,"/playlist/delete")

    def playlist_update (self, **ka):
        self._check_ka(ka, ['playlist_id'], ['name', 'description', 'is_public', 'is_collaborative', 'tracks_id'])
        res = self._api_request(ka,"/playlist/update")
        return res

    def artist_getSimilarArtists (self, **ka):
        self._check_ka(ka, ['artist_id'])
        return self._api_request(ka,"/artist/getSimilarArtists")


