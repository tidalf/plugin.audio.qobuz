import hashlib
import pickle
import os

from base import CacheBaseDecorator
from util.file import FileUtil, RenamedTemporaryFile

class CacheFileDecorator(CacheBaseDecorator):
    
    def __init__(self):
        self.base_path = None

    def retrieve(self, obj, key, *a, **ka):
        filename = self._make_path(obj, key)
        return self.load_from_store(filename)

    def make_key(self, obj, *a, **ka):
        argstr = '/'.join(a[:])
        argstr += '/'.join([ '%s=%s' % (key, ka[key]) for key in sorted(ka)])
        m = hashlib.md5()
        m.update(argstr)
        return m.hexdigest()

    def _make_path(self, obj, key):
        xpath = []
        xpath.append(self.base_path)
        fileName = key + '.dat'
        return os.path.join(os.path.join(*xpath), fileName)

    def store(self, obj, key, data):
        filename = self._make_path(obj, key)
        try:
            with RenamedTemporaryFile(filename) as fo:
                pickle.dump(data, fo, protocol=pickle.HIGHEST_PROTOCOL)
                fo.flush()
                os.fsync(fo)
        except Exception as e:
            print "Error: writing failed %s\nMessage %s" % (filename, e)
            return False
        return True
    
    def load_from_store(self, filename):
        path = os.path.join(self.base_path, filename)
        if not os.path.exists(path):
            return None
        with open(filename, 'rb') as f:
            return pickle.load(f)
        return None
    
    def get_ttl(self, obj, *a, **ka):
        return 3600

    def delete(self, obj, key, *a, **ka):
        cache = self._make_path(obj, key)
        fu = FileUtil()
        return fu.unlink(cache)
