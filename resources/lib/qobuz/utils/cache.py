import os
import re
import time

import qobuz
from debug import warn, info

class cache_manager():
    def __init__(self):
        pass
    
    def delete_user_data(self):
        cache = qobuz.path.cache
        if not self._cache_path_exists(cache):
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
        self._delete_files(cache, ldel)
              
    def _cache_path_exists(self, path):
        if not path:
            warn(self, "Cache directory is not set")
            return False
        if not os.path.exists(path):
            warn(self, "Cache directory doesn't seem to exist")
            return False
        return True
        
    def _delete_files(self, base_path, list):
        for f in list:
            info(self, "Deleting file: " + f)
            path = os.path.join(base_path, f)
            try:
                os.unlink(path)
            except:
                warn(self, "Something wrong happen when unlinking file: " + f)
                continue
            retry = 3
            ret = False
            while retry > 0:
                if os.path.exists(path):
                    time.sleep(0.250)
                    retry -= 1
                    continue
                else:
                    ret = True
                    break
            if not ret:
                warn(self, "Cannot remove file: " + path)
            else:
                info(self, "File deleted: " + path)
            
    def delete_all_data(self):
        cache = qobuz.path.cache
        if not self._cache_path_exists(cache):
            return False
        list = os.listdir(cache)
        ldel = []
        for f in list:
            if not f.endswith('.dat'):
                continue
            ldel.append(f)
        self._delete_files(cache, ldel)
    