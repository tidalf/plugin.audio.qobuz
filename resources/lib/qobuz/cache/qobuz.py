'''
    qobuz.cache.qobuz
    ~~~~~~~~~~~~~~~~~~

    We are setting ttl here based on key type
    We are caching key who return data in dictionary so further request of
    the same key return data from memory.

    :copyright: (c) 2012 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
from file import CacheFile

class CacheQobuz(CacheFile):

    def __init__(self, *a, **ka):
        self.store = {}
        self.black_keys = ['password']
        self.duration_middle = 0.5
        self.duration_long = 1
        super(CacheQobuz, self).__init__()

    def load(self, key, *a, **ka):
        if key in self.store:
            return self.store[key]
        data = super(CacheQobuz, self).load(key, *a, **ka)
        if not data:
            return None
        self.store[key] = data
        return data

    def get_ttl(self, key, *a, **ka):
        if len(a) > 0:
            if a[0] == '/track/getFileUrl':
                return 60*15
        if 'user_id' in ka:
            return self.duration_middle * 60
        return self.duration_long * 60
