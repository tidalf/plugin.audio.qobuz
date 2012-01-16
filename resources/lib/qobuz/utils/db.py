import os
import pprint
import time

from debug import info, warn
try:
    from sqlite3 import dbapi2 as sqlite
    info('sqlite', "Loading sqlite3 as DB engine")
except:
    from pysqlite2 import dbapi2 as sqlite
    info('sqlite', "Loading pysqlite2 as DB engine")
    
    
class QobuzDb(object):

    def __init__(self, path, name):
        self.path = path
        self.name = name
        self.conn = None
        
    def open(self):
        print "Sqlite: Opening database"
        if self.is_open():
            return True
        conn = sqlite.connect(os.path.join(self.path, self.name))
        if not conn:
            return False
        conn.row_factory = sqlite.Row
        self.conn = conn
        return True
    
    def close(self):
        print "Sqlite: Closing database"
        self.conn.close()
        self.conn = None
        
    def is_open(self):
        if self.conn:
            return True
        return False
    
    '''
        ALBUM
    '''
    def get_album(self, id):
        id = str(id).strip()
        print "Get Album with id: " + id
        q = 'SELECT * FROM albums WHERE album_id = ?'
        cursor = self.conn.cursor()
        cursor.execute(q, [id])
        return cursor.fetchone()
    
    def insert_album(self, json):
        id = str(json['id'].strip())
        album = self.get_album(id)
        if album:
            print "Album already in database"
            return album
        print "Need to insert album in database"
        q = "INSERT INTO albums (id, album_id, title, release_date) VALUES (NULL, ?, ?, ?)"
        c = self.conn.cursor()
        c.execute(q, [id, json['title'], json['release_date']])
        self.conn.commit()
        return self.get_album(id)
    
    '''
        TRACK
    '''
    def get_track(self, id):
        id = str(id).strip()
        print "Getting track id: " + id + "\n"
        q = "SELECT * FROM tracks WHERE track_id = ?"
        cursor = self.conn.cursor()
        cursor.execute(q, [id])
        return cursor.fetchone()
    
    def update_track(self, track_id, name, value):
        track_id = str(track_id).strip()
        ti = int(time.time())
        q = "UPDATE tracks SET " + name + " = ?, updated_on = ? WHERE track_id = ?"
        c = self.conn.cursor()
        c.execute(q, [ value, ti, track_id,])
        self.conn.commit()
    
    def insert_track(self, json):
        print "\n" + pprint.pformat(json) + "\n"
        id = str(json['id']).strip()
        track_id = self.get_track(id)
        album = None
        if track_id:
            print "Track already in database"
            return track_id
        if 'album' in json:
            print "album in json\n"
            album = self.insert_album(json['album'])
            if not album:
                print "Cannot insert track without album_id"
                return None
        c = self.conn.cursor()
        print "Album ID: " + str(album['album_id'])
        ti = int(time.time())
        q = 'INSERT INTO tracks (id, track_id, album_id, track_number, title, media_number, duration, streaming_type, played_count, last_played_on, updated_on, created_on) VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, NULL, NULL, ?, ?)'
        c.execute(q, [id, album['album_id'], json['track_number'], json['title'], json['media_number'], json['duration'], json['streaming_type'], ti, ti])
        self.conn.commit()
        return self.get_track(id)
        
        