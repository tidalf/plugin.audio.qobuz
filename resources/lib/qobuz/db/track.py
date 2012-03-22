import pprint
from itable import Itable
import qobuz
class Track(Itable):

    def __init__(self, id = None):
        super(Track, self).__init__(id)
        self.table_name = 'track'
        self.pk = 'id'
        self.fields_name = {'id'               : {'jsonmap': None, 'sqltype': 'INTEGER PRIMARY KEY'},
                            'album_id'        : {'jsonmap': ('album', 'id'), 'sqltype':  'INTEGER'},
                            'composer_id'        : {'jsonmap': ('composer', 'id'), 'sqltype':  'INTEGER'},
                            'copyright'          : {'jsonmap': 'copyright', 'sqltype': 'VARCHAR'},
                            'duration'           : {'jsonmap': 'duration', 'sqltype': 'INTEGER'},
                            'interpreter_id' : {'jsonmap': ('interpreter', 'id'), 'sqltype': 'INTEGER'},
                            'media_number'   : {'jsonmap': 'media_number', 'sqltype': 'INTEGER'},
                            'streaming_type' :{'jsonmap': 'streaming_type', 'sqltype': 'VARCHAR'},
                            'title': {'jsonmap': 'title', 'sqltype': 'VARCHAR'},
                            'track_number': {'jsonmap': 'track_number', 'sqltype': 'INTEGER'},
                            'version': {'jsonmap': 'version', 'sqltype': 'VARCHAR'},
                            'work': {'jsonmap': 'work', 'sqltype': 'VARCHAR'},
                            }

    def fetch(self, handle, id):
        from album import Album
        print "Fetching track with id: " + str(id)
        jtrack = qobuz.api.get_track(id)
        if not jtrack:
            print "Cannot fetch data"
            return False
        print pprint.pformat(jtrack)
        where = {}
        if 'album' in jtrack:
            A = Album()
            album = A.get(handle, jtrack['album']['id'])
            if not album:
                A.insert_json(handle, jtrack['album'])
        for field in self.fields_name.keys():
            f = self.fields_name[field]
            if not f['jsonmap']: continue
            value = self.get_property(jtrack, f['jsonmap'])
            if not value: continue
            where[field] = value
        artist = None
        artist_type = ('artist', 'interpreter', 'composer')
        for a in artist_type:
            if a in jtrack and jtrack[a]['name'] and jtrack[a]['name'] != 'None':
                artist = jtrack[a]
                break
        where['ZARTIST'] = artist['id']
        self.insert(handle, where)
        print pprint.pformat(where)
        return False

