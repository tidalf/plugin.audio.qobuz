import os
import re

import qobuz
from debug import warn, info

class cache_manager():
    def __init__(self):
        pass
    
    def delete_user_data(self):
        cache = qobuz.path.cache
        if not cache:
            warn(self, "Cache directory not set")
            return False
        if not os.path.exists(cache):
            warn(self, "Cache directory doesn't seem to exist")
            return False
        list = os.listdir(cache)
        ldel = []
        
        for f in list:
            if not f.endswith('.dat'): 
                continue
            if f == 'auth.dat':
                ldel.append(f)
            elif f.startswith('userplaylists'):
                ldel.append(f)
            elif f.startswith('track-url'):
                ldel.append(f)
            elif f == 'purchases.dat':
                ldel.append(f)
        for f in ldel:
            path = os.path.join(cache, str(f))
            if os.unlink(path):
                info(self, "Cache file deleted: " + path)
            else:
                warn(self, "Cannot remove cache file: " + path)
    