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
from mydebug import log, info, warn

class ICacheable(object):
    '''
        Interface ICacheable
    '''
    def __init__(self):
        self._raw_data = None
        self.cache_refresh = 60
        self.cache_path = None

    def _load_cache_data(self):
        info(self,"Load: " + self.cache_path)
        if not os.path.exists(self.cache_path):
            return None
        mtime = None
        try:
            mtime = os.path.getmtime(self.cache_path)
        except:
            warn(self,"Cannot stat cache file: " + self.cache_path)
        if self.cache_refresh:
            if (time.time() - mtime) > self.cache_refresh:
                info(self,"Refreshing cache")
                return None
        f = None
        try:
            f = open(self.cache_path,'rb')
        except:
            warn(self,"Cannot open cache file: " + self.cache_path)
            return None
        return pickle.load(f)

    def _save_cache_data(self,data):
        f = open(self.cache_path,'wb')
        pickle.dump(data,f,protocol=pickle.HIGHEST_PROTOCOL)
        f.close()

    def fetch_data(self):
        info(self, "Fetching data: " + self.cache_path)
        self._raw_data = self._load_cache_data()
        if not self._raw_data:
            info(self, "Fetching new data")
            data = self._fetch_data()
            self._save_cache_data(data)
            self._raw_data = data
        return self._raw_data

    def _fetch_data(self):
        assert("Need to implement fetch_data!")

    def get_data(self):
        return self._raw_data
    
    def length(self):
        return len(self._raw_data)
    
    def to_s(self):
        str = "Cache refresh: " + repr(self.cache_refresh) + "\n"
        str += "Cache path: " + self.cache_path + "\n"
        return str
