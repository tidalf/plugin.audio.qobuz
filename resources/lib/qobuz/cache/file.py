'''
    qobuz.storage.file
    ~~~~~~~~~~~~~~~~~~

    Class that implement caching to disk

    :copyright: (c) 2012 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
import hashlib
import pickle
import os

from base import CacheBase
from fileutil import RenamedTemporaryFile, unlink, find
class CacheFile(CacheBase):
    '''Caching to files (base_path/<md5.dat>)
        
        ::Properties:
            base_path: string, location of our cache,
        
        ::Note: 
            if base_path is not set caching is disable
    '''
    def __init__(self, base_path=None):
        self.base_path = base_path        
        self.ventile = False
        super(CacheFile, self).__init__()

    @property
    def base_path(self):
        return self._base_path
    @base_path.setter
    def base_path(self, path):
        '''This setter enable cache when feed with valid path
        '''
        if path is None:
            return
        print "Cache path: %s" % (path)
        if not os.path.exists(path):
            raise Exception('Bad file path: %s' % (path))
        self._base_path = path
        self.enable = True
    @base_path.getter
    def base_path(self):
            return self._base_path

    def load(self, key, *a, **ka):
        filename = self._make_path(key)
        return self.load_from_store(filename)

    def make_key(self, *a, **ka):
        argstr = '/'.join(a[:])
        argstr += '/'.join([ '%s=%s' % (key, ka[key]) for key in sorted(ka)])
        m = hashlib.md5()
        m.update(argstr)
        return m.hexdigest()

    def _make_path(self, key):
        xpath = []
        xpath.append(self.base_path)
        fileName = key + '.dat'
        return os.path.join(os.path.join(*xpath), fileName)

    def sync(self, key, data):
        filename = self._make_path(key)
        unlink(filename)
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

    def get_ttl(self, *a, **ka):
        return 3600

    def delete(self, key, *a, **ka):
        filename = self._make_path(key)
        if not os.path.exists(filename):
            print "Cache file doesn't exist %s" % (filename)
            return False
        #@bug: We are not checking that filename is really unlinked
        unlink(filename)
        return True

    def delete_old(self):
        """Callback deleting one file
        """
        def delete_one(filename, info):
            data = self.load_from_store(filename)
            if not self.check_magic(data):
                raise TypeError('magic mismatch')
            ttl = self.is_fresh( data['key'], data)
            if ttl:
                return True
            if self.delete(data['key']):
                info['count'] += 1
            return True
        info = { 'count': 0 }
        find(self.base_path, '^.*\.dat$', delete_one, info)
        return info['count']

    def delete_all(self):
        '''Clean all data from cache
        '''
        def delete_one(filename, info):
            '''::callback that delete one file
            '''
            data = self.load_from_store(filename)
            if not self.check_magic(data):
                print "Error: bad magic, skipping file %s" % (filename)
                return True
            if self.delete(data['key']):
                info['count'] += 1
            return True
        info = { 'count': 0 }
        find(self.base_path, '^.*\.dat$', delete_one, info)
        return info['count']

