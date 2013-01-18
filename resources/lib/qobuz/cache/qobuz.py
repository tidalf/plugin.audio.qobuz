from file import CacheFileDecorator
from gui.util import getSetting

class CacheQobuzDecorator(CacheFileDecorator):

    def get_ttl(self, obj, key, *a, **ka):
        return 60
        if len(a) > 0:
            if a[0] == '/track/getFileUrl':
                return 60*15
        if 'user_id' in ka:
            return getSetting('cache_duration_middle', isInt=True) * 60
        return getSetting('cache_duration_long', isInt=True) * 60
