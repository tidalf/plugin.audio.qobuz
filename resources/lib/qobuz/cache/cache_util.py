'''
    qobuz.cache.cacheutil
    ~~~~~~~~~~~~~~~~~~~~~

    Little utility class for cleaning cache purpose

    :part_of: kodi-qobuz
    :copyright: (c) 2012-2018 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
import os

from qobuz.debug import getLogger
from qobuz.util.file import find, unlink

logger = getLogger(__name__)


def clean_old(cache):
    def delete_one(filename):
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
    def _delete_nocheck(filename):
        return unlink(filename)

    find(cache.base_path, r'^.*\.dat$', _delete_nocheck)
    find(cache.base_path, r'^.*\.local$', _delete_nocheck)
    return True
