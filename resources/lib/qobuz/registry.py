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
import pprint
from exception import QobuzXbmcError
from api import QobuzApi
from time import time
from utils.file.write import safe_write
import cPickle as pickle
import os
from debug import *
import hashlib

class QobuzLocalStorage(object):

    def __init__(self,**ka):
        # Checking mandatory parameters
        mandatory = ['username', 'password', 'streamFormat']
        for key in mandatory:
            if not key in ka: raise QobuzXbmcError(
                                                       who=self,
                                                       what='missing_parameter',
                                                       additional=key)
        
        # Setting our options
        self.options = ka
        if not 'autoSave' in self.options:
            self.options['autoSave'] = True
        if not 'autoLoad' in self.options:
            self.options['autoLoad'] = True
        if not 'refresh' in self.options:
            self.options['refresh'] = 3600
        if not 'overwrite' in self.options:
            self.options['overwrite'] = True
        if not 'hashKey' in self.options:
            self.options['hashKey'] = False
        # Our dictionary storage
        self.data = {}

        # Qobuz API
        self.api = QobuzApi()
     
        # Login into Qobuz our raise exception   
        key = self.make_key(name='user', id=0)
        data = self.get(name='user', id=0, username=ka['username'], password=ka['password'])
        if not data: raise QobuzXbmcError(who= self, what= 'login_failure', additional= ka['user'])
        # We feed our api wit user data (auth_token, rights ...)
        self.api.set_logged(**data)
    
    def lastError(self):
        return self.api.last_error
    
    def set(self,**ka):
        mandatory = ['name','id']
        for key in mandatory:
            if not key in ka: 
                raise QobuzXbmcError(who=self, what='missing_parameter', additional=key)
        key = self.make_key(**ka)
        if not self.options['overwrite'] and key in self.data:
            raise QobuzXbmcError(who=self, what='key_exist', additional=key)
        self.data[key] = {
                          'name': ka['name'],
                          'id': ka['id'],
                          'saved': False,
                          'data': ka['value'],
                          'updatedOn': time(),
                          'refresh': self.options['refresh']
                          }
        if self.options['autoSave']:
            self.save(key)
        return self

    def save(self,key):
        QobuzXbmcError(who=self, what='not_implemented_in_child_class', additional='save')

    def make_key(self, **ka):
        key = self._make_key(**ka)
        if self.options['hashKey']:
            return self.hash_key(key)
        return key
    
    def _make_key(self, **ka):
        QobuzXbmcError(who= self,what= 'not_implemented_in_child_class',additional='make_key')

    def hash_key(self, key):
        h = hashlib.new('sha256')
        h.update(key)
        return h.hexdigest()
    
    def get(self,*args, **ka):
        key = self.make_key(**ka)
        if not key in self.data:
                self.load(**ka)
        if key in self.data:
            return self.data[key]
        return None

    def load(self, **ka):
        self.hook_pre_load(**ka)
        limit = 1000
        # noRemote prevent data loading from Qobuz (local key only)
        if 'noRemote' in ka and ka['noRemote'] == True:
            return False
        key = self.make_key(**ka)
        if key in self.data and self.fresh(key):
            return self.data[key]
        log(self, "Loading data from Qobuz")
        response = None
        # We are deleting name and id because we don't want to send them
        # to Qobuz
        name = ka['name']
        del ka['name']
        id = ka['id']
        del ka['id']
        # Switching on name
        if name == 'user':
            response = self.api.user_login(**ka)
        elif name == 'product':
            response = self.api.album_get(album_id=id)
        elif name == 'user-playlists':
            response = self.api.playlist_getUserPlaylists()
        elif name == 'user-playlist':
            response = self.api.playlist_get(playlist_id=id,extra='tracks')
        elif name == 'track':
            response = self.api.track_get(track_id=id)
        elif name == 'stream-url':
            response = self.api.track_getFileUrl(track_id=id, format_id=self.options['streamFormat'])
        elif name == 'purchases':
            response = self.api.purchase_getUserPurchases(limit=limit)
        elif name == 'recommendation':
            response = self.api.album_getFeatured(**ka) 
        elif name == 'favorites':
            response = self.api.favorite_getUserFavorites(limit=limit)
        elif name == 'artist':
            response = self.api.artist_get(artist_id=id, limit=limit)
        else:
            QobuzXbmcError(
                        who= self,
                        what= 'qobuz_api_invalid_query',
                        additional= pprint.pformat(ka))
        if not response:
                warn(self, "Loading from Qobuz fail")
                return False
        ka['value'] = response
        ka['name'] = name
        ka['id'] = id
        self.set(**ka)
        return True

    
    def fresh(self, key):
        if not key in self.data:
            return False
        if (time() - self.data[key]['updatedOn']) > self.options['refresh']:
            return False
        return True
        
    def saved(self,key,value=None):
        if not key:
            QobuzXbmcError(who=self, what='missing_parameter', additional='key')
        if not key in self.data:
            QobuzXbmcError(who=self,what= 'undefined_key', additional=key)
        if value == None:
            return self.data[key]['saved']
        self.data[key]['saved'] = True if value else False
        return self

    def delete(self, **ka):
        key = self.make_key(**ka)
        self.data[key] = None
        del self.data[key]
        
