from itable import Itable

class Genre(Itable):
    def __init__(self, id = None):
        super(Genre, self).__init__(id)
        self.table_name = 'genre'
        self.pk = 'id'
        self.fields_name = {
                            'id'               : {'jsonmap': 'id', 'sqltype': 'INTEGER PRIMARY KEY'},
                            'name'               : {'jsonmap': 'name', 'sqltype': 'VARCHAR'},
                             'url'               : {'jsonmap': 'url', 'sqltype': 'VARCHAR'},
                             }
