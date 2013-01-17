import pprint
import hashlib
from time import time
import pickle
import os

from base import CacheBaseDecorator
from util.file import FileUtil

class MissingClassProperty(Exception):
    pass

class CacheFileDecorator(CacheBaseDecorator):

    def retrieve(self, obj, key, *a, **ka):
        cache = self._make_path(obj, key)
        if not os.path.exists(cache):
            return None
        with open(cache, 'rb') as f:
            return pickle.load(f)
        return None

    def make_key(self, obj, *a, **ka):
        argstr = '/'.join(a[:])
        argstr += '/'.join([ '%s=%s' % (key, ka[key]) for key in sorted(ka)])
        m = hashlib.md5()
        m.update(argstr)
        return m.hexdigest()

    def _make_path(self, obj, key):
        if not hasattr(obj, 'cache_base_path'):
            raise MissingClassProperty('cache_base_path')
        xpath = []
        xpath.append(obj.cache_base_path)
        fileName = key + '.dat'
        return os.path.join(os.path.join(*xpath), fileName)

    def store(self, obj, key, data):
        cache = self._make_path(obj, key)
        print 'Cache: %s' % (cache)
        #@todo: We are living file on error ...
        with open(cache, 'wb') as f:
            try:
                pickle.dump(
                            data, f, protocol=pickle.HIGHEST_PROTOCOL)
            except:
                return False
            finally:
                f.flush()
                os.fsync(f)
        return True

    def get_ttl(self, obj, *a, **ka):
        return 3600

    def delete(self, obj, key, *a, **ka):
        cache = self._make_path(obj, key)
        fu = FileUtil()
        return fu.unlink(cache)
