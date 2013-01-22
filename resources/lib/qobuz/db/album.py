import pprint
from itable import Itable

__fields__ = {
'id'          : {'map': 'id', 'type': 'INTEGER PRIMARY KEY'},
'description' : {'map': 'description', 'type': 'VARCHAR'},
'price'       : {'map': 'price', 'type': 'INTEGER'},
'release_date': {'map': 'release_date', 'type': 'VARCHAR'},
'subtitle'    : {'map': 'subtitle', 'type': 'VARCHAR'},
'title'       : {'map': 'title', 'type': 'VARCHAR'},
'url'         : {'map': 'url', 'type': 'VARCHAR'},
''' Foreign key '''
'artist'      : { 'ref': 'artist'},
'genre'       : { 'ref': 'genre' },
'image'       : { 'ref': 'image' },
'label'       : { 'ref': 'label' }
}
class Album(Itable):

    def __init__(self,id=None):
        super(Album,self).__init__(id)
        self.table_name = 'album'
        self.pk = 'id'
        self.fields_name = __fields__

    def fetch(self,handle,id):
        pass
#        from track import Track
#        from artist import Artist
#        from genre import Genre
#        from label import Label
#        print "plop"
#        data = easyapi.get('/album/get', album_id=id)
#        if not data:
#            print "Cannot fetch data"
#            return False
#        print "JPRODUCT: " + pprint.pformat(data)
#        where = {}
#        for artist in ['artist', 'composer', 'interpreter', 'performer']:
#            if not artist in data:
#                continue
#            print "Inserting artist type %s: %s" % (artist, repr(data['artist']))
#            A = Artist()
#            if not A.get(handle, data[artist]['id']):
#                A.insert(handle, data[artist])
#        if 'genre' in data:
#            G = Genre()
#            if not G.get(handle, data['genre']['id']):
#                G.insert(handle, data['genre'])
#        if 'label' in data:
#            L = Label()
#            if not L.get(handle, data['label']['id']):
#                L.insert(handle, data['label'])
#        # AUTO MAP JSON
#        for field in self.fields_name.keys():
#            f = self.fields_name[field]
#            if not f['jsonmap']: continue
#            value = self.get_property(data, f['jsonmap'])
#            if not value: continue
#            where[field] = value
#        for track_data in data['tracks']['items']:
#            if 'performer' in track_data:
#                print "NEED INSERT PERFORMER"
#                track_data['performer_id'] = track_data['performer']['id']
#                del track_data['performer']
#                
#            track_data['album_id'] = data['id']
#            print "TRACK: " + pprint.pformat(track_data)
#            T = Track()
#            if T.get(handle, track_data['id']):
#                continue
#            T.insert(handle, track_data)
#        self.insert(handle, where)


#    def insert_json(self,handle,json):
#        where = {}
#        for field in self.fields_name.keys():
#            f = self.fields_name[field]
#            if not f['jsonmap']: continue
#            value = self.get_property(json,f['jsonmap'])
#            if not value: continue
#            where[field] = value
#        return self.insert(handle,where)

if __name__ == '__main__':
    print "Testing album"
    from manager import Manager
    m = Manager('c:\\qobuzdb\\test-album.sqlite3')
    m.connect()
    a = Album()
    a.create(m.handle)
    
    