'''
    qobuz.storage
    ~~~~~~~~~~~~~~~~~~

    Package that set our default cache and cacheutil
    
    :copyright: (c) 2012 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
__all__ = ['cache', 'cacheutil']

from cache.qobuz import CacheQobuz
cache = CacheQobuz()

from cacheutil import CacheUtil
cacheutil = CacheUtil()