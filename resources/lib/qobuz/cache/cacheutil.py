'''
    qobuz.storage.cacheutil
    ~~~~~~~~~~~~~~~~~~

    Little utility class for cleaning cache purpose

    :copyright: (c) 2012 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''

from util.file import FileUtil

class CacheUtil(object):

    def __init__(self):
        pass

    def clean_old(self, cache):
        """Callback deleting one file
        """
        def delete_one(filename, info):
            info['count'] += 1
            data = cache.load_from_store(filename)
            ttl = cache.is_fresh(None, None, data)
            if ttl:
                return True
            print "TTL: %s / Delete: %s" % (str(ttl), filename)
            cache.delete(None, data['key'])
            return True
        info = {'count': 0}
        fu = FileUtil()
        fu.find(cache.base_path, '^.*\.dat$', delete_one, info)
        return True

    def clean_all(self, cache):
        """Callback deleting one file
        """
        def delete_one(filename, info):
            info['count'] += 1
            data = cache.load_from_store(filename)
            cache.delete(None, data['key'])
            return True
        info = {'count': 0}
        fu = FileUtil()
        fu.find(cache.base_path, '^.*\.dat$', delete_one, info)
        return True
