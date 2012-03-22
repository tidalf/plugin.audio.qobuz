import os, sys
try:
    from sqlite3 import dbapi2 as sqlite
    #logFile.info("Loading sqlite3 as DB engine")
except:
    from pysqlite2 import dbapi2 as sqlite
    #logFile.info("Loading pysqlite2 as DB engine")
from track import Track
from product import Product
from artist import Artist
from genre import Genre

class Manager():

    def __init__(self, path):
        self.path = path
        self.handle = None
        self.tables = {
                       'track':  Track(),
                       'product':  Product(),
                       'artist': Artist(),
                       'genre': Genre(),
                       }
        self.auto_create = True

    def create_new_database(self):
        #os.unlink(self.path)
        handle = sqlite.connect(self.path)
        handle.row_factory = sqlite.Row
        if not handle:
            print "Error: Cannot create database, " + self.path
            return False
        for table_name in self.tables:
            self.tables[table_name].create(handle)
        handle.close()
        return True

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
        #os.unlink(path)
        conn = sqlite.connect(path)
        if not conn:
            print "Cannot open database: %s" % (path)
            return None
        self.handle = conn
        self.handle.row_factory = sqlite.Row
        return conn

    def get(self, table, where = {}, auto_fetch = True):
        if not table in self.tables:
            print "Invalid table: " + table
            return False
        T = self.tables[table]
        row = T.get(self.handle, where[T.pk])
        if not row:
            print "No data in database"
            if T.auto_fetch and auto_fetch:
                print "AutoFethc ENABLE"
                row = T.fetch(self.handle, where[T.pk])
            if not row:
                print "We definitly don't have this data"
                return None
        return row

    def insert(self, table, where):
        if not table in self.tables:
            print "Invalid table" + table
            return False
        T = self.tables[table]
        if not T.pk in where.keys():
            print "Cannot insert data without primary key"
            return False
        if T.get(self.handle, where[T.pk]):
            print "Cannot insert data, primary key already present"
            return False
        return T.insert(self.handle, where)

    def exists(self):
        return os.path.exists(self.path)