class QobuzCacheDefault(QobuzLocalStorage):
    def __init__(self,*args,**ka):
        super(QobuzCacheDefault,self).__init__(*args, **ka)
        if not 'basePath' in ka:
            QobuzXbmcError(who=self, what='missing_parameter',additional='basePath')

    def _make_key(self, *args, **ka):
        if not 'id' in ka: ka['id'] = 0
        return ka['name'] + '-' + str(ka['id']);

    def _make_sub_path(self, xpath, key, size, count):
        if count == 0 or len(key) < size + 1:
            return key + '.dat'
        subp = key[:size]
        root = os.path.join(os.path.join(*xpath), subp)
        if not os.path.exists(root):
            os.mkdir(root)
        xpath.append(subp)
        count -= 1
        return self._make_sub_path(xpath, key[size:], size, count )
        
    def _make_path(self, key):
        xpath = []
        xpath.append(self.options['basePath'])
        fileName = None
        if self.options['hashKey']:
            fileName = self._make_sub_path(xpath, key, 2, 1)
        else:
            fileName = key + '.dat'
        return os.path.join(os.path.join(*xpath), fileName)
    
    def hook_pre_load(self, **ka):
        log(self, "Loading from disk")
        key = self.make_key(**ka)
        cache = self._make_path(key)
        #cache = os.path.join(self.options['basePath'], key+'.dat');
        if not os.path.exists(cache):
            warn(self, "Path doesn't exists " + cache)
            return False
        with open(cache, 'rb') as f:
            f = open(cache, 'rb')
            try:
                self.data[key] = pickle.load(f)
            except: 
                warn(self, "Pickle can't load data from file")
                return False
        return True
        
    def save(self, key = None):
        if key == None:
            count = 0
            for key in self.data:
                if not self.saved(key):
                    count += 1
                    self.save(key)
            return count
        if not key in self.data:
            raise QobuzXbmcError(who=self, what='undefined_key',additional=key)
        cache = self._make_path(key)
        with open(cache, 'wb') as f:
            s = pickle.dump(self.data[key], f, protocol = pickle.HIGHEST_PROTOCOL)
            f.flush()
            os.fsync(f)
        return s
        warn(self, 'Cannot save key ' + key)
        return 0

    def delete(self, **ka):
        key = self.make_key(**ka)
        info(self, 'Deleting key: ' + key)
        cache = os.path.join(self.options['basePath'], key + '.dat')
        if not os.path.exists(cache):
            return False
        sw = safe_write();
        if sw.unlink(cache):
            super(QobuzCacheDefault, self).delete(**ka)

class QobuzCacheCommon(QobuzLocalStorage):
    def __init__(self,*args,**ka):
        print "Loading Common cache"
        import xbmcaddon
        import xbmc
        import StorageServer
        #StorageServer.dbg = True
        self.storage = StorageServer.StorageServer('plugin_audio_qobuz', 24)
        super(QobuzCacheCommon,self).__init__(*args, **ka)
        print "import ok"
        
    def _make_key(self, *args, **ka):
            if not 'id' in ka: ka['id'] = 0
            return "" + ka['name'] + '-' + str(ka['id']);
    
    def hook_pre_load(self, **ka):
        key = self.make_key(**ka)
        data = self.storage.get(key)
        log(self, "LOADING " + key + ' / ' + pprint.pformat(data))
        if data:
            self.data[key] = pickle.loads(data)
    
    def save(self, key = None):
        if key == None:
            count = 0
            for key in self.data:
                if not self.saved(key):
                    count += 1
                    self.save(key)
            return count
        if not key in self.data:
            QobuzXbmcError(who=self,what='undefined_key', additional=key)
        data = pickle.dumps(self.data[key], 0)
        print "SAVE key " + key + ' / ' + pprint.pformat(data)
        self.storage.set(key, data)
        self.saved(key,True)
        return 1

class QobuzRegistry():
    
    def __init__(self,*args,**ka):
        if not 'cacheType' in ka:
            ka['cacheType'] = 'default'
        if ka['cacheType'] == 'default':
            self.cache = QobuzCacheDefault(*args,**ka)
        elif ka['cacheType'] == 'xbmc-common':
            cache = None
            try:
                cache = QobuzCacheCommon(*args, **ka)
            except Exception:
                cache = QobuzCacheDefault(*args, **ka)
            self.cache = cache
        else:
            QobuzXbmcError(who=self, what='unknown_cache_type',additionnal=ka['cacheType'])
        return None
    
    def get_api(self):
        return self.cache.api
    
    def lastError(self):
        return self.cache.lastError()
    
    def get(self,**ka):
        if not 'id' in ka:
            ka['id'] = 0
        return self.cache.get(**ka);

    def set(self,**ka):
        self.cache.set(**ka)
        
    def save(self):
        self.cache.save()
        
    def delete(self, **ka):
        if not 'id' in ka:
            ka['id'] = 0
        self.cache.delete(**ka)
    
    def make_key(self, **ka):
        return self.cache.make_key(**ka)


if __name__ == '__main__':
#    try:
#        QobuzXbmcError({'Who': 'TestException','What': 'test_exception','With': 'TestingException'})
#    except(QobuzXbmcError):
#        pass

    reg = QobuzRegistry(user='SET_USER', password='SET_PASSWORD', cacheType='xbmc-common',
                   basePath='c:/tmp/qobuz/',
                   autoSave=True,
                   autoLoad=True, refresh=3600)
    
    user_playlists = reg.get(name='user-playlists', id=12342323)
    if not user_playlists:
        print "Error:" + repr(reg.lastError()) 
    for pl in user_playlists['data']['playlists']['items']:
        print  '[' + repr(pl['id']) + ']' + "Name: " + pl['name']
        playlist = reg.get(name='playlist', id=pl['id'])
        