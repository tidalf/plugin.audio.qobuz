import pprint
from itable import Itable

class Artist(Itable):
    def __init__(self, id = None):
        super(Artist, self).__init__(id)
        self.table_name = 'artist'
        self.pk = 'id'
        self.fields_name = {
                            'id'               : {'jsonmap': 'id', 'sqltype': 'INTEGER PRIMARY KEY'},
                            'name'               : {'jsonmap': 'name', 'sqltype': 'VARCHAR'},
                             }

    def insert_json(self, handle, json):
        where = {}
        for field in self.fields_name.keys():
            f = self.fields_name[field]
            if not f['jsonmap']: continue
            value = self.get_property(json, f['jsonmap'])
            if not value: continue
            where[field] = value
        return self.insert(handle, where)
