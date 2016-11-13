'''
    qobuz.api.easy
    ~~~~~~~~~~~~~~

    Add 'get' to qobuz.api.raw, All requests made trough this method are
    cached (see qobuz.cache.qobuz)

    :part_of: xbmc-qobuz
    :copyright: (c) 2012-2016 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
from qobuz.cache import cache
from qobuz.api.raw import RawApi
from qobuz import debug
from qobuz.gui.util import notify_error, notify_warn
from qobuz.api.user import current as current_user
from qobuz.util import common
from qobuz import config

class InvalidQuery(Exception):
    pass

class EasyApi(RawApi):

    def __init__(self):
        self.cache_base_path = None
        super(EasyApi, self).__init__()

    def get_notify(self):
        return config.app.registry.get('notify_api_error', to='bool')

    notify = property(get_notify)

    @cache.cached
    def get(self, *a, **ka):
        """Wrapper that cache query to our raw api. We are enforcing format
        because cache entry key are made based on *a and **ka parameters.
        ('artist/get' and '/artist/get' will generate different key)
        Path are mapped to raw api and raise InvalidQuery on error

        ::example
        from qobuz.api import api
        from qobuz.cache import cache
        cache.base_path = '/srv/qobuz/cache/'
        data = api.get('/artist/get')
        data = api.get('/user/login',
                        username=api.username,
                        password=api.password)

        :: note Named parameters are sorted before we generate our key

        ::return
            Pyton Dictionary on success
            None on error

        ::note api.error will contain last error message
        """
        key_to_del = []
        for key, value in ka.items():
            if value is None or value == '':
                key_to_del.append(key)
        for key in key_to_del:
            del ka[key]
        if not a[0] or not a[0].startswith('/'):
            raise InvalidQuery("Missing starting << / >>")
        path = '/'.join(a)
        path.replace('//', '/')  # Defected for n / ...
        path = path[1:]
        if path.endswith('/'):
            raise InvalidQuery('Invalid trailing << / >>')
        xpath = path.split('/')
        if len(xpath) < 1:
            raise InvalidQuery(path)
        methname = '%s_%s' % (xpath[0], xpath[1])
        if not hasattr(self, methname):
            raise InvalidQuery(path)
        """Passing user_id create different key for the cache...
        """
        for label in self.__clean_ka(xpath[0], xpath[1], **ka):
            del ka[label]
        response = getattr(self, methname)(**ka)
        if self.status_code != 200:
            debug.warn(self, 'Method: {method}/{status_code}: {error}',
                       method=methname, error=self.error,
                       status_code=self.status_code)
            if self.notify:
                notify_error('API Error/{method} {status_code}'.format(method=methname,
                                                                       status_code=self.status_code),
                             '{error}'.format(error=self.error))
        return response

    def __clean_ka(self, endpoint, method, **ka):
        """We are removing some key that are not needed by our raw api but
        generate different cache entry (Data bound to specific user...)
        """
        keys = []
        if endpoint == 'track' and method == 'getFileUrl':
            if 'user_id' in ka:
                keys.append('user_id')
        if endpoint == 'purchase' and method == 'getUserPurchases':
            if 'user_id' in ka:
                keys.append('user_id')
        return keys

    def login(self, username, password):
        """We are storing our authentication token back to our raw api on
        success.

        ::return
            True on success, else False
        """
        if common.is_empty(username) and common.is_empty(password):
            return True
        current_user.set_credentials(username, password)
        if not current_user.login(api=self):
            debug.error(self, 'Cannot login with current credentials')
            return False
        return True
