'''
    qobuz.settings
    ~~~~~~~~~~~~~~

    This file is part of qobuz-xbmc

    :copyright: (c) 2012 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
from collections import defaultdict


class SettingsProxy(object):
    '''Class that act as a proxy to a underlying dictionnary

        ::parameters:
            - proxy: Our underlying dictionary (can be set after creation)

        ::methods:
            - lock/unlock: When locked, trying to assign data to new key 
            raise a KeyError (We are locking our singleton)
    '''
    def __init__(self, proxy=None):
        self._lock = False
        self.proxy = proxy

    def lock(self):
        self._lock = True

    def unlock(self):
        self._lock = False

    def get(self, key, **ka):
        return self.proxy[key]

    def set(self, key, value, **ka):
        self.proxy[key] = value

    def __getitem__(self, *a, **ka):
        return self.proxy.__getitem__(*a, **ka)

    def __setitem__(self, *a, **ka):
        if self._lock and not a[0] in self.proxy:
            raise KeyError(a[0])
        return self.proxy.__setitem__(*a, **ka)

    def __iter__(self):
        return self.proxy.__iter__()

    def __len__(self, *a, **ka):
        return self.proxy.__len__(*a, **ka)


class Settings(defaultdict):
    pass

settings = SettingsProxy(Settings())
settings['pagination_limit'] = 12
settings['auto_pagination'] = True
settings['image_size_default'] = 'large'
settings['search_enable'] = True
settings['recommendation_enable'] = True
settings['cache_duration_short'] = 5
settings['cache_duration_long'] = 60 * 24
settings['cache_duration_middle'] = 60 * 12
settings['stream_format'] = 5
settings['stream_type'] = 'flac'
settings.lock()

if __name__ == '__main__':
    print "Length %s" % (len(settings))
    for key in settings:
        print "<%s> => %s" % (key, settings[key])
