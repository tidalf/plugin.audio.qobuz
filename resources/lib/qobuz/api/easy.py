'''
    qobuz.api.easy
    ~~~~~~~~~~~~~~~~~~

    Add 'get' to qobuz.api.raw, All requests made trough this method are 
    cached (see qobuz.cache.qobuz)
    
    :copyright: (c) 2012 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
from qobuz.debug import warn
from qobuz.cache import cache
#from cache.sql import CacheSQL
from raw  import QobuzApiRaw
from qobuz.settings import settings

class InvalidQuery(Exception):
    pass

#sql = CacheSQL()

class QobuzApiEasy(QobuzApiRaw):

    def __init__(self):
        self.cache_base_path = None
        super(QobuzApiEasy, self).__init__()
        self.is_logged = False
        self.username = None
        self.password = None

    @property
    def pagination_limit(self):
        return settings['pagination_limit']
    @pagination_limit.setter
    def pagination_limit(self, value):
        settings['pagination_limit'] = value
    @pagination_limit.getter
    def pagination_limit(self):
        return settings['pagination_limit']

    @property
    def stream_format(self):
        return settings['stream_format']
    @stream_format.setter
    def stream_format(self, value):
        settings['stream_format'] = value
    @stream_format.getter
    def stream_format(self):
        return settings['stream_format']

    @cache.cached
#    @sql.cached
    def get(self, *a, **ka):
        '''Wrapper that cache query to our raw api. We are enforcing format
        because cache entry key are made based on *a and **ka parameters. 
        ('artist/get' and '/artist/get' will generate different key)
        Path are mapped to raw api and raise InvalidQuery on error

        ::example
        from api import api
        from cache import cache
        cace.base_path = '/srv/qobuz/cache/'
        data = api.get('/artist/get')
        data = api.get('/user/login', 
                        username=api.username, 
                        password=api.password)
                        
        :: note Named parameters are sorted before we generate our key
        
        ::return
            Pyton Dictionary on success
            None on error
            
        ::note api.error will contain last error message
        '''
        if not a[0] or not a[0].startswith('/'):
            raise InvalidQuery("Missing starting << / >>")
        path = '/'.join(a)
        path.replace('//', '/') # Defected for n / ...
        path = path[1:]
        if path.endswith('/'):
            raise InvalidQuery('Invalid trailing << / >>')
        xpath = path.split('/')
        if len(xpath) < 1:
            raise InvalidQuery(path)
        methname = '%s_%s' % (xpath[0], xpath[1])
        if not hasattr(self, methname):
            raise InvalidQuery(path)
        '''Passing user_id create different key for the cache...
        '''
        for label in self.__clean_ka(xpath[0], xpath[1], **ka):
            del ka[label]
        data = getattr(self, methname)(**ka)
        if data is None and self.error:
            warn(self, self.error)
        return data

    def __clean_ka(self, endpoint, method, **ka):
        ''' We are removing some key that are not needed by our raw api but 
        generate different cache entry (Data bound to specific user...) '''
        keys = []
        if endpoint == 'track' and method == 'getFileUrl':
            if 'user_id' in ka:
                keys.append('user_id')
        if endpoint == 'purchase' and method == 'getUserPurchases':
            if 'user_id' in ka:
                keys.append('user_id')
        return keys
        
    def login(self, username, password):
        '''We are storing our authentication token back to our raw api on 
        success.

        ::return 
            True on success, else False
        '''
        self.username = username
        self.password = password
        data = self.get('/user/login', username=username, password=password)
        if not data:
            return False
        user = data['user']
        self.set_user_data(user['id'], data['user_auth_token'])
        self.is_logged = True
        return True
    
    def logout(self):
        if self.username and cache.base_path:
            cache.delete(cache.make_key('/user/login', 
                                        username=self.username, 
                                        password=self.password))
        self.username = None
        self.password = None
        self.is_logged = False
        return super(QobuzApiEasy, self).logout()
