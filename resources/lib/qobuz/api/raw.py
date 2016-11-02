'''
    qobuz.api.raw
    ~~~~~~~~~~~~~

    Our base api, all method are mapped like in <endpoint>_<method>
    see Qobuz API on GitHub (https://github.com/Qobuz/api-documentation)

    :part_of: xbmc-qobuz
    :copyright: (c) 2012-2016 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
import sys
import pprint
from time import time
import math
import hashlib
import socket
import binascii
from itertools import izip, cycle
import requests
import copy

from qobuz import exception
from qobuz import debug
from qobuz.api.user import current as user

socket.timeout = 5

class RawApi(object):

    def __init__(self):
        self.appid = '285473059'  # XBMC
        self.version = '0.2'
        self.baseUrl = 'http://www.qobuz.com/api.json'
        self.error = None
        self.status_code = None
        self.status = None
        self._baseUrl = '%s/%s' % (self.baseUrl, self.version)
        self.session = requests.Session()
        self.statContentSizeTotal = 0
        self.statTotalRequest = 0
        self.__set_s4()

    def _api_error_string(self, request, url='', params={}, json=''):
        return '{reason} ({status_code}): {error}'.format(reason=request.reason,
                                                          status_code=self.status_code,
                                                          error=self.error)

    def _check_ka(self, ka, mandatory, allowed=[]):
        '''Checking parameters before sending our request
        - if mandatory parameter is missing raise error
        - if a given parameter is neither in mandatory or allowed
        raise error (Creating exception class like MissingParameter
        may be a good idea)
        '''
        for label in mandatory:
            if not label in ka:
                raise exception.MissingParameter(label)
        for label in ka:
            if label not in mandatory and label not in allowed:
                raise exception.InvalidParameter(label)

    def __set_s4(self):
        '''appid and associated secret is for this app usage only
        Any use of the API implies your full acceptance of the
        General Terms and Conditions
        (http://www.qobuz.com/apps/api/QobuzAPI-TermsofUse.pdf)
        '''
        s3b = 'Bg8HAA5XAFBYV15UAlVVBAZYCw0MVwcKUVRaVlpWUQ8='
        s3s = binascii.a2b_base64(s3b)
        self.s4 = ''.join(chr(ord(x) ^ ord(y))
                          for (x, y) in izip(s3s,
                                             cycle(self.appid)))

    def _api_request(self, params, uri, **opt):
        '''Qobuz API HTTP get request
            Arguments:
            params:    parameters dictionary
            uri   :    service/method
            opt   :    Optionnal named parameters
                        - noToken=True/False

            Return None if something went wrong
            Return raw data from qobuz on success as dictionary

            * on error you can check error and status_code

            Example:

                ret = api._api_request({'username':'foo',
                                  'password':'bar'},
                                 'user/login', noToken=True)
                print 'Error: %s [%s]' % (api.error, api.status_code)

            This should produce something like:
            Error: [200]
            Error: Bad Request [400]
        '''
        self.statTotalRequest += 1
        self.error = None
        self.status_code = None
        self.status = None
        url = self._baseUrl + uri
        useToken = False if (opt and 'noToken' in opt) else True
        headers = {}
        if useToken and user.get_token():
            headers['x-user-auth-token'] = user.get_token()
        headers['x-app-id'] = self.appid
        '''DEBUG'''
        _copy_params = copy.deepcopy(params)
        if 'password' in _copy_params:
            _copy_params['password'] = '***'
        '''END / DEBUG'''
        r = None
        try:
            r = self.session.post(url, data=params, headers=headers)
        except Exception as e:
            self.status_code = 500
            self.error = 'Post request fail: %s' % e
            debug.error(self, self.error)
            return None
        self.status_code = int(r.status_code)
        if self.status_code != 200:
            self.error = self._api_error_string(r, url, _copy_params)
            debug.error(self, self.error)
            return None
        if not r.content:
            self.error = 'Request return no content'
            self.status_code = 500
            debug.error(self, self.error)
            return None
        self.statContentSizeTotal += sys.getsizeof(r.content)
        '''Retry get if connexion fail'''
        try:
            response_json = r.json()
        except Exception as e:
            debug.warn(self, 'Json loads failed to load... retrying!\n{}', repr(e))
            try:
                response_json = r.json()
            except:
                self.error = "Failed to load json two times...abort"
                debug.warn(self, self.error)
                return None
        try:
            self.status = response_json['status']
        except:
            pass
        if self.status == 'error':
            self.error = self._api_error_string(r, url, _copy_params,
                                                response_json)
            self.status_code = 500
            debug.warn(self, self.error)
            return None
        return response_json

    def user_login(self, **ka):
        data = self._user_login(**ka)
        if not data:
            return None
        return data

    def _user_login(self, **ka):
        self._check_ka(ka, ['username', 'password'], ['email'])
        data = self._api_request(ka, '/user/login', noToken=True)
        if not data:
            return None
        if not 'user' in data:
            return None
        if not 'id' in data['user']:
            return None
        if not data['user']['id']:
            return None
        data['user']['email'] = ''
        data['user']['firstname'] = ''
        data['user']['lastname'] = ''
        return data

    def user_update(self, **ka):
        self._check_ka(ka, [], ['player_settings'])
        return self._api_request(ka, '/user/update')

    def track_get(self, **ka):
        self._check_ka(ka, ['track_id'])
        return self._api_request(ka, '/track/get')

    def track_getFileUrl(self, intent="stream", **ka):
        self._check_ka(ka, ['format_id', 'track_id'])
        ka['request_ts'] = time()
        params = {'format_id': str(ka['format_id']),
                  'intent': intent,
                  'request_ts': ka['request_ts'],
                  'request_sig': str(hashlib.md5('trackgetFileUrlformat_id'
                                                 + str(ka['format_id'])
                                                 + 'intent'+intent
                                                 + 'track_id'
                                                 + str(ka['track_id'])
                                                 + str(ka['request_ts'])
                                                 + self.s4).hexdigest()),
                  'track_id': str(ka['track_id'])
                  }
        return self._api_request(params, '/track/getFileUrl')

    def track_search(self, **ka):
        self._check_ka(ka, ['query'], ['limit'])
        return self._api_request(ka, '/track/search')

    def track_resportStreamingStart(self, track_id):
        # Any use of the API implies your full acceptance
        # of the General Terms and Conditions
        # (http://www.qobuz.com/apps/api/QobuzAPI-TermsofUse.pdf)
        params = {'user_id': user.get_id(), 'track_id': track_id}
        return self._api_request(params, '/track/reportStreamingStart')

    def track_resportStreamingEnd(self, track_id, duration):
        duration = math.floor(int(duration))
        if duration < 5:
            debug.warn(self, 'Duration lesser than 5s, abort reporting')
            return None
        # @todo ???
        user_auth_token = ''  # @UnusedVariable
        try:
            user_auth_token = self.user_auth_token  # @UnusedVariable
        except:
            debug.warn(self, 'No authentification token')
            return None
        params = {'user_id': self.user_id,
                  'track_id': track_id,
                  'duration': duration
                  }
        return self._api_request(params, '/track/reportStreamingEnd')

    def album_get(self, **ka):
        self._check_ka(ka, ['album_id'])
        return self._api_request(ka, '/album/get')

    def album_getFeatured(self, **ka):
        self._check_ka(ka, [], ['type', 'genre_id', 'limit', 'offset'])
        return self._api_request(ka, '/album/getFeatured')

    def purchase_getUserPurchases(self, **ka):
        self._check_ka(ka, [], ['order_id', 'order_line_id', 'flat', 'limit',
                                'offset'])
        return self._api_request(ka, '/purchase/getUserPurchases')

    def search_getResults(self, **ka):
        self._check_ka(ka, ['query'], ['type', 'limit', 'offset'])
        mandatory = ['query', 'type']
        for label in mandatory:
            if not label in ka:
                raise exception.MissingParameter(label)
        return self._api_request(ka, '/search/getResults')

    def favorite_getUserFavorites(self, **ka):
        self._check_ka(ka, [], ['user_id', 'type', 'limit', 'offset'])
        return self._api_request(ka, '/favorite/getUserFavorites')

    def favorite_create(self, **ka):
        mandatory = ['artist_ids', 'album_ids', 'track_ids']
        found = None
        for label in mandatory:
            if label in ka:
                found = label
        if not found:
            raise exception.MissingParameter('artist_ids|albums_ids|track_ids')
        return self._api_request(ka, '/favorite/create')

    def favorite_delete(self, **ka):
        mandatory = ['artist_ids', 'album_ids', 'track_ids']
        found = None
        for label in mandatory:
            if label in ka:
                found = label
        if not found:
            raise exception.MissingParameter('artist_ids|albums_ids|track_ids')
        return self._api_request(ka, '/favorite/delete')

    def playlist_get(self, **ka):
        self._check_ka(ka, ['playlist_id'], ['extra', 'limit', 'offset'])
        return self._api_request(ka, '/playlist/get')

    def playlist_getUserPlaylists(self, **ka):
        self._check_ka(ka, ['type'], ['user_id', 'username', 'order', 'offset', 'limit'])
        if not 'user_id' in ka and not 'username' in ka:
            ka['user_id'] = user.get_id()
        return self._api_request(ka, '/playlist/getUserPlaylists')

    def playlist_addTracks(self, **ka):
        self._check_ka(ka, ['playlist_id', 'track_ids'])
        return self._api_request(ka, '/playlist/addTracks')

    def playlist_deleteTracks(self, **ka):
        self._check_ka(ka, ['playlist_id'], ['playlist_track_ids'])
        return self._api_request(ka, '/playlist/deleteTracks')

    def playlist_subscribe(self, **ka):
        mandatory = ['playlist_id']
        found = None
        for label in mandatory:
            if label in ka:
                found = label
        if not found:
            raise exception.MissingParameter('playlist_id')
        return self._api_request(ka, '/playlist/subscribe')

    def playlist_unsubscribe(self, **ka):
        self._check_ka(ka, ['playlist_id'])
        return self._api_request(ka, '/playlist/unsubscribe')

    def playlist_create(self, **ka):
        self._check_ka(ka, ['name'], ['is_public',
                                      'is_collaborative', 'tracks_id', 'album_id'])
        if not 'is_public' in ka:
            ka['is_public'] = True
        if not 'is_collaborative' in ka:
            ka['is_collaborative'] = False
        return self._api_request(ka, '/playlist/create')

    def playlist_delete(self, **ka):
        self._check_ka(ka, ['playlist_id'])
        if not 'playlist_id' in ka:
            raise exception.MissingParamter('playlist_id')
        return self._api_request(ka, '/playlist/delete')

    def playlist_update(self, **ka):
        self._check_ka(ka, ['playlist_id'], ['name', 'description',
                                             'is_public', 'is_collaborative', 'tracks_id'])
        return self._api_request(ka, '/playlist/update')

    def playlist_getPublicPlaylists(self, **ka):
        self._check_ka(ka, [], ['type', 'limit', 'offset'])
        return self._api_request(ka, '/playlist/getPublicPlaylists')

    def artist_getSimilarArtists(self, **ka):
        limit_max = 100 # @note: when limit > 100 server respond 40x
        if 'limit' in ka and ka['limit'] > limit_max:
            ka['limit'] = limit_max
        self._check_ka(ka, ['artist_id'], ['limit', 'offset'])
        return self._api_request(ka, '/artist/getSimilarArtists')

    def artist_get(self, **ka):
        self._check_ka(ka, ['artist_id'], ['extra'])
        return self._api_request(ka, '/artist/get')

    def genre_list(self, **ka):
        self._check_ka(ka, [], ['parent_id', 'limit', 'offset'])
        return self._api_request(ka, '/genre/list')

    def label_list(self, **ka):
        self._check_ka(ka, [], ['limit', 'offset'])
        return self._api_request(ka, '/label/list')

    def label_get(self, **ka):
        self._check_ka(ka, ['label_id'], ['limit', 'offset'])
        return self._api_request(ka, '/label/get')

    def article_listRubrics(self, **ka):
        self._check_ka(ka, [], ['extra', 'limit', 'offset'])
        return self._api_request(ka, '/article/listRubrics')

    def article_listLastArticles(self, **ka):
        self._check_ka(ka, [], ['rubric_ids', 'offset', 'limit'])
        return self._api_request(ka, '/article/listLastArticles')

    def article_get(self, **ka):
        self._check_ka(ka, ['article_id'])
        return self._api_request(ka, '/article/get')

    def collection_getAlbums(self, **ka):
        self._check_ka(ka, [], ['source', 'artist_id', 'query',
                                'limit', 'offset'])
        return self._api_request(ka, '/collection/getAlbums')

    def collection_getArtists(self, **ka):
        self._check_ka(ka, [], ['source', 'query',
                                'limit', 'offset'])
        return self._api_request(ka, '/collection/getArtists')

    def collection_getTracks(self, **ka):
        self._check_ka(ka, [], ['source', 'artist_id', 'album_id', 'query',
                                'limit', 'offset'])
        return self._api_request(ka, '/collection/getTracks')
