'''
    qobuz.cache.cacheutil
    ~~~~~~~~~~~~~~~~~~~~~

    Little utility class for cleaning cache purpose

    :part_of: xbmc-qobuz
    :copyright: (c) 2012-2016 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
import os
from qobuz.util.file import find
from qobuz import debug

def clean_old(cache):
    """Callback deleting one file
    """
    def delete_one(filename, info):
        data = cache.load_from_store(filename)
        if not cache.check_magic(data):
            raise TypeError('magic mismatch')
        ttl = cache.is_fresh(data['key'], data)
        if ttl:
            return True
        cache.delete(data['key'])
        return True
    find(cache.base_path, '^.*\.dat$', delete_one)
    return True


def clean_all(cache):
    """Clean all data from cache
    """
    def delete_one(filename, info, check_magic=True):
        '''::callback that delete one file
        '''
        data = cache.load_from_store(filename)
        if check_magic and not cache.check_magic(data):
            debug.error(__name__, "Error: bad magic, skipping file {}", filename)
            return True
        cache.delete(data['key'])
        return True
    def delete_nocheck(filename, info):
        os.unlink(filename)
        return True
    find(cache.base_path, '^.*\.dat$', delete_one)
    find(cache.base_path, '^.*\.local$', delete_nocheck)
    return True
