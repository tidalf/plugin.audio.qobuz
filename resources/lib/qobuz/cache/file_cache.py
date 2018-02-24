'''
    qobuz.cache.file
    ~~~~~~~~~~~~~~~~

    Class that implement caching to disk

    :part_of: xbmc-qobuz
    :copyright: (c) 2012-2016 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
try:
    '''cPickle is a faster implementation of pickle, we are using it if
    present
    '''
    import cPickle as pickle
except ImportError:
    import pickle
import os

from qobuz.cache.base_cache import BaseCache
from qobuz.debug import getLogger
from qobuz.util.file import RenamedTemporaryFile, unlink
from qobuz.util.hash import hashit

logger = getLogger(__name__)


class FileCache(BaseCache):
    def __init__(self):
        self.base_path = None
        self.ventile = False
        super(FileCache, self).__init__()

    def load(self, key, *a, **ka):
        filename = self._make_path(key)
        return self.load_from_store(filename)

    def make_key(self, *a, **ka):
        argstr = '/'.join(a[:])
        argstr += '/'.join(['%s=%s' % (key, ka[key]) for key in sorted(ka)])
        return hashit(argstr)

    def _make_path(self, key):
        return os.path.join(self.base_path, '%s.dat' % key)

    def sync(self, key, data):
        filename = self._make_path(key)
        unlink(filename)
        try:
            with RenamedTemporaryFile(filename) as fo:
                pickle.dump(data, fo, protocol=pickle.HIGHEST_PROTOCOL)
                fo.flush()
                os.fsync(fo)
        except Exception as e:
            unlink(filename)
            logger.error('Error: writing failed %s\nMessage %s', filename, e)
            return False
        return True

    def load_from_store(self, filename):
        path = os.path.join(self.base_path, filename)
        if not os.path.exists(path):
            return None
        with open(path, 'rb') as f:
            return pickle.load(f)
        return None

    @classmethod
    def get_ttl(cls, *a, **ka):
        return 3600

    def delete(self, key, *a, **ka):
        filename = self._make_path(key)
        if not os.path.exists(filename):
            return False
        return unlink(filename)
