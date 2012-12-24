import pprint
from exception import QobuzXbmcError
from api import QobuzApi
from time import time
from utils.file.write import safe_write
import cPickle as pickle
import os
from debug import *

class QobuzLocalStorage(object):

    def __init__(self,**ka):
        # Checking mandatory parameters
        mandatory = ['user', 'password', 'streamFormat']
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
        
        # Our dictionary storage
        self.data = {}

        # Qobuz API
        self.api = QobuzApi()
     
        # Login into Qobuz our raise exception   
        key = self.make_key(name='user', id=0)
        data = self.get(name='user', id=0, user=ka['user'], password=ka['password'])
        if not data: raise QobuzXbmcError(who= self, what= 'login_failure', additional= ka['user'])
        print "We are logged"
        # We feed our api wit user data (auth_token, rights ...)
        self.api.set_logged(**data)
        print 'Token: ' + self.api.authtoken
    
    
    def lastError(self):
        return self.api.last_error
        
    def set(self,**kwargs):
        mandatory = ['name','id']
        for key in mandatory:
            if not key in kwargs: 
                raise QobuzXbmcError(who=self, what='missing_parameter', additionnal=key)
        key = self.make_key(**kwargs)
        if not self.options['overwrite'] and key in self.data:
            raise QobuzXbmcError(who=self, what='key_exist', additional=key)
        self.data[key] = {
                          'name': kwargs['name'],
                          'id': kwargs['id'],
                          'saved': False,
                          'data': kwargs['value'],
                          'updatedOn': time(),
                          'refresh': self.options['refresh']
                          }
        if self.options['autoSave']:
            print "AutoSaving...\n"
            self.save(key)
        return self

    def save(self,key):
        QobuzXbmcError(who=self, what='not_implemented_in_child_class', additional='save')

    def make_key(self,*args, **kwargs):
        QobuzXbmcError(who= self,what= 'not_implemented_in_child_class',additional='make_key')

    def get(self,*args, **kwargs):
        key = self.make_key(**kwargs)
        if not key in self.data:
            self.load(**kwargs)
        if key in self.data:
            return self.data[key]
        return None

    def load(self, **ka):
        log(self, "Loading data from Qobuz")
        if ka['name'] == 'user':
            response = self.api.login(ka['user'], ka['password'])
        elif ka['name'] == 'product':
            response = self.api.get_product(ka['id'])
        elif ka['name'] == 'user-playlists':
            response = self.api.get_user_playlists()
        elif ka['name'] == 'playlist':
            response = self.api.get_playlist(ka['id'])
        elif ka['name'] == 'track':
            response = self.api.get_track(ka['id'])
        elif ka['name'] == 'stream-url':
            context_type = ''
            context_id = ''
            format_id = self.options['streamFormat']
            response = self.api.get_track_url(ka['id'], context_type, context_id, format_id)
        elif ka['name'] == 'purchases':
            response = self.api.get_purchases(100)
        elif ka['name'] == 'recommendation':
            response = self.api.get_recommandations(ka['genre_id'], ka['genre_type'], 100) 
        elif ka['name'] == 'favorites':
            response = self.api.get_favorites(100)
        else:
            QobuzXbmcError(
                        who= self,
                        what= 'qobuz_api_invalid_query',
                        additional= pprint.pformat(ka))
        if not response:
                warn(self, "Loading from Qobuz fail")
                return False
        ka['value'] = response
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

    def delete(self, **kwargs):
        key = self.make_key(**kwargs)
        self.data[key] = None
        del self.data[key]
        
class QobuzCacheDefault(QobuzLocalStorage):
    def __init__(self,*args,**kwargs):
        super(QobuzCacheDefault,self).__init__(*args, **kwargs)
        if not 'basePath' in kwargs:
            QobuzXbmcError(who=self, what='missing_parameter',additional='basePath')

    def make_key(self, *args, **kwargs):
        if not 'id' in kwargs: kwargs['id'] = 0
        return kwargs['name'] + '-' + str(kwargs['id']);

    def _load_from_disk(self, **kwargs):
        key = self.make_key(**kwargs)
        cache = os.path.join(self.options['basePath'], key+'.dat');
        data = None
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
            
    def load(self, **kwargs):
        key = self.make_key(**kwargs)
        if not self._load_from_disk(**kwargs):
            pass
        if key in self.data and self.fresh(key):
            return self.data[key]
        return super(QobuzCacheDefault, self).load(**kwargs)
        
    def save(self, key = None):
        if key == None:
            count = 0
            for key in self.data:
                if not self.saved(key):
                    count += 1
                    self.save(key)
            return count
        if not key in self.data:
            QobuzXbmcError({'Who': self,'What': 'undefined_key','With': key})
        cache = os.path.join(self.options['basePath'], key+'.dat');
        with open(cache, 'wb') as f:
            s = pickle.dump(self.data[key], f, protocol = pickle.HIGHEST_PROTOCOL)
            f.flush()
            os.fsync(f)
        return s
        sw = safe_write()
        sw.write(self.options.basePath, self.data[key])
        self.saved(key,True)
        return 1

    def delete(self, **kwargs):
        key = self.make_key(**kwargs)
        info(self, 'Deleting key: ' + key)
        cache = os.path.join(self.options['basePath'], key + '.dat')
        if not os.path.exists(cache):
            return False
        sw = safe_write();
        if sw.unlink(cache):
            super(QobuzCacheDefault, self).delete(**kwargs)

class QobuzCacheCommon(QobuzLocalStorage):
    def __init__(self,*args,**kwargs):
        print "Loading Common cache"
        import xbmcaddon
        import xbmc
        import StorageServer
        #StorageServer.dbg = True
        self.storage = StorageServer.StorageServer('plugin_audio_qobuz', 24)
        super(QobuzCacheCommon,self).__init__(*args, **kwargs)
        print "import ok"
        
    def make_key(self, *args, **kwargs):
            if not 'id' in kwargs: kwargs['id'] = 0
            return "" + kwargs['name'] + '-' + str(kwargs['id']);
    
    def load(self, **kwargs):
        key = self.make_key(**kwargs)
        data = self.storage.get(key)
        log(self, "LOADING " + key + ' / ' + pprint.pformat(data))
        if data:
            print pprint.pformat(data)
            return pickle.loads(data)
        return super(QobuzCacheCommon, self).load(**kwargs)
    
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
    
    def __init__(self,*args,**kwargs):
        if not 'cacheType' in kwargs:
            kwargs['cacheType'] = 'default'
        if kwargs['cacheType'] == 'default':
            self.cache = QobuzCacheDefault(*args,**kwargs)
        elif kwargs['cacheType'] == 'xbmc-common':
            cache = None
            try:
                cache = QobuzCacheCommon(*args, **kwargs)
            except Exception:
                cache = QobuzCacheDefault(*args, **kwargs)
            self.cache = cache
        else:
            QobuzXbmcError(who=self, what='unknown_cache_type',additionnal=kwargs['cacheType'])
        return None

    def lastError(self):
        return self.cache.lastError()
    
    def get(self,**kwargs):
        if not 'id' in kwargs:
            kwargs['id'] = 0
        return self.cache.get(**kwargs);

    def set(self,**kwargs):
        self.cache.set(**kwargs)
        
    def save(self):
        self.cache.save()
        
    def delete(self, **kwargs):
        if not 'id' in kwargs:
            kwargs['id'] = 0
        self.cache.delete(**kwargs)
    
    def make_key(self, **kwargs):
        return self.cache.make_key(**kwargs)


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
        