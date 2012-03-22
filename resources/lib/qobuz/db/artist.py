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
