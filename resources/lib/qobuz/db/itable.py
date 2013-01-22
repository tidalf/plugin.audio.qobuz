import sys, os
import pprint

class Itable(object):

    def __init__(self, id = None):
        self.id = id
        self.created_on = None
        self.update_on = None
        self.auto_create = True
        self.table_name = None
        self.fields_name = []
        self.pk = None
        self.auto_fetch = False

    def _create(self, handle, query):
        cursor = handle.cursor()
        if not cursor.execute(query):
            return False
        handle.commit()
        cursor.close()
        return True

    def create(self, handle):
        count = 0
        lkeys = self.fields_name.keys()
        size = len(lkeys)
        txt = ''
        fn = self.fields_name
        pprint.pprint(fn)
        for f in lkeys:
            if 'ref' in fn[f]:
                count += 1
                continue
#            print "F %s" % (f)
            txt += "%s %s" % (f, fn[f]['type'].upper())
            if count < (size - 1): 
                txt += ', '
            count += 1
        query = "CREATE TABLE IF NOT EXISTS %s (%s);" % (self.table_name, txt)
        return self._create(handle, query)

    def get(self, handle, id):
        cursor = handle.cursor()
        query = "SELECT * FROM %s WHERE %s = ?" % (self.table_name, self.pk)
        cursor.execute(query, (id,))
        row = cursor.fetchone()
        if not row:
            print self.table_name + " get: return no result"
            return None
        return row


    def get_property(self, struct, path):
        if not struct: return None
        if not path: return None
        if isinstance(path, (basestring)):
            if path in struct:
                return struct[path]
            return None
        if isinstance(path, (list, tuple)):
            if len(path) < 0: return None
            if len(path) == 1:
                if not path[0] in struct: return None
                return struct[path[0]]
            if not path[0] in struct: return None
            return self.get_property(struct[path[0]], path[1:])

    def insert_json(self, handle, json):
        where = {}
        for field in self.fields_name.keys():
            f = self.fields_name[field]
            if not f['jsonmap']: continue
            value = self.get_property(json,f['jsonmap'])
            if not value: continue
            where[field] = value
        return self.insert(handle,where)
    
    def insert(self, handle, where):
        if self.pk and not where.get(self.pk):
            print "[IGNORE] Cannot insert data without Primary Key: " + repr(self.pk)
            return False
        placeholder = '? ' + (',? ' * (len(where) - 1))
        query = "INSERT INTO %s (%s) VALUES (%s)" % (self.table_name, ','.join(where.keys()), placeholder)
        cursor = handle.cursor()
        cursor.execute(query, where.values())
        handle.commit()
        cursor.close()     
        print "Query %s \n%s" % (query, pprint.pformat(where.keys()))
        return True

    def fetch(self, handle, id):
        print "MUST BE IMPLEMENTED: Fetch data for " + self.table_name + " with id: " + str(id)
        return False



