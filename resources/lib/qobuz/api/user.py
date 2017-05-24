from qobuz import debug
from qobuz import config
from qobuz.node import getNode, Flag

audio_format = {
    'mp3': (5, 'stream', 'MP3 320'),
    'flac': (6, 'stream', 'FLAC Lossless'),
    'hires': (7, 'stream', 'FLAC Hi-Res 24 bit =< 96kHz'),
    'hires_hsr': (27, 'stream', 'FLAC Hi-Res 24 bit >96 kHz & =< 192 kHz')
}


def search(src, node, kind='tracks'):
    for n in src.data[kind]['items']:
        if n['id'] == node.nid:
            return True
    return False


def is_purchased(track):
    purchases = getNode(Flag.PURCHASE, parameters={'search-type': 'all'})
    purchases.data = purchases.fetch()
    if search(purchases, track):
        return True
    album = getNode(
        Flag.ALBUM, parameters={'nid': track.get_property('album/id')})
    album.data = album.fetch()
    if album.data is None:
        return False
    if search(purchases, album, kind='albums'):
        return True
    return False


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

    def stream_format(self, track=None):
        stream_type = 'mp3'
        if not self.is_free_account() :
            stream_type = config.app.registry.get('streamtype')
            if track is not None:
                if stream_type == 'hires':
                    if self.get_property('user/credential/parameters/hires_streaming') == True or (is_purchased(track) and self.get_property('user/credential/parameters/hires_purchases_streaming') == True):
                        if track.get_maximum_sampling_rate() > 96:
                            stream_type = 'hires_hsr'
                        elif track.get_maximum_sampling_rate() > 45 or track.get_property('maximum_bit_depth') == 24:
                            stream_type = 'hires'
                        else:
                            stream_type = 'flac'
                    else: 
                        stream_tye = 'flac'
                else:
                   stream_type = 'flac'
        return audio_format[stream_type]

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
        data = self.api.get('/user/login',
                            username=self.username,
                            password=self.password)
        if data is None:
            self.code = self.api.status_code
            self.error = self.api.error
            return False
        self.data = data
        self.logged = True
        return True


current = User()
