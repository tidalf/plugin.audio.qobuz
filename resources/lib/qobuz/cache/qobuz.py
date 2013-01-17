from file import CacheFileDecorator

class CacheQobuzDecorator(CacheFileDecorator):

    def get_ttl(self, obj, *a, **ka):
        return 30
