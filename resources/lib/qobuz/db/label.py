from itable import Itable

class Label(Itable):
    def __init__(self, id = None):
        super(Label, self).__init__(id)
        self.table_name = 'label'
        self.pk = 'id'
        self.fields_name = {
                            'id'               : {'jsonmap': 'id', 'sqltype': 'INTEGER PRIMARY KEY'},
                            'name'               : {'jsonmap': 'name', 'sqltype': 'VARCHAR'},
                            'url'               : {'jsonmap': 'url', 'sqltype': 'VARCHAR'},
                             }
