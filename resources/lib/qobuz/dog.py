import re

class dog():
    
    def __init__(self):
        self.allowed_keys = {
                             'mode'      : '^\d{1,10}$',
                             'nid'       : '^\d{1,14}$',
                             'nt'        : '^\d{1,10}$',
#                             'id'        : '^\d{1,14}$',

#                             'genre_id'  : '^\d{1,3}$',
#                             'genre'     : '^(\d{1,3}|null)$', # Duplicate genre_id
#                             'genre_type': '^[\w\d_-]+$',
#                             'type'      : '^[\w\d_-]+$', # Duplicate genre_type
#                             'query'     : '^$[\w\d :_-]{1,20}',
#                             'url'       : '^.*$',
#                             'tracks_id' : '^\d{1,20}$',
#                             'search-type': '^(songs|albums|artists)$',
#                             'display-by': '^(songs|product)$',
                             }            
    
    ''' Match value against regexp '''
    def kv_is_ok(self, key, value):
        print key  + ' - ' + value
        if key not in self.allowed_keys:
            return False
        match = None
        try: match = re.match(self.allowed_keys[key], value)
        except: pass
        if match == None:
            return False
        return True 