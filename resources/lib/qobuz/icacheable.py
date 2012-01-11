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
import time
import pickle
from mydebug import log,info,warn

class ICacheable2(object):
    def __init(self):
        self._raw_data = None
        self.cache_refresh = None
        self.cache_path = None
        self.object_id = None
        self.object_name = None

    def set_cache_path(self,name,id):
        assert("Need to be overloaded")

    def get_cache_path(self):
        assert("Need to be overloaded")

    def _load_cache_data(self):
        assert("Need to be overloaded")

    def _save_cache_data(self,data):
        assert("Need to be overloaded")

    def fetch_data(self):
        assert("Need to be overloaded")

    def _fetch_data(self):
        assert("Subclass need to implement this")

    def get_data(self):
        assert("Need to be overloaded")

    def length(self):
        assert("Need to be overloaded")

class ICacheable(object):
    '''
        Interface ICacheable
    '''
    def __init__(self, path, name, id = None):
        self._raw_data = None
        self.cache_refresh = 0
        self.cache_path = None
        self.cache_object_id = None
        self.cache_object_path = None
        self.cache_object_name = None
        self.set_cache_path(path, name, id)
        
    def set_cache_path(self, path, name, id):
        if not name:
            warn(self, "Cannot set path without name or id")
            return False
        self.cache_object_name = name
        self.cache_path = path
        self.cache_object_path = self.cache_object_name
        if id != None:
            id = str(id)
            self.cache_object_id = id
            self.cache_object_path += '-' + self.cache_object_id 
        self.cache_object_path += '.dat'
        info(self, "Cache for " + name + " set to: " + self.cache_object_path)
    
    def get_cache_refresh(self):
        return self.cache_refresh
    
    def get_cache_path(self):
        if not self.cache_path or not self.cache_object_path:
            warn(self, "Needd cache_path and cache_object_path")
            return None
        return os.path.join(self.cache_path, self.cache_object_path)
    
    def set_cache_refresh(self, refresh):
        self.cache_refresh = refresh
        
    def _load_cache_data(self):
        cache = self.get_cache_path()
        info(self,"Load: " + cache)
        if not os.path.exists(cache):
            return None
        mtime = None
        try:
            mtime = os.path.getmtime(cache)
        except:
            warn(self,"Cannot stat cache file: " + cache)
        refresh = self.get_cache_refresh()
        if refresh:
            if (time.time() - mtime) > refresh:
                info(self,"Refreshing cache")
                return None
        f = None
        try:
            f = open(cache,'rb')
        except:
            warn(self,"Cannot open cache file: " + cache)
            return None
        return pickle.load(f)

    def _save_cache_data(self, data):
        cache = self.get_cache_path()
        f = open(cache,'wb')
        pickle.dump(data,f,protocol=pickle.HIGHEST_PROTOCOL)
        f.close()

    def set_raw_data(self, raw):
        self._raw_data = raw
        
    def get_raw_data(self):
        return self._raw_data
    
    def fetch_data(self):
        cache = self.get_cache_path()
        if not cache:
            warn(self, "No cache path, cannot fetch data")
            return None
        info(self,"Fetching data: " + cache)
        data = self._load_cache_data()
        if not data:
            info(self,"Fetching new data")
            data = self._fetch_data()
            if not data:
                warn(self, "Cache empty and cannot fetch new data ...")
                return None
            self._save_cache_data(data)
        self.set_raw_data(data)
        return self.get_raw_data()

    def _fetch_data(self):
        assert("Need to implement fetch_data!")

    def get_data(self):
        return self.get_raw_data()

    def length(self):
        assert("Must be overloaded")
        exit(0)

#    def to_s(self):
#        str = "Cache refresh: " + repr(self.cache_refresh) + "\n"
#        str += "Cache path: " + self.cache_path + "\n"
#        return str
