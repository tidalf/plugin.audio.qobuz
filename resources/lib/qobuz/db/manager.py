import os, sys
try:
    from sqlite3 import dbapi2 as sqlite
    #logFile.info("Loading sqlite3 as DB engine")
except:
    from pysqlite2 import dbapi2 as sqlite
    #logFile.info("Loading pysqlite2 as DB engine")
from track import Track
from album import Album
from artist import Artist
from genre import Genre
from label import Label

class DbmErrors(Exception):
    def __init__(self, *a, **ka):
        self.code = 500
        self.message = a[0] if len(a) > 0 else None
        super(DbmErrors, self).__init__(*a, **ka)

class ErrorDatabaseCreate(DbmErrors):
    pass
class ErrorDatabaseConnect(DbmErrors):
    pass
class ErrorInvalidTableName(DbmErrors):
    pass

class DbmHandle():
    def __init__(self, path):
        if path is None:
            raise DbmErrors()
        self.path = path
        
    def __enter__(self):
        print "Path: %s" % (self.path)
        handle = sqlite.connect(self.path)
        if handle is None:
            raise DbmErrors()
        self.handle = handle
        return self.handle
    
    def __exit__(self, type, value, traceback):
        if self.handle:
            print "Closing handle"
            self.handle.close()
            self.handle = None
            
class Manager():

    def __init__(self, path):
        self.path = path
        self.handle = None
        self.tables = {
                       'track':  Track(),
                       'album':  Album(),
                       'artist': Artist(),
                       'genre': Genre(),
                       'label': Label()
                       }
        self.auto_create = True
        self.error = None
    
    def create_new_database(self):
        with DbmHandle(self.path) as handle:
            handle.row_factory = sqlite.Row
            if not handle:
                raise ErrorDatabaseCreate(self.path)
            for table_name in self.tables:
                self.tables[table_name].create(handle)
        return True

    def connect(self, path = None):
        if path: self.path = path
        else: path = self.path
#        if self.exists():
#            os.unlink(self.path)
        if not self.exists():
            if not self.auto_create:
                self.error = "Database doesn't exist and auto create is false."
                raise ErrorDatabaseConnect(self.error)
            self.create_new_database()
        conn = sqlite.connect(path)
        if not conn:
            self.error = "Cannot open database: %s" % (path)
            raise ErrorDatabaseConnect(self.error)
        self.handle = conn
        self.handle.row_factory = sqlite.Row
        return conn

    def get(self, table, where = {}, auto_fetch = True):
        if not table in self.tables:
            raise ErrorInvalidTableName(table)
        T = self.tables[table]
        print "T %s" % (repr(T))
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

    def get_track(self, id):
        cursor = self.handle.cursor()
        query = "SELECT t.id as id, t.copyright AS copyright, " \
        "t.duration AS duration, t.media_number AS media_number," \
        "t.streaming_type AS streaming_type, t.title as title, " \
        "t.track_number AS track_number, t.version AS version, " \
        "t.work AS work, " \
        "p.image AS image, " \
        "ai.name AS interpreter_name " \
        "FROM track AS t, " \
        "product AS p, " \
        "artist AS ai, artist AS ac " \
        "WHERE t.product_id = p.id AND (t.interpreter_id IS NULL OR t.interpreter_id = ai.id) AND (t.composer_id IS NULL OR t.composer_id = ac.id) " \
        "AND t.id = ? "
        print "Query: " + query
        cursor.execute(query, (id,))
        row = cursor.fetchone()
        if not row:
            print "No result"
            return None
        return row

    def insert(self, table, where):
        if not table in self.tables:
            print "Invalid table " + table
            return False
        T = self.tables[table]
        if not T.pk in where.keys():
            print "Cannot insert data without primary key"
            return False
        if T.get(self.handle, where[T.pk]):
            print "Cannot insert data, primary key already present"
            return False
        return T.insert(self.handle, where)

    def insert_json(self, table, json):
        if not table in self.tables:
            print "Invalid table " + table
            return False
        T = self.tables[table]
        if not T.pk in json:
            print "JSON Data doesn't contain 'id'"
            return False
        row = T.get(self.handle, json['id'])
        if row:
            print "Cannot insert data, primary key already present"
            return row
        if not T.insert_json(self.handle, json):
            return None
        return T.get(self.handle, json['id'])

    def exists(self):
        return os.path.exists(self.path)
    
    def close(self):
        if not self.handle:
            return True
        self.handle.close()
        self.handle = False

if __name__ == '__main__':
    path = os.path.join('c:', os.path.sep, 'qobuzdb', 'db.sqlite3')
    print "Manager, db path: %s" % (path)
    m = Manager(path)
    m.connect()
    m.get('product', {'id': '0825646555819'})
    m.close()