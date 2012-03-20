try:
    from sqlite3 import dbapi2 as sqlite
    #logFile.info("Loading sqlite3 as DB engine")
except:
    from pysqlite2 import dbapi2 as sqlite
    #logFile.info("Loading pysqlite2 as DB engine")

import sys, os

class Itable(object):
    def __init__(self, id = None):
        self.id = id
        self.created_on = None
        self.update_on = None     
        self.auto_create = True

class Track(Itable):
    def __init__(self, id = None):
        super(Track, self).__init__(id)


class Album(Itable):
    def __init__(self, id = None):
        super(Album, self).__init__(id)


class Db():
    
    def __init__(self, path):
        self.path = path
        self.handle = None
        self.tables = {'track': Track(), 'album': Album() }
        self.auto_create = True
    
    def create_new_database(self):
        for table_name in self.tables:
            print "Create table: " + table_name
    
    def connect(self, path = None):
        if path: self.path = path
        else: path = self.path
        if not self.exists():
            if not self.auto_create:
                print "Database doesn't exist and auto create is false."
                return False
            if not self.create_new_database():
                print "Cannot create new database"
                return False
        conn = sqlite.connect(path)
        if not conn:
            print "Cannot open database: %s" % (path)
            return None
        return conn
    
    def close(self):
        pass
    
    def exists(self):
        return os.path.exists(self.path)
    