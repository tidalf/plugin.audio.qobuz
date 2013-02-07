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
from qobuz.settings import settings

class CacheFileTTL(CacheFile):

    def __init__(self, *a, **ka):
        super(CacheFileTTL, self).__init__()
        self.store = {}
        self.black_keys = ['password']


    def load(self, key, *a, **ka):
        if key in self.store:
            return self.store[key]
        data = super(CacheFileTTL, self).load(key, *a, **ka)
        if not data:
            return None
        self.store[key] = data
        return data

    def get_ttl(self, key, *a, **ka):
        if len(a) > 0:
            if a[0] == '/track/getFileUrl':
                return settings['cache_duration_short'] * 60
        if 'user_id' in ka:
            return settings['cache_duration_middle'] * 60
        return settings['cache_duration_long'] * 60
