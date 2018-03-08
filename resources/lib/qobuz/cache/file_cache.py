'''
    qobuz.cache.file
    ~~~~~~~~~~~~~~~~

    Class that implement caching to disk

    :part_of: xbmc-qobuz
    :copyright: (c) 2012-2016 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
import json
import os
import zlib

from qobuz.cache.base_cache import BaseCache
from qobuz.debug import getLogger
from qobuz.util.common import json_dumps
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

    def sync(self, key, data, *a, **ka):
        filename = self._make_path(key)
        unlink(filename)
        try:
            with RenamedTemporaryFile(filename) as wh:
                wh.write(zlib.compress(json_dumps(data)))
                wh.flush()
                os.fsync(wh)
        except Exception as e:
            unlink(filename)
            logger.error('Error: writing failed %s\nMessage %s', filename, e)
            return False
        return True

    def load_from_store(self, path):
        item_path = os.path.join(self.base_path, path)
        if not os.path.exists(item_path):
            return None
        do_unlink = False
        with open(item_path, 'rb') as rh:
            try:
                return json.loads(zlib.decompress(rh.read()))
            except Exception as e:
                logger.error('Loading item fail %s', e)
                do_unlink = True
        if do_unlink:
            unlink(item_path)

    @classmethod
    def get_ttl(cls, *a, **ka):
        return 3600

    def delete(self, key, *a, **ka):
        filename = self._make_path(key)
        if not os.path.exists(filename):
            return False
        return unlink(filename)
