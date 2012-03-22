import pprint
from itable import Itable

class Product(Itable):

    def __init__(self, id = None):
        super(Product, self).__init__(id)
        self.table_name = 'product'
        self.pk = 'id'
        self.fields_name = {
                            'id'               : {'jsonmap': 'id', 'sqltype': 'INTEGER PRIMARY KEY'},
                            'artist_id': {'jsonmap': ('artist', 'id'), 'sqltype': 'INTEGER'},
                            'description': {'jsonmap': 'descrption', 'sqltype': 'VARCHAR'},
                            'genre_id' : {'jsonmap': ('genre', 'id'), 'sqltype': 'INTEGER'},
                            'image'               : {'jsonmap': ('image', 'large'), 'sqltype': 'VARCHAR'},
                            'label_id'               : {'jsonmap': ('label', 'id'), 'sqltype': 'INTEGER'},
                            'price'               : {'jsonmap': 'price', 'sqltype': 'INTEGER'},
                            'release_date'               : {'jsonmap': 'release_date', 'sqltype': 'VARCHAR'},
                             'subtitle'               : {'jsonmap': 'subtitle', 'sqltype': 'VARCHAR'},
                             'title'               : {'jsonmap': 'title', 'sqltype': 'VARCHAR'},
                             'url'               : {'jsonmap': 'url', 'sqltype': 'VARCHAR'},
                             }

    def insert_json(self, handle, json):
        print "Insert json"
        where = {}
        for field in self.fields_name.keys():
            print "Looking field: " + field
            f = self.fields_name[field]
            if not f['jsonmap']: continue
            value = self.get_property(json, f['jsonmap'])
            print "JKEY: " + repr(value)
            if not value: continue
            where[field] = value
        print pprint.pformat(where)
        self.insert(handle, where)
        return False
