'''
    qobuz.storage
    ~~~~~~~~~~~~~

    This module contains persistent storage classes.

    :part_of: kodi-qobuz
    :copyright: (c) 2012-2018 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
from datetime import datetime
import collections
import csv
import json
import os
import shutil
import time

from qobuz.debug import getLogger
from qobuz.util.common import json_dump

logger = getLogger(__name__)


class _PersistentDictMixin(object):
    '''Persistent dictionary with an API compatible with shelve and anydbm.

    The dict is kept in memory, so the dictionary operations run as fast as
    a regular dictionary.

    Write to disk is delayed until close or sync (similar to gdbm's fast mode).

    Input file format is automatically discovered.
    Output file format is selectable between json, and csv.
    All three serialization formats are backed by fast C implementations.
    '''

    def __init__(self, filename, flag='c', mode=None, file_format='json'):
        self.flag = flag  # r=readonly, c=create, or n=new
        self.mode = mode  # None or an octal triple like 0644
        self.file_format = file_format  # 'csv', 'json'
        self.filename = filename
        if flag is not 'n' and os.access(filename, os.R_OK):
            fileobj = open(filename, 'rb')
            with fileobj:
                self.load(fileobj)

    def sync(self):
        '''Write the dict to disk
        '''
        if self.flag == 'r':
            return False
        filename = self.filename
        tempname = filename + '.tmp'
        fileobj = open(tempname, 'wb')
        try:
            self.dump(fileobj)
        except Exception as e:
            fileobj.close()
            os.remove(tempname)
            raise e
        finally:
            fileobj.close()
        if not os.path.exists(tempname):
            logger.error('Temporary file does not exists %s', tempname)
            return False
        shutil.move(tempname, self.filename)  # atomic commit
        if self.mode is not None:
            os.chmod(self.filename, self.mode)
        return True

    def close(self):
        '''Calls sync
        '''
        self.sync()

    def __enter__(self):
        return self

    def __exit__(self, *exc_info):
        self.close()

    def dump(self, fileobj):
        '''Handles the writing of the dict to the file object
        '''
        if self.file_format == 'csv':
            csv.writer(fileobj).writerows(self.raw_dict().items())
        elif self.file_format == 'json':
            json_dump(self.raw_dict(), fileobj)
        else:
            raise NotImplementedError('Unknown format: ' + repr(
                self.file_format))

    def load(self, fileobj):
        '''Load the dict from the file object
        '''
        for loader in (json.load, csv.reader):
            fileobj.seek(0)
            try:
                return self.initial_update(loader(fileobj))
            except Exception as e:
                logger.warn('StorageLoadError %s', e)
        raise ValueError('File not in a supported format, %s', e)

    def raw_dict(self):
        '''Returns the underlying dict
        '''
        raise NotImplementedError


class Storage(collections.MutableMapping, _PersistentDictMixin):
    '''Storage that acts like a dict but also can persist to disk.

    :param filename: An absolute filepath to reprsent the storage on disk. The
                     storage will loaded from this file if it already exists,
                     otherwise the file will be created.
    :param file_format: 'json' or 'csv'. json is the default. Be
                        aware that json and csv have limited support for python
                        objets.

    .. warning:: Currently there are no limitations on the size of the storage.
                 Please be sure to call :meth:`Storage.clear`
                 periodically.
    '''

    def __init__(self, filename, file_format='json'):
        '''Acceptable formats are 'csv', 'json'
        '''
        self._items = {}
        _PersistentDictMixin.__init__(self, filename, file_format=file_format)

    def __setitem__(self, key, val):
        self._items.__setitem__(key, val)

    def __getitem__(self, key):
        return self._items.__getitem__(key)

    def __delitem__(self, key):
        self._items.__delitem__(key)

    def __iter__(self):
        return iter(self._items)

    def __len__(self):
        if self._items is None:
            return -1
        return self._items.__len__

    def raw_dict(self):
        '''Returns the wrapped dict
        '''
        return self._items

    initial_update = collections.MutableMapping.update


class TimedStorage(Storage):
    '''A dict with the ability to persist to disk and TTL for items.
    '''

    def __init__(self, filename, file_format='json', TTL=None):
        '''TTL if provided should be a datetime.timedelta. Any entries
        older than the provided TTL will be removed upon load and upon item
        access.
        '''
        self.TTL = TTL
        Storage.__init__(self, filename, file_format=file_format)

    def __setitem__(self, key, val, raw=False):
        if raw:
            self._items[key] = val
        else:
            self._items[key] = (val, time.time())

    def __getitem__(self, key):
        val, timestamp = self._items[key]
        if self.TTL and (
                datetime.utcnow() - datetime.utcfromtimestamp(timestamp) >
                self.TTL):
            del self._items[key]
            return self._items[key][0]  # Will raise KeyError
        return val

    def initial_update(self, mapping):
        '''Initially fills the underlying dictionary with keys, values and
        timestamps.
        '''
        for key, val in mapping.items():
            _, timestamp = val
            if not self.TTL or (
                    datetime.utcnow() - datetime.utcfromtimestamp(timestamp) <
                    self.TTL):
                self.__setitem__(key, val, raw=True)
