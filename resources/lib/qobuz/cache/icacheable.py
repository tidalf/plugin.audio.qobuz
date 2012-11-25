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
import cPickle as pickle
import hashlib
import weakref

from debug import log, info, error, warn, debug
from  utils.file.write import safe_write

class ICacheable(object):
    '''
        Interface ICacheable
    '''
    def __init__(self, path, name, id = None, hash_path = True):
        self._raw_data = None
        self.cache_refresh = 0
        self.cache_path = None
        self.cache_object_id = None
        self.cache_object_path = None
        self.cache_object_name = None
        self.set_hashing_path(hash_path)
        self.set_cache_path(path, name, id)
        self.no_network = False
        
    def set_hashing_path(self, b):
        if b: self.hashing_path = True
        else: self.hashing_path = False
        
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
        if self.hashing_path:
            hash = hashlib.new('SHA1')
            hash.update(self.cache_object_path)
            digest = hash.hexdigest()
            newdir = digest[0:2]
            self.cache_path = os.path.join(path, newdir)
            self.cache_object_path = digest
            if not os.path.exists(self.cache_path):
                try: os.mkdir(self.cache_path)
                except: warn(self, "Cannot make directory: " + self.cache_path)
        self.cache_object_path += '.dat'
        debug(self, "Cache for " + name + " set to: " + self.cache_object_path)

    def get_cache_refresh(self):
        return self.cache_refresh

    def get_cache_path(self):
        if not self.cache_path or not self.cache_object_path:
            warn(self, "Needd cache_path and cache_object_path")
            return None
        return os.path.join(self.cache_path, self.cache_object_path)

    def set_cache_refresh(self, refresh):
        r = int(refresh)
        if r > 0:
            r = r * 60
        else:
            r = -1
        self.cache_refresh = r

    def hook_pre_refresh(self):
        pass

    def _load_cache_data(self):
        cache = self.get_cache_path()
        debug(self, "Load: " + cache)
        if not os.path.exists(cache):
            return None
        mtime = None
        try:
            mtime = os.path.getmtime(cache)
        except:
            warn(self, "Cannot stat cache file: " + cache)
        refresh = self.get_cache_refresh()
        if refresh and refresh != -1:
            diff = time.time() - mtime
            if diff > refresh:
                debug(self, "Refreshing cache")
                self.hook_pre_refresh()
                return None
        data = None
        with open(cache, 'rb') as f:
            f = open(cache, 'rb')
            try:
                data = pickle.load(f)
            except: 
                warn(self, "Picke can't load data from file")
                return None 
        return data

    def delete_cache(self):
        cache = self.get_cache_path()
        sf = safe_write()
        return sf.unlink(cache)

    def _save_cache_data(self, data):
        cache = self.get_cache_path()
        if not cache:
            error(self, "Cache is not set")
        s = None
        with open(cache, 'wb') as f:
            s = pickle.dump(data, f, protocol = pickle.HIGHEST_PROTOCOL)
            f.flush()
            os.fsync(f)
        return s

    def set_raw_data(self, raw):
        self._raw_data = raw

    def get_raw_data(self):
        return self._raw_data

    def fetch_data(self, progress = None):
        cache = self.get_cache_path()
        if not cache:
            warn(self, "No cache path, cannot fetch data")
            return None
        debug(self, "Fetching data: " + cache)
        if progress: progress.update_line1("Fetching data ...")
        data = self._load_cache_data()
        if not data:
            if self.no_network: 
                info(self, "No network flag set (don't)")
                return None
            if progress: progress.update_line1("Fetching data from Internet")
            debug(self, "No data cached, fetching new one")
            data = self._fetch_data()
            if data == None:
                warn(self, "Cache empty and fetching new data fail")
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

