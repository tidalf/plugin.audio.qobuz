from cache import cache
from api.raw  import QobuzApiRaw

class InvalidQuery(Exception):
    pass

class QobuzApiEasy(QobuzApiRaw):

    def __init__(self):
        self.cache_base_path = None
        super(QobuzApiEasy, self).__init__()
        self.is_logged = False
        self.stream_format = 5

    @cache.cached
    def get(self, *a, **ka):
        path = '/'.join(a)
        path.replace('//', '/') # Defected for n / ...
        if path.startswith('/'):
            path = path[1:]
        if path.endswith('/'):
            path = path[0:len(path) - 1]
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
        return getattr(self, methname)(**ka)

    def __clean_ka(self, endpoint, method, **ka):
        keys = []
        if endpoint == 'track' and method == 'getFileUrl':
            if 'user_id' in ka:
                keys.append('user_id')
        if endpoint == 'purchase' and method == 'getUserPurchases':
            if 'user_id' in ka:
                keys.append('user_id')
        return keys
        
    def login(self, username, password):
        self.username = username
        self.password = password
        data = self.get('user/login', username=username, password=password)
        if not data:
            return False
        user = data['user']
        self.set_user_data(user['id'], data['user_auth_token'])
        self.is_logged = True
        return True
