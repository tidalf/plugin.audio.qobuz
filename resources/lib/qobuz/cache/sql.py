'''
    qobuz.storage.sql
    ~~~~~~~~~~~~~~~~~~

    Intercept our query to feed our sql database

    :copyright: (c) 2012 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
from base import CacheBase
import pprint
from db.manager import Manager


class CacheSQL(CacheBase):

    def __init__(self, *a, **ka):
        self.parseable = ['albums', 'album']
        self.black_keys = ['password']
        super(CacheSQL, self).__init__()

    def load(self, key, *a, **ka):
        print "Loading key: %s" % (key)

    def make_key(self, key, *a, **ka):
        return key

    def get_ttl(self, key, *a, **ka):
        return 0

    def parse_artist(self, manager, data, parent_id):
        print "Parsing artist"
        print pprint.pformat(data)
        manager.insert('artist', data)

    def parse_album(self, manager, data, parent_id):
        print "Parsing album"
        manager.insert('album', data)

    def parse(self, manager, data, tid=None):
        if tid is None:
            tid = data['id'] if 'id' in data else None
        fields = {}
        for label in data:
            if isinstance(label, (basestring, bool, int)):
                fields[label] = data[label]
                continue
            print "Label : %s" % (label)
            try:
                if 'items' in data[label]:
                    label = label[:-1]
                    methname = 'parse_' + label
                    for item in data[label]['items']:
                        return getattr(self, methname)(manager, data[label], tid)
                        print "Items... %s" % (repr(item))
                        self.parse(manager, item, tid)
                        continue
            except Exception as e:
                print "Exception: %s" % (str(e))
                continue
            if label in self.parseable:
                methname = 'parse_' + label
                return getattr(self, methname)(manager, data[label], tid)
            else:
                print "Null... %s" % (label)

        print pprint.pformat(fields)
#        for label in self.collection:
#            if label in data:
#                methname = 'parse_' + label
#                if hasattr(self, methname):
#                    getattr(self, methname)(data['label'])
#                else:
#                    self.parse(data[methname])

    def sync(self, key, data, *a, **ka):
        m = Manager('c:\\qobuzdb\\qobuz.sqlite3')
        m.connect('c:\\qobuzdb\\qobuz.sqlite3')
#        m.create_new_database()
        try:
            self.parse(m, data['data'])
        except Exception as e:
            print "Exception %s" % (repr(e))
            raise e
        m.close()
        return False
