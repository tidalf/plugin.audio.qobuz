'''
    qobuz.storage.qobuz
    ~~~~~~~~~~~~~~~~~~

    We are setting ttl here based on key type
    
    :copyright: (c) 2012 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
from file import CacheFile
from gui.util import getSetting

class CacheQobuz(CacheFile):

    def __init__(self, *a, **ka):
        self._store = {}
        self.black_keys = ['password']
        super(CacheQobuz, self).__init__()

    def get_ttl(self, key, *a, **ka):
        if len(a) > 0:
            if a[0] == '/track/getFileUrl':
                return 60*15
        if 'user_id' in ka:
            return getSetting('cache_duration_middle', isInt=True) * 60
        return getSetting('cache_duration_long', isInt=True) * 60
    
    def sync(self, key, data):
        '''We don't want to store password in the cache'''
        import pprint    
#        if 'password' in data['ka']:
#            data['ka']['password'] = '***'
        if 'user' in data['data']:
            if 'password' in data['data']['user']:
                print 'Removing password from cached data'
                data['data']['user']['password'] = '***'
        print "SAVING: %s" % (pprint.pformat(data))
        return super(CacheQobuz, self).sync(key, data)