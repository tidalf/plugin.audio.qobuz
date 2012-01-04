###############################################################################
# Interface ICacheable
###############################################################################
import os
import time
import pickle
from mydebug import log, info, warn

class ICacheable(object):

    def __init__(self):
        self._raw_data = None
        self.cache_refresh = 60
        self.cache_path = None

    def _load_cache_data(self):
        log(self,"Load: " + self.cache_path)
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
        self._raw_data = self._load_cache_data()
        if not self._raw_data:
            data = self._fetch_data()
            self._save_cache_data(data)
            self._raw_data = data
        return self._raw_data

    def _fetch_data(self):
        assert("Need to implement fetch_data!")

    def to_s(self):
        str = "Cache refresh: " + repr(self.cache_refresh) + "\n"
        str += "Cache path: " + self.cache_path + "\n"
        return str
