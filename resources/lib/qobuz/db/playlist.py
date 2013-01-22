import pprint
from itable import Itable

class Playlist(Itable):
    def __init__(self, id = None):
        super(Artist, self).__init__(id)
        self.table_name = 'artist'
        self.pk = 'id'
        self.fields_name = {
                            'id'               : {'jsonmap': 'id', 'sqltype': 'INTEGER PRIMARY KEY'},
                            'name'               : {'jsonmap': 'name', 'sqltype': 'VARCHAR'},
                            'owner_id'               : {'jsonmap': ('owner', 'id'), 'sqltype': 'INTEGER'},
                            'created_at'               : {'jsonmap': ('created_at', 'id'), 'sqltype': 'INTEGER'},
                            'description'               : {'jsonmap': 'description', 'sqltype': 'VARCHAR'},
                            'is_collaborative'               : {'jsonmap': 'is_collaborative', 'sqltype': 'INTEGER'},
                            'is_public'               : {'jsonmap': 'is_public', 'sqltype': 'INTEGER'},
                            'position'               : {'jsonmap': 'position', 'sqltype': 'INTEGER'},
                            'updatede_at'               : {'jsonmap': 'updated_at', 'sqltype': 'INTEGER'},
                             }

    def insert_json(self, handle, json):
        print "INSERT PLAYLIST"
#        where = {}
#        for field in self.fields_name.keys():
#            f = self.fields_name[field]
#            if not f['jsonmap']: continue
#            value = self.get_property(json, f['jsonmap'])
#            if not value: continue
#            where[field] = value
#        print pprint.pformat(where)
#        return self.insert(handle, where)
