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
        self.table_name = None
        self.fields_name = []

    def _create(self, handle, query):
        print "Query: " + query
        cursor = handle.cursor()
        if not cursor.execute(query):
            return False
        handle.commit()
        cursor.close()
        print "Table created: " + self.table_name
        return True

    def get(self, handle, id, fields = None):
        cursor = handle.cursor()
        if not cursor.execute("SELECT * FROM ? WHERE Z_PK = ?", (self.table_name, id)):
            return None
        return cursor

    def insert(self, handle, **kwargs):
        print "Inserting data into table: " + self.table_name
        keys = []
        values = []
        for fn in kwargs:
            if fn not in self.fields_name:
                print "Invalid field '%s' in table '%s'" % (fn, self.table_name)
                return False
        kwargs['Z_PK'] = 'NULL'
        query = "INSERT INTO %s (%s) VALUES (%s)" % (self.table_name, ','.join(kwargs.keys()), ','.join(kwargs.values()))
        print "Query: " + query
        cursor = handle.cursor()
        if not cursor.execute(query):
            print "Cannot insert data into table: " + self.table_name
            return False
        handle.commit()
        cursor.close()
        return True

class Track(Itable):

    def __init__(self, id = None):
        super(Track, self).__init__(id)
        self.table_name = 'ZTRACK'
        self.fields_name = ('Z_PK',
                            'Z_ENT',
                            'Z_OPT',
                            'ZISAVAILABLEFORSTREAMING',
                            'ZDISCNUMBER',
                            'ZTRACKID',
                            'ZDOWNLOADQUEUEINDEX',
                            'ZISSAMPLE',
                            'ZISAVAILABLEOFFLINE',
                            'ZIMPORTSTATE',
                            'ZBOUGHT',
                            'ZTRACKNUMBER',
                            'ZARTIST',
                            'ZALBUM',
                            'ZSYNCTIMESTAMP',
                            'ZSHAREURL',
                            'ZFILE_MD5',
                            'ZTRACKURL',
                            'ZTITLE',
                            'ZARTISTNAME',
                            'ZINTERPRETERS',
                            'ZALBUMID',
                            'ZWORK',
                            'ZSAMPLEURL',
                            'ZCOPYRIGHT')

    def create(self, handle):
        query = 'CREATE TABLE ZTRACK ( Z_PK INTEGER PRIMARY KEY, Z_ENT INTEGER, Z_OPT INTEGER, ZISAVAILABLEFORSTREAMING INTEGER, ZDISCNUMBER INTEGER, ZTRACKID INTEGER, ZDOWNLOADQUEUEINDEX INTEGER, ZISSAMPLE INTEGER, ZISAVAILABLEOFFLINE INTEGER, ZIMPORTSTATE INTEGER, ZBOUGHT INTEGER, ZTRACKNUMBER INTEGER, ZARTIST INTEGER, ZALBUM INTEGER, ZSYNCTIMESTAMP VARCHAR, ZSHAREURL VARCHAR, ZFILE_MD5 VARCHAR, ZTRACKURL VARCHAR, ZTITLE VARCHAR, ZARTISTNAME VARCHAR, ZINTERPRETERS VARCHAR, ZALBUMID VARCHAR, ZWORK VARCHAR, ZSAMPLEURL VARCHAR, ZCOPYRIGHT VARCHAR );'
        return self._create(handle, query)

class Album(Itable):

    def __init__(self, id = None):
        super(Album, self).__init__(id)
        self.table_name = 'ZALBUM'

    def create(self, handle):
        query = 'CREATE TABLE ZALBUM ( Z_PK INTEGER PRIMARY KEY, Z_ENT INTEGER, Z_OPT INTEGER, ZIMPORTSTATE INTEGER, ZAVGUSERSNOTE FLOAT, ZLASTMETAREQUEST FLOAT, ZSYNCREVIEWSTIMESTAMP FLOAT, ZMETADESCRIPTION VARCHAR, ZLABEL VARCHAR, ZCOLLECTION VARCHAR, ZSYNCTIMESTAMP VARCHAR, ZPICTUREURLSMALL VARCHAR, ZSHAREURL VARCHAR, ZURL VARCHAR, ZPRESSAWARDS VARCHAR, ZDISPLAYSUBGENRE VARCHAR, ZBOOKLET VARCHAR, ZPICTUREURLBIG VARCHAR, ZPROGRAM VARCHAR, ZRELEASEDATE VARCHAR, ZARTISTNAME VARCHAR, ZSUMMARY VARCHAR, ZTITLE VARCHAR, ZALBUMID VARCHAR, ZGENRE VARCHAR );'
        return self._create(handle, query)

class Artist(Itable):
    def __init__(self, id = None):
        super(Artist, self).__init__(id)
        self.table_name = 'ZARTIST'

    def create(self, handle):
        query = 'CREATE TABLE ZARTIST ( Z_PK INTEGER PRIMARY KEY, Z_ENT INTEGER, Z_OPT INTEGER, ZIMPORTSTATE INTEGER, ZTITLE VARCHAR, ZSYNCTIMESTAMP VARCHAR );'
        return self._create(handle, query)

class Db():

    def __init__(self, path):
        self.path = path
        self.handle = None
        self.tables = {
                       'track':  Track(),
                       'album':  Album(),
                       'artist': Artist()
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
        conn = sqlite.connect(path)
        if not conn:
            print "Cannot open database: %s" % (path)
            return None
        self.handle = conn
        return conn

    def get(self, table, id, fields = None):
        if not table in self.tables:
            print "Invalid table: " + table
            return False
        return self.tables[table].get(id, fields)

    def insert(self, table, **kwargs):
        if not table in self.tables:
            print "Invalid table" + table
            return False
        return self.tables[table].insert(self.handle, **kwargs)

    def exists(self):
        return os.path.exists(self.path)

