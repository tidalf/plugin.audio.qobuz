import pprint
import pickle

import qobuz
from debug import *
from utils.icacheable import ICacheable
from cache.playlist import Cache_playlist

class Cache_current_playlist(ICacheable):

    def __init__(self):
        super(Cache_current_playlist, self).__init__(qobuz.path.cache,
                                            'current-playlist')
        self.data = None
        self.set_cache_refresh(-1)
        debug(self, "Cache duration: " + str(self.cache_refresh))
        self.fetch_data()

    def _fetch_data(self):
        return self.data

    def _load_cache_data(self):
        data = super(Cache_current_playlist, self)._load_cache_data()
        self.data = data
        return data

    def set_id(self, id):
        print "Setting id for current playlist: " + str(id)
        if self.data and 'id' in self.data and self.data['id'] == id:
            print "Playlist already selected"
            return True
        playlist = Cache_playlist(id)
        playlist.fetch_data()
        if not playlist:
            print "Cannot get playlist with id: " + str(id)
            return False
        self.data = playlist.get_raw_data()
        #print repr(self.data)
        self.save()



    def get_id(self):
        if not self.data:
            return None
        if not 'id' in self.data:
            return None
        if self.data['id']:
            return int(self.data['id'])
        return None

    def save(self):
        self._save_cache_data(self.data)

