import pprint
from itable import Itable
class Track(Itable):

    def __init__(self, id = None):
        super(Track, self).__init__(id)
        self.table_name = 'track'
        self.pk = 'id'
        self.fields_name = {
            'id': { 'jsonmap': 'id', 'sqltype': 'INTEGER PRIMARY KEY' },
                            'album_id'        : {'jsonmap': ('album_id'), 'sqltype':  'INTEGER'},
                            'composer_id'        : {'jsonmap': ('composer', 'id'), 'sqltype':  'INTEGER'},
                            'copyright'          : {'jsonmap': 'copyright', 'sqltype': 'VARCHAR'},
                            'duration'           : {'jsonmap': 'duration', 'sqltype': 'INTEGER'},
                            'interpreter_id' : {'jsonmap': ('interpreter', 'id'), 'sqltype': 'INTEGER'},
                            'performer_id'   : {'jsonmap': ('performer', 'id'), 'sqltype': 'INTEGER'},
                            'media_number'   : {'jsonmap': 'media_number', 'sqltype': 'INTEGER'},
                            'streaming_type' :{'jsonmap': 'streaming_type', 'sqltype': 'VARCHAR'},
                            'title': {'jsonmap': 'title', 'sqltype': 'VARCHAR'},
                            'track_number': {'jsonmap': 'track_number', 'sqltype': 'INTEGER'},
                            'version': {'jsonmap': 'version', 'sqltype': 'VARCHAR'},
                            'work': {'jsonmap': 'work', 'sqltype': 'VARCHAR'},
                            'genre_id': {'jsonmap': ('album', 'genre', 'id'), 'sqltype': 'INTEGER'},
                            'streamable': {'jsonmap': 'streamable', 'sqltype': 'INTEGER'},
                            'purchasable': {'jsonmap': 'purchasable', 'sqltype': 'INTEGER'},
                            }

    def fetch(self, handle, id):
        from product import Product
        from artist import Artist
        jtrack = qobuz.api.get_track(id)
        if not jtrack:
            print "Cannot fetch data"
            return False
        print pprint.pformat(jtrack)
        where = {}
        if 'album' in jtrack:
            P = Product()
            album = P.get(handle, jtrack['album']['id'])
            if not album:
                P.insert_json(handle, jtrack['album'])
        for field in self.fields_name.keys():
            f = self.fields_name[field]
            if not f['jsonmap']: continue
            value = self.get_property(jtrack, f['jsonmap'])
            if not value: continue
            where[field] = value
        if 'interpreter' in jtrack:
            I = Artist()
            interpreter = I.get(handle, jtrack['interpreter'])
            if not interpreter:
                I.insert(handle, jtrack['interpreter'])
        if 'performer' in jtrack:
            I = Artist()
            interpreter = I.get(handle, jtrack['performer'])
            if not interpreter:
                I.insert(handle, jtrack['performer'])
        artist = None
        artist_type = ('artist', 'interpreter', 'composer', 'performer')
        for a in artist_type:
            if a in jtrack and jtrack[a]['name'] and jtrack[a]['name'] != 'None':
                artist = jtrack[a]
                break
        self.insert(handle, where)
        return False

    def insert_json(self, handle, json):
        print "JSON: " + pprint.pformat(json)
        from product import Product
        from artist import Artist
        where = {}
        subtype = ['album', 'interpreter', 'composer', 'performer']
        for type in subtype:
            if type in json:
                db = None
                if type == 'album': db = Product()
                elif type in ['interpreter', 'composer', 'performer']: 
                    db = Artist()
                if not 'id' in json[type] or not json[type]['id']: continue
                if not db.get(handle, int(json[type]['id'])):
                    db.insert_json(handle, json[type])
        for field in self.fields_name.keys():
            f = self.fields_name[field]
            if not f['jsonmap']: continue
            value = self.get_property(json, f['jsonmap'])
            if not value: continue
            where[field] = value
        print "Where %s" % (pprint.pformat(where))
        return self.insert(handle, where)

