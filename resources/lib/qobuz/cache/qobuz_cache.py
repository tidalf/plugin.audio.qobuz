'''
    qobuz.cache.qobuz
    ~~~~~~~~~~~~~~~~~

    We are setting ttl here based on key type
    We are caching key who return data in dictionary so further request of
    the same key return data from memory.

    :part_of: xbmc-qobuz
    :copyright: (c) 2012-2016 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
from qobuz.cache.file_cache import FileCache
from qobuz import config


class QobuzCache(FileCache):
    def __init__(self, *a, **ka):
        self.store = {}
        self.black_keys = ['password']
        super(QobuzCache, self).__init__()

    def load(self, key, *a, **ka):
        if key in self.store:
            return self.store[key]
        data = super(QobuzCache, self).load(key, *a, **ka)
        if not data:
            return None
        self.store[key] = data
        return data

    def get_ttl(self, key, *a, **ka):
        if len(a) > 0:
            if a[0] == '/track/getFileUrl':
                return 60 * 15
        if 'user_id' in ka:
            return config.app.registry.get('cache_duration_middle',
                                           to='int') * 60
        return config.app.registry.get('cache_duration_long', to='int') * 60
