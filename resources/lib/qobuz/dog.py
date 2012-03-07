import re

class dog():

    def __init__(self):
        self.allowed_keys = {
                             'mode'      : '^\d{1,10}$',
                             'nid'       : '^\d{1,14}$',
                             'nt'        : '^\d{1,10}$',
                             'genre-type': '^(editor-picks|best-sellers|press-awards|new-releases)$',
                             'genre-id'  : '^\d+$',
                             }

    ''' Match value against regexp '''
    def kv_is_ok(self, key, value):
        print key + ' - ' + value
        if key not in self.allowed_keys:
            return False
        match = None
        try: match = re.match(self.allowed_keys[key], value)
        except: pass
        if match == None:
            return False
        return True
