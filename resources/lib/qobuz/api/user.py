from qobuz import debug
from qobuz import config

class User(object):

    def __init__(self, username=None, password=None):
        self.logged = False
        self.error = None
        self.code = 0
        self.username = username
        self.password = password
        self.data = {}
        self.api = None

    def init_states(self):
        self.logged = False
        self.error = None
        self.code = 0
        self.data = {}

    def is_free_account(self):
        if self.logged:
             if self.get_token() is not None:
                 return False
        return True

    def stream_format(self):
        return 6 if config.app.registry.get('streamtype') == 'flac' else 5

    def hires(self):
        return config.app.registry.get('hires_enabled', to='bool')

    def set_credentials(self, username, password):
        self.username = username
        self.password = password

    def get_property(self, key, default=None):
        root = self.data
        for part in key.split('/'):
            if part not in root:
                return default
            root = root[part]
        if root is None:
            return default
        return root

    def get_id(self, default=None):
        return self.get_property('user/id', default=default)

    def get_token(self, default=None):
        return self.get_property('user_auth_token', default=default)

    def login(self, api=None):
        if api is not None:
            self.api = api
        self.init_states()
        if self.api is None:
            raise RuntimeError('Api is not set')
        data = self.api.get('/user/login', username=self.username,
                       password=self.password)
        if data is None:
            self.code = self.api.status_code
            self.error = self.api.error
            return False
        self.data = data
        self.logged = True
        return True

current = User()
